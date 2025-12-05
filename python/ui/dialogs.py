import customtkinter as ctk


def ask_delete_dialog(root: ctk.CTk, url: str, on_confirm):
    if not url:
        return

    dialog = ctk.CTkToplevel(root)
    dialog.title("Confirmation")
    dialog.resizable(False, False)

    try:
        dialog._apply_appearance_mode()
        dialog._corner_radius = 8
        dialog._border_width = 0
    except Exception:
        pass

    dialog.update_idletasks()
    dialog.geometry("300x120")

    x = root.winfo_x() + (root.winfo_width() // 2) - 150
    y = root.winfo_y() + (root.winfo_height() // 2) - 60
    dialog.geometry(f"300x120+{x}+{y}")

    dialog.grab_set()

    label = ctk.CTkLabel(
        dialog,
        text="Voulez-vous vraiment supprimer ce site ?",
        justify="center",
        anchor="center",
        wraplength=260,
    )
    label.pack(pady=(15, 10))

    cancel_button = ctk.CTkButton(
        dialog,
        text="Annuler",
        width=95,
        command=dialog.destroy,
    )
    cancel_button.pack(side="left", padx=(40, 10), pady=(0, 15))

    delete_button = ctk.CTkButton(
        dialog,
        text="Supprimer",
        width=95,
        fg_color="#b33939",
        hover_color="#922b21",
        command=lambda: _confirm_and_close(dialog, url, on_confirm),
    )
    delete_button.pack(side="right", padx=(10, 40), pady=(0, 15))


def _confirm_and_close(dialog: ctk.CTkToplevel, url: str, on_confirm):
    try:
        on_confirm(url)
    finally:
        dialog.destroy()


def ask_error_dialog(root: ctk.CTk, message: str):
    dialog = ctk.CTkToplevel(root)
    dialog.title("Erreur")
    dialog.resizable(False, False)

    try:
        dialog._apply_appearance_mode()
        dialog._corner_radius = 8
        dialog._border_width = 0
    except Exception:
        pass

    dialog.update_idletasks()
    dialog.geometry("300x120")

    x = root.winfo_x() + (root.winfo_width() // 2) - 150
    y = root.winfo_y() + (root.winfo_height() // 2) - 60
    dialog.geometry(f"300x120+{x}+{y}")

    dialog.grab_set()

    label = ctk.CTkLabel(
        dialog,
        text=message,
        justify="center",
        anchor="center",
        wraplength=260,
    )
    label.pack(pady=(20, 15))

    ok_button = ctk.CTkButton(
        dialog,
        text="OK",
        width=120,
        command=dialog.destroy,
    )
    ok_button.pack(pady=(0, 10))
