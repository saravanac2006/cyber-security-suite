"""Page wrapper — delegates to ai_threat_hunter/app.py, isolating its core package."""
import sys
import os
import runpy

_ROOT    = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_APP_DIR = os.path.join(_ROOT, "ai_threat_hunter")
_APP_FILE = os.path.join(_APP_DIR, "app.py")
_OTHER   = os.path.join(_ROOT, "deepfake_detector")

# ── Isolate this project's 'core' package from the other project's ────────────
# Flush any cached core.* modules that may belong to the other project
for _k in list(sys.modules.keys()):
    if _k == "core" or _k.startswith("core."):
        del sys.modules[_k]

# Remove the other project from sys.path; put this one first
if _OTHER in sys.path:
    sys.path.remove(_OTHER)
if _APP_DIR not in sys.path:
    sys.path.insert(0, _APP_DIR)

_prev_cwd = os.getcwd()
os.chdir(_APP_DIR)
try:
    runpy.run_path(_APP_FILE, run_name="__main__")
finally:
    os.chdir(_prev_cwd)
