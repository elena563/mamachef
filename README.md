# Mamachef - Your Friend in the Kitchen
 
**CS50W Web Programming with Python and JavaScript - Final Project**
 
Mamachef is a full-stack web application designed to be a practical everyday kitchen companion. Users can build a personal recipe catalogue with step-by-step instructions, browse other users' public recipes, follow recipes through an interactive guided cooking mode with integrated timers, and manage a shopping list that can be exported to PDF. The application is fully mobile-responsive and built around a component-based frontend architecture.
 
---
 
## Distinctiveness and Complexity
 
Mamachef is neither a social network nor an e-commerce platform, and it differs from every prior CS50W project in both domain and technical scope.
 
**Why it is distinct.** The course projects cover a wiki (Project 1), an auction site (Project 2), an email client (Project 3), and a social network (Project 4). Mamachef belongs to none of these categories. Its domain is kitchen management: users create structured recipes, cook through them step by step, and track what they need to buy. Recipes are publicly browsable so users can discover what others have shared, but there is no social graph, no feed, no followers, and no interactions between users. It is a utility, not a networking platform. There is also no product catalogue, no cart, and no checkout flow.
 
**Why it is complex.** The complexity of Mamachef is not concentrated in a single feature, it comes from several layers that together go well beyond a standard CRUD application:
 
- The **data model** is non-trivial. Recipes contain multiple ordered steps, each with its own instructions, ingredients, and optional timer duration, a schema that requires several related models with foreign keys and ordering constraints, rather than a single flat table.
 
- The **ingredient validation and NLP pipeline** is where my background in data science shaped the project most directly. Having worked with NLP before, I wanted to build something more useful than plain text fields. Ingredient names are validated and normalised at submission time using **spaCy** for linguistic analysis, **NLTK** for tokenisation and morphological processing, and **inflect** for singular/plural equivalences. The system detects near-duplicates and suggests corrections when a similar ingredient already exists, a layer of intelligence that required domain knowledge to design well.
 
- The **autocomplete system** is backed by a dedicated Django JSON endpoint queried via the Fetch API as the user types, with no third-party library involved.
 
- The **shopping list** supports real-time AJAX toggling of purchased items, bulk deletion, and server-side PDF export using **ReportLab**, simple and interesting library to do this directly in Python.
 
- The **guided cooking mode** is built entirely in JavaScript: it navigates through steps one at a time and runs a countdown timer (with start, pause, and reset) for any step that has a duration, all without page reloads.
 
The **frontend architecture** uses **Django Cotton** throughout, a library that brings component-based templating to Django with explicit props, closer in spirit to React components, still using vanilla JavaScript and templates.
The **Tailwind CSS pipeline** via `django-tailwind` and `pytailwindcss` adds a real build step with CSS purging and a watcher process, rather than a CDN import.
 
---
 
## Files

### Root

- **`manage.py`**
- **`requirements.txt`**    Python dependencies
- **`README.md`**

### `mamachef/` - Django project configuration

- **`settings.py`**    Global configuration
- **`urls.py`**
- **`wsgi.py`** / **`asgi.py`**
- **`__init__.py`** 

### `kitchen/`    Main application

- **`models.py`**    Data models: `Recipe`, `RecipeStep`, `Ingredient`, `RecipeIngredient`, `ShoppingList`, `ShoppingListItem`, `UserProfile`.
- **`views.py`**    Views: recipe list/search/filter, detail, create/edit/delete, guided mode, shopping list management, AJAX endpoints (mark bought, ingredient autocomplete, PDF export), favourite toggle, user profile, login/logout/registration.
- **`urls.py`**    URL patterns for kitchen views and APIs.
- **`forms.py`**    Django forms
- **`admin.py`**    Model registration for Django admin (empty).
- **`variables.py`**    Support constants and variables.
- **`tests.py`**    Basic tests (empty at the moment).
- **`migrations/`**    Database migrations
- **`templates/`**    HTML templates

### `functions/`    Python utilities

- **`ingredient_validation.py`**    Ingredient validation and normalization (spaCy, NLTK, inflect, similarity, suggestions).
- **`pdf.py`**    Shopping list PDF generation (ReportLab).
- **`recipe_helpers.py`**    Helper functions for filters, recipe logic, etc.

### `kitchen/templates/`    Kitchen HTML templates

- **`home.html`**    App home
- **`login.html`**    User login.
- **`profile.html`**    User profile (avatar, own/favourite recipes).
- **`recipes.html`**    Recipe list with filters/search.
- **`recipe_detail.html`**    Recipe detail, ingredients, steps, favourites.
- **`guided_mode.html`**    Guided mode: step-by-step recipe, JS timer.
- **`recipe_form.html`**    Recipe create/edit form (dynamic JS for ingredients/steps).
- **`register.html`**    User registration.
- **`shopping_list.html`**    Shopping list (AJAX check, bulk delete, PDF export).

### `templates/`    Base template and Cotton components

- **`base.html`**    Base layout, navbar, title/content blocks.
- **`cotton/`**    Reusable components (Django Cotton):
   - **`button.html`**    Generic button with variants.
   - **`chip_input.html`**    Chip-style input.
   - **`form_field.html`**    Form input wrapper.
   - **`header.html`**    Main navbar.
   - **`messages_box.html`**    Message box.
   - **`recipe_card.html`**    Recipe card for lists.
   - **`search_bar.html`**    Search/filter bar.

### `static/js/`    Custom JavaScript

- **`guided_mode.js`**    Guided mode step navigation and timer.
- **`recipe_form.js`**    Dynamic recipe form (ingredients, steps, ingredient autocomplete via fetch).
- **`shopping_list.js`**    Shopping list check via fetch/AJAX, UI update.

### `theme/`    Tailwind CSS theme

- **`apps.py`**    Django app config for the theme (empty).
- **`static_src/src/styles.css`**    CSS entry file (Tailwind base/components/utilities).

 
## How to Run the Application
 
### Prerequisites
 
- Python 3.10 or higher
- Node.js and npm (required by Django-Tailwind)
### Steps
 
1. **Clone the repository**
   ```bash
   git clone https://github.com/elena563/mamachef.git
   cd mamachef
   ```
 
2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate        # On Windows: venv\Scripts\activate
   ```
 
3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```
 
4. **Install Tailwind CSS dependencies**
   ```bash
   python manage.py tailwind install
   ```
 
5. **Download the spaCy language model** (required for ingredient validation)
   ```bash
   python -m spacy download en_core_web_sm
   ```
 
6. **Apply database migrations**
   ```bash
   python manage.py migrate
   ```
 
7. **Run the development servers**    two terminals are required
   Terminal 1:
   ```bash
   python manage.py runserver
   ```
 
   Terminal 2 (Tailwind watcher, recompiles CSS on template changes):
   ```bash
   python manage.py tailwind start
   ```
 
8. **Open the app** at [http://127.0.0.1:8000](http://127.0.0.1:8000)
---
 
## Additional Notes
 
Planned future extensions include recipe categories and tags, stricter unit conversion between metric and imperial, a proper test suite, and a weekly meal planner.