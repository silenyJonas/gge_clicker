import tkinter as tk
from tkinter import ttk
from services.base_tab import BaseTab

class ScanTab(BaseTab, ttk.Frame):
    """Třída pro záložku Scan, která dědí z BaseTab."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.selected_json = tk.StringVar(value="sand")  # výchozí hodnota
        self.scan_distance_var = tk.StringVar(value="999999")  # výchozí hodnota v poli
        self.create_widgets()

    def create_widgets(self):
        """Vytváří widgety pro tuto záložku."""

        # rámec pro radiobuttony v jedné řadě
        frame_radios = ttk.Frame(self)
        frame_radios.pack(pady=10, anchor="w")

        ttk.Radiobutton(frame_radios, text="Zima", variable=self.selected_json, value="winter").pack(side="left", padx=5)
        ttk.Radiobutton(frame_radios, text="Písek", variable=self.selected_json, value="sand").pack(side="left", padx=5)
        ttk.Radiobutton(frame_radios, text="Oheň", variable=self.selected_json, value="fire").pack(side="left", padx=5)

        # rámec pro scan distance
        frame_distance = ttk.Frame(self)
        frame_distance.pack(pady=5, anchor="w")

        ttk.Label(frame_distance, text="Scan vzdálenost:").pack(side="left", padx=(0, 5))
        self.distance_entry = ttk.Entry(frame_distance, textvariable=self.scan_distance_var, width=10)
        self.distance_entry.pack(side="left")

        # tlačítko pro spuštění scanu
        button = ttk.Button(self, text="Spustit Scan", command=self.button_action)
        button.pack(pady=20, anchor="w")

    def button_action(self):
        """Akce, která se provede po stisknutí tlačítka."""
        chosen = self.selected_json.get()

        try:
            scan_distance = int(self.scan_distance_var.get())
        except ValueError:
            scan_distance = 999999  # fallback, pokud je špatný vstup

        self.ScanFort(chosen, scan_distance=scan_distance)
