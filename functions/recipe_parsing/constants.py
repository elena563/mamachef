# Constants for recipe parsing

UNIT_MAP = {
    'g': 'g',
    'gram': 'g',
    'grams': 'g',

    'kg': 'kg',
    'kilogram': 'kg',
    'kilograms': 'kg',

    'ml': 'ml',
    'milliliter': 'ml',
    'milliliters': 'ml',

    'l': 'l',
    'liter': 'l',
    'liters': 'l',

    'tbsp': 'tbsp',
    'tbs': 'tbsp',
    'tblsp': 'tbsp',
    'tablespoon': 'tbsp',
    'tablespoons': 'tbsp',

    'tsp': 'tsp',
    'teaspoon': 'tsp',
    'teaspoons': 'tsp',

    'cup': 'cup',
    'cups': 'cup',

    'oz': 'pcs',
    'ounce': 'pcs',
    'ounces': 'pcs',

    'lb': 'pcs',
    'lbs': 'pcs',
    'pound': 'pcs',
    'pounds': 'pcs',
}

QS_WORDS = {
    'pinch',
    'dash',
    'drizzle',
    'dusting',
    'to taste'
}

MAX_STEPS = 15
MIN_STEP_LEN = 8
MAX_STEP_CHARS = 300
SHORT_STEP_CHARS = 200