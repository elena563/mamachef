import json

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic.edit import CreateView, UpdateView

from functions.pdf import generate_list_pdf
from functions.recipe_helpers import (
    filter_recipes,
    save_dynamic_fields,
    save_list_items,
)

from .forms import RecipeForm, UserForm, UserProfileForm
from .models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    ShoppingListItem,
    UserProfile,
)
from .variables import UNIT_CHOICES, UNIT_LIST_CHOICES

# pages


def home(request):
    recipes = Recipe.objects.all().order_by("-created_at")[:6]
    meat_recipes = Recipe.objects.filter(category="Meat")[:3]
    pasta_recipes = Recipe.objects.filter(category="Pasta")[:3]
    dessert_recipes = Recipe.objects.filter(category="Dessert")[:3]
    return render(
        request,
        "home.html",
        {
            "recipes": recipes,
            "meat_recipes": meat_recipes,
            "pasta_recipes": pasta_recipes,
            "dessert_recipes": dessert_recipes,
        },
    )


def recipes(request):
    """Recipes page view with search functionality"""
    recipes = Recipe.objects.all().order_by("-created_at")

    search_query = request.GET.get("q", "").strip()
    ingredients = [i.strip() for i in request.GET.getlist("ingredients") if i.strip()]
    difficulty = [d for d in request.GET.getlist("difficulty") if d != "All difficulties"]
    preparation_time = request.GET.get("preparation_time")
    cooking_method = [c for c in request.GET.getlist("cooking_method") if c != "All cooking methods"]
    category = [c for c in request.GET.getlist("category") if c != "All categories"]

    recipes = filter_recipes(
        recipes,
        search_query,
        ingredients,
        difficulty,
        preparation_time,
        cooking_method,
        category,
    )

    difficulty_levels = ["All difficulties"] + list(
        Recipe.objects.values_list("difficulty", flat=True).distinct()
    )
    cooking_method_choices = ["All cooking methods"] + list(
        Recipe.objects.values_list("cooking_method", flat=True).distinct()
    )
    preparation_time_ranges = [
        "All preparation times",
        "less than 30 minutes",
        "30-60 minutes",
        "more than 60 minutes",
    ]
    category_choices = ["All categories"] + list(Recipe.objects.values_list("category", flat=True).distinct())

    return render(
        request,
        "recipes.html",
        {
            "recipes": recipes,
            "search_query": search_query,
            "difficulty_levels": difficulty_levels,
            "cooking_method_choices": cooking_method_choices,
            "preparation_time_ranges": preparation_time_ranges,
            "category_choices": category_choices,
            "selected_difficulty": request.GET.get("difficulty", "All difficulties"),
            "selected_cooking_method": request.GET.get("cooking_method", "All cooking methods"),
            "selected_preparation_time": request.GET.get("preparation_time", "All preparation times"),
            "selected_category": request.GET.get("category", "All categories"),
        },
    )


def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    ingredients = RecipeIngredient.objects.filter(recipe=recipe)
    steps = recipe.steps.all()
    return render(
        request,
        "recipe_detail.html",
        {"recipe": recipe, "ingredients": ingredients, "steps": steps},
    )


def guided_mode(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    steps = recipe.steps.all()
    return render(request, "guided_mode.html", {"recipe": recipe, "steps": steps})


@login_required
def profile(request):
    user = request.user
    profile_obj, _ = UserProfile.objects.get_or_create(user=user)
    recipes = Recipe.objects.filter(author=user)

    if request.method == "POST":
        uform = UserForm(request.POST, instance=user)
        pform = UserProfileForm(request.POST, request.FILES, instance=profile_obj)
        if uform.is_valid() and pform.is_valid():
            uform.save()
            pform.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("Kitchen:profile")
        else:
            messages.error(request, "There were errors saving your profile.")
    else:
        uform = UserForm(instance=user)
        pform = UserProfileForm(instance=profile_obj)

    return render(
        request,
        "profile.html",
        {
            "recipes": recipes,
            "uform": uform,
            "pform": pform,
            "profile": profile_obj,
        },
    )


# CRUD


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            ShoppingList.objects.create(user=user)
            login(request, user)
            return redirect("Kitchen:home")
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})


class RecipeFormView(LoginRequiredMixin):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipe_form.html"

    def form_invalid(self, form):
        for error in form.non_field_errors():
            messages.error(self.request, error)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("Kitchen:recipe_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unit_choices"] = [choice[0] for choice in UNIT_CHOICES]

        # Prepare used_ingredients names for each step to make template checks easier
        if self.object and self.object.pk:
            steps_with_used = []
            for step in self.object.steps.all():
                step.used_ingredient_names = list(step.used_ingredients.values_list("name", flat=True))
                steps_with_used.append(step)
            context["steps"] = steps_with_used
        else:
            context["steps"] = []

        if self.object and self.object.image_asset:
            context["image_asset_url"] = self.object.image_asset.url
        elif self.object and self.object.image_url:
            context["image_asset_url"] = self.object.image_url
        else:
            context["image_asset_url"] = ""

        return context


class RecipeCreateView(RecipeFormView, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)

        if not save_dynamic_fields(self.request, self.object):
            self.object.delete()
            return self.form_invalid(form)
        return response


class RecipeUpdateView(RecipeFormView, UpdateView):
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != request.user:
            messages.error(request, "You do not have permission to edit this recipe.")
            return redirect("Kitchen:recipe_detail", pk=self.object.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()

        with transaction.atomic():
            RecipeIngredient.objects.filter(recipe=self.object).delete()
            self.object.steps.all().delete()

            if not save_dynamic_fields(self.request, self.object):
                return self.form_invalid(form)
        return super().form_valid(form)


def ingredient_autocomplete(request):
    query = request.GET.get("q", "").strip().lower()

    if len(query) < 1:
        return JsonResponse({"ingredients": []})

    ingredients = Ingredient.objects.filter(name__istartswith=query).values_list("name", flat=True)[:10]

    return JsonResponse({"ingredients": list(ingredients)})


@login_required
@require_POST
def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if recipe.author != request.user:
        messages.error(request, "You do not have permission to delete this recipe.")
        return redirect("Kitchen:recipe_detail", pk=pk)
    recipe.delete()
    return redirect("Kitchen:recipes")


@login_required
def add_to_favorites(request, pk):
    user_profile = request.user.profile
    recipe = get_object_or_404(Recipe, pk=pk)
    if recipe in user_profile.favorite_recipes.all():
        user_profile.favorite_recipes.remove(recipe)
    else:
        user_profile.favorite_recipes.add(recipe)
    referer = request.META.get("HTTP_REFERER")
    if referer:
        return redirect(referer)
    return redirect("Kitchen:recipes")


@login_required
def shopping_list(request):
    shop_list = get_object_or_404(ShoppingList, user=request.user)

    if request.method == "POST":
        list_name = request.POST.get("list_name", "").strip()
        if list_name:
            shop_list.name = list_name
            shop_list.save()

        with transaction.atomic():
            ShoppingListItem.objects.filter(shopping_list=shop_list).delete()

            if not save_list_items(request, shop_list):
                return render(
                    request,
                    "shopping_list.html",
                    {
                        "shopping_list": shop_list,
                        "items": shop_list.items.all(),
                        "unit_choices": [choice[0] for choice in UNIT_LIST_CHOICES],
                    },
                )
        return redirect("Kitchen:shopping_list")

    bought_items = shop_list.items.filter(bought=True)
    return render(
        request,
        "shopping_list.html",
        {
            "shopping_list": shop_list,
            "unit_choices": [choice[0] for choice in UNIT_LIST_CHOICES],
            "bought_items": bought_items,
        },
    )


@login_required
def add_to_list(request):
    shopping_list = request.user.shopping_list
    ingredient_ids = request.POST.getlist("ingredient")

    for qi_id in ingredient_ids:
        recipe_ing = RecipeIngredient.objects.get(id=qi_id)
        ingredient = recipe_ing.ingredient
        quantity = recipe_ing.quantity
        unit = recipe_ing.unit
        item, created = ShoppingListItem.objects.get_or_create(
            shopping_list=shopping_list,
            ingredient=ingredient,
            defaults={"quantity": quantity, "unit": unit},
        )

        # TODO: check on units, conversion

        if not created:
            item.quantity += quantity
            item.save()
    referer = request.META.get("HTTP_REFERER")
    if referer:
        return redirect(referer)
    return redirect("Kitchen:recipes")


@login_required
def export_pdf(request):
    shop_list = get_object_or_404(ShoppingList, user=request.user)
    pdf = generate_list_pdf(shop_list)
    return FileResponse(pdf, as_attachment=True, filename=f"{shop_list.name}.pdf")


@require_POST
@login_required
def toggle_item_bought(request, item_id):
    item = get_object_or_404(ShoppingListItem, id=item_id)
    if item.shopping_list.user != request.user:
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)
    data = json.loads(request.body)
    item.bought = data.get("bought", False)
    item.save()
    return JsonResponse({"success": True, "bought": item.bought})
