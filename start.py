#!/usr/bin/env python
import subprocess
import sys
import time
import webbrowser

# Run streamlit in the background
process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py", "--logger.level=error"])

# Wait a moment for Streamlit to start
time.sleep(3)

# Open the browser to localhost:8501
webbrowser.open("http://localhost:8501")

# Keep the process running
try:
    process.wait()
except KeyboardInterrupt:
    process.terminate()
