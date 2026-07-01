import csv
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
INPUT_FILE = REPO_DIR / "data" / "history.csv"
OUTPUT_FILE = REPO_DIR / "data" / "history_horaire.csv"

def hour_key(date_str: str) -> str:
    # On garde uniquement AAAA-MM-JJ HH
    return date_str.strip()[:13]

def generate_hourly_history() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Fichier introuvable : {INPUT_FILE}")

    seen_hours = set()
    kept_rows = []

    with INPUT_FILE.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            h = hour_key(row["date"])
            if h not in seen_hours:
                seen_hours.add(h)
                kept_rows.append(row)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["date", "temperature", "pluie", "majsite", "succesAPI"],
            delimiter=";"
        )
        writer.writeheader()
        writer.writerows(kept_rows)

    print(f"{len(kept_rows)} lignes écrites dans {OUTPUT_FILE}")