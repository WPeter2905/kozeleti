#!/usr/bin/env python
import subprocess
import sys
import os
import time
import webbrowser

try:
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"Starting Streamlit app from: {script_dir}")
    
    # Try to find and use venv Python
    venv_python = os.path.join(script_dir, ".venv", "bin", "python")
    
    if os.path.exists(venv_python):
        python_exe = venv_python
        print(f"Using virtual environment: {python_exe}")
    else:
        python_exe = sys.executable
        print(f"Virtual environment not found, using system Python: {python_exe}")
    
    print("Launching Streamlit...")
    
    # Try to open browser after a delay
    def open_browser():
        time.sleep(4)
        try:
            print("Opening browser to http://localhost:8501")
            webbrowser.open("http://localhost:8501")
        except Exception as e:
            print(f"Could not open browser: {e}")
    
    import threading
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Run streamlit
    subprocess.run([python_exe, "-m", "streamlit", "run", "app.py", "--logger.level=error"], check=False)

except KeyboardInterrupt:
    print("\nStopping application...")
    sys.exit(0)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
