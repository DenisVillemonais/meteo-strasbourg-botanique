import csv
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

API_KEY = os.environ["METEOFRANCE_API_KEY"]
STATION_ID = "67482001"
REPO_DIR = Path(__file__).resolve().parent
DATA_FILE = REPO_DIR / "data" / "latest.json"
URL = "https://public-api.meteofrance.fr/public/DPObs/v2/station/horaire"

params = {
    "id_station": STATION_ID,
    "date": datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0).isoformat().replace("+00:00", "Z"),
    "format": "json",
}

headers = {
    "apikey": API_KEY,
    "accept": "application/json",
}

def k_to_c(value):
    return round(value - 273.15, 2) if value is not None else None

HISTORY_FILE = REPO_DIR / "data" / "history.csv"

def append_history(date_iso, heure_locale, temperature, pluie, majsite, succes_api):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    file_exists = HISTORY_FILE.exists()

    with HISTORY_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        if not file_exists:
            writer.writerow(["date", "heurelocale", "temperature", "pluie", "majsite", "succesAPI"])
        writer.writerow([date_iso, heure_locale, temperature, pluie, majsite, succes_api])

r = requests.get(URL, params=params, headers=headers, timeout=30)
r.raise_for_status()
data = r.json()

# Indicateur de succès/échec de l'appel API
api_status = "succès API" if data else "échec API"
api_status_bool = "yes" if data else "no"


if not data:
    print("Aucune donnée renvoyée par l'API Météo-France pour cet instant, mise à jour partielle.")

    if DATA_FILE.exists():
        existing = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    else:
        existing = {}

    existing["site_updated_at"] = datetime.now(ZoneInfo("Europe/Paris")).strftime("%Y-%m-%d %H:%M:%S %Z")
    existing["api_status"] = api_status

    DATA_FILE.write_text(
        json.dumps(existing, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    # exit(0)
else:
    obs = data[0]
    heure_utc = obs.get("validity_time")
    heure_paris = None

    if heure_utc is not None:
        dt_utc = datetime.fromisoformat(heure_utc.replace("Z", "+00:00"))
        dt_paris = dt_utc.astimezone(ZoneInfo("Europe/Paris"))
        heure_paris = dt_paris.strftime("%Y-%m-%d %H:%M:%S %Z")

    result = {
        "station": STATION_ID,
        "heure_utc": heure_utc,
        "heure_paris": heure_paris,
        "temperature_c": k_to_c(obs.get("t")) if obs else None,
        "temperature_max_c": k_to_c(obs.get("tx")) if obs else None,
        "temperature_min_c": k_to_c(obs.get("tn")) if obs else None,
        "point_rosee_c": k_to_c(obs.get("td")) if obs else None,
        "pluie_1h_mm": obs.get("rr1") if obs else None,
        "humidite_pct": obs.get("u") if obs else None,
        "vent_direction_deg": obs.get("dd") if obs else None,
        "vent_moyen_ms": obs.get("ff") if obs else None,
        "rafale_ms": obs.get("raf") if obs else None,
        "pression_pa": obs.get("pres") if obs else None,
        "pression_mer_pa": obs.get("pmer") if obs else None,
        "latitude": obs.get("lat") if obs else None,
        "longitude": obs.get("lon") if obs else None,
        # Heure de la tentative (toujours renseignée)
        "site_updated_at": datetime.now(ZoneInfo("Europe/Paris")).strftime("%Y-%m-%d %H:%M:%S %Z"),
        # Indicateur de statut API
        "api_status": api_status,
    }

    DATA_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    append_history(
        date_iso=dt_paris,
        heure_locale=heure_paris,
        temperature=result["temperature_c"],
        pluie=result["pluie_1h_mm"],
        majsite=result["site_updated_at"],
        succes_api=api_status_bool,
    )

subprocess.run(["git", "-C", str(REPO_DIR), "add", "-A"], check=True)
subprocess.run(["git", "-C", str(REPO_DIR), "commit", "-m", "Mise à jour météo automatique"], check=False)
subprocess.run(["git", "-C", str(REPO_DIR), "push"], check=True)