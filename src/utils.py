import platform
import getpass
import socket
import time
import requests

def get_user_info():
    try:
        res = requests.get("https://ipinfo.io/json", timeout=5)
        data = res.json()
        ip = data.get("ip", "N/A")
        country = data.get("country", "N/A")
        region = data.get("region", "N/A")
        city = data.get("city", "N/A")
        org = data.get("org", "N/A")
        loc = data.get("loc", "N/A")

        return f"""
Connexion détectée :
IP publique : {ip}
Ville : {city}, Région : {region}, Pays : {country}
Fournisseur : {org}
Coordonnées : {loc}
Timestamp : {time.strftime('%Y-%m-%d %H:%M:%S')}

Système :
Utilisateur : {getpass.getuser()}
Machine : {socket.gethostname()}
OS : {platform.system()} {platform.release()}
Architecture : {platform.machine()}
Python : {platform.python_version()}
"""
    except Exception as e:
        return f"[ERREUR localisation] {e}"

def check_app_status():
    # Pour la version publique, toujours actif.
    return True, ""
