import tkinter as tk
from tkinter import ttk

class ScanTab(ttk.Frame):
    """Šestá záložka - ukázka."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        """Vytváří widgety pro tuto záložku."""
        label = ttk.Label(self, text="Toto je obsah šesté záložky.")
        label.pack(padx=20, pady=20)

        button = ttk.Button(self, text="Tlačítko 6", command=self.button_action)
        button.pack(pady=10)

    def button_action(self):
        """Akce, která se provede po stisknutí tlačítka."""
        print("Akce z Tab6 byla provedena.")