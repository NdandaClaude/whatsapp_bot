import time
import requests
from PIL import Image, ImageTk
from io import BytesIO

from DrissionPage import ChromiumPage, ChromiumOptions

def display_qr_code(page, ui):
    try:
        ui.log("[INFO] Connexion à WhatsApp Web...")
        wait_time = 0
        while True:
            canvas = page.ele('tag:canvas')
            messages = page.eles('css:div.message-in, div.message-out')
            if canvas:
                break
            elif messages:
                ui.log("[INFO] Déjà connecté à WhatsApp Web ✅")
                return
            else:
                time.sleep(1)
                wait_time += 1
                if wait_time > 30:
                    ui.log("[QR TIMEOUT] Impossible de détecter WhatsApp Web.")
                    return

        page.get_screenshot(path='qr_code.png', full_page=False)
        img = Image.open("qr_code.png")
        img = img.resize((700, 500))
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        photo = ImageTk.PhotoImage(data=buffer.getvalue())

        qr_window = ui.create_qr_window(photo)
        ui.log("[INFO] QR Code affiché. Scanne-le avec WhatsApp.")

        while page.ele('tag:canvas'):
            time.sleep(1)
        qr_window.destroy()
    except Exception as e:
        ui.log(f"[QR ERROR] {e}")

def get_ia_reply(message, config, ui):
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {"role": "system", "content": config["prompt_identity"]},
            {"role": "user", "content": message}
        ],
        "model": config["model"]
    }
    try:
        resp = requests.post("https://router.huggingface.co/novita/v3/openai/chat/completions",
                             headers=headers, json=payload, timeout=15)
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        ui.log(f"[ERREUR API] {e}")
        return "Désolé, je n'arrive pas à répondre pour l'instant."

def find_unread_chats(page):
    badges = page.eles('xpath:.//span[contains(@aria-label, "non lu")]')
    return badges[1:] if badges else []

def process_chat(page, chat, config, ui):
    try:
        chat.click()
        time.sleep(1)
        messages = page.eles('css:div.message-in, div.message-out')
        if not messages:
            return
        last = messages[-1].ele('css:span.selectable-text')
        if not last:
            return
        text = last.text
        ui.log(f"[Message reçu] {text}")
        reply = get_ia_reply(text, config, ui)
        ui.log(f"[Réponse IA] {reply}")

        text_box = page.ele('xpath://div[@contenteditable="true" and @aria-placeholder="Entrez un message"]')
        if text_box:
            text_box.click()
            text_box.input(reply)
            time.sleep(0.5)
            send_button = page.ele('css:span[data-icon="send"]')
            if send_button:
                send_button.click()

        page.run_js("""
            document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', keyCode: 27, which: 27}));
        """)
    except Exception as e:
        ui.log(f"[ERREUR discussion] {e}")

def main_bot(config, ui, get_user_info, check_app_status):
    active, reason = check_app_status()
    if not active:
        ui.log(f"❌ Application désactivée. Motif : {reason}")
        ui.show_error("Bot désactivé", f"⛔ Bot désactivé.\n\nMotif : {reason}")
        return

    # Optionnel : ui.log(get_user_info())

    options = ChromiumOptions()
    options.headless(True)
    page = ChromiumPage(options)
    page.get('https://web.whatsapp.com')
    display_qr_code(page, ui)

    while not ui.stop_flag:
        unread_chats = find_unread_chats(page)
        if unread_chats:
            for chat in unread_chats:
                if ui.stop_flag:
                    break
                process_chat(page, chat, config, ui)
                time.sleep(2)
        else:
            ui.log("[INFO] Rien de nouveau. Nouvelle vérif dans 2s.")
            time.sleep(2)

    ui.log("[BOT] Arrêt demandé, fermeture du bot...")
