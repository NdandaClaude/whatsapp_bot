import tkinter as tk
from tkinter import messagebox, scrolledtext
from .config import load_config, save_config
import threading

class BotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 WhatsApp Bot IA")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)

        self.bot_thread = None
        self.stop_flag = False
        self.console_log = self._create_console_log(root)

        self.api_var = tk.StringVar()
        self.model_var = tk.StringVar()

        self.api_entry = self._create_input(root, 0, "Clé API HuggingFace :", self.api_var)
        self.model_entry = self._create_input(root, 1, "Modèle IA :", self.model_var)

        label_style = {"bg": "#1e1e1e", "fg": "#00e676", "font": ("Segoe UI", 10, "bold")}
        tk.Label(root, text="Prompt d'identité :", **label_style).grid(row=2, column=0, sticky="nw", padx=10, pady=5)

        prompt_frame = tk.Frame(root, bg="#3a3a3a", highlightthickness=1, highlightbackground="#00e676", bd=0)
        prompt_frame.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, width=68, height=15,
                                                     bg="#3a3a3a", fg="#ffffff",
                                                     insertbackground="white",
                                                     font=("Segoe UI", 10), relief=tk.FLAT, bd=0,
                                                     wrap=tk.WORD)
        self.prompt_text.pack(fill="both", padx=6, pady=6)

        style_btn = {
            "bg": "#00e676", "fg": "#1e1e1e",
            "activebackground": "#00c853",
            "activeforeground": "#ffffff",
            "font": ("Segoe UI", 9, "bold"),
            "relief": tk.FLAT,
            "padx": 6, "pady": 4
        }

        left_btns = tk.Frame(root, bg="#1e1e1e")
        left_btns.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        self.save_btn = tk.Button(left_btns, text="💾 Sauvegarder", command=self.save_config, **style_btn)
        self.save_btn.pack(side="left", padx=(0, 8))

        self.help_btn = tk.Button(left_btns, text="❓ Aide", command=self.open_help, **style_btn)
        self.help_btn.pack(side="left")

        right_btns = tk.Frame(root, bg="#1e1e1e")
        right_btns.grid(row=3, column=1, padx=10, pady=10, sticky="e")

        self.run_btn = tk.Button(right_btns, text="🚀 Lancer", command=self.start_bot, **style_btn)
        self.run_btn.pack(side="left", padx=(0, 8))

        self.stop_btn = tk.Button(right_btns, text="🛑 Stop", command=self.stop_bot, state=tk.DISABLED, **style_btn)
        self.stop_btn.pack(side="left")

        self.load_config_ui()

    def _create_input(self, parent, row, label, var_text):
        label_style = {"bg": "#1e1e1e", "fg": "#00e676", "font": ("Segoe UI", 10, "bold")}
        tk.Label(parent, text=label, **label_style).grid(row=row, column=0, sticky="w", padx=10, pady=5)
        frame = tk.Frame(parent, bg="#3a3a3a", highlightthickness=1, highlightbackground="#00e676", bd=0)
        frame.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        entry = tk.Entry(frame, textvariable=var_text, bg="#3a3a3a", fg="#ffffff", insertbackground="white",
                         font=("Segoe UI", 10), relief=tk.FLAT, bd=1)
        entry.pack(fill="both", padx=6, pady=4)
        return entry

    def load_config_ui(self):
        config = load_config()
        self.api_var.set(config.get("api_key", ""))
        self.model_var.set(config.get("model", ""))
        self.prompt_text.insert(tk.END, config.get("prompt_identity", ""))

    def save_config(self):
        config = {
            "api_key": self.api_var.get(),
            "model": self.model_var.get(),
            "prompt_identity": self.prompt_text.get("1.0", tk.END).strip()
        }
        save_config(config)
        messagebox.showinfo("Config", "✅ Configuration sauvegardée !")

    def start_bot(self):
        config = {
            "api_key": self.api_var.get(),
            "model": self.model_var.get(),
            "prompt_identity": self.prompt_text.get("1.0", tk.END).strip()
        }
        if not config["api_key"]:
            messagebox.showwarning("Erreur", "Veuillez entrer votre clé API.")
            return
        save_config(config)
        self.stop_flag = False
        self.stop_btn.config(state=tk.NORMAL)
        self.run_btn.config(state=tk.DISABLED)
        from .bot import main_bot
        from .utils import get_user_info, check_app_status
        self.bot_thread = threading.Thread(target=main_bot, args=(config, self, get_user_info, check_app_status), daemon=True)
        self.bot_thread.start()
        messagebox.showinfo("Bot", "🤖 Bot lancé ! Scanne le QR Code si demandé.")

    def stop_bot(self):
        self.stop_flag = True
        self.stop_btn.config(state=tk.DISABLED)
        self.run_btn.config(state=tk.NORMAL)
        messagebox.showinfo("Bot", "🛑 Bot arrêté.")

    def open_help(self):
        aide_win = tk.Toplevel(self.root)
        aide_win.title("📘 Aide & Explications")
        aide_win.configure(bg="#1e1e1e")
        aide_win.resizable(False, False)

        tk.Label(aide_win, text="🤖 WhatsApp Bot IA - Guide rapide",
                 bg="#1e1e1e", fg="#00e676", font=("Segoe UI", 12, "bold")).pack(pady=(10, 5))
        texte = """
🔹 À quoi sert ce bot ?
Ce bot lit automatiquement les messages non lus sur WhatsApp Web,
et répond avec une IA (HuggingFace) selon le style défini dans le prompt.

🔹 Clé API HuggingFace :
Obtenez votre clé ici : https://huggingface.co/settings/tokens

🔹 Modèle IA :
Par défaut : deepseek/deepseek-v3-0324 (d'autres modèles compatibles peuvent fonctionner)

🔹 Prompt d'identité :
Définissez *la personnalité* de votre bot IA.
"""
        exemple_prompt = (
            "Tu es un assistant IA utile, professionnel et sympathique.\n"
            "Tu réponds de façon concise et polie."
        )
        contenu = tk.Label(aide_win, text=texte, justify="left", anchor="w",
                           bg="#1e1e1e", fg="white", font=("Segoe UI", 10))
        contenu.pack(padx=20, pady=(5, 0), anchor="w")
        exemple = tk.Text(aide_win, height=6, wrap="word",
                          bg="#2a2a2a", fg="#00e676",
                          font=("Segoe UI", 9), relief=tk.FLAT)
        exemple.insert("1.0", exemple_prompt)
        exemple.configure(state="disabled")
        exemple.pack(padx=20, pady=(0, 10), fill="x")
        tk.Button(aide_win, text="Fermer", command=aide_win.destroy,
                  bg="#00e676", fg="#1e1e1e",
                  font=("Segoe UI", 9, "bold"),
                  relief=tk.FLAT, padx=6, pady=4).pack(pady=(0, 15))

    def _create_console_log(self, parent):
        frame_log = tk.Frame(parent, bg="#1e1e1e")
        frame_log.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 10))
        log_box = scrolledtext.ScrolledText(frame_log, height=8, bg="#121212", fg="#00e676",
                                            font=("Consolas", 9), state="disabled", relief=tk.FLAT,
                                            insertbackground="white")
        log_box.pack(fill="both", expand=True)
        return log_box

    def log(self, message):
        self.console_log.config(state="normal")
        self.console_log.insert(tk.END, f"{message}\n")
        self.console_log.see(tk.END)
        self.console_log.config(state="disabled")

    def create_qr_window(self, photo):
        qr_window = tk.Toplevel(self.root)
        qr_window.title("🔐 Connexion WhatsApp")
        qr_window.configure(bg="#1e1e1e")
        qr_window.resizable(False, False)
        label = tk.Label(qr_window, image=photo, bg="#1e1e1e")
        label.image = photo
        label.pack(padx=20, pady=20)
        tk.Label(qr_window, text="Scanne le QR Code avec ton WhatsApp", fg="white", bg="#1e1e1e",
                 font=("Segoe UI", 10)).pack(pady=(0, 15))
        return qr_window

    def show_error(self, title, msg):
        messagebox.showerror(title, msg)
