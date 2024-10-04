import os
import subprocess
import sys

required_packages = [
    "asyncio",
    "bs4",
    "discord",
    "ffmpeg",
    "gtts",
    "io",
    "mutagen",
    "mcrcon",
    "openai",
    "openpyxl",
    "os",
    "pandas",
    "platform",
    "pokebase",
    "pyttsx3",
    "pydub",
    "pyaudio",
    "random",
    "re",
    "requests",
    "time",
    "tracemalloc",
    "bs4",
    "psutil",
    "pyarrow",
    "rcon",
    "qrcode",
    "pyqrcode",
    "png",
    "pypix",
    "fpdf",
    "socket",
    "struct",
    "spotipy",
    "socket",
    "subprocess",
    "telnetlib",
    "translate",
    "wave",
]

missing_packages = []

for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        missing_packages.append(package)

if missing_packages:
    print(f"Sua casa ainda não está pronta para receber o Bruno. Vamos preparar os itens que faltam. Aqui está: {missing_packages}")
    for package in missing_packages:
        subprocess.run([sys.executable, "-m", "pip", "install", package, "--upgrade", "--user"])
        print(f"Instalado {package}")
os.system("python main.py -log")