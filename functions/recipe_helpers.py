from kitchen.models import Ingredient, RecipeIngredient

def save_ingredients(request_post, recipe):
    names = request_post.getlist('ingredient')
    quantities = request_post.getlist('quantity')
    units = request_post.getlist('unit')

    for i in range(len(names)):
        name = names[i].strip().lower()
        if not name:
            continue
        ingredient, created = Ingredient.objects.get_or_create(name=name)
        RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, quantity=quantities[i], unit=units[i])