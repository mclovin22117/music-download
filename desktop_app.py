#!/usr/bin/env python3
"""
Launch the desktop application.
"""
import sys
import os

# Change to project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Now import and run
if __name__ == "__main__":
    from app.gui.main_window import main
    main()