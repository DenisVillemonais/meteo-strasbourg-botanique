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


r = requests.get(URL, params=params, headers=headers, timeout=30)
r.raise_for_status()
data = r.json()

if not data:
    raise RuntimeError("Aucune donnée renvoyée par l'API Météo-France.")

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
    "temperature_c": k_to_c(obs.get("t")),
    "temperature_max_c": k_to_c(obs.get("tx")),
    "temperature_min_c": k_to_c(obs.get("tn")),
    "point_rosee_c": k_to_c(obs.get("td")),
    "pluie_1h_mm": obs.get("rr1"),
    "humidite_pct": obs.get("u"),
    "vent_direction_deg": obs.get("dd"),
    "vent_moyen_ms": obs.get("ff"),
    "rafale_ms": obs.get("raf"),
    "pression_pa": obs.get("pres"),
    "pression_mer_pa": obs.get("pmer"),
    "latitude": obs.get("lat"),
    "longitude": obs.get("lon"),
    "site_updated_at": datetime.now(ZoneInfo("Europe/Paris")).strftime("%Y-%m-%d %H:%M:%S %Z"),
}

DATA_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

subprocess.run(["git", "-C", str(REPO_DIR), "add", "data/latest.json"], check=True)
subprocess.run(["git", "-C", str(REPO_DIR), "commit", "-m", "Mise à jour météo automatique"], check=False)
subprocess.run(["git", "-C", str(REPO_DIR), "push"], check=True)
