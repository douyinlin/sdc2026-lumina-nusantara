"""Compatibility entry point for the current guided-UI browser check."""
from pathlib import Path
import runpy
if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("check_post_selection_ui.py")), run_name="__main__")
