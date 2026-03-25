import uuid
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile
import aiofiles
import logging

logger = logging.getLogger(__name__)

class ImageUploadService:
    def __init__(self, upload_dir: str = "static/products"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)


    async def save_image(
        self,
        file: UploadFile,
        product_id: int,
        is_main: bool = False
    ) -> Tuple[str, int, str]:
        ext = Path(file.filename).suffix.lower()
        filename = f"{product_id}_{uuid.uuid4().hex}{ext}"
        subfolder = "main" if is_main else "gallery"

        file_path = self.upload_dir / subfolder / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        content = await file.read()
        file_size = len(content)

        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)

        url = f"/static/products/{subfolder}/{filename}"
        return url, file_size, file.content_type


    @staticmethod
    async def delete_image(image_url: str) -> bool:
        """Delete image file by URL.

        Args:
            image_url: URL of the image to delete

        Returns:
            bool: True if file was deleted, False otherwise
        """
        try:
            file_path = Path(image_url.lstrip('/'))

            if not str(file_path).startswith('static/'):
                return False

            if not file_path.exists():
                return False

            if not file_path.is_file():
                return False

            file_path.unlink()
            return True

        except PermissionError:
            return False

        except OSError as e:
            logger.error(f"OS error when deleting {image_url}: {e}")
            return False

        except Exception as e:
            logger.error(f"Unexpected error when deleting {image_url}: {e}", exc_info=True)
            return False
