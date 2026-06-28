# Site GitHub Pages météo — Strasbourg Botanique

Ce projet contient :
- `index.html` : la page statique publiée sur GitHub Pages ;
- `data/latest.json` : les dernières données météo affichées sur la page ;
- `update_weather.py` : le script Python à lancer toutes les heures sur votre serveur local.

## 1. Préparer le dépôt GitHub

1. Créez un dépôt GitHub, par exemple `meteo-strasbourg-botanique`.
2. Copiez ces fichiers dans le dépôt.
3. Activez GitHub Pages dans **Settings > Pages** en publiant depuis la branche principale.

## 2. Préparer le serveur local

Installez Python et `requests`, puis définissez votre clé API Météo-France dans une variable d'environnement.

### Linux / macOS

```bash
export METEOFRANCE_API_KEY="VOTRE_NOUVELLE_CLE_API"
pip install requests
```

### Windows PowerShell

```powershell
setx METEOFRANCE_API_KEY "VOTRE_NOUVELLE_CLE_API"
pip install requests
```

## 3. Test manuel

Depuis le dossier du dépôt :

```bash
python update_weather.py
```

Le script :
- appelle l'API Météo-France ;
- met à jour `data/latest.json` ;
- fait `git add`, `git commit`, puis `git push`.

## 4. Automatisation horaire

### Avec cron (Linux)

Éditez la crontab avec `crontab -e` puis ajoutez :

```cron
5 * * * * cd /chemin/vers/meteo-strasbourg-botanique && /usr/bin/python3 update_weather.py >> weather.log 2>&1
```

Cela lancera le script à 5 minutes de chaque heure.

## 5. Important

Ne mettez jamais votre clé API Météo-France dans `index.html` ni dans le dépôt GitHub public. Utilisez une variable d'environnement sur votre serveur local.
