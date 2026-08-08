from django.test import TestCase

from kitchen.models import Recipe, Ingredient, RecipeIngredient
from functions.recipe_helpers import filter_recipes

class RecipeHelpersTestCase(TestCase):
    def setUp(self):
        ingredient1 = Ingredient.objects.create(name='Ingredient 1')
        ingredient2 = Ingredient.objects.create(name='Ingredient 2')

        self.recipe1 = Recipe.objects.create(name='Recipe 1', difficulty='Easy')
        self.recipe2 = Recipe.objects.create(name='Recipe 2', difficulty='Hard')
        
        RecipeIngredient.objects.create(recipe=self.recipe1, ingredient=ingredient1, quantity=1, unit='cup')
        RecipeIngredient.objects.create(recipe=self.recipe2, ingredient=ingredient2, quantity=2, unit='tbsp')

    def test_filter_recipes(self):
        recipes = Recipe.objects.all()
        filtered_recipes = filter_recipes(recipes, ingredients=['Ingredient 1'])
        self.assertIn(self.recipe1, filtered_recipes)

        filtered_recipes = filter_recipes(recipes, search_query='Recipe 2')
        self.assertIn(self.recipe2, filtered_recipes)

        filtered_recipes = filter_recipes(recipes, difficulty='Medium')
        self.assertNotIn(self.recipe1, filtered_recipes)
        self.assertNotIn(self.recipe2, filtered_recipes)

