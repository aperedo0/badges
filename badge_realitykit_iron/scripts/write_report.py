"""Current report entry point; historical implementations are in previous/."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("write_forged_report.py")), run_name="__main__")
