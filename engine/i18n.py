"""
Lightweight i18n service.

Translation files live in  translations/<lang>.json  as flat key→string dicts.
Missing keys fall back to English, then to the raw key so nothing silently breaks.
"""

import json
import os
from typing import Dict

SUPPORTED_LANGS = ['en', 'de']
DEFAULT_LANG = 'en'

_TRANSLATIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'translations')
_cache: Dict[str, dict] = {}


def _load(lang: str) -> dict:
    """Load and cache a translation catalog.  Thread-safe enough for single-process Flask."""
    if lang not in _cache:
        path = os.path.join(_TRANSLATIONS_DIR, f'{lang}.json')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                _cache[lang] = json.load(f)
        else:
            _cache[lang] = {}
    return _cache[lang]


def t(key: str, lang: str = DEFAULT_LANG, **ctx) -> str:
    """
    Return the localized string for *key* in *lang*.

    Falls back to English, then to the bare key so the UI never shows empty strings.
    Supports simple {var} interpolation via ctx kwargs.
    """
    text = _load(lang).get(key) or _load(DEFAULT_LANG).get(key, key)
    if ctx:
        try:
            text = text.format(**ctx)
        except (KeyError, ValueError):
            pass
    return text


def catalog(lang: str) -> dict:
    """Return the full translation catalog dict for *lang* (used for window.I18N injection)."""
    base = dict(_load(DEFAULT_LANG))   # start with English so all keys are present
    base.update(_load(lang))           # overlay target language
    return base
