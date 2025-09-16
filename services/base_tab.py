import tkinter as tk
from tkinter import ttk
import time
import threading
from .config_reader import ConfigReader
from .shared_data import message_queue, LogMessage
import pyautogui
class BaseTab(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.config_reader = ConfigReader(filepath="configuration.json")
        self.is_running = False

        self.click_delay_offset = self.config_reader.get_value("settings.offsets.default_click_delay")

        if parent:
            parent.bind("<F1>", self.toggle_loop)

    def SendAttackFirstWaveAuto(self, target_x, target_y, kingdom=None, feather_horse=None, note=None):
        pyautogui.press("Tab")
        pyautogui.typewrite(str(target_x))
        pyautogui.press("Tab")
        pyautogui.typewrite(str(target_y))
        pyautogui.press("Enter")

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