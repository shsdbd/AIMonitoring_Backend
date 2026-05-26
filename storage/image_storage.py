from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status


STATIC_DIR = Path("static")
IMAGE_DIR = STATIC_DIR / "images"
ALLOWED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}


async def save_upload_image(image: UploadFile) -> tuple[Path, str]:
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="png 또는 jpeg 이미지 파일만 업로드할 수 있습니다.",
        )

    suffix = Path(image.filename or "").suffix.lower()
    if suffix not in ALLOWED_IMAGE_SUFFIXES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="파일 확장자는 .png, .jpg, .jpeg만 허용됩니다.",
        )

    date_path = datetime.now().strftime("%Y/%m/%d")
    save_dir = IMAGE_DIR / date_path
    save_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}{suffix}"
    save_path = save_dir / filename

    with save_path.open("wb") as buffer:
        while chunk := await image.read(1024 * 1024):
            buffer.write(chunk)

    return save_path, f"/static/images/{date_path}/{filename}"
