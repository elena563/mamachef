import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mamachef.settings")
django.setup()

from kitchen.models import Recipe, RecipeIngredient, ShoppingListItem  # noqa: E402

for r in Recipe.objects.all():
    changed = False
    for field in ["difficulty", "cooking_method", "category"]:
        val = getattr(r, field)
        if val and val != val.lower():
            setattr(r, field, val.lower())
            changed = True
    if changed:
        r.save()

for m in RecipeIngredient.objects.all():
    if m.unit and m.unit != m.unit.lower():
        m.unit = m.unit.lower()
        m.save()

for s in ShoppingListItem.objects.all():
    if s.unit and s.unit != s.unit.lower():
        s.unit = s.unit.lower()
        s.save()

print("Done")
