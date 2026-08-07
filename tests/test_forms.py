from django.test import TestCase, RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage

from functions.recipe_helpers import save_dynamic_fields
from kitchen.models import Recipe, Ingredient, RecipeIngredient


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
