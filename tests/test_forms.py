import os
import tempfile
from io import BytesIO
from PIL import Image

from django.test import TestCase, RequestFactory, override_settings
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.uploadedfile import SimpleUploadedFile

from functions.recipe_helpers import save_dynamic_fields
from kitchen.models import Recipe, Ingredient, RecipeIngredient
from kitchen.forms import RecipeForm

from tests.helpers import ImageMixin

class RecipeFormTest(TestCase, ImageMixin):

    def valid_data(self):
        return {
            'name': 'Test Recipe',
            'description': 'This is a test recipe.',
            'difficulty': 'Easy',
            'preparation_time': 30,
            'servings': 4,
            'cooking_method': 'Baked',
            'category': 'Dessert',
        }
    
    def test_recipe_form_valid(self):
        form = RecipeForm(data=self.valid_data())
        self.assertTrue(form.is_valid())
        recipe = form.save()
        self.assertEqual(Recipe.objects.count(), 1)
        self.assertEqual(recipe.name, 'Test Recipe')

    def test_update_recipe(self):
        recipe = Recipe.objects.create(name='Old Name')
        data = self.valid_data()
        data['name'] = 'New Name'
        form = RecipeForm(data=data, instance=recipe)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        recipe.refresh_from_db()
        self.assertEqual(recipe.name, 'New Name')

    def test_recipe_form_required_fields(self):
        form_data = {
            'name': '',
            'description': 'This is a test recipe.',
            'difficulty': 'Easy',
            'preparation_time': 30,
            'servings': 4,
            'cooking_method': 'Baked',
            'category': 'Dessert',
        }
        form = RecipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_recipe_form_validation_errors(self):
        form_data = {
            'name': 'A' * 256,  # Exceeds max_length
            'description': 'This is a test recipe.',
            'difficulty': 'InvalidChoice',  # Not in choices
            'preparation_time': -5,  # Invalid negative value
            'servings': 0,  # Invalid value less than min
            'cooking_method': 'Baked',
            'category': 'Dessert',
        }
        form = RecipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('difficulty', form.errors)
        self.assertIn('preparation_time', form.errors)
        self.assertIn('servings', form.errors)

    def test_image_asset_and_url_not_both(self):
        data = self.valid_data()
        data['image_url'] = 'https://example.com/x.jpg'
        upload = self.make_upload(name='dish.png')
        form = RecipeForm(data=data, files={'image_asset': upload})
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        

class SaveDynamicFieldsTest(TestCase):
    def setUp(self):
        self.recipe = Recipe.objects.create(name="Test Recipe")
        self.tomato = Ingredient.objects.create(name="Tomato")
        self.onion = Ingredient.objects.create(name="Onion")
        self.factory = RequestFactory()

    def _request(self, data):
        request = self.factory.post('/dummy-url/', data)
        request.session = {}
        request._messages = FallbackStorage(request)
        return request

    def test_save_dynamic_fields_with_valid_data(self):
        data = {
            'ingredient': ['Tomato', 'Onion'],
            'quantity': ['2', '1'],
            'unit': ['pieces', 'pieces'],
            'step': ['Chop the tomatoes.', 'Slice the onions.'],
            'timer': ['5', '3'],
            'used_ingredients_0': 'Tomato',
            'used_ingredients_1': 'Onion',
        }
        request = self._request(data)
        save_dynamic_fields(request, self.recipe)

        self.assertEqual(RecipeIngredient.objects.filter(recipe=self.recipe).count(), 2)
        self.assertEqual(self.recipe.steps.count(), 2)

        step0 = self.recipe.steps.get(order=0)
        step1 = self.recipe.steps.get(order=1)
        self.assertEqual(list(step0.used_ingredients.all()), [self.tomato])
        self.assertEqual(list(step1.used_ingredients.all()), [self.onion])

    def test_save_dynamic_fields_falls_back_to_plain_list(self):
        data = {
            'ingredient': ['Tomato'],
            'quantity': ['2'],
            'unit': ['pieces'],
            'step': ['Chop the tomatoes.'],
            'timer': ['5'],
            'used_ingredients': ['Tomato'],
        }
        request = self._request(data)
        save_dynamic_fields(request, self.recipe)

        step0 = self.recipe.steps.get(order=0)
        self.assertEqual(list(step0.used_ingredients.all()), [self.tomato])

    def test_save_dynamic_fields_with_invalid_ingredient(self):
        data = {
            'ingredient': ['InvalidIngredient'],
            'quantity': ['1'],
            'unit': ['pieces'],
            'step': ['Do something.'],
            'timer': ['5'],
            'used_ingredients_0': 'InvalidIngredient',
        }
        request = self._request(data)
        save_dynamic_fields(request, self.recipe)

        self.assertEqual(RecipeIngredient.objects.filter(recipe=self.recipe).count(), 0)
        self.assertEqual(self.recipe.steps.count(), 0)


class RecipeImageCompressionTest(TestCase, ImageMixin):

    def test_upload_compresses_to_webp(self):
        upload = self.make_upload(name='dish.png')
        form = RecipeForm(data={'name': 'Test'}, files={'image_asset': upload})
        self.assertTrue(form.is_valid(), form.errors)

        recipe = form.save()
        self.assertTrue(recipe.image_asset.name.endswith('.webp'))
        recipe.image_asset.open()
        self.assertEqual(Image.open(recipe.image_asset).format, 'WEBP')

    def test_replacing_image_deletes_old_file(self):
        with tempfile.TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            first = RecipeForm(data={'name': 'First'}, files={'image_asset': self.make_upload(name='a.png')})
            recipe = first.save()
            old_path = recipe.image_asset.path
            self.assertTrue(os.path.exists(old_path))

            second = RecipeForm(data={'name': 'First'}, files={'image_asset': self.make_upload(name='b.png')}, instance=recipe)
            second.save()
            self.assertFalse(os.path.exists(old_path))