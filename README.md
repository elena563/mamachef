# Mamachef - Your Friend in the Kitchen
 
Mamachef is a full-stack web application designed to be a practical everyday kitchen companion. Users can build a personal recipe catalogue with step-by-step instructions, browse other users' public recipes, follow recipes through an interactive guided cooking mode with integrated timers, and manage a shopping list that can be exported to PDF. The application is fully mobile-responsive and built around a component-based frontend architecture.

### Project Concept and Inspiration

Mamachef originated in a university course on Software Design and Development, where I built a similarly named application in Java with Spring Boot with my teammates Samuele and Stefano. That project defined the domain model and core requirements.  
The core idea became my final project for CS50W course. I rebuilt it from scratch in Django and JavaScript, adding NLP validation, guided cooking mode, PDF export, autocomplete, and the component-based architecture. I thank Samuele and Stefano for their collaboration on the original and for letting me keep the idea alive.

## Features 🥘

- Create, edit and delete recipes
- Multi-step recipes with used ingredients and optional timers
- **Guided cooking mode** with JavaScript timer
- **Shopping list** with AJAX updates and PDF export
- Ingredient autocomplete
- **NLP-based ingredient validation** and normalization
- User authentication and favourite recipes

The project also includes two internal Django commands to fetch recipes from API and generate some missing fields such as the recipe description and difficulty level, using a LLM from Groq.

## Technologies

**Backend:**  

[![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white)](https://www.djangoproject.com/)  
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)

**Frontend:** Django Templates, Django Cotton, Tailwind CSS, Vanilla JavaScript  
**Libraries:** spaCy, NLTK, inflect, ReportLab


## Project Structure

```
mamachef/
│
├── kitchen/               # Main Django app, templates and custom Django commands
├── functions/             # NLP, PDF and helper utilities
│ ├── llms/                # LLM configuration
│ └── recipe_parsing/      # helper function for fetched recipe parsing
├── templates/             # Base templates and Cotton components
├── static/js/             # JavaScript modules
├── theme/                 # Tailwind configuration
├── mamachef/              # Project settings
├── tests/                 # Unit tests
├── requirements.txt
└── manage.py
```

## Usage

### Live Demo

Explore the user interface online by visiting [the website](https://mamachef.alwaysdata.net/).

### From Source
 
#### Prerequisites
 
- Python 3.10 or higher
- Node.js and npm (required by Django-Tailwind)

#### Steps
 
1. Clone the repository: `git clone https://github.com/elena563/mamachef.git`
2. Navigate to the project directory: `cd mamachef`
3. Create and activate a virtual environment
4. Install dependencies: `pip install -r requirements.txt`
5. Install Tailwind CSS dependencies: `python manage.py tailwind install`
6. Download the spaCy language model (required for ingredient validation): `python -m spacy download en_core_web_sm`
7. Apply database migrations: `python manage.py migrate`
8. Run the development servers:  
   Terminal 1:
   ```bash
   python manage.py runserver
   ```
 
   Terminal 2 (Tailwind watcher, recompiles CSS on template changes):
   ```bash
   python manage.py tailwind start
   ```
Run tests with: `python manage.py test` to ensure everything is working correctly.

 
## Future Improvements

- Recipe categories and tags
- Meal planner
- Unit conversion
- Automated test suite

### License

MIT License. Feel free to use, fork, and modify the project.

## Contact

Elena Zen - info.elenazen@gmail.com - [My Portfolio Website](https://elenazen.it)

Thank you for visiting my portfolio!