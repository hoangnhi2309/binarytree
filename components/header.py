import tkinter as tk
import tkinter.ttk as ttk
import random
import threading
import time
import tkinter.messagebox as messagebox
from tkinter.filedialog import asksaveasfilename
from PIL import Image, ImageTk
import os
class Header(tk.Frame):
    def __init__(self, parent, on_menu_click):
        super().__init__(parent, bg="#b0b0b0")
        self.pack(fill='x')

        self.on_menu_click = on_menu_click
        self.menu_buttons = {}

        logo_image = Image.open("binarytree.png").resize((75, 75))
        self.logo_photo = ImageTk.PhotoImage(logo_image)

        logo_label = tk.Label(self, image=self.logo_photo, bg="#b0b0b0")
        logo_label.pack(side="left", padx=(10, 5), pady=5)

        menu_items = ["Binary Tree", "Binary Search Tree", "AVL Tree"]
        for item in menu_items:
            normal_font = ("Arial", 20, "bold")
            underline_font = ("Arial", 20, "bold", "underline")

            btn = tk.Label(self, text=item, font=normal_font,
                           bg="#b0b0b0", fg="black", cursor="hand2")
            btn.pack(side="left", padx=30)
            btn.bind("<Enter>", lambda e, b=btn: b.config(font=underline_font))
            btn.bind("<Leave>", lambda e, b=btn: b.config(font=normal_font))
            btn.bind("<Button-1>", lambda e, name=item: self.menu_clicked(name))

            self.menu_buttons[item] = btn

    def menu_clicked(self, name):
        self.set_active(name)
        self.on_menu_click(name)

    def set_active(self, active_name):
        for name, btn in self.menu_buttons.items():
            if name == active_name:
                btn.config(fg="#164933", font=("Arial", 20, "bold", "underline"))
            else:
                btn.config(fg="black", font=("Arial", 20, "bold"))
