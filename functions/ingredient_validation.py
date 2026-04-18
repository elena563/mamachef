import spacy
from nltk.corpus import wordnet as wn
import nltk
import inflect

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
    token = _nlp(name)[0]
    synsets = wn.synsets(token.lemma_, pos=wn.NOUN)

    if not synsets:
        singular = token.lemma_
        plural = _inflect.plural(singular)
        return singular != plural
    else:
        for i, synset in enumerate(synsets):
            definition = synset.definition().lower()
            
            uncountable_indicators = ['substance', 'material', 'liquid', 'powder']
            if any(indicator in definition for indicator in uncountable_indicators):
                return False
            
            countable_indicators = ['fruit', 'vegetable', 'object', 'item', 'cell']
            if any(indicator in definition for indicator in countable_indicators):
                return True
            
        # if no indicator found
        plural = _inflect.plural(token.lemma_)
        return token.lemma_ != plural