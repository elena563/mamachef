from deep_translator import GoogleTranslator
from langdetect import DetectorFactory, LangDetectException, detect_langs

DetectorFactory.seed = 0

SUPPORTED_LANGUAGES = ("en", "it")


def detect_input_language(texts):
    """Detects the input language once from the aggregated texts."""
    combined = " ".join(text.strip() for text in texts if text and text.strip())
    if not combined:
        return None, "Not enough text to detect the language"
    try:
        languages = detect_langs(combined)
    except LangDetectException:
        return None, "Could not detect the language"
    if not languages:
        return None, "Could not detect the language"
    lang = languages[0].lang
    if lang not in SUPPORTED_LANGUAGES:
        return None, f"Not supported language: {lang}"
    return lang, None


def translate_text(text, source, target):
    if not text or not text.strip():
        return text
    return GoogleTranslator(source=source, target=target).translate(text)
