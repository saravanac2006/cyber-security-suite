"""
AI-powered threat explainer with MITRE ATT&CK mapping, kill chain, and IR playbook.
Uses key rotation — no API key required from the user.
"""
import json
import re
import pandas as pd
from core.key_rotator import next_key, mark_exhausted, save_user_key

try:
    import anthropic
    _ANTHROPIC_OK = True
except ImportError:
    _ANTHROPIC_OK = False

_ANALYSIS_PROMPT = """You are a Principal Threat Intelligence Analyst and Incident Responder with 15+ years
of SOC experience. You specialise in MITRE ATT&CK mapping, malware analysis, and enterprise incident response.

You have been handed the following network security alert from an IDS/ML detection system.
Perform an exhaustive, evidence-based analysis. Every claim must reference the specific data provided.
Do NOT give generic advice — be precise, context-aware, and actionable.

ALERT DATA:
- Threat Type     : {label}
- Source IP       : {src_ip}
- Destination IP  : {dst_ip}
- Destination Port: {dst_port}
- Source Port     : {src_port}
- Protocol        : {protocol}
- Bytes Sent      : {bytes_sent:,} bytes
- Bytes Received  : {bytes_recv:,} bytes
- Session Duration: {duration}s
- Firewall Action : {action}
- User Account    : {user}
- ML Risk Score   : {risk}/100
- Timestamp       : {timestamp}

ANALYSIS REQUIREMENTS — be exhaustive on every section:

1. THREAT CLASSIFICATION: What exact attack technique does this represent?
2. MITRE ATT&CK: Map to specific tactic + technique + sub-technique (use real T-numbers)
3. KILL CHAIN PHASE: Which Cyber Kill Chain phase (Recon / Weaponization / Delivery / Exploitation / Installation / C2 / Exfiltration)?
4. EVIDENCE ANALYSIS: What specific data points prove this is malicious vs. benign?
5. IMPACT ASSESSMENT: What damage could occur if not contained — data loss, lateral movement, persistence?
6. THREAT ACTOR PROFILE: Type of attacker (script kiddie / APT / insider), sophistication, likely motivation
7. INDICATORS OF COMPROMISE: Specific IOCs derived from this alert (IPs, ports, patterns)
8. IMMEDIATE ACTIONS: First 15 minutes — what must a SOC analyst do RIGHT NOW?
9. INVESTIGATION STEPS: Forensic investigation plan — what logs, endpoints, packets to check?
10. CONTAINMENT & ERADICATION: How to stop the attack and clean up
11. LONG-TERM REMEDIATION: Architecture/policy changes to prevent recurrence
12. FALSE POSITIVE ASSESSMENT: How confident are you this is real? What could explain it innocently?

Respond ONLY with valid JSON — no markdown, no extra text:
{{
  "severity": "CRITICAL|HIGH|MEDIUM|LOW",
  "confidence": <0-100>,
  "title": "<specific descriptive title — not generic>",
  "threat_category": "<one-word category: Reconnaissance|Initial Access|Execution|Persistence|Privilege Escalation|Defense Evasion|Credential Access|Discovery|Lateral Movement|Collection|Exfiltration|Impact|C2>",
  "mitre_attack": {{
    "tactic_id": "TA####",
    "tactic_name": "<tactic name>",
    "technique_id": "T####",
    "technique_name": "<technique name>",
    "sub_technique_id": "T####.###",
    "sub_technique_name": "<sub-technique name or null>"
  }},
  "kill_chain_phase": "<phase name>",
  "executive_summary": "<3-4 sentence professional summary of the attack, what happened, and why it is dangerous>",
  "evidence_analysis": "<2-3 sentences citing specific data points from the alert that prove malicious intent>",
  "impact_assessment": "<2-3 sentences on what damage could occur — data loss, system compromise, lateral movement>",
  "threat_actor_profile": {{
    "type": "<Automated Script|Botnet|Opportunistic Attacker|Targeted APT|Insider Threat|Unknown>",
    "sophistication": "<Low|Medium|High|Nation-State>",
    "motivation": "<Financial|Espionage|Disruption|Data Theft|Credential Harvesting|Unknown>",
    "analysis": "<1-2 sentences on why you assessed this actor type>"
  }},
  "false_positive_likelihood": "<Very Low|Low|Medium|High>",
  "false_positive_explanation": "<what innocent scenario could generate this pattern>",
  "indicators_of_compromise": [
    "<specific IOC — IP:port, hash, pattern>",
    "<second IOC>",
    "<third IOC>"
  ],
  "immediate_actions": [
    "<action 1 — specific, with urgency>",
    "<action 2>",
    "<action 3>",
    "<action 4>"
  ],
  "investigation_steps": [
    "<step 1 — specific log source or tool>",
    "<step 2>",
    "<step 3>",
    "<step 4>"
  ],
  "containment_eradication": [
    "<containment step 1>",
    "<eradication step 2>"
  ],
  "long_term_remediation": [
    "<architectural or policy change 1>",
    "<change 2>",
    "<change 3>"
  ],
  "related_threat_types": ["<related threat>", "<related threat>"],
  "analyst_notes": "<any caveats, edge cases, or additional context>"
}}"""


_RULE_FALLBACK = {
    "Port Scan": {
        "severity": "HIGH", "confidence": 85,
        "title": "Network Reconnaissance — Multi-Port Scan",
        "threat_category": "Reconnaissance",
        "mitre_attack": {"tactic_id": "TA0043", "tactic_name": "Reconnaissance",
                         "technique_id": "T1046", "technique_name": "Network Service Discovery",
                         "sub_technique_id": None, "sub_technique_name": None},
        "kill_chain_phase": "Reconnaissance",
        "executive_summary": "A source IP conducted systematic probing of multiple destination ports, exhibiting classic pre-attack reconnaissance. This activity maps directly to MITRE T1046 and is typically the first phase before targeted exploitation of discovered open services.",
        "evidence_analysis": "High volume of connection attempts across multiple ports with minimal bytes transferred per connection, consistent with SYN scanning. Most connections result in DENY, confirming this is probing not legitimate traffic.",
        "impact_assessment": "If the attacker identifies open services, they will pivot to exploitation. Unpatched services discovered during this scan are at immediate risk. Lateral movement is likely if internal hosts are reached.",
        "threat_actor_profile": {"type": "Automated Script", "sophistication": "Low", "motivation": "Credential Harvesting", "analysis": "Automated scanning tools (nmap, masscan) are used; low sophistication consistent with opportunistic attacker."},
        "false_positive_likelihood": "Low",
        "false_positive_explanation": "Legitimate vulnerability scanners (Nessus, Qualys) generate similar patterns — verify if a scheduled scan was authorized.",
        "indicators_of_compromise": ["Source IP scanning multiple ports", "< 500 bytes per connection", "High DENY rate on firewall"],
        "immediate_actions": ["Block source IP at perimeter firewall", "Alert network security team", "Check if any scanned ports are publicly exposed", "Add IP to threat intel blocklist"],
        "investigation_steps": ["Pull all logs for source IP in last 24h", "Check if any scanned port had ALLOW action", "Correlate with IDS signatures", "GeoIP lookup on source IP"],
        "containment_eradication": ["Block IP at firewall and border router", "Add to SIEM watchlist for 30 days"],
        "long_term_remediation": ["Deploy IDS rule to auto-block IPs exceeding 10 ports/minute", "Implement network segmentation", "Harden firewall egress rules"],
        "related_threat_types": ["Brute Force", "Exploitation of Public-Facing Application"],
        "analyst_notes": "Cross-check with authorized scan schedules before escalating.",
    },
    "Brute Force": {
        "severity": "CRITICAL", "confidence": 92,
        "title": "Credential Brute-Force — SSH/RDP Service",
        "threat_category": "Credential Access",
        "mitre_attack": {"tactic_id": "TA0006", "tactic_name": "Credential Access",
                         "technique_id": "T1110", "technique_name": "Brute Force",
                         "sub_technique_id": "T1110.001", "sub_technique_name": "Password Guessing"},
        "kill_chain_phase": "Exploitation",
        "executive_summary": "An external IP is conducting automated credential brute-forcing against an authentication service (SSH/RDP). This MITRE T1110.001 technique is used to gain initial foothold by exhausting password combinations. Immediate blocking is required to prevent unauthorized access.",
        "evidence_analysis": "Repeated DENY actions on port 22 or 3389 from a single source IP within a short window indicates automated login attempts. The pattern of small, frequent requests matches common tools like Hydra and Medusa.",
        "impact_assessment": "Successful credential compromise grants the attacker a persistent foothold. They can establish SSH tunnels for lateral movement, deploy ransomware, or exfiltrate sensitive data. RDP compromise is particularly severe as it provides full GUI access.",
        "threat_actor_profile": {"type": "Automated Script", "sophistication": "Low", "motivation": "Credential Harvesting", "analysis": "High-volume automated tool usage; likely a botnet or commodity cracking tool targeting default credentials."},
        "false_positive_likelihood": "Very Low",
        "false_positive_explanation": "Unlikely to be false positive unless a legitimate user forgot their password repeatedly — check account lockout logs.",
        "indicators_of_compromise": ["Source IP with >50 auth failures/minute", "Destination port 22 or 3389", "DENY action on every attempt"],
        "immediate_actions": ["Block source IP at firewall IMMEDIATELY", "Check if any login succeeded (ALLOW action)", "Lock affected user accounts as precaution", "Enable geo-blocking if IP is from unexpected country"],
        "investigation_steps": ["Pull auth logs from target server", "Check for any successful logins from source IP", "Review account lockout events in Active Directory", "Correlate with VPN logs"],
        "containment_eradication": ["Block IP at all network perimeter points", "Force password reset for targeted accounts", "Enable MFA on all remote access services"],
        "long_term_remediation": ["Enforce MFA on SSH/RDP", "Implement fail2ban or equivalent", "Deploy privileged access workstation (PAW)", "Disable password auth — use SSH keys only"],
        "related_threat_types": ["C2 / Suspicious", "Data Exfiltration"],
        "analyst_notes": "Check if this IP appears in threat intel feeds (AbuseIPDB, VirusTotal).",
    },
    "Data Exfiltration": {
        "severity": "CRITICAL", "confidence": 88,
        "title": "Large-Scale Data Exfiltration Detected",
        "threat_category": "Exfiltration",
        "mitre_attack": {"tactic_id": "TA0010", "tactic_name": "Exfiltration",
                         "technique_id": "T1048", "technique_name": "Exfiltration Over Alternative Protocol",
                         "sub_technique_id": "T1048.003", "sub_technique_name": "Exfiltration Over Unencrypted Non-C2 Protocol"},
        "kill_chain_phase": "Exfiltration",
        "executive_summary": "An internal host transferred an abnormally large data volume to an external destination, strongly indicating unauthorized data exfiltration. This is a critical severity incident requiring immediate host isolation to prevent further data loss.",
        "evidence_analysis": "Outbound bytes far exceed baseline — the upload-to-download ratio is highly asymmetric. The destination IP is not in approved egress whitelist. Data transfer magnitude suggests entire file collections, databases, or disk images are being sent.",
        "impact_assessment": "Depending on data classification, this could represent a notifiable data breach under GDPR/HIPAA. Sensitive PII, IP, credentials, or financial data may be compromised. Regulatory fines and reputational damage are likely consequences.",
        "threat_actor_profile": {"type": "Insider Threat", "sophistication": "Medium", "motivation": "Data Theft", "analysis": "Internal source suggests compromised internal host or malicious insider. The large transfer volume implies deliberate, pre-planned data staging."},
        "false_positive_likelihood": "Low",
        "false_positive_explanation": "Could be authorized cloud backup to a new destination — verify with asset owner and check if transfer was scheduled.",
        "indicators_of_compromise": ["Internal host transferring >1MB to external IP", "Unusual destination not in whitelist", "Transfer during off-hours"],
        "immediate_actions": ["ISOLATE source host from network immediately", "Preserve memory dump and disk image", "Notify CISO and legal team", "Identify what data was accessible on source host"],
        "investigation_steps": ["Pull SIEM logs for source host last 72h", "Check what files/directories were accessed before transfer", "Identify all external connections from source IP", "Review DLP alerts"],
        "containment_eradication": ["Isolate host in quarantine VLAN", "Revoke all credentials associated with host", "Block destination IP at all egress points"],
        "long_term_remediation": ["Deploy DLP solution with content inspection", "Implement egress filtering and proxy", "Classify and encrypt sensitive data at rest", "Zero-trust network access (ZTNA)"],
        "related_threat_types": ["C2 / Suspicious", "Lateral Movement"],
        "analyst_notes": "Determine if breach notification is required — document all findings for legal.",
    },
    "C2 / Suspicious": {
        "severity": "HIGH", "confidence": 80,
        "title": "Command & Control Beaconing — Malware Suspected",
        "threat_category": "C2",
        "mitre_attack": {"tactic_id": "TA0011", "tactic_name": "Command and Control",
                         "technique_id": "T1071", "technique_name": "Application Layer Protocol",
                         "sub_technique_id": "T1071.001", "sub_technique_name": "Web Protocols"},
        "kill_chain_phase": "Command & Control",
        "executive_summary": "An internal host is exhibiting periodic low-volume beaconing to an external C2 server. This MITRE T1071 pattern is a hallmark of installed malware awaiting instructions. The host is likely already compromised and under adversary control.",
        "evidence_analysis": "Regular interval connections with symmetric small payloads match C2 keep-alive traffic. The non-standard high port and unusual external destination are strong indicators. This pattern is consistent with RAT or backdoor communication.",
        "impact_assessment": "A compromised host under C2 control gives the adversary persistent access. They can issue commands for lateral movement, deploy additional payloads, conduct reconnaissance, or trigger ransomware encryption at will.",
        "threat_actor_profile": {"type": "Targeted APT", "sophistication": "High", "motivation": "Espionage", "analysis": "Periodic beaconing with jitter and small payload size suggests sophisticated malware with C2 evasion techniques, consistent with APT or advanced criminal group."},
        "false_positive_likelihood": "Medium",
        "false_positive_explanation": "Legitimate software update checks or telemetry services can appear similar — correlate with installed software on host.",
        "indicators_of_compromise": ["Periodic beaconing at regular intervals", "Small symmetric traffic (keep-alive)", "Non-standard high-numbered destination port"],
        "immediate_actions": ["Isolate host in quarantine VLAN without cutting power", "Capture live memory (Volatility)", "Block C2 destination IP/domain at firewall", "Notify IR team immediately"],
        "investigation_steps": ["Memory forensics for injected processes and network sockets", "Check process list for suspicious parent-child relationships", "DNS log review for DGA domains", "Endpoint EDR telemetry review"],
        "containment_eradication": ["Reimage infected host after forensic preservation", "Block all C2 infrastructure at DNS/IP level", "Hunt for lateral movement from this host"],
        "long_term_remediation": ["Deploy EDR solution (CrowdStrike/SentinelOne)", "Implement DNS RPZ for C2 domain blocking", "Enable network traffic inspection", "Threat hunt for similar beaconing patterns across fleet"],
        "related_threat_types": ["Data Exfiltration", "Lateral Movement"],
        "analyst_notes": "Extract C2 payload and submit to malware sandbox for full analysis.",
    },
    "Anomalous Traffic": {
        "severity": "MEDIUM", "confidence": 65,
        "title": "Statistically Anomalous Network Behaviour",
        "threat_category": "Discovery",
        "mitre_attack": {"tactic_id": "TA0007", "tactic_name": "Discovery",
                         "technique_id": "T1040", "technique_name": "Network Sniffing",
                         "sub_technique_id": None, "sub_technique_name": None},
        "kill_chain_phase": "Reconnaissance",
        "executive_summary": "The ML anomaly detection model flagged this event as a statistical outlier compared to the established baseline traffic profile. While the specific threat is unclassified, the deviation from normal behavior warrants investigation.",
        "evidence_analysis": "The combination of traffic volume, timing, protocol, and port usage deviates significantly from peer-group baseline. This could represent an early-stage attack, misconfiguration, or novel threat pattern not matching known signatures.",
        "impact_assessment": "Impact depends on root cause. If malicious, this may represent early reconnaissance or a novel attack technique. Prompt investigation prevents escalation to a more severe incident.",
        "threat_actor_profile": {"type": "Unknown", "sophistication": "Unknown", "motivation": "Unknown", "analysis": "Insufficient evidence to profile actor — further investigation required."},
        "false_positive_likelihood": "Medium",
        "false_positive_explanation": "Software updates, backup jobs, or new applications can cause anomalous traffic. Verify with asset owner.",
        "indicators_of_compromise": ["Statistical deviation from traffic baseline", "Unusual traffic pattern for host", "Unexpected protocol or port combination"],
        "immediate_actions": ["Log and monitor for recurrence", "Notify asset owner for context", "Pull session details from firewall logs", "Escalate if pattern repeats within 2 hours"],
        "investigation_steps": ["Review full session logs for this host pair", "Check asset inventory for both IPs", "Correlate with change management system", "Review endpoint process list at time of event"],
        "containment_eradication": ["Monitor and track — do not block without confirmation", "Set SIEM alert for any repeat within 24 hours"],
        "long_term_remediation": ["Tune baseline model with confirmed normal traffic", "Improve asset inventory and tagging", "Deploy UEBA for user behavior analysis"],
        "related_threat_types": ["Port Scan", "C2 / Suspicious"],
        "analyst_notes": "Low confidence classification — corroborate with additional sources before escalating.",
    },
}


class ThreatExplainer:
    def __init__(self, user_key: str = ""):
        self._user_key = user_key

    def explain(self, row: pd.Series) -> dict:
        label = str(row.get("anomaly_label", "Anomalous Traffic"))
        key = next_key(self._user_key)
        if key and _ANTHROPIC_OK:
            try:
                result = self._explain_with_ai(row, label, key)
                # If user's own key worked, save it
                if key == self._user_key.strip() and self._user_key.strip():
                    save_user_key(key)
                return result
            except Exception as e:
                msg = str(e)
                if "429" in msg or "quota" in msg.lower() or "overloaded" in msg.lower():
                    mark_exhausted(key)
                # fall through
        return _RULE_FALLBACK.get(label, _RULE_FALLBACK["Anomalous Traffic"])

    def _explain_with_ai(self, row: pd.Series, label: str, key: str) -> dict:
        client = anthropic.Anthropic(api_key=key)
        prompt = _ANALYSIS_PROMPT.format(
            label=label,
            src_ip=row.get("source_ip", "N/A"),
            dst_ip=row.get("dest_ip", "N/A"),
            dst_port=row.get("dest_port", "N/A"),
            src_port=row.get("source_port", "N/A"),
            protocol=row.get("protocol", "N/A"),
            bytes_sent=int(row.get("bytes_sent", 0)),
            bytes_recv=int(row.get("bytes_recv", 0)),
            duration=row.get("duration", 0),
            action=row.get("action", "N/A"),
            user=row.get("user", "N/A"),
            risk=int(row.get("risk_score", 0)),
            timestamp=str(row.get("timestamp", "N/A")),
        )
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            return _RULE_FALLBACK.get(label, _RULE_FALLBACK["Anomalous Traffic"])
        return json.loads(m.group())
