# aowow-docker

Dockerized setup for **AoWoW** (AzerothCore Database Viewer) running on **PHP 8.4 + Apache**, paired with an automated, multi-core **MPQExtractor + FFmpeg** tool container for client assets and audio conversion.

## Features
- **PHP 8.4 + Apache:** Preconfigured with `mysqli`, `gd` (FreeType + JPEG), `simplexml`, `xml`, and `mod_rewrite`.
- **Persistent Docker Volume (`aowow_data`):** Keeps generated configuration, icons, zone maps, datasets, and audio files intact across container restarts and updates.
- **All-in-One MPQ & Audio Tool Container (`mpq-extractor`):** Compiles `MPQExtractor` from source, extracts required DBC/Interface/Sound files in proper patch order, normalizes filenames to lowercase, and converts `.wav`/`.mp3` audio files in parallel across all CPU cores using `ffmpeg`.
- **Seamless AzerothCore Network Integration:** Connects directly to your existing AzerothCore Docker network (`ac-database`).

---

## Quick Start

### 1. Clone & Configure
```bash
git clone https://github.com/psylopterix/aowow-docker.git
cd aowow-docker
cp .env.example .env
```

Find your AzerothCore Docker network name:
```bash
docker network ls
```
Look for the network ending in `_ac-network` (e.g. `wow-server-playerbots_ac-network`).  
Update `.env` with your `AC_DOCKER_NETWORK` (e.g. `wow-server-playerbots_ac-network`) and `WOW_DATA_DIR` (path to your WoW 3.3.5a `Data` directory).

### 2. Build & Start AoWoW
```bash
docker compose up -d --build
```

### 3. Extract Client MPQ Data & Convert Audio
Run the one-shot tool container (this extracts DBCs, icons, maps, and converts audio files in parallel):
```bash
docker compose --profile tools run --rm mpq-extractor
```

### 4. Run the Interactive AoWoW Setup
```bash
docker exec -it aowow php aowow --setup
```
- For **Web Server Host** (`SITE_HOST`): enter `localhost:81` (or your `AOWOW_PORT`).
- For **Static Content Host** (`STATIC_HOST`): enter `localhost:81/static`.
- When prompted that `http://localhost:81/robots.txt` cannot be accessed from inside the container, press **`c`** (*continue anyway*).

Once setup finishes and you create your admin account, open **`http://localhost:81`** in your browser.

---

## Optional: Using the Pre-Patched Fork (PHP 8.4 + AzerothCore Fixes)
Until the upstream PRs are merged into `azerothcore/aowow`, you can build directly from the combined `all-fixes` branch:
```bash
docker compose build --build-arg AOWOW_REPO=https://github.com/psylopterix/aowow.git --build-arg AOWOW_BRANCH=all-fixes
docker compose up -d
```
