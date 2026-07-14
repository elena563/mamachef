import requests
import re
from django.core.management.base import BaseCommand
from kitchen.models import Recipe, Ingredient, RecipeIngredient, Step
from functions.recipe_parsing import get_ingredients, parse_measure, map_category
from functions.recipe_parsing import parse_steps

class Command(BaseCommand):
    help = 'Import recipes from API'

    def handle(self, *args, **options):

        categories = ['Beef', 'Chicken', 'Dessert', 'Lamb', 'Pasta', 'Pork', 'Seafood', 'Side', 'Starter', 'Vegan', 'Vegetarian', 'Breakfast', 'Goat']

        for category in categories:
            url = f"https://www.themealdb.com/api/json/v1/1/filter.php?c={category}"
            response = requests.get(url)
            data = response.json()

            meals = data["meals"][:2]
            ids = [meal["idMeal"] for meal in meals]

            for id in ids:
                url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={id}"
                response = requests.get(url)
                data = response.json()

                meal = data["meals"][0]

                #print(meal['strMeal'], map_category(meal['strCategory']), meal['strMealThumb'])
                
                recipe = Recipe.objects.create(
                    name=meal['strMeal'],
                    category=map_category(meal['strCategory']),
                    servings=4,
                    image_url=meal['strMealThumb'],
                    )
                
                ingredients = get_ingredients(meal)
                for ingredient_name, ingredient_measure in ingredients:
                    #print(f"Ingredient: {ingredient_name}, Measure: {ingredient_measure}")

                    quantity, unit, note = parse_measure(ingredient_measure)
                    #print(f"Ingredient: {ingredient_name}, Quantity: {quantity}, Unit: {unit}, Note: {note}")
                    
                    ingredient, created = Ingredient.objects.get_or_create(name=ingredient_name)
                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        ingredient=ingredient,
                        quantity=quantity,
                        unit=unit,
                    )
                
                
                instructions = meal['strInstructions']

                clean_steps = parse_steps(instructions)
                for step_number, step_text in enumerate(clean_steps, start=1):
                    Step.objects.create(
                        recipe=recipe,
                        description=step_text,
                        order=step_number,
                    )
                
                #print(f"Recipe: {meal['strMeal']}, Steps: {len(clean_steps) if clean_steps else 0}")
                #print(f"Steps: {clean_steps if clean_steps else 0}")