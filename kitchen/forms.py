from django import forms
from .models import Recipe
from django.contrib.auth.models import User
from .models import UserProfile

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'description', 'difficulty', 'cooking_method','preparation_time', 'servings']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'name': 'Recipe Name',
            'description': 'Description',
            'difficulty': 'Difficulty',
            'cooking_method': 'Cooking Method',
            'preparation_time': 'Preparation Time (minutes)',
            'servings': 'Servings',
        }
        help_texts = {
            'preparation_time': 'Enter the time in minutes',
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'Username',
            'email': 'Email',
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture']
        labels = {
            'bio': 'Bio',
            'profile_picture': 'Profile Picture',
        }
