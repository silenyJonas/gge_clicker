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
from .db_writer import DbWriter
from PIL import Image
import pytesseract
from PIL import Image
import os
import easyocr
import re
from datetime import datetime, timedelta
import keyboard

class BaseTab(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.config_reader = ConfigReader(filepath="configuration.json")
        self.is_running = False
        self.db_writer = DbWriter()
        self.click_delay_offset = self.config_reader.get_value("settings.offsets.default_click_delay")
        self.reader = easyocr.Reader(['en'], gpu=True)
        self.stop_event = threading.Event()
        if parent:
            parent.bind("<F1>", self.toggle_loop)

    def GetDistance(self, castle_x, castle_y, target_x, target_y):

        dx = target_x - castle_x
        dy = target_y - castle_y
        return math.sqrt(dx * dx + dy * dy)

    def ScanFort(self, json_name: str, scan_distance=99999):
        """Provede scan pevností z JSON a hlásí postup do GUI logu."""

        def _scan_loop():
            countdown = self.config_reader.get_value("settings.offsets.default_time_before_run")
            for x in range(countdown, 0, -1):
                if self.stop_event.is_set():
                    self.log_message(status="info", message="ScanFort zastaven uživatelem během odpočtu")
                    return
                self.log_message(status="info", message=f"Spuštění ScanFort za: {x}")
                time.sleep(1)

            # souřadnice hradu
            castle_x, castle_y = 0, 0
            if json_name == "winter":
                castle_x = self.config_reader.get_value("main_castle_cords.winter.x")
                castle_y = self.config_reader.get_value("main_castle_cords.winter.y")
            elif json_name == "sand":
                castle_x = self.config_reader.get_value("main_castle_cords.sand.x")
                castle_y = self.config_reader.get_value("main_castle_cords.sand.y")
            else:
                castle_x = self.config_reader.get_value("main_castle_cords.fire.x")
                castle_y = self.config_reader.get_value("main_castle_cords.fire.y")

            # JSON pevnosti
            base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fortress_data_storage")
            json_path = os.path.join(base_dir, f"{json_name}.json")
            with open(json_path, "r", encoding="utf-8") as f:
                fort_data = json.load(f)

            forts_sorted = sorted(fort_data.items(), key=lambda kv: int(kv[0].split("_")[1]))
            counter = 1

            for fort_key, target in forts_sorted:
                if self.stop_event.is_set():
                    self.log_message(status="info", message="ScanFort zastaven uživatelem")
                    return
                private_click_offset_01 = 0.1
                private_click_offset_02 = 0.2
                private_click_offset_05 = 0.2
                target_x, target_y = target["x"], target["y"]
                distance = self.GetDistance(castle_x, castle_y, target_x, target_y)
                if distance > scan_distance:
                    self.log_message(
                        status="info",
                        message=f"Sken: [{target_x}:{target_y}] přeskočen (vzdálenost {distance:.2f} > {scan_distance}) | Note: {counter}/{len(forts_sorted)}"
                    )
                    counter += 1
                    continue

                try:


                    pyautogui.click(self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_select_cords.x"),
                                    self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_select_cords.y"))
                    pyautogui.click(self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_select_cords.x"),
                                    self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_select_cords.y"))
                    time.sleep(private_click_offset_01)
                    pyautogui.typewrite(str(target_x))
                    pyautogui.press("Tab")
                    pyautogui.typewrite(str(target_y))
                    pyautogui.press("Enter")
                    time.sleep(private_click_offset_05)
                    pyautogui.moveTo(self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.x"),
                                     self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.y"))
                    time.sleep(private_click_offset_01)
                    pyautogui.click(self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.x") + 5,
                                    self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_1.y") + 5)
                    time.sleep(private_click_offset_01)
                    pyautogui.moveTo(self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_2.x"),
                                     self.config_reader.get_value("actions_click_patter.send_attack_first_wave_auto.click_2.y"))
                    time.sleep(0.1)

                    # OCR a zápis paralelně
                    cords = f"{target_x}:{target_y}"
                    kingdom = "ZIM" if json_name=="winter" else "PSK" if json_name=="sand" else "OHN"
                    threading.Thread(target=self.AnalyzeScreenFort, kwargs={"kingdom": kingdom, "cords": cords, "stop_event": self.stop_event}, daemon=True).start()

                except Exception as e:
                    self.log_message(status="error", message=f"Chyba při scanu [{target_x}:{target_y}]: {e}")

                self.log_message(status="ok", message=f"Scan dokončen: [{target_x}:{target_y}] | Note: {counter}/{len(forts_sorted)}")
                counter += 1
                time.sleep(private_click_offset_02)

            self.log_message(status="info", message="ScanFort dokončen.")

        # vlákno pro sken
        thread = threading.Thread(target=_scan_loop, daemon=True)
        thread.start()

        # vlákno pro kontrolu klávesy "S"
        def _stop_listener():
            keyboard.wait("s")  # čeká, až uživatel zmáčkne "s"
            self.stop_event.set()
            self.log_message(status="warn", message="Uživatel zastavil ScanFort stiskem klávesy 'S'")

        threading.Thread(target=_stop_listener, daemon=True).start()

    def AnalyzeScreenFort(self, kingdom="", cords="", stop_event=None):
        # okamžitá kontrola, zda bylo vlákno zastaveno
        if stop_event is not None and stop_event.is_set():
            return

        x = int(self.config_reader.get_value("settings.scan_screen_size.x"))
        y = int(self.config_reader.get_value("settings.scan_screen_size.y"))
        width = int(self.config_reader.get_value("settings.scan_screen_size.width"))
        height = int(self.config_reader.get_value("settings.scan_screen_size.height"))

        # screenshot
        screenshot = pyautogui.screenshot(region=(x, y, width, height))

        # cesta k uložení
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(base_dir, "images", "scan_cooldown_screen.png")
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        screenshot.save(image_path)

        # OCR
        result = self.reader.readtext(image_path, detail=0)
        extracted_text = " ".join(result).strip()

        if extracted_text:
            # převede text na budoucí čas
            extracted_text = self.calculate_future_time(extracted_text)
            # spojí informace do formátu: kingdom;cords;čas
            extracted_text = f"{kingdom};{cords};{extracted_text}"
            self.db_writer.WriteToDb(extracted_text)
            self.log_message(status="ok", message=f"Načtený text: {extracted_text}")
        else:
            self.log_message(status="warn", message="OCR nenašlo žádný text")

    def calculate_future_time(self, text: str):
        # extrahujeme čísla po "Lze napadnout za:"
        match = re.search(r"Lze napadnout za:\s*([\d:.]+)", text)
        if not match:
            return None

        time_str = match.group(1).replace(".", ":")  # tečky převedeme na dvojtečky
        parts = list(map(int, time_str.split(":")))

        if len(parts) == 3:
            h, m, s = parts
        elif len(parts) == 2:
            h, m, s = 0, parts[0], parts[1]
        elif len(parts) == 1:
            h, m, s = 0, 0, parts[0]
        else:
            return None

        delta = timedelta(hours=h, minutes=m, seconds=s)
        future_time = datetime.now() + delta

        # Vrátíme celé datum a čas: YYYY-MM-DD H:M:S
        return future_time.strftime("%Y-%m-%d %H:%M:%S")


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
        time.sleep(0.1)
        pyautogui.click(
            self.config_reader.get_value("close_all_windows.prime_time.x"),
            self.config_reader.get_value("close_all_windows.prime_time.y")
        )

        time.sleep(0.1)
        pyautogui.click(
            self.config_reader.get_value("close_all_windows.map_found.x"),
            self.config_reader.get_value("close_all_windows.map_found.y")
        )
        time.sleep(0.1)
        pyautogui.click(
            self.config_reader.get_value("close_all_windows.free_outpost.x"),
            self.config_reader.get_value("close_all_windows.free_outpost.y")
        )
        time.sleep(0.1)
        pyautogui.click(
            self.config_reader.get_value("close_all_windows.triple_action.x"),
            self.config_reader.get_value("close_all_windows.triple_action.y")
        )
        time.sleep(0.1)
        pyautogui.click(
            self.config_reader.get_value("close_all_windows.info_dialog.x"),
            self.config_reader.get_value("close_all_windows.info_dialog.y")
        )
        time.sleep(0.1)
        pyautogui.click(
            self.config_reader.get_value("close_all_windows.close_ali.x"),
            self.config_reader.get_value("close_all_windows.close_ali.y")
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