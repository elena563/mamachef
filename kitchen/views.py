from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

from .models import Recipe, RecipeIngredient, Ingredient, RecipeIngredient, UserProfile
from .forms import RecipeForm
from functions.recipe_helpers import save_dynamic_fields

# pages

def home(request):
    recipes = Recipe.objects.all()
    return render(request, 'home.html', {'recipes':recipes})

def recipes(request):
    """Recipes page view"""
    recipes = Recipe.objects.all()
    return render(request, 'recipes.html', {'recipes': recipes})

def recipe_detail(request, pk):
    """Recipe detail view"""
    recipe = get_object_or_404(Recipe, pk=pk)
    ingredients = RecipeIngredient.objects.filter(recipe=recipe)
    steps = recipe.steps.all()
    return render(request, 'recipe_detail.html', {'recipe': recipe, 'ingredients': ingredients, 'steps': steps})

@login_required
def profile(request):
    user = request.user
    recipes = Recipe.objects.filter(author=user)
    return render(request, 'profile.html', {'recipes': recipes})

# CRUD

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('Kitchen:home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

class RecipeFormView:
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipe_form.html'

    def get_success_url(self):
        return reverse_lazy('Kitchen:recipe_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unit_choices'] = [choice[0] for choice in RecipeIngredient.UNIT_CHOICES]
        return context

class RecipeCreateView(RecipeFormView,CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        
        save_dynamic_fields(self.request.POST, self.object)
        return response

class RecipeUpdateView(RecipeFormView,UpdateView):
    def form_valid(self, form):
        self.object = form.save()

        RecipeIngredient.objects.filter(recipe=self.object).delete()
        self.object.steps.all().delete()
        save_dynamic_fields(self.request.POST, self.object)
        return super().form_valid(form)


def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    recipe.delete()
    return redirect('Kitchen:recipes')

@login_required
def add_to_favorites(request, pk):
    user_profile = request.user.profile
    recipe = get_object_or_404(Recipe, pk=pk)
    if recipe in user_profile.favorite_recipes.all():
        user_profile.favorite_recipes.remove(recipe)
    else:
        user_profile.favorite_recipes.add(recipe)
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('Kitchen:recipes')