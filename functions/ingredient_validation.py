import spacy
from nltk.corpus import wordnet as wn
import nltk
import inflect
from difflib import SequenceMatcher

from kitchen.models import Ingredient

nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
_nlp = spacy.load("en_core_web_sm")
_inflect = inflect.engine()

def validate_new_ingredient(name):
    synsets = wn.synsets(name, pos=wn.NOUN)
    if not synsets:
        return False
    
    food_categories = {'noun.food', 'noun.plant', 'noun.substance'}

    for synset in synsets:
        synset_word = synset.name().split('.')[0]
        if synset_word == name and synset.lexname() in food_categories:
            return True # exact match
        
    primary_synset = synsets[0]
    if primary_synset.lexname() in food_categories:
        lemma_names = [lemma.name() for lemma in primary_synset.lemmas()]
        if name in lemma_names or name.replace('_', ' ') in lemma_names:
            return True # match with lemma names
        
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
            
            uncountable_indicators = ['substance', 'material', 'liquid', 'powder', 'flesh', 'meat', 'food']
            if any(indicator in definition for indicator in uncountable_indicators):
                return False
            
            countable_indicators = ['fruit', 'vegetable', 'object', 'item', 'cell']
            if any(indicator in definition for indicator in countable_indicators):
                return True
            
        # if no indicator found
        plural = _inflect.plural(token)
        return token != plural
 

def find_similar_ingredients(name, threshold=0.85):
    """avoid duplicates and typos by finding similar existing ingredients"""
    first_letter = name[0] if name else ''  # reduce comparisons
    candidates = Ingredient.objects.filter(name__istartswith=first_letter)

    similar = []
    for ing in candidates:
        ratio = SequenceMatcher(None, name, ing.name).ratio()
        if ratio > threshold:
            similar.append((ing, ratio))
    return sorted(similar, key=lambda x: x[1], reverse=True)


def get_or_validate_ingredient(name):
    # get if exists
    if Ingredient.objects.filter(name__iexact=name).exists():
        return Ingredient.objects.get(name__iexact=name), None  
    
    # find existing match
    similar = find_similar_ingredients(name)
    if similar:
        return similar[0][0], None
    
    # if totally new
    if not validate_new_ingredient(name):
        return None, f"'{name}' is not a valid ingredient"
    
    ingredient = Ingredient.objects.create(
        name=name if not is_countable(name) else _inflect.plural_noun(name) or name,
        countable=is_countable(name)
    )
    return ingredient, None

def get_ingredient_or_custom(name):
    ingredient, error = get_or_validate_ingredient(name)
    if error:
        return name, True
    return ingredient, False


def validate_quantity_unit(quantity, unit, ingredient_name):
    if unit == 'q.s.':
        return True, None
    
    if quantity is None or quantity.strip() == '':
        return False, "Quantity is required unless unit is 'q.s.'"
    
    try:
        float(quantity)
    except ValueError:
        return False, f"'{quantity}' is not a valid number for quantity"
    
    if not ingredient_name.countable and unit == 'pcs':
        return False, f"Unit '{unit}' is not appropriate for uncountable ingredient '{ingredient_name}'"
    
    return True, None