import tkinter as tk
from tkinter import ttk
import threading
import time
from services.base_tab import BaseTab  # děděno z BaseTab pro logování

class NomadTab(BaseTab, ttk.Frame):
    """Třetí záložka - Nomádi."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # --- Výchozí hodnoty ---
        self.is_running = False
        self.feather_horses = True
        self.use_fill_all_waves = False
        self.first_wave_from_bottom = 1
        self.other_waves_from_bottom = 2
        self.auto_fill_waves = False
        self.target_x = 0
        self.target_y = 0
        self.max_attacks = 10

        self.create_widgets()

    def create_widgets(self):
        """Vytváří widgety pro tuto záložku."""

        # --- Typ koně ---
        horse_frame = ttk.Frame(self)
        horse_frame.pack(pady=10, anchor="w")
        ttk.Label(horse_frame, text="Typ koně:").pack(side=tk.LEFT, padx=(0, 10))

        self.feather_horses_var = tk.BooleanVar(value=self.feather_horses)
        ttk.Radiobutton(horse_frame, text="Gold koně", variable=self.feather_horses_var, value=False,
                        command=self._on_horse_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(horse_frame, text="Pírko koně", variable=self.feather_horses_var, value=True,
                        command=self._on_horse_changed).pack(side=tk.LEFT, padx=5)

        # --- Volba použití vln ---
        wave_frame = ttk.Frame(self)
        wave_frame.pack(pady=10, anchor="w")
        ttk.Label(wave_frame, text="Strategie útoku:").pack(side=tk.LEFT, padx=(0, 10))

        self.wave_mode_var = tk.StringVar(value="first")
        ttk.Radiobutton(wave_frame, text="Použít první vlnu pouze", variable=self.wave_mode_var, value="first",
                        command=self._on_wave_mode_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(wave_frame, text="Použít fill všech vln", variable=self.wave_mode_var, value="all",
                        command=self._on_wave_mode_changed).pack(side=tk.LEFT, padx=5)

        # --- Extra inputy (jen pro fill všech vln) ---
        self.extra_frame = ttk.Frame(self)
        # první vlna od spodu
        first_wave_frame = ttk.Frame(self.extra_frame)
        first_wave_frame.pack(pady=5, anchor="w")
        ttk.Label(first_wave_frame, text="První vlna od spodu:").pack(side=tk.LEFT, padx=(0, 5))
        self.first_wave_entry = ttk.Entry(first_wave_frame, width=10)
        self.first_wave_entry.insert(0, str(self.first_wave_from_bottom))
        self.first_wave_entry.pack(side=tk.LEFT)

        # ostatní vlny od spodu
        other_wave_frame = ttk.Frame(self.extra_frame)
        other_wave_frame.pack(pady=5, anchor="w")
        ttk.Label(other_wave_frame, text="Ostatní vlny od spodu:").pack(side=tk.LEFT, padx=(0, 5))
        self.other_wave_entry = ttk.Entry(other_wave_frame, width=10)
        self.other_wave_entry.insert(0, str(self.other_waves_from_bottom))
        self.other_wave_entry.pack(side=tk.LEFT)

        # automatické doplnění
        auto_fill_frame = ttk.Frame(self.extra_frame)
        auto_fill_frame.pack(pady=5, anchor="w")
        ttk.Label(auto_fill_frame, text="Doplnit vlny automaticky vojáky:").pack(side=tk.LEFT, padx=(0, 5))
        self.auto_fill_var = tk.BooleanVar(value=self.auto_fill_waves)
        ttk.Checkbutton(auto_fill_frame, variable=self.auto_fill_var).pack(side=tk.LEFT)

        # --- Souřadnice tábora ---
        coords_frame = ttk.Frame(self)
        coords_frame.pack(pady=5, anchor="w")
        ttk.Label(coords_frame, text="Souřadnice tábora:").pack(side=tk.LEFT, padx=(0, 5))
        self.target_x_entry = ttk.Entry(coords_frame, width=6)
        self.target_x_entry.insert(0, str(self.target_x))
        self.target_x_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(coords_frame, text=":").pack(side=tk.LEFT)
        self.target_y_entry = ttk.Entry(coords_frame, width=6)
        self.target_y_entry.insert(0, str(self.target_y))
        self.target_y_entry.pack(side=tk.LEFT, padx=2)

        # --- Maximální počet útoků ---
        max_attacks_frame = ttk.Frame(self)
        max_attacks_frame.pack(pady=5, anchor="w")
        ttk.Label(max_attacks_frame, text="Maximální počet útoků:").pack(side=tk.LEFT, padx=(0, 5))
        self.max_attacks_entry = ttk.Entry(max_attacks_frame, width=10)
        self.max_attacks_entry.insert(0, str(self.max_attacks))
        self.max_attacks_entry.pack(side=tk.LEFT)

        # --- Ovládací tlačítka Start / Stop ---
        control_frame = ttk.Frame(self)
        control_frame.pack(pady=15, anchor="center")
        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_action)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_action)
        self.stop_button.pack(side=tk.LEFT, padx=5)

    # --- Callbacky ---
    def _on_horse_changed(self):
        self.feather_horses = bool(self.feather_horses_var.get())
        horse_type = "Pírko" if self.feather_horses else "Gold"
        self.log_message(status="info", message=f"Typ koně byl změněn na: {horse_type}")

    def _on_wave_mode_changed(self):
        mode = self.wave_mode_var.get()
        if mode == "all":
            self.extra_frame.pack(pady=10, anchor="w")
            self.use_fill_all_waves = True
        else:
            self.extra_frame.pack_forget()
            self.use_fill_all_waves = False
        self.log_message(status="info", message=f"Strategie útoku nastavena na: {mode}")

    # --- Start / Stop ---
    def start_action(self):
        if self.is_running:
            self.log_message(status="info", message="Akce již běží!")
            return
        try:
            if self.use_fill_all_waves:
                self.first_wave_from_bottom = int(self.first_wave_entry.get())
                self.other_waves_from_bottom = int(self.other_wave_entry.get())
                self.auto_fill_waves = bool(self.auto_fill_var.get())

            self.target_x = int(self.target_x_entry.get())
            self.target_y = int(self.target_y_entry.get())
            self.max_attacks = int(self.max_attacks_entry.get())
        except ValueError:
            self.log_message(status="error", message="Chyba: zadejte platná čísla pro vlny, souřadnice a útoky.")
            return

        self.is_running = True
        self.log_message(status="info", message="Nomádská akce spuštěna!")
        threading.Thread(target=self._run_loop, daemon=True).start()

    def stop_action(self):
        if not self.is_running:
            self.log_message(status="info", message="Akce není spuštěna!")
            return
        self.is_running = False
        self.log_message(status="info", message="Akce zastavena.")

    def _run_loop(self):
        """Smyčka, která spouští děděnou funkci NomadOrSamuOnContinent."""
        countdown = self.config_reader.get_value("settings.offsets.default_time_before_run")
        for x in range(countdown, 0, -1):
            if not self.is_running:
                self.log_message(status="info", message="Akce přerušena během odpočtu.")
                return
            self.log_message(status="info", message=f"Spuštění za: {x}")
            time.sleep(1)

        self.log_message(status="info", message="Hlavní akce spuštěna!")
        try:
            self.NomadOrSamuOnContinent(
                horses=self.feather_horses,
                use_fill_all_waves=self.use_fill_all_waves,
                first_wave_from_bottom=self.first_wave_from_bottom,
                other_waves_from_bottom=self.other_waves_from_bottom,
                auto_fill_waves=self.auto_fill_waves,
                target_x=self.target_x,
                target_y=self.target_y,
                max_attacks=self.max_attacks
            )  # děděná metoda, implementace není zde
        except Exception as e:
            self.log_message(status="error", message=f"Chyba při spuštění NomadOrSamuOnContinent: {e}")

        self.is_running = False
        self.log_message(status="info", message="Akce dokončena.")
