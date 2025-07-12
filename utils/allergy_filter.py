from utils.error_handler import error_handler
import re

# Attempt to import kivy logger, but create a dummy if it fails.
try:
    from kivy.logger import Logger
except ImportError:
    import logging
    Logger = logging.getLogger(__name__)
    Logger.info = Logger.debug
    Logger.warning = Logger.warning
    Logger.error = Logger.error
    Logger.critical = Logger.critical

# Core allergen mapping
ALLERGEN_MAP = {
    'peanut': ['peanut', 'peanuts', 'arachis', 'arachis hypogaea'],
    'tree nut': ['almond', 'almonds', 'brazil nut', 'brazil nuts', 'cashew', 'cashews', 'hazelnut', 'hazelnuts', 
                 'macadamia', 'macadamias', 'pecan', 'pecans', 'pistachio', 'pistachios', 'walnut', 'walnuts'],
    'milk': ['milk', 'dairy', 'cream', 'butter', 'cheese', 'whey', 'casein', 'lactose', 'lactate'],
    'egg': ['egg', 'eggs', 'albumin', 'albumen', 'ovalbumin', 'ovomucin', 'ovomucoid'],
    'soy': ['soy', 'soya', 'soybean', 'soybeans', 'edamame', 'tofu', 'tempeh', 'miso'],
    'wheat': ['wheat', 'gluten', 'flour', 'bread', 'pasta', 'semolina', 'durum', 'spelt', 'kamut', 'triticale'],
    'fish': ['fish', 'anchovy', 'anchovies', 'bass', 'cod', 'flounder', 'haddock', 'halibut', 'mackerel', 
             'salmon', 'sardine', 'sardines', 'snapper', 'sole', 'swordfish', 'tilapia', 'trout', 'tuna'],
    'shellfish': ['shellfish', 'shrimp', 'prawn', 'crab', 'lobster', 'crayfish', 'crawfish', 'clam', 'mussel', 
                  'oyster', 'scallop', 'squid', 'octopus', 'cuttlefish'],
    'sesame': ['sesame', 'sesame seed', 'sesame seeds', 'tahini', 'benne', 'benne seed', 'benne seeds'],
    'sulfite': ['sulfite', 'sulphite', 'sulfites', 'sulphites', 'sulfur dioxide', 'sulphur dioxide'],
    'celery': ['celery', 'celery root', 'celeriac'],
    'mustard': ['mustard', 'mustard seed', 'mustard seeds', 'mustard powder'],
    'lupin': ['lupin', 'lupine', 'lupins', 'lupines', 'lupin flour', 'lupine flour'],
    'mollusc': ['mollusc', 'molluscs', 'mollusk', 'mollusks', 'snail', 'snails', 'escargot'],
    'crustacean': ['crustacean', 'crustaceans', 'shrimp', 'prawn', 'crab', 'lobster', 'crayfish', 'crawfish']
}

# Reverse mapping: ingredient term → allergen category
REVERSE_ALLERGEN_MAP = {}
for category, terms in ALLERGEN_MAP.items():
    for term in terms:
        REVERSE_ALLERGEN_MAP[term.lower()] = category


def _expand_allergens(input_allergens):
    """
    Expands user-provided allergen input into all relevant ingredient terms,
    including handling reverse lookups (e.g., 'cheese' → 'milk' allergens).
    """
    expanded = set()

    for user_input in input_allergens:
        a_lower = user_input.lower()
        if a_lower in ALLERGEN_MAP:
            expanded.update(term.lower() for term in ALLERGEN_MAP[a_lower])
        elif a_lower in REVERSE_ALLERGEN_MAP:
            parent = REVERSE_ALLERGEN_MAP[a_lower]
            expanded.update(term.lower() for term in ALLERGEN_MAP[parent])
        else:
            expanded.add(a_lower)

    return list(expanded)


@error_handler
def perform_allergy_filter(menu_data, allergen_input_string):
    """
    Filters a menu based on user-entered allergens.

    Args:
        menu_data (list): A list of menu item dictionaries.
        allergen_input_string (str): Comma- or space-separated string of allergens.

    Returns:
        list of filtered menu items with flags and offending allergens.
    """
    if not allergen_input_string:
        Logger.warning("[AllergyFilter] Allergen input string is empty.")
        return None

    # Split on comma or space, clean out empty entries
    input_allergens = [a.strip() for a in re.split(r'[,\s]+', allergen_input_string) if a.strip()]
    if not input_allergens:
        Logger.warning("[AllergyFilter] No valid allergens provided after parsing.")
        return None

    filtered_menu = []
    for row in menu_data:
        ingredients = row.get('ingredients', '')
        ingredients_list = ingredients if isinstance(ingredients, list) else [i.strip() for i in ingredients.split(',')]

        # Build a set of normalized words from all ingredient phrases
        ingredient_words = set()
        for phrase in ingredients_list:
            normalized = re.sub(r'[^a-zA-Z0-9 ]', ' ', phrase.lower())
            ingredient_words.update(normalized.split())

        offending_keywords = set()
        for user_allergen in input_allergens:
            expanded_terms = _expand_allergens([user_allergen])
            for term in expanded_terms:
                if term.lower() in ingredient_words:
                    offending_keywords.add(user_allergen.lower())
                    break

        filtered_row = {
            'item': row.get('item', ''),
            'ingredients': ', '.join(ingredients_list),
            'offending': list(offending_keywords),
            'is_safe': len(offending_keywords) == 0
        }
        filtered_menu.append(filtered_row)

    return filtered_menu
