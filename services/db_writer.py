# gge_clicker/fortress_data_storage/db_writer.py
import os
from datetime import datetime

class DbWriter:
    def __init__(self):
        self.base_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "fortress_data_storage"
        )
        self.json_name = ""
        self.db_path = ""

    def WriteToDb(self, data: str, json_name: str):
        """Připíše řetězec na konec db.txt (s novým řádkem)."""
        self.db_path = os.path.join(self.base_dir, json_name + "_db.txt")
        try:
            with open(self.db_path, "a", encoding="utf-8") as f:
                f.write(data.strip() + "\n")
        except Exception as e:
            print(f"[DbWriter] Chyba při zápisu do DB: {e}")

    def getSortedDb(self, json_name: str):
        """Vrátí budoucí záznamy z db.txt seřazené podle času."""
        self.db_path = os.path.join(self.base_dir, json_name + ".txt")
        sorted_list = []

        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"[DbWriter] Soubor {self.db_path} nenalezen.")
            return []

        now = datetime.now()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                _, _, time_part = line.split(";")
                record_time = datetime.strptime(time_part, "%Y-%m-%d %H:%M:%S")
                if record_time > now:
                    sorted_list.append((record_time, line))
            except Exception as e:
                print(f"[DbWriter] Chybný záznam: {line}")
                continue

        sorted_list.sort(key=lambda x: x[0])
        return [x[1] for x in sorted_list]
