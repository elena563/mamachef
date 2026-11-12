from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Ingredient, Recipe, Step


@admin.register(Recipe)
class RecipeAdmin(TranslationAdmin):
    pass


@admin.register(Ingredient)
class IngredientAdmin(TranslationAdmin):
    pass


@admin.register(Step)
class StepAdmin(TranslationAdmin):
    pass
