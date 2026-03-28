from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.urls import reverse_lazy

from .models import Recipe
from .forms import RecipeForm

def home(request):
    """Home page view"""
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('Kitchen:home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def recipes(request):
    """Recipes page view"""
    return render(request, 'recipes.html')

class RecipeCreateView(CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipe_form.html'
    success_url = reverse_lazy('kitchen:home')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class RecipeUpdateView(UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipe_form.html'
    success_url = reverse_lazy('kitchen:home')

def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    recipe.delete()
    return redirect('Kitchen:recipes')