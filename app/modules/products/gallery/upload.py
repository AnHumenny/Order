import uuid
import io
from pathlib import Path
from typing import Tuple, Optional
from fastapi import UploadFile
import aiofiles
from PIL import Image
import re
from app.core.config import settings


class ImageUploadService:
    """Service for handling product image uploads to the gallery directory."""

    def __init__(self, upload_dir: str = settings.path_to_image):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_image(
            self,
            file: UploadFile,
            product_id: int,
            category_id: Optional[int]
    ) -> Tuple[str, int, str]:
        """Structure: static/products/{category_id}/{product_id}/"""

        if category_id is not None:
            product_folder = self.upload_dir / str(category_id) / str(product_id)
        else:
            product_folder = self.upload_dir / "0" / str(product_id)

        product_folder.mkdir(parents=True, exist_ok=True)

        filename = f"{uuid.uuid4().hex}.webp"
        file_path = product_folder / filename

        content = await file.read()
        img = Image.open(io.BytesIO(content))

        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        if img.width > 1920 or img.height > 1920:
            img.thumbnail((1920, 1920), Image.Resampling.LANCZOS)

        output = io.BytesIO()
        img.save(output, format="WEBP", quality=85, method=6)
        optimized_content = output.getvalue()

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(optimized_content)

        file_size = len(optimized_content)

        if category_id is not None:
            url = f"/static/products/{category_id}/{product_id}/{filename}"
        else:
            url = f"/static/products/0/{product_id}/{filename}"

        return url, file_size, "image/webp"


    @staticmethod
    def _sanitize_name(name: str) -> str:
        """Clears the name for use on the way"""

        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        name = name.strip().lower()
        name = name[:50]
        return name or "unknown"


    @staticmethod
    async def delete_image(image_url: str) -> bool:
        """Delete image file by URL."""

        try:
            file_path = Path(image_url.lstrip('/'))
            if file_path.exists() and str(file_path).startswith('static/'):
                file_path.unlink()
                return True
        except (PermissionError, OSError):
            pass
        return False
