import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
INPUT_FILE = REPO_DIR / "data" / "history_horaire.csv"
OUTPUT_FILE = REPO_DIR / "data" / "graph_24h.png"


def generate_weather_graph() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Fichier introuvable : {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE, sep=";")
    # df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d %H:%M:%S %Z", errors="coerce")
    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
    df["pluie"] = pd.to_numeric(df["pluie"], errors="coerce")

    df = df.dropna(subset=["date"]).sort_values("date")
    if df.empty:
        return

    last = df["date"].max()
    df = df[df["date"] >= last - pd.Timedelta(hours=23)]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(14, 8), sharex=True,
        gridspec_kw={"height_ratios": [2, 1]}
    )
    fig.patch.set_facecolor("white")

    ax1.plot(df["date"], df["temperature"], color="#1f77b4", linewidth=2.5, marker="o", markersize=4)
    ax1.set_ylabel("Température (°C)")
    ax1.set_title("24 dernières heures - Température et pluie", pad=14, fontweight="bold")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    ax2.bar(df["date"], df["pluie"], width=0.03, color="#17becf", alpha=0.85)
    ax2.set_ylabel("Pluie (mm)")
    ax2.set_xlabel("Heure")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    for ax in (ax1, ax2):
        ax.grid(True, alpha=0.25)
        ax.margins(x=0.01)

    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(OUTPUT_FILE, dpi=160, bbox_inches="tight")
    plt.close(fig)