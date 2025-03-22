import json
import os

CONFIG_DIR = "Steering Controls/Loadout"  # Direktori penyimpanan config
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")  # Path lengkap ke config.json

# ✅ Default Config
default_config = {
    "steering_sensitivity": 1.0,
    "steering_deadzone": 5,
    "max_wheel_rotation": 450,
    "gas_min": 20000,
    "gas_max": 32767,
    "brake_min": 9000,
    "brake_max": 29000
}

def save_config(config):
    """Simpan konfigurasi ke file JSON di Loadout folder"""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)  # Buat folder kalau belum ada

    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)
    print(f"✅ Config saved in {CONFIG_FILE}!")

def load_config():
    """Load konfigurasi dari file JSON, kalau gak ada, pakai default"""
    if not os.path.exists(CONFIG_FILE):
        print("⚠️ Config file not found! Using default values.")
        save_config(default_config)  # Buat file baru kalau belum ada

    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)

    print(f"✅ Config loaded from {CONFIG_FILE}!")
    return config
