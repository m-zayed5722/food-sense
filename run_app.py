#!/usr/bin/env python3
"""
Simple launcher script for the Menu Enrichment Streamlit app
"""
import subprocess
import sys
import os

def main():
    """Launch the Streamlit app"""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the Streamlit app
    app_path = os.path.join(script_dir, "streamlit_app", "app.py")
    
    try:
        print("🍽️ Starting Menu Item Enrichment App...")
        print("🌐 Navigate to: http://localhost:8501")
        print("⏹️ Press Ctrl+C to stop the server")
        print()
        
        # Launch Streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching app: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()