import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "deepfake_detector"))
os.chdir(os.path.join(os.path.dirname(__file__), "..", "deepfake_detector"))
exec(open(os.path.join(os.path.dirname(__file__), "..", "deepfake_detector", "app.py")).read())
