from django.core.management.base import BaseCommand
from kitchen.models import Recipe
from functions.recipe_parsing import generate

class Command(BaseCommand):
    help = 'Generates missing fields for recipes'

    def handle(self, *args, **options):

        to_fill = Recipe.objects.filter(description__isnull=True) | Recipe.objects.filter(difficulty__isnull=True)

        for recipe in to_fill:
            try:
                result = generate(recipe.name)
                if result:
                    
                    recipe.description = result.get('description', recipe.description)
                    recipe.difficulty = result.get('difficulty', recipe.difficulty)
                    recipe.save()
                    self.stdout.write(self.style.SUCCESS(f"Updated recipe '{recipe.name}' with generated fields."))
                    #print(repr(result))
                    #print(f"Generated fields for recipe '{recipe.name}': {result.get('description')}, {result.get('difficulty')}")
                    
                else:
                    self.stdout.write(self.style.WARNING(f"No result for recipe '{recipe.name}'."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error generating fields for recipe '{recipe.name}': {e}"))