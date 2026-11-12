import functools
import logging
import threading

from langdetect import DetectorFactory, LangDetectException, detect_langs

DetectorFactory.seed = 0

SUPPORTED_LANGUAGES = ("en", "it")

logger = logging.getLogger(__name__)

_translation_lock = threading.Lock()


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


@functools.lru_cache(maxsize=4096)
def _translate_cached(text, source, target):
    from argostranslate import translate as argos_translate

    with _translation_lock:
        return argos_translate.translate(text, source, target)


def translate_text(text, source, target):
    if not text or not text.strip():
        return text
    if source == target:
        return text
    try:
        return _translate_cached(text, source, target)
    except Exception:
        logger.warning("Argos translation failed (%s -> %s)", source, target, exc_info=True)
        return ""


def translate_batch(texts, source, target):
    return [translate_text(text, source, target) for text in texts]
