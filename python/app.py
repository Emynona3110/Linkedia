import customtkinter as ctk
from ui.main_window import LinkediaApp

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

if __name__ == "__main__":
    root = ctk.CTk()
    app = LinkediaApp(root)
    root.mainloop()
