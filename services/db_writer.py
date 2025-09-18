import os

class DbWriter:
    def __init__(self):
        # cesta k souboru db.txt
        base_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "fortress_data_storage"
        )
        self.db_path = os.path.join(base_dir, "db.txt")

    def WriteToDb(self, data: str):
        """Připíše řetězec na konec db.txt (s novým řádkem)."""
        try:
            with open(self.db_path, "a", encoding="utf-8") as f:
                f.write(data.strip() + "\n")
        except Exception as e:
            print(f"[DbWriter] Chyba při zápisu do DB: {e}")

    def DbSorter(self):
        """Zatím nic nedělá (pouze placeholder)."""
        pass
