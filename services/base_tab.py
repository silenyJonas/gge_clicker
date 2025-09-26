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
from datetime import datetime
import os
from datetime import datetime
import time

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
    #SCAN_PEVNOSTI_____________________________________________
    def ClearFortArray(self):
        """Vymaže celý obsah fortress_data_storage/db.txt"""

        # sestavení cesty k db.txt relativně k umístění tohoto souboru
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "fortress_data_storage", "db.txt")

        # otevření v režimu 'w' přepíše soubor prázdným obsahem
        with open(db_path, "w", encoding="utf-8") as f:
            f.write("")

        # pro jistotu log
        self.log_message(status="ok", message="Soubor db.txt byl vymazán.")

    def GetDistance(self, castle_x, castle_y, target_x, target_y):

        dx = target_x - castle_x
        dy = target_y - castle_y
        return math.sqrt(dx * dx + dy * dy)

    def ScanFort(self, json_name: str, scan_distance=99999, dismiss_popups=True):
        """Provede scan pevností z JSON a hlásí postup do GUI logu."""
        self.ClearFortArray()
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
                if (dismiss_popups and counter % 10 == 0):
                    self.CloseWindowsPopups()

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
                    threading.Thread(target=self.AnalyzeScreenFort, kwargs={"kingdom": kingdom, "cords": cords, "json_name": json_name, "stop_event": self.stop_event}, daemon=True).start()

                except Exception as e:
                    self.log_message(status="error", message=f"Chyba při scanu [{target_x}:{target_y}]: {e}")

                self.log_message(status="ok", message=f"Scan dokončen: [{target_x}:{target_y}] | Note: {counter}/{len(forts_sorted)}")
                counter += 1
                time.sleep(private_click_offset_02)

            self.log_message(status="info", message="ScanFort dokončen.")
            self.SortFortArray(json_name=json_name)

        # vlákno pro sken
        thread = threading.Thread(target=_scan_loop, daemon=True)
        thread.start()

        # vlákno pro kontrolu klávesy "S"
        def _stop_listener():
            keyboard.wait("s")  # čeká, až uživatel zmáčkne "s"
            self.stop_event.set()
            self.log_message(status="warn", message="Uživatel zastavil ScanFort stiskem klávesy 'S'")

        threading.Thread(target=_stop_listener, daemon=True).start()

    def AnalyzeScreenFort(self, json_name: str, kingdom="", cords="", stop_event=None, ):
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
            self.db_writer.WriteToDb(extracted_text, json_name)
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

    def SortFortArray(self, json_name):
        # cesta k db.txt
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "fortress_data_storage", json_name + "_db.txt")

        if not os.path.exists(db_path):
            self.log_message(status="error", message="Soubor db.txt nebyl nalezen")
            return []

        # načteme řádky
        with open(db_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        def parse_line(line: str):
            try:
                parts = line.split(";")
                kingdom, cords, dt_str = parts
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                return (kingdom, cords, dt)
            except Exception as e:
                self.log_message(status="error", message=f"Chyba při parsování řádku: {line} ({e})")
                return None

        parsed = [p for p in (parse_line(line) for line in lines) if p]

        # seřadíme podle datetime od nejbližšího po nejvzdálenější
        sorted_data = sorted(parsed, key=lambda x: x[2])

        # pokud chceš, můžeš to vrátit zpět jako stringy
        result_lines = [f"{k};{c};{dt.strftime('%Y-%m-%d %H:%M:%S')}" for k, c, dt in sorted_data]

        # přepíšeme db.txt seřazeným obsahem
        with open(db_path, "w", encoding="utf-8") as f:
            f.write("\n".join(result_lines) + "\n")

        self.log_message(status="ok", message=f"Seřazeno {len(result_lines)} záznamů podle času.")
        return result_lines

    # SCAN_PEVNOSTI_KONEC_____________________________________________
    # POSLAT_BASIC_UTOK_______________________________________________
    def SelectCode(self, selected_code):
        print(type(selected_code))
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.select_attack_code.base_click.x"),
            self.config_reader.get_value("actions_click_patter.select_attack_code.base_click.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.select_attack_code.code_"+str(selected_code)+".x"),
            self.config_reader.get_value("actions_click_patter.select_attack_code.code_"+str(selected_code)+".y"),
        )
        time.sleep(self.click_delay_offset)
    def SendAttackFirstWaveAuto(self,target_x=None, target_y=None, send_with_cords = True, kingdom=None, feather_horse=None, note=None, attack_code=None):
        if send_with_cords:
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
        self.CloseWindowsPopups()
        #close windows end
        time.sleep(self.click_delay_offset)
        if attack_code != None:
            print(type(attack_code))
            self.SelectCode(attack_code)

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

        if send_with_cords:
            self.log_message(
                status="ok",
                message="Útok poslán na: ["+str(target_x)+":"+str(target_y)+"] | Note: "+note
            )

    def BerimondRefill(self, troops_from_left):
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_1.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_1.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_2.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_2.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.troops_offsets.offset_troop_"+str(troops_from_left)+".x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.troops_offsets.offset_troop_"+str(troops_from_left)+".y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_3.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_3.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_4.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_4.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_5.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_5.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_6.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_6.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_7.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_7.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_8.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_8.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_9.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_9.y")
        )
        time.sleep(self.click_delay_offset)
        pyautogui.click(
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_10.x"),
            self.config_reader.get_value("actions_click_patter.refill_berimond.click_10.y")
        )
        self.log_message(
            status="ok",
            message="Jednotky doplněny"
        )


    def BerimondOnContinent(self, max_attacks, horses, attacks_between_refill, troops_from_left, delay_between_attacks):
        for x in range(max_attacks):
            if x % attacks_between_refill == 0 and x != 0:
                #refill
                self.BerimondRefill(troops_from_left)

            time.sleep(delay_between_attacks)

            #click pravo dole
            time.sleep(0.1)
            pyautogui.click(
                self.config_reader.get_value("actions_click_patter.berimond_find_target_right_down.x"),
                self.config_reader.get_value("actions_click_patter.berimond_find_target_right_down.y")
            )

            time.sleep(self.config_reader.get_value("settings.offsets.default_click_delay"))
            self.SendAttackFirstWaveAuto(send_with_cords=False, feather_horse=horses)

            time.sleep(0.1)
            pyautogui.click(
                self.config_reader.get_value("actions_click_patter.berimond_no_troop_army_1.x"),
                self.config_reader.get_value("actions_click_patter.berimond_no_troop_army_1.y")
            )
            time.sleep(0.1)
            pyautogui.click(
                self.config_reader.get_value("actions_click_patter.berimond_no_troop_army_2.x"),
                self.config_reader.get_value("actions_click_patter.berimond_no_troop_army_2.y")
            )
            self.log_message(
                status="ok",
                message="Útok poslán | Note: " + str(x+1)+"/"+str(max_attacks),
            )
            #time.sleep(self.config_reader.get_value("settings.offsets.default_click_delay"))

    def BerimondOnGreen(self):
        print("BerimondOnGreen")

    def CloseWindowsPopups(self):
        sleep_time = 0.1
        time.sleep(sleep_time)
        pyautogui.click(
            self.config_reader.get_value("close_all_windows.prime_time.x"),
            self.config_reader.get_value("close_all_windows.prime_time.y")
        )

        time.sleep(sleep_time)
        pyautogui.click(
            self.config_reader.get_value("close_all_windows.map_found.x"),
            self.config_reader.get_value("close_all_windows.map_found.y")
        )
        time.sleep(sleep_time)
        pyautogui.click(
            self.config_reader.get_value("close_all_windows.free_outpost.x"),
            self.config_reader.get_value("close_all_windows.free_outpost.y")
        )
        time.sleep(sleep_time)
        pyautogui.click(
            self.config_reader.get_value("close_all_windows.triple_action.x"),
            self.config_reader.get_value("close_all_windows.triple_action.y")
        )
        time.sleep(sleep_time)
        pyautogui.click(
            self.config_reader.get_value("close_all_windows.info_dialog.x"),
            self.config_reader.get_value("close_all_windows.info_dialog.y")
        )
        time.sleep(sleep_time)
        pyautogui.click(
            self.config_reader.get_value("close_all_windows.close_ali.x"),
            self.config_reader.get_value("close_all_windows.close_ali.y")
        )
    # POSLAT_BASIC_UTOK_KONEC_________________________________________
    # JEZDENI_PEVNOSTI________________________________________________


    def FilterFortressListByDistance(self, records, max_distance):
        """
        Vrátí seznam záznamů, které vyhovují vzdálenosti od hlavního hradu.

        :param records: seznam záznamů ve formátu "OHN;575:575;2025-09-21 18:08:43"
        :param max_distance: maximální vzdálenost
        :return: filtrovaný seznam záznamů
        """
        filtered = []
        for record in records:
            try:
                world_code, coords, _ = record.split(";")
                target_x, target_y = map(int, coords.split(":"))

                # nastavení souřadnic hradu podle světa
                if world_code == "ZIM":
                    castle_x = self.config_reader.get_value("main_castle_cords.winter.x")
                    castle_y = self.config_reader.get_value("main_castle_cords.winter.y")
                elif world_code == "PSK":
                    castle_x = self.config_reader.get_value("main_castle_cords.sand.x")
                    castle_y = self.config_reader.get_value("main_castle_cords.sand.y")
                else:  # OHN
                    castle_x = self.config_reader.get_value("main_castle_cords.fire.x")
                    castle_y = self.config_reader.get_value("main_castle_cords.fire.y")

                # pokud některá souřadnice není nastavena, přeskočíme záznam
                if castle_x is None or castle_y is None:
                    continue

                # vzdálenost
                distance = self.GetDistance(int(castle_x), int(castle_y), target_x, target_y)
                if distance <= max_distance:
                    filtered.append(record)
            except Exception as e:
                self.log_message(status="error", message=f"Chybný záznam: {record} | {e}")

        return filtered

    def SingletaskingFortressRider(self, feather_forse=True, distance=99999, closing_popups=True, scan_before_run=False,
                                   world_scan=None):

        self.log_message(status="info", message="Single-tasking rotace spuštěna.")
        if scan_before_run:
            # udela se scan na world_scan
            pass

        if closing_popups:
            # proběhne self.CloseWindowsPopups()
            pass

        records = self.ReturnSortedFortressList()
        records = self.FilterFortressListByDistance(records=records, max_distance=distance)

        while self.is_running:

            now = datetime.now()

            if not records:
                self.log_message(status="info", message="Žádné budoucí záznamy v DB.")
                time.sleep(1)
                continue

            try:
                expired_records = []  # seznam záznamů, co už mají čas <= now

                for rec in records:
                    world_code, coords, time_part = rec.split(";")
                    next_time = datetime.strptime(time_part, "%Y-%m-%d %H:%M:%S")
                    delta = (next_time - now).total_seconds()

                    if delta <= 0:
                        expired_records.append(rec)
                    else:
                        # první neexpirovaný -> log a pak break (protože records je seřazené)
                        self.log_message(
                            status="info",
                            message=f"Další: {world_code} | [{coords}] | Za: {int(delta)} s"
                        )
                        break

                # všechny expirované spustíme a odstraníme z records
                for rec in expired_records:
                    world_code, coords, _ = rec.split(";")
                    target_x, target_y = coords.split(":")
                    print(f"Spouštím záznam: {rec}")
                    self.SendAttackFirstWaveAuto(
                        target_x=int(target_x),
                        target_y=int(target_y),
                        feather_horse=feather_forse,
                        note="Útok poslán"
                    )
                    records.remove(rec)

            except Exception as e:
                msg = f"Chyba při čtení záznamů: {e}"
                self.log_message(status="error", message=msg)

            time.sleep(1)

    def BuySpeedBonus(self):
        pass

    def ChangeWorld(self, world_code, winter_castle_list_pos, sand_castle_list_pos, fire_castle_list_pos):
        print(world_code)
        base_x = self.config_reader.get_value("settings.castle_list_cords.base_x")
        base_y = self.config_reader.get_value("settings.castle_list_cords.base_y")
        suffix_winter = self.config_reader.get_value("settings.castle_list_cords.castle_y_"+str(winter_castle_list_pos))
        suffix_sand = self.config_reader.get_value("settings.castle_list_cords.castle_y_"+str(sand_castle_list_pos))
        suffix_fire = self.config_reader.get_value("settings.castle_list_cords.castle_y_"+str(fire_castle_list_pos))

        sleep_time = self.config_reader.get_value("settings.offsets.default_click_delay")

        print(suffix_winter)
        print(suffix_sand)
        print(suffix_fire)

        time.sleep(sleep_time)
        pyautogui.click(
            base_x,
            base_y
        )
        time.sleep(sleep_time)
        if world_code == "ZIM":
            pyautogui.click(
                base_x,
                suffix_winter
            )
        if world_code == "PSK":
            pyautogui.click(
                base_x,
                suffix_sand
            )
        if world_code == "OHN":
            pyautogui.click(
                base_x,
                suffix_fire
            )

        self.log_message(
            status="ok",
            message="Svět změněn na: "+ world_code
        )

        time.sleep(sleep_time)


    def MultitaskingFortressRider(self,winter_atk_code,sand_atk_code,fire_atk_code, winter_castle_list_pos = 2, sand_castle_list_pos = 3, fire_castle_list_pos = 4, feather_forse=True, distance=99999, closing_popups=True, scan_before_run=False,
                                   world_scan=None ):

        self.log_message(status="info", message="multi-tasking rotace spuštěna.")
        if scan_before_run:
            # udela se scan na world_scan
            pass

        if closing_popups:
            # proběhne self.CloseWindowsPopups()
            pass

        records = self.ReturnSortedFortressList()
        records = self.FilterFortressListByDistance(records=records, max_distance=distance)

        while self.is_running:

            now = datetime.now()

            if not records:
                self.log_message(status="info", message="Žádné budoucí záznamy v DB.")
                time.sleep(1)
                continue

            try:
                expired_records = []  # seznam záznamů, co už mají čas <= now

                for rec in records:
                    world_code, coords, time_part = rec.split(";")
                    next_time = datetime.strptime(time_part, "%Y-%m-%d %H:%M:%S")
                    delta = (next_time - now).total_seconds()

                    if delta <= 0:
                        expired_records.append(rec)
                    else:
                        # první neexpirovaný -> log a pak break (protože records je seřazené)
                        self.log_message(
                            status="info",
                            message=f"Další: {world_code} | [{coords}] | Za: {int(delta)} s"
                        )
                        break

                # všechny expirované spustíme a odstraníme z records
                for rec in expired_records:
                    world_code, coords, _ = rec.split(";")
                    target_x, target_y = coords.split(":")
                    selected_atk_code = ""
                    if world_code == "ZIM":
                        selected_atk_code = str(winter_atk_code)
                    if world_code == "PSK":
                        selected_atk_code = str(sand_atk_code)
                    if world_code == "OHN":
                        selected_atk_code = str(fire_atk_code)

                    self.ChangeWorld(
                        world_code=world_code,
                        winter_castle_list_pos=winter_castle_list_pos,
                        sand_castle_list_pos=sand_castle_list_pos,
                        fire_castle_list_pos=fire_castle_list_pos
                    )
                    self.SendAttackFirstWaveAuto(
                        attack_code=selected_atk_code,
                        target_x=target_x,
                        target_y=target_y,
                        feather_horse=feather_forse,
                        note="Útok poslán"
                    )
                    records.remove(rec)

            except Exception as e:
                msg = f"Chyba při čtení záznamů (Multitasking): {e}"
                self.log_message(status="error", message=msg)

            time.sleep(1)

    def ReturnSortedFortressList(self):
        if not hasattr(self, "db_writer"):
            self.log_message(status="error", message="DbWriter není inicializován!")
            return []

        # předpokládáme, že JSON název = "db" nebo podle potřeby
        return self.db_writer.getSortedDb("db")

    # JEZDENI_PEVNOSTI_START__________________________________________
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
        log = LogMessage(
            time=time.time(),
            status=status,
            module=self.__class__.__name__,
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

    def NomadOrSamuOnContinent(self, horses,use_fill_all_waves,first_wave_from_bottom,other_waves_from_bottom,auto_fill_waves, target_x, target_y, max_attacks):
        pass