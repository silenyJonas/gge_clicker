# tabs/fortress.py
import tkinter as tk
from tkinter import ttk
from services.base_tab import BaseTab
import threading
import time

class FortressTab(BaseTab, ttk.Frame):
    """Záložka pro pevnosti."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Výchozí hodnoty
        self.max_distance = 9999
        self.feather_horses = True
        self.auto_dismiss_windows = False
        self.scan_before_riding = False
        self.extra_world = "winter"
        self.rubies_spent = 0

        # nová proměnná místo combined_world
        self.selected_world = "one"  # one | all | zim_pis | zim_ohn | pis_ohn

        # --- výchozí indexy hradů ---
        self.winter_castle_index = 2
        self.sand_castle_index = 3
        self.fire_castle_index = 4

        # --- nové inputy pro předvolby útoků ---
        self.winter_atk_code = 1
        self.sand_atk_code = 5
        self.fire_atk_code = 4

        self.create_widgets()

    def create_widgets(self):
        """Vytváří widgety pro tuto záložku."""
        # --- Rámeček pro vzdálenost + tlačítko uložit ---
        distance_frame = ttk.Frame(self)
        distance_frame.pack(pady=10, anchor="w")

        ttk.Label(distance_frame, text="Maximální vzdálenost:").pack(side=tk.LEFT, padx=(0, 5))
        self.distance_entry = ttk.Entry(distance_frame, width=10)
        self.distance_entry.insert(0, str(self.max_distance))
        self.distance_entry.pack(side=tk.LEFT, padx=(0, 5))

        save_distance_button = ttk.Button(distance_frame, text="Uložit vzdálenost", command=self._save_distance_only)
        save_distance_button.pack(side=tk.LEFT, padx=(5, 0))

        # --- Vyježděno rubínů ---
        rubies_frame = ttk.Frame(self)
        rubies_frame.pack(pady=(5, 10), anchor="w")
        ttk.Label(rubies_frame, text="Vyježděno rubínů za rotaci:").pack(side=tk.LEFT, padx=(0, 5))
        self.rubies_label = ttk.Label(rubies_frame, text=str(self.rubies_spent))
        self.rubies_label.pack(side=tk.LEFT)

        # --- Inputy pro indexy hradů ---
        castles_frame = ttk.Frame(self)
        castles_frame.pack(pady=10, anchor="w")

        # Zima
        zim_frame = ttk.Frame(castles_frame)
        zim_frame.pack(anchor="w", pady=(0, 5))
        ttk.Label(zim_frame, text="Kolikátý od spoda je Zima hrad:").pack(side=tk.LEFT, padx=(0, 5))
        self.winter_castle_entry = ttk.Entry(zim_frame, width=10)
        self.winter_castle_entry.insert(0, str(self.winter_castle_index))
        self.winter_castle_entry.pack(side=tk.LEFT)

        # Písek
        pis_frame = ttk.Frame(castles_frame)
        pis_frame.pack(anchor="w", pady=(0, 5))
        ttk.Label(pis_frame, text="Kolikátý od spoda je Písek hrad:").pack(side=tk.LEFT, padx=(0, 5))
        self.sand_castle_entry = ttk.Entry(pis_frame, width=10)
        self.sand_castle_entry.insert(0, str(self.sand_castle_index))
        self.sand_castle_entry.pack(side=tk.LEFT)

        # Oheň
        ohn_frame = ttk.Frame(castles_frame)
        ohn_frame.pack(anchor="w")
        ttk.Label(ohn_frame, text="Kolikátý od spoda je Oheň hrad:").pack(side=tk.LEFT, padx=(0, 5))
        self.fire_castle_entry = ttk.Entry(ohn_frame, width=10)
        self.fire_castle_entry.insert(0, str(self.fire_castle_index))
        self.fire_castle_entry.pack(side=tk.LEFT)

        # --- Inputy pro předvolby útoků ---
        atk_frame = ttk.Frame(self)
        atk_frame.pack(pady=10, anchor="w")

        # Zima atk
        zim_atk_frame = ttk.Frame(atk_frame)
        zim_atk_frame.pack(anchor="w", pady=(0, 5))
        ttk.Label(zim_atk_frame, text="Pozice předvolby na Zimu od spoda:").pack(side=tk.LEFT, padx=(0, 5))
        self.winter_atk_entry = ttk.Entry(zim_atk_frame, width=10)
        self.winter_atk_entry.insert(0, str(self.winter_atk_code))
        self.winter_atk_entry.pack(side=tk.LEFT)

        # Písek atk
        pis_atk_frame = ttk.Frame(atk_frame)
        pis_atk_frame.pack(anchor="w", pady=(0, 5))
        ttk.Label(pis_atk_frame, text="Pozice předvolby na Písek od spoda:").pack(side=tk.LEFT, padx=(0, 5))
        self.sand_atk_entry = ttk.Entry(pis_atk_frame, width=10)
        self.sand_atk_entry.insert(0, str(self.sand_atk_code))
        self.sand_atk_entry.pack(side=tk.LEFT)

        # Oheň atk
        ohn_atk_frame = ttk.Frame(atk_frame)
        ohn_atk_frame.pack(anchor="w", pady=(0, 5))
        ttk.Label(ohn_atk_frame, text="Pozice předvolby na Oheň od spoda:").pack(side=tk.LEFT, padx=(0, 5))
        self.fire_atk_entry = ttk.Entry(ohn_atk_frame, width=10)
        self.fire_atk_entry.insert(0, str(self.fire_atk_code))
        self.fire_atk_entry.pack(side=tk.LEFT)

        # --- Koně ---
        horse_frame = ttk.Frame(self)
        horse_frame.pack(pady=10, anchor="w")

        ttk.Label(horse_frame, text="Typ koně:").pack(side=tk.LEFT, padx=(0, 10))
        self.feather_horses_var = tk.BooleanVar(value=self.feather_horses)

        ttk.Radiobutton(horse_frame, text="Gold koně", variable=self.feather_horses_var, value=False,
                        command=self._on_horse_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(horse_frame, text="Pírko koně", variable=self.feather_horses_var, value=True,
                        command=self._on_horse_changed).pack(side=tk.LEFT, padx=5)

        # --- Výběr světa (více možností) ---
        world_frame = ttk.Frame(self)
        world_frame.pack(pady=10, anchor="w")

        ttk.Label(world_frame, text="Svět:").pack(side=tk.LEFT, padx=(0, 10))
        self.world_var = tk.StringVar(value=self.selected_world)

        self.rb_world_one = ttk.Radiobutton(world_frame, text="Jeden svět", variable=self.world_var, value="one",
                                            command=self._on_world_changed)
        self.rb_world_all = ttk.Radiobutton(world_frame, text="Všechny světy", variable=self.world_var, value="all",
                                            command=self._on_world_changed)
        self.rb_world_zim_pis = ttk.Radiobutton(world_frame, text="Zima + Písek", variable=self.world_var, value="zim_pis",
                                                command=self._on_world_changed)
        self.rb_world_zim_ohn = ttk.Radiobutton(world_frame, text="Zima + Oheň", variable=self.world_var, value="zim_ohn",
                                                command=self._on_world_changed)
        self.rb_world_pis_ohn = ttk.Radiobutton(world_frame, text="Písek + Oheň", variable=self.world_var, value="pis_ohn",
                                                command=self._on_world_changed)

        self.rb_world_one.pack(side=tk.LEFT, padx=5)
        self.rb_world_all.pack(side=tk.LEFT, padx=5)
        self.rb_world_zim_pis.pack(side=tk.LEFT, padx=5)
        self.rb_world_zim_ohn.pack(side=tk.LEFT, padx=5)
        self.rb_world_pis_ohn.pack(side=tk.LEFT, padx=5)

        # --- Odklikávání ---
        dismiss_frame = ttk.Frame(self)
        dismiss_frame.pack(pady=10, anchor="w")

        ttk.Label(dismiss_frame, text="Použít neustálé odklikávání oken:").pack(side=tk.LEFT, padx=(0, 10))
        self.auto_dismiss_var = tk.BooleanVar(value=self.auto_dismiss_windows)

        ttk.Radiobutton(dismiss_frame, text="Ano", variable=self.auto_dismiss_var, value=True,
                        command=self._on_dismiss_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(dismiss_frame, text="Ne", variable=self.auto_dismiss_var, value=False,
                        command=self._on_dismiss_changed).pack(side=tk.LEFT, padx=5)

        # --- Scan před ježděním ---
        self.scan_frame = ttk.Frame(self)
        self.scan_frame.pack(pady=10, anchor="w")

        ttk.Label(self.scan_frame, text="Udělat scan před ježděním:").pack(side=tk.LEFT, padx=(0, 10))
        self.scan_var = tk.BooleanVar(value=self.scan_before_riding)

        ttk.Radiobutton(self.scan_frame, text="Ano", variable=self.scan_var, value=True,
                        command=self._on_scan_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(self.scan_frame, text="Ne", variable=self.scan_var, value=False,
                        command=self._on_scan_changed).pack(side=tk.LEFT, padx=5)

        # --- Doplňkový svět ---
        self.extra_world_frame = ttk.Frame(self)
        self.extra_world_frame.pack(pady=5, anchor="w")

        ttk.Label(self.extra_world_frame, text="Doplňkový svět:").pack(side=tk.LEFT, padx=(0, 10))
        self.extra_world_var = tk.StringVar(value=self.extra_world)

        self.rb_extra_zima = ttk.Radiobutton(self.extra_world_frame, text="Zima", variable=self.extra_world_var, value="Zima")
        self.rb_extra_pisek = ttk.Radiobutton(self.extra_world_frame, text="Písek", variable=self.extra_world_var, value="Pisek")
        self.rb_extra_ohen = ttk.Radiobutton(self.extra_world_frame, text="Oheň", variable=self.extra_world_var, value="Ohen")

        self.rb_extra_zima.pack(side=tk.LEFT, padx=5)
        self.rb_extra_pisek.pack(side=tk.LEFT, padx=5)
        self.rb_extra_ohen.pack(side=tk.LEFT, padx=5)

        self.extra_world_frame.pack_forget()  # Schovat na začátku

        # --- Ovládací tlačítka Start / Stop ---
        control_frame = ttk.Frame(self)
        control_frame.pack(pady=15, anchor="center")

        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_rotation)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_rotation)
        self.stop_button.pack(side=tk.LEFT, padx=5)

    # --- Callbacky ---
    def _on_horse_changed(self):
        self.feather_horses = bool(self.feather_horses_var.get())
        horse_type = "Pírko" if self.feather_horses else "Gold"
        self.log_message(status="info", message=f"Typ koně byl změněn na: {horse_type}")

    def _on_world_changed(self):
        self.selected_world = self.world_var.get()
        mapping = {
            "one": "Jeden svět",
            "all": "Všechny světy",
            "zim_pis": "Zima + Písek",
            "zim_ohn": "Zima + Oheň",
            "pis_ohn": "Písek + Oheň"
        }
        self.log_message(status="info", message=f"Svět byl změněn na: {mapping.get(self.selected_world, self.selected_world)}")

        # Pokud není "Jeden svět", skryj scan
        if self.selected_world != "one":
            self.scan_var.set(False)
            self.scan_frame.pack_forget()
            self.extra_world_frame.pack_forget()
        else:
            self.scan_frame.pack(pady=10, anchor="w")

    def _on_dismiss_changed(self):
        self.auto_dismiss_windows = bool(self.auto_dismiss_var.get())
        state = "Ano" if self.auto_dismiss_windows else "Ne"
        self.log_message(status="info", message=f"Použít neustálé odklikávání oken: {state}")

    def _on_scan_changed(self):
        self.scan_before_riding = bool(self.scan_var.get())
        if self.scan_before_riding:
            self.extra_world_frame.pack(pady=5, anchor="w")
        else:
            self.extra_world_frame.pack_forget()
        state = "Ano" if self.scan_before_riding else "Ne"
        self.log_message(status="info", message=f"Udělat scan před ježděním: {state}")

    def _save_distance_only(self):
        try:
            self.max_distance = int(self.distance_entry.get())
            self.winter_castle_index = int(self.winter_castle_entry.get())
            self.sand_castle_index = int(self.sand_castle_entry.get())
            self.fire_castle_index = int(self.fire_castle_entry.get())

            self.winter_atk_code = int(self.winter_atk_entry.get())
            self.sand_atk_code = int(self.sand_atk_entry.get())
            self.fire_atk_code = int(self.fire_atk_entry.get())

            self.log_message(status="info", message=f"Maximální vzdálenost nastavena na: {self.max_distance}")
            self.log_message(status="info", message=f"Indexy hradů -> Zima: {self.winter_castle_index}, Písek: {self.sand_castle_index}, Oheň: {self.fire_castle_index}")
            self.log_message(status="info", message=f"Předvolby útoků -> Zima: {self.winter_atk_code}, Písek: {self.sand_atk_code}, Oheň: {self.fire_atk_code}")
        except ValueError:
            self.log_message(status="error", message="Chyba: Zadejte prosím platné číslo pro vzdálenost, indexy hradů a předvolby útoků.")

    # --- Start / Stop rotace ---
    def start_rotation(self):
        if getattr(self, "is_running", False):
            self.log_message(status="info", message="Rotace již běží!")
            return
        self.is_running = True
        self.log_message(status="info", message="Rotace spuštěna!")
        threading.Thread(target=self._rotation_loop, daemon=True).start()

    def stop_rotation(self):
        if not getattr(self, "is_running", False):
            self.log_message(status="info", message="Rotace není spuštěna!")
            return
        self.is_running = False
        self.log_message(status="info", message="Rotace zastavena.")

    def _rotation_loop(self):
        countdown = self.config_reader.get_value("settings.offsets.default_time_before_run")
        for x in range(countdown, 0, -1):
            if not self.is_running:
                self.log_message(status="info", message="Rotace přerušena během odpočtu.")
                return
            self.log_message(status="info", message=f"Spuštění za: {x}")
            time.sleep(1)

        self.log_message(status="info", message="Hlavní rotace spuštěna!")

        if self.selected_world == "one":
            if self.scan_before_riding:
                self.log_message(status="info", message=f"Doplňkový svět po ježdění: {self.extra_world_var.get()}")

            self.SingletaskingFortressRider(
                feather_forse=self.feather_horses,
                distance=self.max_distance,
                closing_popups=self.auto_dismiss_windows,
                scan_before_run=self.scan_before_riding,
                world_scan=self.extra_world
            )
        else:
            try:
                self.winter_atk_code = int(self.winter_atk_entry.get())
                self.sand_atk_code = int(self.sand_atk_entry.get())
                self.fire_atk_code = int(self.fire_atk_entry.get())
                self.winter_castle_entry=int(self.winter_castle_entry.get())
                self.sand_castle_entry=int(self.sand_castle_entry.get())
                self.fire_castle_entry=int(self.fire_castle_entry.get())
            except ValueError:
                self.log_message(status="error", message="Chyba: předvolby útoků musí být čísla.")
                self.is_running = False
                return

            self.MultitaskingFortressRider(
                fire_atk_code=self.fire_atk_code,
                sand_atk_code=self.sand_atk_code,
                winter_atk_code=self.winter_atk_code,
                winter_castle_list_pos=self.winter_castle_entry,
                sand_castle_list_pos=self.sand_castle_entry,
                fire_castle_list_pos=self.fire_castle_entry
            )

    def update_rubies(self, count: int):
        self.rubies_spent = count
        self.rubies_label.config(text=str(self.rubies_spent))
