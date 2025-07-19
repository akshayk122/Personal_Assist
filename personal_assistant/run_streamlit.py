#!/usr/bin/env python3
"""
Launch script for the Personal Assistant Streamlit UI
"""
import subprocess
import sys
import os

def main():
    """Launch the Streamlit app"""
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    streamlit_file = os.path.join(script_dir, "streamlit_ui.py")
    
    # Launch streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", streamlit_file]
    
    print("Launching Personal Assistant Streamlit UI...")
    print("UI will be available at: http://localhost:8501")
    print("Make sure your ACP servers are running!")
    print("---")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nShutting down Streamlit UI...")
    except subprocess.CalledProcessError as e:
        print(f"Error launching Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 