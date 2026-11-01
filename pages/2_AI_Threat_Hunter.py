import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai_threat_hunter"))
os.chdir(os.path.join(os.path.dirname(__file__), "..", "ai_threat_hunter"))
exec(open(os.path.join(os.path.dirname(__file__), "..", "ai_threat_hunter", "app.py")).read())
