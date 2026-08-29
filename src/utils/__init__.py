"""
src/utils/__init__.py

Utility services initialization for PragyanAI College Intelligence Hub.
Exposes Text-to-Speech synthesis, multi-language translation, and verifiable
event certificate generation.
"""

from src.utils.audio_tts import AudioTTSEngine, synthesize_speech_bytes, synthesize_speech_file
from src.utils.certificate_gen import CertificateGenerator, generate_event_certificate
from src.utils.translator import MultilingualTranslator, translate_text

__all__ = [
    "AudioTTSEngine",
    "synthesize_speech_bytes",
    "synthesize_speech_file",
    "MultilingualTranslator",
    "translate_text",
    "CertificateGenerator",
    "generate_event_certificate",
]
