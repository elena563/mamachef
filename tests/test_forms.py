import os
import tempfile

from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from functions.recipe_helpers import save_dynamic_fields, save_list_items
from kitchen.forms import RecipeForm
from kitchen.models import Recipe, RecipeIngredient
from tests.helpers import ImageMixin, KitchenTestCase


class RecipeFormTest(TestCase, ImageMixin):
    def valid_data(self):
        return {
            "name": "Test Recipe",
            "description": "This is a test recipe.",
            "difficulty": "Easy",
            "preparation_time": 30,
            "servings": 4,
            "cooking_method": "Baked",
            "category": "Dessert",
        }

    def test_recipe_form_valid(self):
        form = RecipeForm(data=self.valid_data())
        self.assertTrue(form.is_valid())
        recipe = form.save()
        self.assertEqual(Recipe.objects.count(), 1)
        self.assertEqual(recipe.name, "Test Recipe")

    def test_update_recipe(self):
        recipe = Recipe.objects.create(name="Old Name")
        data = self.valid_data()
        data["name"] = "New Name"
        form = RecipeForm(data=data, instance=recipe)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        recipe.refresh_from_db()
        self.assertEqual(recipe.name, "New Name")

    def test_recipe_form_required_fields(self):
        form_data = {
            "name": "",
            "description": "This is a test recipe.",
            "difficulty": "Easy",
            "preparation_time": 30,
            "servings": 4,
            "cooking_method": "Baked",
            "category": "Dessert",
        }
        form = RecipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_recipe_form_validation_errors(self):
        form_data = {
            "name": "A" * 256,  # Exceeds max_length
            "description": "This is a test recipe.",
            "difficulty": "InvalidChoice",  # Not in choices
            "preparation_time": -5,  # Invalid negative value
            "servings": 0,  # Invalid value less than min
            "cooking_method": "Baked",
            "category": "Dessert",
        }
        form = RecipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("difficulty", form.errors)
        self.assertIn("preparation_time", form.errors)
        self.assertIn("servings", form.errors)

    def test_image_asset_and_url_not_both(self):
        data = self.valid_data()
        data["image_url"] = "https://example.com/x.jpg"
        upload = self.make_upload(name="dish.png")
        form = RecipeForm(data=data, files={"image_asset": upload})
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_update_other_user_recipe_denied(self):
        other_user = User.objects.create_user(username="other", password="pass")
        recipe = Recipe.objects.create(name="tomato pasta", author=other_user)
        self.client.login(username="myuser", password="pass")
        response = self.client.post(reverse("Kitchen:edit_recipe", args=[recipe.pk]), self.valid_data())
        self.assertIn(response.status_code, [302, 403])
        recipe.refresh_from_db()
        self.assertEqual(recipe.name, "tomato pasta")  # unchanged


class SaveDynamicFieldsTest(KitchenTestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()

    def _request(self, data):
        request = self.factory.post("/dummy-url/", data)
        request.session = {}
        request._messages = FallbackStorage(request)
        return request

    def test_save_dynamic_fields_with_valid_data(self):
        data = {
            "ingredient": ["Tomatoes", "Flour"],
            "quantity": ["2", "1"],
            "unit": ["pieces", "pieces"],
            "step": ["Chop the tomatoes.", "Mix the flour."],
            "timer": ["5", "3"],
            "used_ingredients_0": "Tomatoes",
            "used_ingredients_1": "Flour",
        }
        request = self._request(data)
        save_dynamic_fields(request, self.recipe)

        self.assertEqual(RecipeIngredient.objects.filter(recipe=self.recipe).count(), 2)
        self.assertEqual(self.recipe.steps.count(), 2)

        step1 = self.recipe.steps.get(order=1)
        step2 = self.recipe.steps.get(order=2)
        self.assertEqual(list(step1.used_ingredients.all()), [self.tomato])
        self.assertEqual(list(step2.used_ingredients.all()), [self.flour])

    def test_save_dynamic_fields_falls_back_to_plain_list(self):
        data = {
            "ingredient": ["Tomatoes"],
            "quantity": ["2"],
            "unit": ["pieces"],
            "step": ["Chop the tomatoes."],
            "timer": ["5"],
            "used_ingredients": ["Tomatoes"],
        }
        request = self._request(data)
        save_dynamic_fields(request, self.recipe)

        step1 = self.recipe.steps.get(order=1)
        self.assertEqual(list(step1.used_ingredients.all()), [self.tomato])

    def test_save_dynamic_fields_with_invalid_ingredient(self):
        data = {
            "ingredient": ["InvalidIngredient"],
            "quantity": ["1"],
            "unit": ["pieces"],
            "step": ["Do something."],
            "timer": ["5"],
            "used_ingredients_0": "InvalidIngredient",
        }
        request = self._request(data)
        save_dynamic_fields(request, self.recipe)

        self.assertEqual(RecipeIngredient.objects.filter(recipe=self.recipe).count(), 0)
        self.assertEqual(self.recipe.steps.count(), 0)

    def test_save_list_items(self):
        data = {
            "item": ["Sugar", "Whey Flour"],
            "quantity": ["1", "2"],
            "unit": ["kg", "kg"],
            "bought": [False, False],
        }
        request = self._request(data)
        result = save_list_items(request, self.shopping_list)

        self.assertTrue(result)
        self.assertEqual(self.shopping_list.items.count(), 2)
        self.assertEqual(self.shopping_list.items.first().ingredient.name, "Sugar")
        self.assertEqual(self.shopping_list.items.last().custom_name, "Whey Flour")


class RecipeImageCompressionTest(TestCase, ImageMixin):
    def test_upload_compresses_to_webp(self):
        upload = self.make_upload(name="dish.png")
        form = RecipeForm(
            data={"name": "Test", "difficulty": "Easy", "category": "Meat"}, files={"image_asset": upload}
        )
        self.assertTrue(form.is_valid(), form.errors)

        recipe = form.save()
        self.assertTrue(recipe.image_asset.name.endswith(".webp"))
        recipe.image_asset.open()
        self.assertEqual(Image.open(recipe.image_asset).format, "WEBP")

    def test_replacing_image_deletes_old_file(self):
        with (
            tempfile.TemporaryDirectory() as media,
            override_settings(MEDIA_ROOT=media),
        ):
            first = RecipeForm(
                data={"name": "First", "difficulty": "Easy", "category": "Meat"},
                files={"image_asset": self.make_upload(name="a.png")},
            )
            recipe = first.save()
            old_path = recipe.image_asset.path
            self.assertTrue(os.path.exists(old_path))

            second = RecipeForm(
                data={"name": "First", "difficulty": "Easy", "category": "Meat"},
                files={"image_asset": self.make_upload(name="b.png")},
                instance=recipe,
            )
            second.save()
            self.assertFalse(os.path.exists(old_path))
