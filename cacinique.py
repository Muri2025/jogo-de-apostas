import tkinter as tk
from tkinter import messagebox
import random
import qrcode
from PIL import Image, ImageTk

class SlotMachine(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # --- CONFIGURAÇÕES DA JANELA ---
        self.title("Slot Machine Pro")
        self.geometry("700x780")
        self.configure(bg="black")
        self.resizable(False, False)

        # --- VARIÁVEIS DO JOGO ---
        self.saldo = 999
        self.aposta = 1
        self.is_spinning = False
        self.auto_spin_active = False

        self.symbols = ["🍒", "🍋", "🍊", "🍇", "🔔", "⭐", "7️⃣", "💎"]
        self.payouts = {
            "🍒": 4, "🍋": 4, "🍊": 5, "🍇": 6,
            "🔔": 10, "⭐": 16, "7️⃣": 30, "💎": 80
        }

        self.build_ui()

    def build_ui(self):
        # (O CÓDIGO DA INTERFACE PRINCIPAL CONTINUA EXATAMENTE IGUAL)
        font_title = ("Arial", 22, "bold")
        font_info = ("Arial", 12)
        font_slots = ("Segoe UI Emoji", 55)
        font_btn = ("Arial", 10, "bold")
        font_table = ("Courier New", 11)

        top_frame = tk.Frame(self, bg="black")
        top_frame.pack(fill=tk.X, padx=20, pady=20)
        tk.Label(top_frame, text="SLOT MACHINE", font=font_title, bg="black", fg="white").pack(side=tk.LEFT)

        info_frame = tk.Frame(top_frame, bg="black")
        info_frame.pack(side=tk.RIGHT)
        self.lbl_saldo = tk.Label(info_frame, text=f"Saldo: R${self.saldo}", font=font_info, bg="black", fg="#00FF00")
        self.lbl_saldo.pack(anchor="e")
        self.lbl_aposta_top = tk.Label(info_frame, text=f"Aposta: R${self.aposta}", font=font_info, bg="black", fg="white")
        self.lbl_aposta_top.pack(anchor="e")

        slot_border_frame = tk.Frame(self, bg="black", highlightbackground="white", highlightthickness=2)
        slot_border_frame.pack(pady=10)

        self.lbl_slots = []
        for i in range(3):
            lbl = tk.Label(slot_border_frame, text="💎", font=font_slots, bg="black", fg="white", 
                           width=3, height=1, relief="solid", bd=1, highlightbackground="white", highlightthickness=1)
            lbl.grid(row=0, column=i, padx=15, pady=20)
            self.lbl_slots.append(lbl)

        self.lbl_status = tk.Label(self, text="Bem-vindo!", font=("Arial", 14, "bold"), bg="black", fg="white")
        self.lbl_status.pack(pady=10)

        ctrl_frame = tk.Frame(self, bg="black")
        ctrl_frame.pack(pady=10)

        btn_style = {"bg": "black", "fg": "white", "font": font_btn, "activebackground": "#333333", 
                     "activeforeground": "white", "relief": "ridge", "bd": 2, "cursor": "hand2"}

        tk.Label(ctrl_frame, text="Aposta:", font=font_btn, bg="black", fg="white").grid(row=0, column=0, padx=5)
        tk.Button(ctrl_frame, text="-", command=self.dec_aposta, width=3, **btn_style).grid(row=0, column=1, padx=2)
        tk.Button(ctrl_frame, text="+", command=self.inc_aposta, width=3, **btn_style).grid(row=0, column=2, padx=2)
        tk.Button(ctrl_frame, text="MAX", command=self.max_aposta, width=4, **btn_style).grid(row=0, column=3, padx=2)

        self.btn_girar = tk.Button(ctrl_frame, text="GIRAR", command=self.start_spin, width=10, **btn_style)
        self.btn_girar.configure(fg="#FFD700")
        self.btn_girar.grid(row=0, column=4, padx=10)

        self.btn_auto = tk.Button(ctrl_frame, text="AUTO", command=self.toggle_auto, width=6, **btn_style)
        self.btn_auto.grid(row=0, column=5, padx=2)

        extra_ctrl_frame = tk.Frame(self, bg="black")
        extra_ctrl_frame.pack(pady=5)

        tk.Button(extra_ctrl_frame, text="RESET APOSTA", command=self.reset, width=15, **btn_style).grid(row=0, column=0, padx=5)
        
        self.btn_add_money = tk.Button(extra_ctrl_frame, text="ADICIONAR R$", command=self.open_add_saldo_popup, 
                                       width=15, bg="black", fg="#00FF00", font=font_btn, relief="ridge", bd=2)
        self.btn_add_money.grid(row=0, column=1, padx=5)

        table_frame = tk.Frame(self, bg="black", highlightbackground="white", highlightthickness=1)
        table_frame.pack(pady=20, padx=40, fill=tk.BOTH)

        tabela_texto = (
            "3 simbolos iguais: paga (payout) ≠ aposta\n\n"
            "Cherry(🍒):4x \n Lemon(🍋):4x \n Orange(🍊):5x\n"
            "Grape(🍇):6x \n Bell(🔔):10x \n Star(⭐):16x\n"
            "Seven(7️⃣):30x \n Diamond(💎):80x"
        )
        tk.Label(table_frame, text=tabela_texto, font=font_table, bg="black", fg="white").pack(pady=10)

    # ==================== LÓGICA DO POP-UP DE PAGAMENTO (NOVO) ====================
    def open_add_saldo_popup(self):
        self.popup = tk.Toplevel(self)
        self.popup.title("Depósito via Pix")
        self.popup.geometry("350x450") # Janela maior para caber o QR Code
        self.popup.configure(bg="black", highlightbackground="white", highlightthickness=2)
        self.popup.grab_set()

        # Frame para a entrada de valor
        self.frame_input = tk.Frame(self.popup, bg="black")
        self.frame_input.pack(pady=40)

        tk.Label(self.frame_input, text="Quanto deseja adicionar?", font=("Arial", 12, "bold"), bg="black", fg="white").pack(pady=10)
        self.ent_valor = tk.Entry(self.frame_input, font=("Arial", 16), justify='center', width=10)
        self.ent_valor.pack(pady=10)
        self.ent_valor.focus_set()

        btn_gerar = tk.Button(self.frame_input, text="GERAR PIX", bg="#00FF00", fg="black", font=("Arial", 10, "bold"),
                              command=self.processar_geracao_pix)
        btn_gerar.pack(pady=20)

        # Frame para exibir o QR Code (escondido inicialmente)
        self.frame_qr = tk.Frame(self.popup, bg="black")
        
        self.lbl_qr_title = tk.Label(self.frame_qr, text="Aguardando pagamento...", font=("Arial", 12, "bold"), bg="black", fg="#FFD700")
        self.lbl_qr_title.pack(pady=10)

        self.lbl_qr_image = tk.Label(self.frame_qr, bg="black")
        self.lbl_qr_image.pack(pady=10)

        self.lbl_timer = tk.Label(self.frame_qr, text="", font=("Arial", 10), bg="black", fg="white")
        self.lbl_timer.pack(pady=5)

    def processar_geracao_pix(self):
        valor_str = self.ent_valor.get()
        try:
            self.valor_pendente = int(valor_str)
            if self.valor_pendente <= 0:
                raise ValueError
            
            # Esconde a tela de digitar valor e mostra a do QR Code
            self.frame_input.pack_forget()
            self.frame_qr.pack(pady=20)

            # Gera um QR Code visual (usando uma string fake por enquanto)
            pix_fake_payload = f"00020101021126580014br.gov.bcb.pix0136{self.valor_pendente}MOCK"
            qr = qrcode.QRCode(version=1, box_size=6, border=2)
            qr.add_data(pix_fake_payload)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            
            # Converte para o formato do Tkinter
            self.qr_photo = ImageTk.PhotoImage(img)
            self.lbl_qr_image.config(image=self.qr_photo)

            # Inicia o "polling" simulado (verificando o pagamento)
            self.tempo_simulacao = 6 # Segundos até aprovar automaticamente
            self.verificar_pagamento()

        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um número inteiro válido.", parent=self.popup)

    def verificar_pagamento(self):
        # Aqui no futuro faremos a requisição HTTP para a sua API PHP
        
        if self.tempo_simulacao > 0:
            self.lbl_timer.config(text=f"Simulando resposta da API em... {self.tempo_simulacao}s")
            self.tempo_simulacao -= 1
            self.after(1000, self.verificar_pagamento) # Aguarda 1 segundo e roda de novo
        else:
            # Pagamento Aprovado!
            self.saldo += self.valor_pendente
            self.update_displays()
            self.lbl_status.config(text=f"PIX RECEBIDO! R${self.valor_pendente} adicionados.", fg="#00FF00")
            self.popup.destroy()

    # (O RESTANTE DA LÓGICA DO JOGO FICA IGUAL - inc_aposta, start_spin, etc)
    def update_displays(self):
        self.lbl_saldo.config(text=f"Saldo: R${self.saldo}")
        self.lbl_aposta_top.config(text=f"Aposta: R${self.aposta}")

    def inc_aposta(self):
        if not self.is_spinning and self.aposta < self.saldo:
            self.aposta += 1
            self.update_displays()

    def dec_aposta(self):
        if not self.is_spinning and self.aposta > 1:
            self.aposta -= 1
            self.update_displays()

    def max_aposta(self):
        if not self.is_spinning and self.saldo > 0:
            self.aposta = self.saldo
            self.update_displays()

    def reset(self):
        if not self.is_spinning:
            self.aposta = 1 if self.saldo > 0 else 0
            self.update_displays()

    def toggle_auto(self):
        if self.auto_spin_active:
            self.auto_spin_active = False
            self.btn_auto.config(bg="black", fg="white")
        else:
            self.auto_spin_active = True
            self.btn_auto.config(bg="white", fg="black")
            self.start_spin()

    def start_spin(self):
        if self.is_spinning: return
        if self.saldo < self.aposta or self.saldo <= 0:
            self.lbl_status.config(text="Saldo insuficiente!", fg="red")
            self.auto_spin_active = False
            self.btn_auto.config(bg="black", fg="white")
            return

        self.is_spinning = True
        self.saldo -= self.aposta
        self.update_displays()
        self.lbl_status.config(text="Girando...", fg="white")
        self.spin_cycles = 15
        self.animate_spin()

    def animate_spin(self):
        if self.spin_cycles > 0:
            for lbl in self.lbl_slots:
                lbl.config(text=random.choice(self.symbols))
            self.spin_cycles -= 1
            self.after(80, self.animate_spin)
        else:
            self.check_win()

    def check_win(self):
        res = [random.choice(self.symbols) for _ in range(3)]
        for i, lbl in enumerate(self.lbl_slots):
            lbl.config(text=res[i])

        if res[0] == res[1] == res[2]:
            multiplicador = self.payouts[res[0]]
            premio = self.aposta * multiplicador
            self.saldo += premio
            self.lbl_status.config(text=f"GANHOU! +R${premio}", fg="#00FF00")
        else:
            self.lbl_status.config(text="Tente novamente!", fg="white")

        self.update_displays()
        self.is_spinning = False
        if self.auto_spin_active:
            if self.saldo >= self.aposta:
                self.after(1000, self.start_spin)
            else:
                self.auto_spin_active = False
                self.btn_auto.config(bg="black", fg="white")

if __name__ == "__main__":
    app = SlotMachine()
    app.mainloop()