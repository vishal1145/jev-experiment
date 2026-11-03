import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)


class Config:
    DATABASE = os.getenv(
        "DATABASE_PATH",
        str(INSTANCE_DIR / "smartdesk.db")
    )

    FRONTEND_ORIGIN = os.getenv(
        "FRONTEND_ORIGIN",
        "http://localhost:5173"
    )

    JEV_MODEL = os.getenv("JEV_MODEL", "jev-latest")

    HUMAN_REVIEW_THRESHOLD = float(
        os.getenv("HUMAN_REVIEW_THRESHOLD", "0.65")
    )
