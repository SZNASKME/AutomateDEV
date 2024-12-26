from pathlib import Path
import sys

if getattr(sys, "frozen", False):
    base_dir = Path(sys._MEIPASS)
else:
    base_dir = Path(__file__).parent.parent

BASE_PATH = base_dir
APP_LOGO_PATH = base_dir / "Assets" / "Icon" / "Stonebranch_icon.png"
FEATURES_JSON_PATH = base_dir / "enableFeatures.json"