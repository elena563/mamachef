from django import forms
from .models import Recipe, Ingredient, RecipeIngredient, Step

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'description', 'difficulty', 'preparation_time', 'servings']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'name': 'Recipe Name',
            'description': 'Description',
            'difficulty': 'Difficulty',
            'preparation_time': 'Preparation Time (minutes)',
            'servings': 'Servings',
        }
        help_texts = {
            'preparation_time': 'Enter the time in minutes',
        }
