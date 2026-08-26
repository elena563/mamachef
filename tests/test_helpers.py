from django.test import TestCase

from functions.ingredient_validation import get_or_validate_ingredient, is_countable
from functions.pdf import generate_list_pdf
from functions.recipe_helpers import filter_recipes
from kitchen.models import Ingredient, Recipe, RecipeIngredient, ShoppingListItem
from tests.helpers import KitchenTestCase


class RecipeHelpersTestCase(TestCase):
    def setUp(self):
        ingredient1 = Ingredient.objects.create(name="Ingredient 1")
        ingredient2 = Ingredient.objects.create(name="Ingredient 2")

        self.recipe1 = Recipe.objects.create(name="Recipe 1", difficulty="Easy")
        self.recipe2 = Recipe.objects.create(name="Recipe 2", difficulty="Hard")

        RecipeIngredient.objects.create(recipe=self.recipe1, ingredient=ingredient1, quantity=1, unit="cup")
        RecipeIngredient.objects.create(recipe=self.recipe2, ingredient=ingredient2, quantity=2, unit="tbsp")

    def test_filter_recipes(self):
        recipes = Recipe.objects.all()
        filtered_recipes = filter_recipes(recipes, ingredients=["Ingredient 1"])
        self.assertIn(self.recipe1, filtered_recipes)

        filtered_recipes = filter_recipes(recipes, search_query="Recipe 2")
        self.assertIn(self.recipe2, filtered_recipes)

        filtered_recipes = filter_recipes(recipes, difficulty="Medium")
        self.assertNotIn(self.recipe1, filtered_recipes)
        self.assertNotIn(self.recipe2, filtered_recipes)


class IngredientTest(KitchenTestCase):
    def setUp(self):
        super().setUp()

    def test_search_existing_ingredient_lowercase(self):
        ingredient, error = get_or_validate_ingredient("tomato")

        self.assertIsNone(error)
        self.assertEqual(ingredient.name, "Tomatoes")
        self.assertEqual(Ingredient.objects.filter(name="Tomatoes").count(), 1)

    def test_create_new_ingredient_title_case(self):
        ingredient, error = get_or_validate_ingredient("olive oil")

        self.assertIsNone(error)
        self.assertIsNotNone(ingredient)
        self.assertEqual(ingredient.name, "Olive Oil")
        self.assertEqual(Ingredient.objects.filter(name="Olive Oil").count(), 1)

    def test_invalid_ingredient(self):
        ingredient, error = get_or_validate_ingredient("12345")

        self.assertIsNone(ingredient)
        self.assertIsNotNone(error)
        self.assertEqual(error, "'12345' is not a valid ingredient")

    def test_unique_constraint_lower(self):
        with self.assertRaises(Exception):
            Ingredient.objects.create(name="tomatoes")

    def test_is_countable(self):
        self.assertTrue(is_countable(self.tomato.name))
        self.assertFalse(is_countable(self.flour.name))

    def test_generate_pdf(self):
        ShoppingListItem.objects.create(
            shopping_list=self.shopping_list,
            ingredient=self.tomato,
            quantity=2,
            unit="pcs",
        )
        pdf = generate_list_pdf(self.shopping_list)

        self.assertIsNotNone(pdf)
        self.assertTrue(pdf.getvalue().startswith(b"%PDF"))  # Check if the generated content is a PDF


class ModelPropertyTest(KitchenTestCase):
    def test_recipe_image_none(self):
        self.assertIsNone(self.recipe.image)

    def test_recipe_image_falls_back_to_url(self):
        self.recipe.image_url = "https://example.com/pasta.jpg"
        self.recipe.save()

        self.assertEqual(self.recipe.image, "https://example.com/pasta.jpg")

    def test_recipe_image_prefers_asset(self):
        self.recipe.image_url = "https://example.com/pasta.jpg"
        self.recipe.image_asset = "dishes/pasta.jpg"
        self.recipe.save()

        self.assertEqual(self.recipe.image, self.recipe.image_asset.url)
