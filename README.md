# Mamachef - Your Friend in the Kitchen
 
Mamachef is a full-stack web application designed to be a practical everyday kitchen companion. Users can build a personal recipe catalogue with step-by-step instructions, browse other users' public recipes, follow recipes through an interactive guided cooking mode with integrated timers, and manage a shopping list that can be exported to PDF. The application is fully mobile-responsive and built around a component-based frontend architecture.
 
---

## Live Demo

Explore the user interface online by visiting [the website](https://mamachef.alwaysdata.net/).

## Project Concept and Inspiration

Mamachef originated in a university course on Software Design and Development, where I built a similarly named application in Java with Spring Boot with my teammates Samuele and Stefano. That project defined the domain model and core requirements.  
The core idea became my final project for CS50W course. I rebuilt it from scratch in Django and JavaScript, adding NLP validation, guided cooking mode, PDF export, autocomplete, and the component-based architecture. I thank Samuele and Stefano for their collaboration on the original and for letting me keep the idea alive.

## Features

- Create, edit and delete recipes
- Multi-step recipes with ingredients and optional timers
- Guided cooking mode with JavaScript timer
- Shopping list with AJAX updates and PDF export
- Ingredient autocomplete
- NLP-based ingredient validation and normalization
- User authentication and favourite recipes

## Tech Stack

### Backend

- Django
- SQLite
- spaCy
- NLTK
- inflect
- ReportLab

### Frontend

- Django Templates
- Django Cotton
- Tailwind CSS
- Vanilla JavaScript (Fetch API)

## Project Structure

```
mamachef/
│
├── kitchen/          # Main Django app
├── functions/        # NLP, PDF and helper utilities
├── templates/        # Base templates and Cotton components
├── static/js/        # JavaScript modules
├── theme/            # Tailwind configuration
├── mamachef/         # Project settings
├── requirements.txt
└── manage.py
```
 
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
 
## Future Improvements

- Recipe categories and tags
- Meal planner
- Unit conversion
- Automated test suite