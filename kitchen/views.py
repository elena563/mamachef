from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Recipe, RecipeIngredient, Ingredient, RecipeIngredient, UserProfile
from .forms import RecipeForm
from functions.recipe_helpers import save_dynamic_fields, filter_recipes

# pages

def home(request):
    recipes = Recipe.objects.all()
    return render(request, 'home.html', {'recipes':recipes})

def recipes(request):
    """Recipes page view with search functionality"""
    recipes = Recipe.objects.all()
    
    search_query = request.GET.get('q', '').strip()
    ingredients = [i.strip() for i in request.GET.getlist('ingredients') if i.strip()]
    difficulty = [d for d in request.GET.getlist('difficulty') if d != 'All difficulties']
    preparation_time = request.GET.get('preparation_time')
    
    recipes = filter_recipes(recipes, search_query, ingredients, difficulty, preparation_time)

    difficulty_levels = ['All difficulties'] + list(Recipe.objects.values_list('difficulty', flat=True).distinct())
    preparation_time_ranges = ['All preparation times', 'less than 30 minutes', '30-60 minutes', 'more than 60 minutes']
    
    return render(request, 'recipes.html', {
        'recipes': recipes,
        'search_query': search_query,
        'difficulty_levels': difficulty_levels,
        'preparation_time_ranges': preparation_time_ranges
    })

def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    ingredients = RecipeIngredient.objects.filter(recipe=recipe)
    steps = recipe.steps.all()
    return render(request, 'recipe_detail.html', {'recipe': recipe, 'ingredients': ingredients, 'steps': steps})

def guided_mode(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    steps = recipe.steps.all()
    return render(request, 'guided_mode.html', {'recipe': recipe, 'steps': steps})

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
        
        # Prepare used_ingredients names for each step to make template checks easier
        if self.object and self.object.pk:
            steps_with_used = []
            for step in self.object.steps.all():
                step.used_ingredient_names = list(step.used_ingredients.values_list('name', flat=True))
                steps_with_used.append(step)
            context['steps'] = steps_with_used
        else:
            context['steps'] = []
        
        return context

class RecipeCreateView(RecipeFormView,CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        
        if not save_dynamic_fields(self.request, self.object):
            self.object.delete()
            return self.form_invalid(form)
        return response

class RecipeUpdateView(RecipeFormView,UpdateView):
    def form_valid(self, form):
        self.object = form.save()

        RecipeIngredient.objects.filter(recipe=self.object).delete()
        self.object.steps.all().delete()
        
        if not save_dynamic_fields(self.request, self.object):
            return self.form_invalid(form)
        return super().form_valid(form)
    

def ingredient_autocomplete(request):
    query = request.GET.get('q', '').strip().lower()
    
    if len(query) < 2:  # Inizia a suggerire dopo almeno 2 caratteri
        return JsonResponse({'ingredients': []})
    
    # Cerca ingredienti che contengono la query
    ingredients = Ingredient.objects.filter(
        name__icontains=query
    ).values_list('name', flat=True)[:10]  # Limita a 10 risultati
    
    return JsonResponse({
        'ingredients': list(ingredients)
    })


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