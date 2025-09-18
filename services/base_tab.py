import json
import math
import tkinter as tk
from tkinter import ttk
import time
import threading
from .config_reader import ConfigReader
from .shared_data import message_queue, LogMessage
import pyautogui
import os

class BaseTab(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.config_reader = ConfigReader(filepath="configuration.json")
        self.is_running = False

        self.click_delay_offset = self.config_reader.get_value("settings.offsets.default_click_delay")

        if parent:
            parent.bind("<F1>", self.toggle_loop)

    def GetDistance(self, castle_x, castle_y, target_x, target_y):

        dx = target_x - castle_x
        dy = target_y - castle_y
        return math.sqrt(dx * dx + dy * dy)

    def ScanFort(self, json_name: str, scan_distance=99999):
        """Provede scan pevností z JSON a hlásí postup do GUI logu."""

        def _scan_loop():
            # odpočítávání před spuštěním (informativní)
            countdown = self.config_reader.get_value("settings.offsets.default_time_before_run")
            for x in range(countdown, 0, -1):
                self.log_message(status="info", message=f"Spuštění ScanFort za: {x}")
                time.sleep(1)

            # zvolené souřadnice hradu
            castle_x, castle_y = 0, 0
            if json_name == "winter":
                castle_x = self.config_reader.get_value("main_castle_cords.winter.x")
                castle_y = self.config_reader.get_value("main_castle_cords.winter.y")
            elif json_name == "sand":
                castle_x = self.config_reader.get_value("main_castle_cords.sand.x")
                castle_y = self.config_reader.get_value("main_castle_cords.sand.y")
            else:  # fire
                castle_x = self.config_reader.get_value("main_castle_cords.fire.x")
                castle_y = self.config_reader.get_value("main_castle_cords.fire.y")

            # cesta k JSON souboru
            base_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "fortress_data_storage"
            )
            json_path = os.path.join(base_dir, f"{json_name}.json")

            with open(json_path, "r", encoding="utf-8") as f:
                fort_data = json.load(f)

            forts_sorted = sorted(fort_data.items(), key=lambda kv: int(kv[0].split("_")[1]))
            counter = 1

            # Pro každou pevnost
            for fort_key, target in forts_sorted:
                target_x, target_y = target["x"], target["y"]

                # kontrola vzdálenosti
                distance = self.GetDistance(castle_x, castle_y, target_x, target_y)
                if distance > scan_distance:
                    self.log_message(
                        status="info",
                        message=f"Sken: [{target_x}:{target_y}] přeskočen (vzdálenost {distance:.2f} > {scan_distance}) | Note: {counter}/{len(forts_sorted)}"
                    )
                    counter += 1
                    continue

                # vykonání akce pevnosti (pyautogui)
                try:
                    # pyautogui.press("Tab")
                    pyautogui.click(
                        self.config_reader.get_value(
                            "actions_click_patter.send_attack_first_wave_auto.click_select_cords.x"),
                        self.config_reader.get_value(
                            "actions_click_patter.send_attack_first_wave_auto.click_select_cords.y")
                    )
                    pyautogui.click(
                        self.config_reader.get_value(
                            "actions_click_patter.send_attack_first_wave_auto.click_select_cords.x"),
                        self.config_reader.get_value(
                            "actions_click_patter.send_attack_first_wave_auto.click_select_cords.y")
                    )
                    time.sleep(self.click_delay_offset)
                    pyautogui.typewrite(str(target_x))
                    pyautogui.press("Tab")
                    pyautogui.typewrite(str(target_y))
                    pyautogui.press("Enter")
                    time.sleep(self.click_delay_offset)
                    pyautogui.moveTo(
                        self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.x"),
                        self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.y")
                    )
                    time.sleep(self.click_delay_offset)
                    pyautogui.moveTo(
                        self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.x" )+ 5,
                        self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.y" )+ 5
                    )
                    time.sleep(self.click_delay_offset)
                    pyautogui.moveTo(
                        self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.x"),
                        self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.y")
                    )
                    pyautogui.click(
                        self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.x"),
                        self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.y")
                    )
                    time.sleep(self.click_delay_offset)
                    pyautogui.moveTo(
                        self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_2.x"),
                        self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_2.y")
                    )

                except Exception as e:
                    self.log_message(status="error", message=f"Chyba při scanu [{target_x}:{target_y}]: {e}")

                self.log_message(
                    status="ok",
                    message=f"Scan dokončen: [{target_x}:{target_y}] | Note: {counter}/{len(forts_sorted)}"
                )
                counter += 1
                time.sleep(self.click_delay_offset)

            self.log_message(status="info", message="ScanFort dokončen.")

        # spustíme ve vlákně, GUI zůstane responzivní
        thread = threading.Thread(target=_scan_loop)
        thread.daemon = True
        thread.start()

    @staticmethod
    def WriteFort(text: str):
        # sestavení cesty k db.txt relativně k umístění tohoto souboru
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "fortress_data_storage", "db.txt")

        # připsání textu na konec souboru
        with open(db_path, "a", encoding="utf-8") as f:
            f.write(text + "\n")



    def SendAttackFirstWaveAuto(self, target_x, target_y, kingdom=None, feather_horse=None, note=None):
        #pyautogui.press("Tab")
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_select_cords.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_select_cords.y")
        )
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_select_cords.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_select_cords.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.typewrite(str(target_x))
        pyautogui.press("Tab")
        pyautogui.typewrite(str(target_y))
        pyautogui.press("Enter")
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_2.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_2.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_3.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_3.y")
        )

        #close windows
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("close_all_windows.prime_time.x"),
            self.config_reader.get_value("close_all_windows.prime_time.y")
        )

        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("close_all_windows.map_found.x"),
            self.config_reader.get_value("close_all_windows.map_found.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("close_all_windows.free_outpost.x"),
            self.config_reader.get_value("close_all_windows.free_outpost.y")
        )
        #close windows end
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_4.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_4.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_5.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_5.y")
        )
        time.sleep(self.click_delay_offset)
        #kone:
        if(feather_horse):
            pyautogui.click(
                self.config_reader.get_value("horses.feather.x"),
                self.config_reader.get_value("horses.feather.y")
            )
        else:
            pyautogui.click(
                self.config_reader.get_value("horses.gold.x"),
                self.config_reader.get_value("horses.gold.y")
            )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_6.x"),
            self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_6.y")
        )
        time.sleep(self.click_delay_offset)


        self.log_message(
            status="ok",
            message="Útok poslán na: ["+str(target_x)+":"+str(target_y)+"] | Note: "+note
        )


    def toggle_loop(self, event=None):
        """Spustí nebo zastaví smyčku pro útok na základě stavu."""
        if self.is_running:
            self.is_running = False
            self.log_message(
                status="stopped",
                message="Smyčka byla zastavena."
            )
            self.update_button_text()
        else:
            self.is_running = True
            self.log_message(
                status="running",
                message="Smyčka byla spuštěna."
            )
            self.update_button_text()
            self.start_attack_loop()

    def start_attack_loop(self):
        """Spustí smyčku útoku v samostatném vlákně."""
        thread = threading.Thread(target=self._attack_loop)
        thread.daemon = True
        thread.start()

    def log_message(self, status: str, message: str):
        """Pomocná metoda pro vytvoření a vložení objektu zprávy do fronty."""
        log = LogMessage(
            time=time.time(),
            status=status,
            module=self.__class__.__name__,  # Získá název aktuální třídy (např. 'BaronTab')
            message=message
        )
        message_queue.put(log)
    def _attack_loop(self):
        """Abstraktní metoda, která musí být implementována v podtřídě."""
        raise NotImplementedError("Tato metoda musí být implementována v podtřídě.")

    def update_button_text(self):
        """Abstraktní metoda pro aktualizaci textu tlačítka."""
        raise NotImplementedError("Tato metoda musí být implementována v podtřídě.")

    def ReturnConfigValue(self, key_path):
        return self.config_reader.get_value(key_path)