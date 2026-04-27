import shutil
from pathlib import Path
from uuid import uuid4

from app.config import settings


async def save_uploaded_file(file_bytes: bytes, filename: str, subdir: str = "papers") -> str:
    save_dir = Path(settings.STORAGE_PATH) / subdir
    save_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(filename).suffix or ".bin"
    file_name = f"{uuid4().hex}{ext}"
    file_path = save_dir / file_name

    file_path.write_bytes(file_bytes)
    return str(file_path)


def delete_file(file_path: str) -> bool:
    path = Path(file_path)
    if path.exists():
        path.unlink()
        return True
    return False
