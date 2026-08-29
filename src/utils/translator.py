"""
src/utils/translator.py

Multilingual Localization Engine using deep-translator for PragyanAI College Hub.
Supports seamless translation of institutional metrics and AI guidance into
Kannada, Hindi, Tamil, Telugu, and English.
"""

from typing import Dict, List, Optional
from deep_translator import GoogleTranslator


class MultilingualTranslator:
    """Provides on-the-fly and cached text translations across Indian languages."""

    LANGUAGE_MAP: Dict[str, str] = {
        "English": "en",
        "ಕನ್ನಡ (Kannada)": "kn",
        "हिंदी (Hindi)": "hi",
        "தமிழ் (Tamil)": "ta",
        "తెలుగు (Telugu)": "te",
    }

    _translation_cache: Dict[str, str] = {}

    @classmethod
    def translate(
        cls,
        text: str,
        target_lang: str = "kn",
        source_lang: str = "auto",
    ) -> str:
        """Translates text to the specified target language code."""
        if not text or not text.strip():
            return ""

        # Avoid redundant translation if source and target are both English
        if target_lang == "en" and source_lang == "en":
            return text

        cache_key = f"{source_lang}_{target_lang}_{hash(text)}"
        if cache_key in cls._translation_cache:
            return cls._translation_cache[cache_key]

        try:
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            # Break large text blocks into sub-4000 character chunks to respect API limits
            if len(text) > 3500:
                chunks = [text[i : i + 3500] for i in range(0, len(text), 3500)]
                translated_chunks = [translator.translate(chunk) for chunk in chunks]
                result = "".join(translated_chunks)
            else:
                result = translator.translate(text)

            cls._translation_cache[cache_key] = result
            return result
        except Exception:
            # Fallback gracefully to original text upon translation timeout or network disruption
            return text

    @classmethod
    def get_supported_languages(cls) -> Dict[str, str]:
        """Returns the dictionary of supported display names to language codes."""
        return cls.LANGUAGE_MAP


def translate_text(text: str, target_lang: str = "kn") -> str:
    """Helper function to perform quick translation."""
    return MultilingualTranslator.translate(text, target_lang=target_lang)
