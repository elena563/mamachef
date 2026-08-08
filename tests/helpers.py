from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

class ImageMixin:
    def make_image(self, size=(400, 400), color='red'):
        buffer = BytesIO()
        Image.new('RGB', size, color).save(buffer, 'PNG')
        buffer.seek(0)
        return buffer

    def make_upload(self, name='dish.png'):
        return SimpleUploadedFile(name, self.make_image().read(), content_type='image/png')