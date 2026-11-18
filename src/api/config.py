from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

ALLOWED_EXTENSIONS = {".csv"}