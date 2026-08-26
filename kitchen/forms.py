from django import forms
from django.contrib.auth.models import User

from functions.image_helpers import compress_image

from .models import Recipe, UserProfile


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            "image_asset",
            "image_url",
            "name",
            "description",
            "difficulty",
            "cooking_method",
            "preparation_time",
            "servings",
            "category",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
        labels = {
            "image_asset": "Image",
            "image_url": "Image URL",
            "name": "Recipe Name",
            "description": "Description",
            "difficulty": "Difficulty",
            "cooking_method": "Cooking Method",
            "preparation_time": "Preparation Time (minutes)",
            "servings": "Servings",
            "category": "Category",
        }
        help_texts = {
            "preparation_time": "Enter the time in minutes",
            "image_url": "Provide an image file or an image URL",
        }

    def clean(self):
        cleaned_data = super().clean()
        image_asset = cleaned_data.get("image_asset")
        image_url = cleaned_data.get("image_url")

        if image_asset and image_url:
            raise forms.ValidationError("Provide either an image file or an image URL, not both.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            if instance.image_asset:
                old_asset = None
                if self.instance.pk:
                    old_asset = (
                        Recipe.objects.filter(pk=self.instance.pk)
                        .values_list("image_asset", flat=True)
                        .first()
                    )
                if not old_asset or old_asset != instance.image_asset.name:
                    instance.image_asset = compress_image(instance.image_asset)
                    instance.save()
                    if old_asset:
                        instance.image_asset.storage.delete(old_asset)
                else:
                    instance.save()
            else:
                instance.save()
            self.save_m2m()
        return instance


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]
        labels = {
            "username": "Username",
            "email": "Email",
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["bio", "profile_picture"]
        labels = {
            "bio": "Bio",
            "profile_picture": "Profile Picture",
        }
