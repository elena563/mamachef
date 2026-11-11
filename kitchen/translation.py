from modeltranslation.translator import TranslationOptions, register

from .models import Ingredient, Recipe, Step


@register(Recipe)
class RecipeTranslationOptions(TranslationOptions):
    fields = ("name", "description", "notes")


@register(Ingredient)
class IngredientTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Step)
class StepTranslationOptions(TranslationOptions):
    fields = ("description",)
