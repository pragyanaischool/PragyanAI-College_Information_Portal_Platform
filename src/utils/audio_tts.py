"""
src/utils/audio_tts.py

Text-to-Speech (TTS) audio synthesis service using gTTS for PragyanAI College Hub.
Enables instant voice playback for agent responses in English, Kannada, and Hindi.
"""

import io
import re
from typing import Optional
from gTTS import gTTS


class AudioTTSEngine:
    """Manages audio narration synthesis and text cleaning for speech output."""

    SUPPORTED_LANGUAGES = {
        "en": "English",
        "kn": "Kannada",
        "hi": "Hindi",
        "ta": "Tamil",
        "te": "Telugu",
    }

    @staticmethod
    def clean_markdown_for_speech(markdown_text: str) -> str:
        """Removes Markdown headers, bullets, tables, and URLs to produce natural speech."""
        text = re.sub(r"```[\s\S]*?```", "", markdown_text)  # Remove code fences
        text = re.sub(r"`.*?`", "", text)                     # Remove inline code
        text = re.sub(r"http\S+|www\.\S+", "", text)          # Strip URLs
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text) # Keep link label only
        text = re.sub(r"[#*_~>|]", " ", text)                 # Remove MD formatting tokens
        text = re.sub(r"---", " ", text)                      # Remove horizontal dividers
        text = re.sub(r"\s+", " ", text).strip()              # Normalize spaces
        return text

    @classmethod
    def synthesize_to_bytes(
        cls,
        text: str,
        lang_code: str = "en",
        slow: bool = False,
    ) -> io.BytesIO:
        """Synthesizes text into an in-memory MP3 audio stream for Streamlit playback."""
        cleaned_text = cls.clean_markdown_for_speech(text)
        if not cleaned_text:
            cleaned_text = "No audio content available for this response."

        target_lang = lang_code if lang_code in cls.SUPPORTED_LANGUAGES else "en"
        tts = gTTS(text=cleaned_text[:1200], lang=target_lang, slow=slow)

        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer

    @classmethod
    def synthesize_to_file(
        cls,
        text: str,
        output_filepath: str,
        lang_code: str = "en",
        slow: bool = False,
    ) -> str:
        """Synthesizes text and saves it directly to a local MP3 file path."""
        cleaned_text = cls.clean_markdown_for_speech(text)
        target_lang = lang_code if lang_code in cls.SUPPORTED_LANGUAGES else "en"
        tts = gTTS(text=cleaned_text[:1200], lang=target_lang, slow=slow)
        tts.save(output_filepath)
        return output_filepath


def synthesize_speech_bytes(text: str, lang_code: str = "en") -> io.BytesIO:
    """Helper function to generate in-memory MP3 audio bytes."""
    return AudioTTSEngine.synthesize_to_bytes(text, lang_code=lang_code)


def synthesize_speech_file(text: str, output_path: str, lang_code: str = "en") -> str:
    """Helper function to save synthesized speech directly to disk."""
    return AudioTTSEngine.synthesize_to_file(text, output_path, lang_code=lang_code)
