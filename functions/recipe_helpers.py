from kitchen.models import Ingredient, RecipeIngredient, ShoppingListItem
from django.db.models import Q, Count
from django.contrib import messages

from .ingredient_validation import get_or_validate_ingredient, get_ingredient_or_custom, validate_quantity_unit

def save_dynamic_fields(request, recipe):
    names = request.POST.getlist('ingredient')
    quantities = request.POST.getlist('quantity')
    units = request.POST.getlist('unit')

    steps = request.POST.getlist('step')
    timers = request.POST.getlist('timer')
    used_ingredients_list = request.POST.getlist('used_ingredients')

    has_errors = False
    
    for i in range(len(names)):
        name = names[i].strip().lower()
        if not name:
            messages.error(request, f"Ingredient name is required for ingredient #{i+1}")
            has_errors = True
            continue
        ingredient, error = get_or_validate_ingredient(name)
        if error:
            messages.error(request, error)
            has_errors = True
            continue
        
        quantity = quantities[i] if quantities[i] and quantities[i].strip() else None
        is_valid, error = validate_quantity_unit(quantity, units[i], ingredient)
        if not is_valid:
            messages.error(request, error)
            has_errors = True
        else:
            RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, quantity=quantity, unit=units[i])

    for i in range(len(steps)):
        step = steps[i].strip()
        if not step:
            continue
        timer = timers[i] if i < len(timers) and timers[i] and timers[i].strip() else None
        step_obj = recipe.steps.create(description=step, timer=timer, order=i)
        
        if i < len(used_ingredients_list) and used_ingredients_list[i]:
            ingredient_names = [name.strip().lower() for name in used_ingredients_list[i].split(',') if name.strip()]
            ingredients_to_add = []
            for name in ingredient_names:
                try:
                    ingredient = Ingredient.objects.get(name=name)
                    ingredients_to_add.append(ingredient)
                except Ingredient.DoesNotExist:
                    pass
            
            if ingredients_to_add:
                step_obj.used_ingredients.set(ingredients_to_add)
    
    return not has_errors

def save_list_items(request, shop_list):
    names = request.POST.getlist('item')
    quantities = request.POST.getlist('quantity')
    units = request.POST.getlist('unit')

    has_errors = False
    
    for i in range(len(names)):
        name = names[i].strip().lower()
        if not name:
            messages.error(request, f"Item name is required for item #{i+1}")
            has_errors = True
            continue
        
        item, is_custom = get_ingredient_or_custom(name)

        quantity = quantities[i] if quantities[i] and quantities[i].strip() else None
        if not is_custom:
            is_valid, error = validate_quantity_unit(quantity, units[i], item, for_list=True)
        if not is_valid:
            messages.error(request, error)
            has_errors = True
        else:
            ShoppingListItem.objects.create(
                shopping_list=shop_list,
                ingredient=item if isinstance(item, Ingredient) else None, 
                custom_name=item if isinstance(item, str) else None, 
                quantity=quantity, unit=units[i]
            )
    
    return not has_errors

def filter_recipes(recipes, search_query=None, ingredients=None, difficulty=None, preparation_time=None):
    if search_query:
        recipes = recipes.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if ingredients:
        recipes = recipes.filter(
            ingredients__ingredient__name__in=ingredients
        ).annotate(num_ingredients=Count('ingredients__ingredient')).order_by('-num_ingredients').distinct()
    
    if difficulty:
        recipes = recipes.filter(difficulty__in=difficulty)

    if preparation_time and preparation_time != 'All preparation times':
        if preparation_time == 'less than 30 minutes':
            recipes = recipes.filter(preparation_time__lt=30)
        elif preparation_time == '30-60 minutes':
            recipes = recipes.filter(preparation_time__gte=30, preparation_time__lte=60)
        elif preparation_time == 'more than 60 minutes':
            recipes = recipes.filter(preparation_time__gt=60)

    return recipes