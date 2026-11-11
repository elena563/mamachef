from django.utils.translation import gettext_lazy as _

DIFFICULTY_CHOICES = [
    ("easy", _("Easy")),
    ("medium", _("Medium")),
    ("hard", _("Hard")),
]
COOKING_METHOD_CHOICES = [
    ("baked", _("Baked")),
    ("stovetop", _("Stovetop")),
    ("microwaved", _("Microwaved")),
    ("no cook", _("No Cook")),
]

UNIT_CHOICES = [
    ("g", _("grams")),
    ("kg", _("kilograms")),
    ("ml", _("milliliters")),
    ("l", _("liters")),
    ("tsp", _("teaspoons")),
    ("tbsp", _("tablespoons")),
    ("cup", _("cups")),
    ("pcs", _("pieces")),
    ("q.s.", _("quantum sufficit (as needed)")),
]

UNIT_LIST_CHOICES = [
    ("pcs", _("pieces")),
    ("g", _("grams")),
    ("kg", _("kilograms")),
    ("ml", _("milliliters")),
    ("l", _("liters")),
]

RECIPE_CATEGORY_CHOICES = [
    ("Meat", _("Meat")),
    ("Fish", _("Fish")),
    ("Vegetarian", _("Vegetarian")),
    ("Vegan", _("Vegan")),
    ("Dessert", _("Dessert")),
    ("Side", _("Side")),
    ("Starter", _("Starter")),
    ("Pasta", _("Pasta")),
    ("Breakfast", _("Breakfast")),
]
