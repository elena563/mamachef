from django.test import TestCase
from kitchen.models import Ingredient
from functions.ingredient_validation import get_or_validate_ingredient  

class IngredientTest(TestCase):

    def setUp(self):
        Ingredient.objects.create(name="Tomatoes", countable=True)

    def test_search_existing_ingredient_lowercase(self):
        ingredient, error = get_or_validate_ingredient("tomato")
        
        self.assertIsNone(error)
        self.assertEqual(ingredient.name, "Tomatoes")
        self.assertEqual(Ingredient.objects.count(), 1)

    def test_create_new_ingredient_title_case(self):
        ingredient, error = get_or_validate_ingredient("olive oil")
        
        self.assertIsNone(error)
        self.assertIsNotNone(ingredient)
        self.assertEqual(ingredient.name, "Olive Oil")
        self.assertEqual(Ingredient.objects.count(), 2)

    def test_unique_constraint_lower(self):
        with self.assertRaises(Exception):
            Ingredient.objects.create(name="tomatoes")