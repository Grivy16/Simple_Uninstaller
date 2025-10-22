import webview
import os
import winreg
from plyer import notification
import subprocess

REG_PATHS = [
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_CURRENT_USER,  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
]

ma_liste = []

def get_installed_programs():
    programs = []
    for root, path in REG_PATHS:
        try:
            key = winreg.OpenKey(root, path)
        except FileNotFoundError:
            continue
        for i in range(0, winreg.QueryInfoKey(key)[0]):
            try:
                subkey_name = winreg.EnumKey(key, i)
                subkey = winreg.OpenKey(key, subkey_name)
                try:
                    name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                except FileNotFoundError:
                    continue
                try:
                    uninstall, _ = winreg.QueryValueEx(subkey, "UninstallString")
                except FileNotFoundError:
                    uninstall = None
                if name:
                    programs.append({"name": name, "uninstall": uninstall})
            except OSError:
                continue
    # Supprimer les doublons
    seen = set()
    unique = []
    for p in programs:
        if p["name"] not in seen:
            unique.append(p)
            seen.add(p["name"])
    return sorted(unique, key=lambda x: x["name"].lower())

# --- Désinstallation ---
def run_uninstall(cmd):
    if not cmd:
        notification.notify(
            title="Erreur",
            message="Impossible de trouver la commande de désinstallation.",
            app_name="Unistaller notification",
            timeout=5  # durée en secondes
        )
        return
    try:
        # MSI : msiexec /x
        if cmd.lower().endswith(".msi") or "msiexec" in cmd.lower():
            if not cmd.lower().startswith("msiexec"):
                cmd = f'msiexec /x "{cmd}" /quiet'
        subprocess.Popen(cmd, shell=True)
    except Exception as e:
        notification.notify(
            title="Erreur",
            message="Impossible d’exécuter : {e}.",
            app_name="Unistaller notification",
            timeout=5  # durée en secondes
        )
def to_list():
    programs = get_installed_programs()
    for p in programs :
        if p["name"]:
            ma_liste.append(p["name"])

def get_uninstall(item):
    programs = get_installed_programs()
    for p in programs:
        if p["name"] == item:
            uninstall_cmd = p.get("uninstall")
            if uninstall_cmd:
                return uninstall_cmd
            else:
                return None
    return None

# Liste Python
to_list()
# Classe API pour JS ↔ Python
class API:
    def get_items(self):
        return ma_liste

    def item_selected(self, item):
        run_uninstall(get_uninstall(item))
        return "OK reçu par Python"

# Chemin absolu du HTML
current_dir = os.path.dirname(os.path.abspath(__file__))
html_file = os.path.join(current_dir, "index.html")

# Crée la fenêtre et associe l'API directement
api = API()
window = webview.create_window("Ma Liste", html_file, js_api=api)

# Démarre l'application
webview.start()
