from unittest.mock import patch

from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.urls import reverse

from functions.ingredient_validation import get_or_validate_ingredient
from functions.language_helpers import detect_input_language, translate_text
from functions.recipe_helpers import save_dynamic_fields
from kitchen.models import Recipe
from tests.helpers import KitchenTestCase

ENGLISH_TEXT = (
    "Today I want to prepare a delicious pasta dish with tomatoes and fresh basil for dinner. "
    "First boil the water and cook the pasta for about ten minutes, then add the sauce."
)
ITALIAN_TEXT = (
    "Oggi voglio preparare un delizioso piatto di pasta con pomodori e basilico fresco per cena. "
    "Prima far bollire l'acqua e cuocere la pasta per circa dieci minuti, poi aggiungere il sugo."
)
GERMAN_TEXT = (
    "Heute möchte ich ein leckeres Nudelgericht mit Tomaten und frischem Basilikum zum Abendessen "
    "zubereiten. Zuerst das Wasser kochen und die Nudeln etwa zehn Minuten garen."
)


class EchoTranslator:
    def __init__(self, *args, **kwargs):
        self.source = kwargs.get("source")
        self.target = kwargs.get("target")

    def translate(self, text):
        return f"[{self.target}] {text}"


class IngredientTranslator(EchoTranslator):
    def translate(self, text):
        if self.source == "it":
            return "tomato"
        return "pomodoro"


class DetectInputLanguageTest(SimpleTestCase):
    def test_detects_english(self):
        lang, error = detect_input_language([ENGLISH_TEXT])

        self.assertEqual(lang, "en")
        self.assertIsNone(error)

    def test_detects_italian(self):
        lang, error = detect_input_language([ITALIAN_TEXT])

        self.assertEqual(lang, "it")
        self.assertIsNone(error)

    def test_aggregates_multiple_texts(self):
        lang, error = detect_input_language(["", "   ", ITALIAN_TEXT, "Cuocere la pasta."])

        self.assertEqual(lang, "it")
        self.assertIsNone(error)

    def test_unsupported_language(self):
        lang, error = detect_input_language([GERMAN_TEXT])

        self.assertIsNone(lang)
        self.assertIn("Not supported language", error)

    def test_empty_text(self):
        lang, error = detect_input_language(["", "   "])

        self.assertIsNone(lang)
        self.assertEqual(error, "Not enough text to detect the language")


class TranslateTextTest(SimpleTestCase):
    def test_empty_text_is_returned_unchanged(self):
        self.assertEqual(translate_text("", "en", "it"), "")
        self.assertEqual(translate_text("   ", "en", "it"), "   ")

    def test_delegates_to_google_translator(self):
        with patch("functions.language_helpers.GoogleTranslator", EchoTranslator):
            self.assertEqual(translate_text("hello", "en", "it"), "[it] hello")


class IngredientLanguageTest(TestCase):
    def test_uses_provided_language_without_detection(self):
        with (
            patch("functions.ingredient_validation.GoogleTranslator", IngredientTranslator),
            patch("functions.ingredient_validation.detect") as mock_detect,
        ):
            ingredient, error = get_or_validate_ingredient("pomodoro", lang="it")

        mock_detect.assert_not_called()
        self.assertIsNone(error)
        self.assertIsNotNone(ingredient)
        self.assertEqual(ingredient.name_it, "pomodoro")


class SaveDynamicFieldsLanguageTest(KitchenTestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()

    def _request(self, data):
        request = self.factory.post("/dummy-url/", data)
        request.session = {}
        request._messages = FallbackStorage(request)
        return request

    def test_italian_steps_are_stored_in_both_languages(self):
        data = {"step": ["Cuocere la pasta.", "Aggiungere il pomodoro."], "timer": ["", ""]}
        request = self._request(data)

        with patch(
            "functions.recipe_helpers.translate_text",
            side_effect=lambda text, source, target: f"[{target}] {text}",
        ) as mock_translate:
            result = save_dynamic_fields(request, self.recipe, lang="it")

        self.assertTrue(result)
        step = self.recipe.steps.get(order=1)
        self.assertEqual(step.description_it, "Cuocere la pasta.")
        self.assertEqual(step.description_en, "[en] Cuocere la pasta.")
        mock_translate.assert_any_call("Cuocere la pasta.", "it", "en")

    def test_english_steps_are_translated_to_italian(self):
        data = {"step": ["Boil the pasta."], "timer": [""]}
        request = self._request(data)

        with patch(
            "functions.recipe_helpers.translate_text",
            side_effect=lambda text, source, target: f"[{target}] {text}",
        ):
            result = save_dynamic_fields(request, self.recipe, lang="en")

        self.assertTrue(result)
        step = self.recipe.steps.get(order=1)
        self.assertEqual(step.description_en, "Boil the pasta.")
        self.assertEqual(step.description_it, "[it] Boil the pasta.")


class RecipeMultilingualViewTest(KitchenTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username="testuser", password="testpass123")

    def recipe_data(self, name, description, step):
        return {
            "name": name,
            "description": description,
            "notes": "",
            "difficulty": "easy",
            "cooking_method": "no cook",
            "preparation_time": 20,
            "servings": 2,
            "category": "Pasta",
            "step": step,
            "timer": ["" for _ in step],
        }

    def test_create_italian_recipe_stores_both_languages(self):
        with (
            patch("kitchen.views.detect_input_language", return_value=("it", None)),
            patch("functions.language_helpers.GoogleTranslator", EchoTranslator),
        ):
            response = self.client.post(
                reverse("Kitchen:new_recipe"),
                self.recipe_data("Pasta al pomodoro", ITALIAN_TEXT, ["Cuocere la pasta."]),
            )

        self.assertEqual(response.status_code, 302)
        recipe = Recipe.objects.latest("id")
        self.assertEqual(recipe.name_it, "Pasta al pomodoro")
        self.assertEqual(recipe.name_en, "[en] Pasta al pomodoro")
        self.assertEqual(recipe.description_it, ITALIAN_TEXT)
        self.assertEqual(recipe.description_en, f"[en] {ITALIAN_TEXT}")
        step = recipe.steps.get(order=1)
        self.assertEqual(step.description_it, "Cuocere la pasta.")
        self.assertEqual(step.description_en, "[en] Cuocere la pasta.")

    def test_update_english_recipe_stores_both_languages(self):
        recipe = Recipe.objects.create(
            name_en="Old name",
            name_it="Vecchio nome",
            difficulty="easy",
            category="Pasta",
            author=self.user,
        )

        with (
            patch("kitchen.views.detect_input_language", return_value=("en", None)),
            patch("functions.language_helpers.GoogleTranslator", EchoTranslator),
        ):
            response = self.client.post(
                reverse("Kitchen:edit_recipe", args=[recipe.pk]),
                self.recipe_data("Tomato pasta", ENGLISH_TEXT, ["Boil the pasta."]),
            )

        self.assertEqual(response.status_code, 302)
        recipe.refresh_from_db()
        self.assertEqual(recipe.name_en, "Tomato pasta")
        self.assertEqual(recipe.name_it, "[it] Tomato pasta")
        self.assertEqual(recipe.description_en, ENGLISH_TEXT)
        self.assertEqual(recipe.description_it, f"[it] {ENGLISH_TEXT}")
        step = recipe.steps.get(order=1)
        self.assertEqual(step.description_en, "Boil the pasta.")
        self.assertEqual(step.description_it, "[it] Boil the pasta.")
