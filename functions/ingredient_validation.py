from difflib import SequenceMatcher

import inflect
import nltk
import spacy
from langdetect import LangDetectException, detect_langs
from nltk.corpus import wordnet as wn

from kitchen.models import Ingredient

from .language_helpers import translate_text

nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)
_nlp = spacy.load("en_core_web_sm")
_inflect = inflect.engine()

# Manual Glossary For Ingredients That Machine Translation Validates Incorrectly
INGREDIENT_GLOSSARY = {
    "pecorino": ("Pecorino Cheese", False),
    "pecorino romano": ("Pecorino Romano Cheese", False),
    "parmigiano": ("Parmigiano Reggiano", False),
    "grana padano": ("Grana Padano", False),
    "mozzarella": ("Mozzarella", False),
    "mozzarella di bufala": ("Buffalo Mozzarella", False),
    "ricotta": ("Ricotta", False),
    "scamorza": ("Scamorza Cheese", False),
    "provola": ("Provola Cheese", False),
    "caciocavallo": ("Caciocavallo Cheese", False),
    "stracchino": ("Stracchino Cheese", False),
    "taleggio": ("Taleggio Cheese", False),
    "gorgonzola": ("Gorgonzola Cheese", False),
    "fontina": ("Fontina Cheese", False),
    "guanciale": ("Guanciale", False),
    "pancetta": ("Pancetta", False),
    "prosciutto": ("Prosciutto", False),
    "prosciutto crudo": ("Prosciutto Crudo", False),
    "prosciutto cotto": ("Cooked Ham", False),
    "lardo": ("Lardo", False),
    "bottarga": ("Bottarga", False),
    "nduja": ("Nduja", False),
    "'nduja": ("Nduja", False),
    "mollica": ("Breadcrumbs", False),
    "pangrattato": ("Breadcrumbs", False),
    "passata": ("Tomato Passata", False),
    "farro": ("Farro", False),
}


def validate_new_ingredient(name):
    formatted_name = name.lower().strip().replace(" ", "_")
    synsets = wn.synsets(formatted_name, pos=wn.NOUN)
    if not synsets:
        return False

    food_categories = {"noun.food", "noun.plant", "noun.substance"}

    for synset in synsets:
        synset_word = synset.name().split(".")[0]
        if synset_word == formatted_name and synset.lexname() in food_categories:
            return True  # exact match

    primary_synset = synsets[0]
    if primary_synset.lexname() in food_categories:
        lemma_names = [lemma.name() for lemma in primary_synset.lemmas()]
        if formatted_name in lemma_names or formatted_name.replace("_", " ") in lemma_names:
            return True  # match with lemma names

    return False


def is_countable(name):
    token = _nlp(name)[0].lemma_
    synsets = wn.synsets(token, pos=wn.NOUN)

    if not synsets:
        singular = token
        plural = _inflect.plural(singular)
        return singular != plural
    else:
        for i, synset in enumerate(synsets):
            definition = synset.definition().lower()

            uncountable_indicators = [
                "substance",
                "material",
                "liquid",
                "powder",
                "flesh",
                "meat",
                "food",
            ]
            if any(indicator in definition for indicator in uncountable_indicators):
                return False

            countable_indicators = ["fruit", "vegetable", "object", "item", "cell"]
            if any(indicator in definition for indicator in countable_indicators):
                return True

        # if no indicator found
        plural = _inflect.plural(token)
        return token != plural


def find_similar_ingredients(name, threshold=0.85):
    """avoid duplicates and typos by finding similar existing ingredients"""
    first_letter = name[0].lower() if name else ""
    candidates = Ingredient.objects.filter(name_en__istartswith=first_letter)

    similar = []
    for ing in candidates:
        ratio = SequenceMatcher(None, name.lower(), ing.name_en.lower()).ratio()
        if ratio > threshold:
            similar.append((ing, ratio))
    return sorted(similar, key=lambda x: x[1], reverse=True)


def normalize_ingredient_name(name):
    """singularizes and capitalizes the ingredient name, returns existing ingredient if found"""
    if is_countable(name):
        singular_form = _inflect.singular_noun(name)
        if singular_form:
            name = singular_form

    target_name = name.title()

    # get if exists
    existing = Ingredient.objects.filter(name_en__iexact=target_name).first()
    if existing:
        return existing, None

    # find existing match
    similar = find_similar_ingredients(name)
    if similar:
        return similar[0][0], None

    # if totally new
    if not validate_new_ingredient(name):
        return None, f"'{name}' is not a valid ingredient"

    return name, None


def _get_glossary_ingredient(name):
    entry = INGREDIENT_GLOSSARY.get(" ".join(name.lower().strip().split()))
    if entry is None:
        return None

    name_en, countable = entry
    existing = (
        Ingredient.objects.filter(name_it__iexact=name.strip()).first()
        or Ingredient.objects.filter(name_en__iexact=name_en).first()
    )
    if existing:
        return existing

    return Ingredient.objects.create(
        name=name_en,
        name_en=name_en,
        name_it=name.strip().title(),
        countable=countable,
    )


def get_or_validate_ingredient(name, lang=None):
    """validates the ingredient name, translates, and returns the Ingredient or an error message"""
    name_clean = name.strip()

    if not lang:
        try:
            candidates = detect_langs(name)
        except LangDetectException:
            candidates = []
        lang = next(
            (candidate.lang for candidate in candidates if candidate.lang in ("en", "it")),
            "en",
        )

    if lang not in ["en", "it"]:
        return None, f"Not supported language: {lang}"

    glossary_ingredient = _get_glossary_ingredient(name_clean)
    if glossary_ingredient:
        return glossary_ingredient, None

    if lang == "en":
        name, error = normalize_ingredient_name(name_clean)
    elif lang == "it":
        name_en = translate_text(name_clean, "it", "en")
        if not name_en:
            return None, "Translation service unavailable. Please try again."
        name, error = normalize_ingredient_name(name_en)

    if error:
        return None, error

    if isinstance(name, Ingredient):
        return name, None

    name_en = name.title().strip()
    name_it = translate_text(name_en, "en", "it")

    ingredient = Ingredient.objects.create(
        name_en=name_en,
        name_it=name_it,
        countable=is_countable(name_en),
    )
    return ingredient, None


def get_ingredient_or_custom(name):
    ingredient, error = get_or_validate_ingredient(name)
    if error:
        return name.title(), True
    return ingredient, False


def validate_quantity_unit(quantity, unit, ingredient_name, for_list=False):
    if unit == "q.s.":
        return True, None

    if (quantity is None or quantity.strip() == "") and not for_list:
        return False, "Quantity is required unless unit is 'q.s.'"

    try:
        float(quantity)
    except ValueError:
        return False, f"'{quantity}' is not a valid number for quantity"

    if not ingredient_name.countable and unit == "pcs" and not for_list:
        return (
            False,
            f"Unit '{unit}' is not appropriate for uncountable ingredient '{ingredient_name.name_en}'",
        )

    return True, None
