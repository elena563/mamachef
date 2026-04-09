from kitchen.models import Ingredient, RecipeIngredient
from django.db.models import Q, Count

def save_dynamic_fields(request_post, recipe):
    names = request_post.getlist('ingredient')
    quantities = request_post.getlist('quantity')
    units = request_post.getlist('unit')

    steps = request_post.getlist('step')
    timers = request_post.getlist('timer')

    for i in range(len(names)):
        name = names[i].strip().lower()
        if not name:
            continue
        ingredient, created = Ingredient.objects.get_or_create(name=name)
        RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, quantity=quantities[i], unit=units[i])

    for i in range(len(steps)):
        step = steps[i].strip()
        if not step:
            continue
        timer = timers[i] if i < len(timers) and timers[i] else None
        recipe.steps.create(description=step, timer=timer, order=i)


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