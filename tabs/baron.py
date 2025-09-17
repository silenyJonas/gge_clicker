# tabs/baron.py
import tkinter as tk
from tkinter import ttk
import threading
import time
from services.base_tab import BaseTab


class BaronTab(BaseTab, ttk.Frame):
    """Třída pro záložku Baronů, která dědí z BaseTab."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Initialize start_index and end_index with default values
        self.start_index = 1
        self.end_index = 35

        # Boolean that will be changed by the radio buttons
        self.feather_horses = True  # výchozí hodnota

        self.create_widgets()
        self.update_button_text()

    def create_widgets(self):
        """Vytváří widgety pro tuto záložku."""
        self.control_button = ttk.Button(
            self,
            text="Spustit (F1)",
            command=self.toggle_loop
        )
        self.control_button.pack(pady=10)

        # Rámeček pro uspořádání vstupních polí
        index_frame = ttk.Frame(self)
        index_frame.pack(pady=10)

        # Vstupní pole pro startovní index
        start_index_label = ttk.Label(index_frame, text="Startovní index:")
        start_index_label.pack(side=tk.LEFT, padx=(0, 5))
        self.start_index_entry = ttk.Entry(index_frame, width=5)
        # Use a default value consistent with initialization
        self.start_index_entry.insert(0, str(self.start_index))
        self.start_index_entry.pack(side=tk.LEFT)

        # Vstupní pole pro koncový index
        end_index_label = ttk.Label(index_frame, text="Koncový index:")
        end_index_label.pack(side=tk.LEFT, padx=(15, 5))
        self.end_index_entry = ttk.Entry(index_frame, width=5)
        # Use a default value consistent with initialization
        self.end_index_entry.insert(0, str(self.end_index))
        self.end_index_entry.pack(side=tk.LEFT)

        # Tlačítko pro uložení hodnot
        save_button = ttk.Button(
            self,
            text="Uložit indexy",
            command=self.save_indices
        )
        save_button.pack(pady=5)

        # Rámeček pro uspořádání radio buttonů (svět + typ koně)
        world_frame = ttk.Frame(self)
        world_frame.pack(pady=10, fill="x")

        world_label = ttk.Label(world_frame, text="Vybrat svět:")
        world_label.pack(side=tk.LEFT, padx=(0, 10))

        # Proměnná pro ukládání hodnoty vybraného Radiobutton (svět)
        self.world_variable = tk.StringVar(value="green")

        # Vytvoření Radiobuttonů pro každý svět s navázaným příkazem
        ttk.Radiobutton(world_frame, text="Green", variable=self.world_variable, value="green",
                        command=self.world_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(world_frame, text="Winter", variable=self.world_variable, value="winter",
                        command=self.world_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(world_frame, text="Sand", variable=self.world_variable, value="sand",
                        command=self.world_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(world_frame, text="Fire", variable=self.world_variable, value="fire",
                        command=self.world_changed).pack(side=tk.LEFT, padx=5)

        # --- Nové: radiobuttony pro typ koně (mění bool feather_horses) ---
        # Použijeme BooleanVar pro vazbu; callback zajistí aktualizaci self.feather_horses
        self.feather_horses_var = tk.BooleanVar(value=self.feather_horses)

        # Rámeček pro typ koně, umístěný vedle world_frame (můžeme přizpůsobit layout)
        horse_frame = ttk.Frame(self)
        horse_frame.pack(pady=5, fill="x")

        horse_label = ttk.Label(horse_frame, text="Typ koně:")
        horse_label.pack(side=tk.LEFT, padx=(0, 10))

        # "Gold kone" nastaví feather_horses = False (např. gold = bez pérka)
        ttk.Radiobutton(horse_frame, text="Gold koně", variable=self.feather_horses_var, value=False,
                        command=self._on_feather_horses_changed).pack(side=tk.LEFT, padx=5)
        # "Pírko kone" nastaví feather_horses = True
        ttk.Radiobutton(horse_frame, text="Pírko koně", variable=self.feather_horses_var, value=True,
                        command=self._on_feather_horses_changed).pack(side=tk.LEFT, padx=5)

    def _on_feather_horses_changed(self):
        """Callback při změně typu koně - aktualizuje self.feather_horses."""
        self.feather_horses = bool(self.feather_horses_var.get())

        # Vybereme text podle hodnoty
        horse_type = "Pírko" if self.feather_horses else "Gold"

        # Zalogujeme změnu
        try:
            self.log_message(
                status="info",
                message=f"Typ koně byl změněn na: {horse_type}"
            )
        except Exception:
            pass

    def world_changed(self):
        """Zaznamená změnu vybraného světa do GUI logu."""
        selected_world = self.world_variable.get()
        self.log_message(
            status="info",
            message=f"Svět byl změněn na: {selected_world}"
        )

    def save_indices(self):
        """Uloží hodnoty ze vstupních polí do proměnných a vypíše je do GUI logu."""
        try:
            self.start_index = int(self.start_index_entry.get())
            self.end_index = int(self.end_index_entry.get())
            self.log_message(
                status="info",
                message=f"Indexy byly uloženy: start={self.start_index}, end={self.end_index}"
            )
        except ValueError:
            self.log_message(
                status="error",
                message="Chyba: Zadejte prosím platná celá čísla pro indexy."
            )
            # The variables are not created here on error, but this is ok now
            # because they are initialized in __init__
            pass # Keep the old values in case of error

    def _attack_loop(self):
        """Vlastní smyčka útoku pro Barony, která běží v pozadí."""
        # Odpočítávání s kontrolou zastavení
        countdown = self.config_reader.get_value("settings.offsets.default_time_before_run")
        for x in range(countdown, 0, -1):
            if not self.is_running:
                return  # Okamžité zastavení, pokud se smyčka vypne
            self.log_message(
                status="info",
                message="Spuštění za: " + str(x)
            )
            time.sleep(1)

        selected_world = self.world_variable.get()
        config_path_prefix = f"entity_list.barons.{selected_world}" if selected_world else "entity_list.barons"
        prefix = "target_"
        private_offset_time = self.config_reader.get_value("settings.offsets.default_time_delay_offset")

        # Hodnota pro malý, častý spánek
        CHECK_INTERVAL = 0.1

        while self.is_running:
            for x in range(self.start_index, self.end_index + 1):
                if not self.is_running:
                    return  # Okamžité zastavení uprostřed smyčky

                # Dynamický výpočet počtu iterací spánku
                if private_offset_time is not None:
                    iterations = int(private_offset_time / CHECK_INTERVAL)
                else:
                    iterations = 0

                # Dlouhý spánek s častou kontrolou
                for _ in range(iterations):
                    if not self.is_running:
                        return
                    time.sleep(CHECK_INTERVAL)

                current_target_key = f"{config_path_prefix}.{prefix}{x}"
                target_x = self.config_reader.get_value(f"{current_target_key}.x")
                target_y = self.config_reader.get_value(f"{current_target_key}.y")

                # Ujistíme se, že hodnoty nejsou None před voláním
                if target_x is not None and target_y is not None:
                    note = f"target: {x}"
                    # Použijeme self.feather_horses při volání (pokud funkce parametr očekává)
                    self.SendAttackFirstWaveAuto(target_x=target_x, target_y=target_y, feather_horse=self.feather_horses, note=note)
                else:
                    self.log_message(
                        status="error",
                        message=f"Chyba: Nebyly nalezeny souřadnice pro cíl '{current_target_key}'."
                    )
            self.is_running = False
            self.log_message(
                status="INFO",
                message="Posílání session baronů úspěšně dokončeno",
            )

    def update_button_text(self):
        """Aktualizuje text tlačítka podle stavu smyčky."""
        if self.is_running:
            self.control_button.config(text="Zastavit (F1)")
        else:
            self.control_button.config(text="Spustit (F1)")
