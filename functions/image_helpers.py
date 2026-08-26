from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image


def compress_image(image, quality=82):
    img = Image.open(image).convert("RGB")
    buffer = BytesIO()
    img.save(buffer, format="WEBP", quality=quality)
    name = image.name.rsplit(".", 1)[0] + ".webp"
    return ContentFile(buffer.getvalue(), name=name)
