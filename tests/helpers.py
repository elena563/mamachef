from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from kitchen.models import Ingredient, Recipe, ShoppingList


class KitchenTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.shopping_list = ShoppingList.objects.create(user=self.user)
        self.recipe = Recipe.objects.create(name="Test Recipe")
        self.tomato = Ingredient.objects.create(name="Tomatoes")
        self.flour = Ingredient.objects.create(name="Flour")


class ImageMixin:
    def make_image(self, size=(400, 400), color="red"):
        buffer = BytesIO()
        Image.new("RGB", size, color).save(buffer, "PNG")
        buffer.seek(0)
        return buffer

    def make_upload(self, name="dish.png"):
        return SimpleUploadedFile(name, self.make_image().read(), content_type="image/png")
