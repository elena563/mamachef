from .constants import QS_WORDS, UNIT_MAP
import re
from fractions import Fraction

def get_ingredients(meal):
    ingredients = []
    for i in range(1, 21):
        ingredient_name = meal.get(f'strIngredient{i}')
        ingredient_measure = meal.get(f'strMeasure{i}')
        if ingredient_name and ingredient_name.strip():
            ingredients.append((ingredient_name.strip(), ingredient_measure.strip() if ingredient_measure else 'pcs'))
    return ingredients

def map_category(category):
    category_mapping = {
        'Beef': 'Meat',
        'Chicken': 'Meat',
        'Dessert': 'Dessert',
        'Lamb': 'Meat',
        'Pasta': 'Pasta',
        'Pork': 'Meat',
        'Seafood': 'Fish',
        'Side': 'Side',
        'Starter': 'Starter',
        'Vegan': 'Vegan',
        'Vegetarian': 'Vegetarian',
        'Breakfast': 'Breakfast',
        'Goat': 'Meat',
        'Miscellaneous': None,
    }
    return category_mapping.get(category, None)



def parse_number(text):
    text = text.strip()

    # 1 1/2
    if re.match(r'^\d+\s+\d+/\d+$', text):
        whole, frac = text.split()
        return float(whole) + float(Fraction(frac))
    # 1/2
    if re.match(r'^\d+/\d+$', text):
        return float(Fraction(text))

    # 6-8 -> media
    if re.match(r'^\d+\s*-\s*\d+$', text):
        a, b = text.split('-')
        return (float(a) + float(b)) / 2

    return float(text)


def parse_measure(measure):
    if not measure:
        return None, 'q.s.', None

    measure = measure.strip().lower()

    if measure in QS_WORDS:
        return None, 'q.s.', None

    # 750g -> 750 g
    measure = re.sub(
        r'^(\d+(?:\.\d+)?(?:/\d+)?)\s*([a-z]+)',
        r'\1 \2',
        measure
    )

    parts = measure.split()

    if not parts:
        return None, 'q.s.', None

    quantity = None
    unit = 'pcs'
    note = None

    for n_tokens in (2, 1):
        if len(parts) >= n_tokens:
            candidate = ' '.join(parts[:n_tokens])

            try:
                quantity = parse_number(candidate)
                parts = parts[n_tokens:]
                break
            except Exception:
                pass

    if quantity is None:
        return None, 'q.s.', measure

    if parts:
        first = parts[0]

        if first in UNIT_MAP:
            unit = UNIT_MAP[first]
            parts = parts[1:]

        elif first.endswith('s') and first[:-1] in UNIT_MAP:
            unit = UNIT_MAP[first[:-1]]
            parts = parts[1:]

        else:
            unit = 'pcs'

    if parts:
        note = ' '.join(parts)

    return quantity, unit, note