import tkinter as tk
from tkinter import ttk

class NomadTab(ttk.Frame):
    """Třetí záložka - ukázka."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        """Vytváří widgety pro tuto záložku."""
        label = ttk.Label(self, text="Toto je obsah třetí záložky.")
        label.pack(padx=20, pady=20)

        button = ttk.Button(self, text="Tlačítko 3", command=self.button_action)
        button.pack(pady=10)

    def button_action(self):
        """Akce, která se provede po stisknutí tlačítka."""
        print("Akce z Tab3 byla provedena.")