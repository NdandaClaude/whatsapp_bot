import json
import os

CONFIG_FILE = 'config.json'

DEFAULT_CONFIG = {
    "api_key": "",
    "model": "deepseek/deepseek-v3-0324",
    "prompt_identity": "Décris ici la personnalité de ton bot IA."
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
