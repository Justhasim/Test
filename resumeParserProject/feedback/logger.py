import os
import json
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def logParse(resume_text, parsed_data, score):
    """Save the raw parse for later analysis."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fn = f"parse_{ts}.json"
    path = os.path.join(LOG_DIR, fn)
    with open(path, "w") as f:
        json.dump({
            "timestamp": ts,
            "resume_text": resume_text,
            "parsed_data": parsed_data,
            "score": score,
            "feedback": None
        }, f, indent=2)
    return fn

def logFeedback(filename, feedback):
    """Append user feedback (True/False) into existing parse log."""
    path = os.path.join(LOG_DIR, filename)
    if not os.path.exists(path):
        return
    data = json.load(open(path))
    data["feedback"] = feedback
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
