from django import forms
from .models import Recipe, Ingredient, RecipeIngredient, Step

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'description', 'difficulty', 'preparation_time']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'name': 'Nome Ricetta',
            'description': 'Descrizione',
            'difficulty': 'Difficoltà',
            'preparation_time': 'Tempo di Preparazione (minuti)',
        }
        help_texts = {
            'preparation_time': 'Inserisci il tempo in minuti',
        }
