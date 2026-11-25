import os, subprocess, pathlib
from concurrent.futures import ThreadPoolExecutor

WOW = pathlib.Path("/wow-data")
BASE_OUT = pathlib.Path(os.environ.get("MPQ_OUT_DIR", "/mpqdata"))
OUT_EN = BASE_OUT / "enus"
OUT_DE = BASE_OUT / "dede"
OUT_EN.mkdir(parents=True, exist_ok=True)
OUT_DE.mkdir(parents=True, exist_ok=True)

def find_ci(base, name):
    for p in base.iterdir():
        if p.name.lower() == name.lower():
            return p
    return None

def run_extract(sub, names, out, patterns):
    d = WOW if sub == "." else find_ci(WOW, sub)
    if not d or not d.is_dir():
        return
    for n in names:
        f = find_ci(d, n)
        if f and f.is_file():
            print(f"-> Extrahiere {f} nach {out}")
            for pat in patterns:
                subprocess.run(["MPQExtractor", "-f", "-c", "-o", str(out), str(f), "-e", pat], check=False)

base = ["common.mpq", "common-2.mpq", "expansion.mpq", "lichking.mpq", "patch.mpq", "patch-2.mpq", "patch-3.mpq"]
engb = ["base-engb.mpq", "backup-engb.mpq", "locale-engb.mpq", "speech-engb.mpq", "expansion-locale-engb.mpq", "expansion-speech-engb.mpq", "lichking-locale-engb.mpq", "lichking-speech-engb.mpq", "patch-engb.mpq", "patch-engb-2.mpq", "patch-engb-3.mpq"]
dede = ["base-dede.mpq", "backup-dede.mpq", "locale-dede.mpq", "speech-dede.mpq", "expansion-locale-dede.mpq", "expansion-speech-dede.mpq", "lichking-locale-dede.mpq", "lichking-speech-dede.mpq", "patch-dede.mpq", "patch-dede-2.mpq", "patch-dede-3.mpq"]

run_extract(".", base, OUT_EN, [r"DBFilesClient\*", r"Interface\*", r"Sound\*"])
run_extract("enGB", engb, OUT_EN, [r"DBFilesClient\*", r"Interface\*", r"Sound\*"])
run_extract("deDE", dede, OUT_DE, [r"DBFilesClient\*", r"Interface\FrameXML\GlobalStrings.lua", r"Interface\WorldMap\*", r"Sound\*"])

for root, dirs, files in os.walk(str(BASE_OUT), topdown=False):
    for item in files + dirs:
        old = os.path.join(root, item)
        new = os.path.join(root, item.lower())
        if old != new:
            os.replace(old, new)

def convert_audio(p: pathlib.Path):
    if p.stat().st_size == 0:
        return
    out = pathlib.Path(str(p) + "_")
    if p.suffix == ".wav":
        cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", str(p), "-acodec", "libvorbis", "-f", "ogg", str(out)]
    else:
        cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", str(p), "-acodec", "libmp3lame", "-f", "mp3", str(out)]
    res = subprocess.run(cmd, check=False)
    if res.returncode == 0 and out.exists():
        p.unlink()

audio_files = [
    p for base_dir in (OUT_EN / "sound", OUT_DE / "sound") if base_dir.exists()
    for p in base_dir.rglob("*") if p.is_file() and p.suffix in (".wav", ".mp3")
]
if audio_files:
    workers = os.cpu_count() or 4
    print(f"-> Konvertiere {len(audio_files)} Audio-Dateien parallel auf {workers} Kernen...")
    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(convert_audio, audio_files))
    print("-> Audio-Konvertierung abgeschlossen!")
