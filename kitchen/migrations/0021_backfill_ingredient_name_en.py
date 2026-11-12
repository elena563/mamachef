import inflect
from django.db import migrations

_inflect = inflect.engine()


def _singularize(name):
    word = name.strip()
    lower = word.lower()
    if lower.endswith(("ss", "sses", "us", "is", "ous")):
        return word
    return _inflect.singular_noun(word) or word


def _merge_into(apps, duplicate, canonical):
    RecipeIngredient = apps.get_model("kitchen", "RecipeIngredient")
    ShoppingListItem = apps.get_model("kitchen", "ShoppingListItem")
    Step = apps.get_model("kitchen", "Step")
    StepIngredients = Step.used_ingredients.through

    RecipeIngredient.objects.filter(ingredient_id=duplicate.pk).update(ingredient_id=canonical.pk)
    ShoppingListItem.objects.filter(ingredient_id=duplicate.pk).update(ingredient_id=canonical.pk)

    for link in list(StepIngredients.objects.filter(ingredient_id=duplicate.pk)):
        StepIngredients.objects.get_or_create(step_id=link.step_id, ingredient_id=canonical.pk)
        link.delete()

    duplicate.delete()


def backfill_ingredient_name_en(apps, schema_editor):
    Ingredient = apps.get_model("kitchen", "Ingredient")

    for ingredient in list(Ingredient.objects.all()):
        source = (ingredient.name_en or ingredient.name or "").strip()
        if not source:
            continue

        target = _singularize(source.title()).title()
        if ingredient.name_en == target:
            continue

        collision = Ingredient.objects.filter(name_en__iexact=target).exclude(pk=ingredient.pk).first()
        if collision:
            _merge_into(apps, ingredient, collision)
        else:
            ingredient.name_en = target
            ingredient.save(update_fields=["name_en"])


class Migration(migrations.Migration):
    dependencies = [
        ("kitchen", "0020_ingredient_name_en_ingredient_name_it_and_more"),
    ]

    operations = [
        migrations.RunPython(backfill_ingredient_name_en, migrations.RunPython.noop),
    ]
