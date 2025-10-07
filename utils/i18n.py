"""Internationalization helpers and common labels."""

from typing import Dict

COMMON_LABELS: Dict[str, Dict[str, str]] = {
    "back": {"en": "Back", "de": "Zurück"},
    "next": {"en": "Next", "de": "Weiter"},
}


def t(key: str, lang: str = "en") -> str:
    """Translate a common key to the requested language.

    Falls back to English when missing.
    """
    if key in COMMON_LABELS:
        return COMMON_LABELS[key].get(lang, COMMON_LABELS[key]["en"])
    # default: return key itself
    return key
