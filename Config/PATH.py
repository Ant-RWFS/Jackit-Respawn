from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#Frontend
FRONTEND_DICT = f"{ROOT}/Frontend"
ASSET_DICT = f"{FRONTEND_DICT}/Asset"
FONT_DICT = f"{ASSET_DICT}/Font"
VIDEO_DICT = f"{ASSET_DICT}/Video"

FONT = {
    "cyber_siberia": f"{FONT_DICT}/CyberSiberia.ttf",
    "moon_house": f"{FONT_DICT}/MoonHouse.ttf",
}
VIDEO = {
    "intro": f"{VIDEO_DICT}/intro.mp4"
}

#Database
DATA_DICT = f'{ROOT}/Data'
DATABASE = f'{DATA_DICT}/test.db'
