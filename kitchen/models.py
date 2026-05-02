from django.db import models
from django.contrib.auth.models import User

from .variables import DIFFICULTY_CHOICES, COOKING_METHOD_CHOICES, UNIT_CHOICES, UNIT_LIST_CHOICES

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', help_text='The user that this profile belongs to')
    bio = models.TextField(null=True, blank=True, verbose_name='Bio', help_text='A brief biography of the user (optional)')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True, verbose_name='Profile Picture', help_text='A profile picture for the user (optional)')
    favorite_recipes = models.ManyToManyField('Recipe', related_name='favorited_by', blank=True, help_text='The recipes that the user has marked as favorites')

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Recipe(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, help_text='The name of the recipe')
    description = models.TextField(null=True, blank=True, verbose_name='Description', help_text='A brief description of the recipe')
    difficulty = models.CharField(max_length=50, choices=DIFFICULTY_CHOICES, null=True, blank=True, verbose_name='Difficulty Level', help_text='The difficulty level of the recipe (e.g., Easy, Medium, Hard)')
    preparation_time = models.IntegerField(null=True, blank=True, verbose_name='Preparation Time (minutes)', help_text='The time required to prepare the recipe in minutes')
    servings = models.IntegerField(null=True, blank=True, verbose_name='Servings', help_text='The number of servings the recipe makes')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes', help_text='The user who created the recipe')
    cooking_method = models.CharField(max_length=50, choices=COOKING_METHOD_CHOICES, null=True, blank=True, verbose_name='Cooking Method', help_text='The cooking method used for the recipe (e.g., Baked, Stovetop, Microwaved, No Cook)')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, help_text='The name of the ingredient')
    countable = models.BooleanField(default=True, help_text='Whether the ingredient is countable (e.g., 2 eggs) or uncountable (e.g., 200g flour)')

    def __str__(self):
        return self.name
    
class RecipeIngredient(models.Model):
    id = models.AutoField(primary_key=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients', help_text='The recipe that this ingredient belongs to')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='recipes', help_text='The ingredient used in the recipe')
    quantity = models.FloatField(null=True, blank=True, verbose_name='Quantity', help_text='The quantity of the ingredient needed for the recipe (e.g., 2 cups, 1 tablespoon)')
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, null=True, blank=True, verbose_name='Unit', help_text='The unit of measurement for the ingredient (e.g., grams, cups)')

    def __str__(self):
        return f"{self.quantity} {self.unit} of {self.ingredient.name} for {self.recipe.name}" 
     

class Step(models.Model):
    id = models.AutoField(primary_key=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='steps', help_text='The recipe that this step belongs to')
    description = models.TextField(help_text='A description of the step')
    order = models.IntegerField(help_text='The order of the step in the recipe')
    timer = models.IntegerField(null=True, blank=True, verbose_name='Timer (minutes)', help_text='The time in minutes that this step takes (optional)')
    used_ingredients = models.ManyToManyField(Ingredient, related_name='steps', blank=True, help_text='The ingredients used in this step')

    def __str__(self):
        return f"Step {self.order} for {self.recipe.name}"


class ShoppingList(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shopping_lists', help_text='The user who owns this shopping list')
    name = models.CharField(default='My Shopping List', max_length=255, help_text='The name of the shopping list')

    def __str__(self):
        return self.name
    
class ShoppingListItem(models.Model):
    id = models.AutoField(primary_key=True)
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, related_name='items', help_text='The shopping list that this item belongs to')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,null=True, blank=True, related_name='shopping_list_items', help_text='The ingredient that needs to be purchased')
    custom_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Custom Name', help_text='Name for custom items that are not in the ingredient database (an item can have either an ingredient or a custom name, but not both)')
    quantity = models.FloatField(null=True, blank=True, verbose_name='Quantity', help_text='The quantity of the ingredient needed for the shopping list (e.g., 2 cups, 1 tablespoon)')
    unit = models.CharField(max_length=10, choices=UNIT_LIST_CHOICES, null=True, blank=True, verbose_name='Unit', help_text='The unit of measurement for the ingredient (e.g., grams, cups)')
    bought = models.BooleanField(default=False, help_text='Whether the item has been bought or not')

    def __str__(self):
        return f"{self.quantity} {self.unit} of {self.ingredient.name} for {self.shopping_list.name}"
    

# ideas: meal planning, recipe categories, user ratings and reviews for recipes, recipe sharing with other users, dietary preferences (e.g., vegetarian, vegan, gluten-free), recipe tags (e.g., quick meals, desserts)