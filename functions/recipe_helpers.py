from kitchen.models import Ingredient, RecipeIngredient

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