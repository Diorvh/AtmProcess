"""Offline, presentation-only translations shared by one Tk window."""
from __future__ import annotations

import json
import re
import tkinter as tk
from functools import lru_cache
from pathlib import Path
from weakref import WeakSet


LANGUAGES = ("zh", "en")
_CATALOG = json.loads((Path(__file__).with_name("locales") / "en.json").read_text(encoding="utf-8"))
_FIELD = re.compile(r"\{(\d+)\}")
_TEMPLATES = []
for _source, _translation in _CATALOG.items():
    if not _FIELD.search(_source):
        continue
    _parts = _FIELD.split(_source)
    _pattern = "".join(re.escape(part) if index % 2 == 0 else "(.*?)" for index, part in enumerate(_parts))
    _TEMPLATES.append((_parts[0], re.compile(_pattern, re.DOTALL), _translation, sum(map(len, _parts[::2]))))
_TEMPLATES.sort(key=lambda item: item[3], reverse=True)


@lru_cache(maxsize=2048)
def translate(source: str, language: str = "zh") -> str:
    if language != "en" or not source:
        return source
    exact = _CATALOG.get(source)
    if isinstance(exact, str):
        return exact
    for prefix, pattern, translation, _specificity in _TEMPLATES:
        if not source.startswith(prefix):
            continue
        match = pattern.fullmatch(source)
        if match is None:
            continue
        values = list(match.groups())
        if isinstance(translation, dict):
            for index in translation.get("translate_fields", []):
                values[index] = translate(values[index], language)
            translation = translation["text"]
        return translation.format(*values)  # Path, filename and numeric fields stay literal unless explicitly marked as UI text.
    return source


class LanguageController:
    def __init__(self, language: str = "zh") -> None:
        self.language = language if language in LANGUAGES else "zh"
        self._targets = WeakSet()

    def text(self, source) -> str:
        return translate(str(source), self.language)

    def register(self, target) -> None:
        self._targets.add(target)

    def set_language(self, language: str) -> None:
        if language not in LANGUAGES:
            raise ValueError(f"Unsupported interface language: {language}")
        if self.language == language:
            return
        self.language = language
        for target in tuple(self._targets):
            try:
                target.refresh_language()
            except tk.TclError:
                self._targets.discard(target)


def language_for(widget) -> LanguageController:
    root = widget._root()
    controller = getattr(root, "_ui_language", None)
    if controller is None:
        controller = LanguageController()
        root._ui_language = controller
    return controller
