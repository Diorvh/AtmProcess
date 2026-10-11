"""Local ttk adapters; editable values and tkinter itself are left untouched."""
from __future__ import annotations

from tkinter import ttk as _ttk

from AtmProcess.ui.localization import language_for


def __getattr__(name):
    return getattr(_ttk, name)


class _LocalizedText:
    def __init__(self, master=None, *, translate=True, **kwargs):
        self._translate_text = translate
        self._source_text = kwargs.get("text", "")
        source_variable = kwargs.pop("textvariable", None)
        self._source_variable = None
        self._variable_trace = None
        super().__init__(master, **kwargs)
        self._language = language_for(self)
        self._language.register(self)
        if source_variable is not None:
            self._bind_source_variable(source_variable)
        self.refresh_language()

    def _bind_source_variable(self, variable) -> None:
        self._unbind_source_variable()
        self._source_variable = variable
        self._variable_trace = variable.trace_add("write", self._variable_changed)

    def _unbind_source_variable(self) -> None:
        if self._variable_trace is not None:
            self._source_variable.trace_remove("write", self._variable_trace)
        self._source_variable = self._variable_trace = None

    def _variable_changed(self, *_args) -> None:
        self.refresh_language()

    def configure(self, cnf=None, **kwargs):
        if isinstance(cnf, str) or (cnf is None and not kwargs):
            return super().configure(cnf, **kwargs)
        options = dict(cnf or {})
        options.update(kwargs)
        if "textvariable" in options:
            variable = options.pop("textvariable")
            if variable:
                self._bind_source_variable(variable)
            else:
                self._unbind_source_variable()
        if "text" in options:
            self._source_text = options.pop("text")
        options["text"] = self._display_text()
        return super().configure(**options)

    config = configure

    def _display_text(self):
        source = self._source_variable.get() if self._source_variable is not None else self._source_text
        return self._language.text(source) if self._translate_text else source

    def refresh_language(self) -> None:
        super().configure(text=self._display_text())  # Never write translated text back to the source Tk variable.

    def destroy(self) -> None:
        self._unbind_source_variable()
        super().destroy()


class Label(_LocalizedText, _ttk.Label):
    pass


class Button(_LocalizedText, _ttk.Button):
    pass


class Checkbutton(_LocalizedText, _ttk.Checkbutton):
    pass


class Radiobutton(_LocalizedText, _ttk.Radiobutton):
    pass


class LabelFrame(_LocalizedText, _ttk.LabelFrame):
    pass


class Notebook(_ttk.Notebook):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._tab_sources = {}
        self._language = language_for(self)
        self._language.register(self)

    def add(self, child, **kwargs):
        if "text" in kwargs:
            self._tab_sources[str(child)] = kwargs["text"]
            kwargs["text"] = self._language.text(kwargs["text"])
        return super().add(child, **kwargs)

    def tab(self, tab_id, option=None, **kwargs):
        if "text" in kwargs:
            key = self.tabs()[self.index(tab_id)]
            self._tab_sources[key] = kwargs["text"]
            kwargs["text"] = self._language.text(kwargs["text"])
        return super().tab(tab_id, option, **kwargs)

    def refresh_language(self) -> None:
        for key in self.tabs():
            if key in self._tab_sources:
                super().tab(key, text=self._language.text(self._tab_sources[key]))


class Treeview(_ttk.Treeview):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._heading_sources = {}
        self._language = language_for(self)
        self._language.register(self)

    def heading(self, column, option=None, **kwargs):
        if "text" in kwargs:
            self._heading_sources[column] = kwargs["text"]
            kwargs["text"] = self._language.text(kwargs["text"])
        return super().heading(column, option, **kwargs)

    def refresh_language(self) -> None:
        for column in ("#0", *self["columns"]):
            if column in self._heading_sources:  # Measurement modes have different columns; ignore inactive headings.
                super().heading(column, text=self._language.text(self._heading_sources[column]))
