from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from core.errors import bad_request


STATIC_DIR = Path("static")
IMAGE_DIR = STATIC_DIR / "images"
ALLOWED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}


async def save_upload_image(image: UploadFile) -> tuple[Path, str]:
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise bad_request(
            error_code="UNSUPPORTED_IMAGE_CONTENT_TYPE",
            message="png 또는 jpeg 이미지 파일만 업로드할 수 있습니다.",
            detail={"content_type": image.content_type},
        )

    suffix = Path(image.filename or "").suffix.lower()
    if suffix not in ALLOWED_IMAGE_SUFFIXES:
        raise bad_request(
            error_code="UNSUPPORTED_IMAGE_EXTENSION",
            message="파일 확장자는 .png, .jpg, .jpeg만 허용됩니다.",
            detail={"filename": image.filename},
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
