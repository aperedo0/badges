"""Remove only generated packaging duplicates; retain the editable sources."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parent
for folder in [root/'shell_pkg',root/'clean/pkg',root/'clean/calibration_pkg',root/'__pycache__']:
    if folder.exists():shutil.rmtree(folder)
for file in [root/'clean/front_geometry.json',root/'clean/calibration.usdz',root/'clean/calibration.json']:
    file.unlink(missing_ok=True)
