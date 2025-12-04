import webbrowser
from tkinter import messagebox

import customtkinter as ctk

from scraper import scrape
from storage import add_or_update_entry, delete_entry, list_entries, get_entry
from search import search


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class LinkediaApp:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("Linkedia")
        self.root.geometry("1100x580")

        self.current_results = []
        self.result_cards = []
        self.selected_index = None

        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure((0, 1, 2), weight=1)

        self.sidebar_frame = ctk.CTkFrame(self.root, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Linkedia",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.appearance_mode_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Apparence :",
            anchor="w",
        )
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))

        self.appearance_mode_optionmenu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode_event,
        )
        self.appearance_mode_optionmenu.grid(row=7, column=0, padx=20, pady=(10, 10))
        self.appearance_mode_optionmenu.set("System")

        self.content_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(2, weight=1)

        self.add_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.add_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.add_frame.grid_columnconfigure(1, weight=1)

        self.add_title_label = ctk.CTkLabel(
            self.add_frame,
            text="Ajouter / Mettre à jour un site",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.add_title_label.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 5))

        self.url_label = ctk.CTkLabel(self.add_frame, text="URL :")
        self.url_label.grid(row=1, column=0, padx=(0, 10), sticky="w")

        self.url_entry = ctk.CTkEntry(self.add_frame)
        self.url_entry.grid(row=1, column=1, padx=(0, 10), pady=(0, 5), sticky="ew")
        self.url_entry.bind("<Return>", lambda e: self.add_url())

        self.add_button = ctk.CTkButton(
            self.add_frame,
            text="Ajouter / Mettre à jour",
            command=self.add_url,
        )
        self.add_button.grid(row=1, column=2, sticky="e")

        self.search_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.search_frame.grid_columnconfigure(0, weight=1)

        self.search_title_label = ctk.CTkLabel(
            self.search_frame,
            text="Rechercher dans la base",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.search_title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))

        self.search_entry = ctk.CTkEntry(self.search_frame)
        self.search_entry.grid(row=1, column=0, padx=(0, 10), sticky="ew")
        self.search_entry.bind("<Return>", lambda e: self.search_query())

        self.search_button = ctk.CTkButton(
            self.search_frame,
            text="Chercher",
            command=self.search_query,
        )
        self.search_button.grid(row=1, column=1, sticky="e")

        self.results_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.results_frame.grid(row=2, column=0, sticky="nsew")
        self.results_frame.grid_columnconfigure(0, weight=1)
        self.results_frame.grid_rowconfigure(1, weight=1)

        self.results_label = ctk.CTkLabel(
            self.results_frame,
            text="Résultats",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.results_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.results_container = ctk.CTkScrollableFrame(self.results_frame)
        self.results_container.grid(row=1, column=0, sticky="nsew")
        self.results_container.grid_columnconfigure(0, weight=1)

        self.refresh_list()

    def change_appearance_mode_event(self, new_mode: str):
        ctk.set_appearance_mode(new_mode)

    def clear_results(self):
        for widget in self.results_container.winfo_children():
            widget.destroy()
        self.result_cards = []
        self.current_results = []
        self.selected_index = None

    def normalize_entry(self, raw):
        if isinstance(raw, dict):
            title = raw.get("title") or raw.get("url") or ""
            url = raw.get("url") or ""
            description = raw.get("description") or ""
            return {"title": title, "url": url, "description": description}

        key = str(raw)
        entry = get_entry(key)
        if isinstance(entry, dict):
            return self.normalize_entry(entry)

        return {"title": key, "url": key, "description": ""}

    def create_result_card(self, index: int, score: float, entry: dict):
        card = ctk.CTkFrame(self.results_container, corner_radius=10)
        card.grid(row=index, column=0, padx=4, pady=4, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        title = entry.get("title") or entry.get("url") or ""
        description = entry.get("description") or ""

        title_label = ctk.CTkLabel(
            card,
            text=title,
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        title_label.grid(row=0, column=0, padx=10, pady=(6, 0), sticky="w")

        if description:
            short_desc = description.strip()
            if len(short_desc) > 140:
                short_desc = short_desc[:137] + "..."
            desc_label = ctk.CTkLabel(
                card,
                text=short_desc,
                anchor="w",
                font=ctk.CTkFont(size=10),
            )
            desc_label.grid(row=1, column=0, padx=10, pady=(0, 6), sticky="w")

        score_label = ctk.CTkLabel(
            card,
            text=f"{score:.1f} %",
            anchor="w",
            font=ctk.CTkFont(size=10),
        )
        score_label.grid(row=2, column=0, padx=10, pady=(0, 6), sticky="w")

        close_label = ctk.CTkLabel(
            card,
            text="×",
            width=12,
            font=ctk.CTkFont(size=20),
            text_color=("gray50", "gray50"),
        )
        close_label.grid(row=0, column=1, padx=8, pady=6, sticky="ne")

        def on_enter(e):
            mode = ctk.get_appearance_mode()
            if mode == "Dark":
                close_label.configure(text_color="white")
            else:
                close_label.configure(text_color="black")

        def on_leave(e):
            close_label.configure(text_color=("gray50", "gray50"))

        close_label.bind("<Enter>", on_enter)
        close_label.bind("<Leave>", on_leave)
        close_label.bind("<Button-1>", lambda e, u=entry["url"]: self.ask_delete_url(u))

        def on_click(event):
            self.select_card(index)
            self.open_selected()

        for widget in (card, title_label):
            widget.bind("<Button-1>", on_click)
            widget.bind("<Double-Button-1>", on_click)

        if description:
            desc_label.bind("<Button-1>", on_click)
            desc_label.bind("<Double-Button-1>", on_click)

        score_label.bind("<Button-1>", lambda e: self.select_card(index))

        self.result_cards.append(card)
        self.update_card_styles()

    def update_card_styles(self):
        for idx, card in enumerate(self.result_cards):
            if idx == self.selected_index:
                card.configure(fg_color=("gray80", "gray25"))
            else:
                card.configure(fg_color=("gray90", "gray15"))

    def select_card(self, index: int):
        if index < 0 or index >= len(self.current_results):
            return
        self.selected_index = index
        self.update_card_styles()

    def _scroll_to_top(self):
        try:
            self.results_container._parent_canvas.yview_moveto(0)
        except Exception:
            pass

    def refresh_list(self):
        entries = list_entries()
        self.clear_results()

        values_iter = []
        if isinstance(entries, dict):
            values_iter = list(entries.values())[::-1]
        elif isinstance(entries, (list, tuple, set)):
            tmp = list(entries)
            if tmp and isinstance(tmp[0], dict):
                values_iter = tmp[::-1]
            elif tmp and isinstance(tmp[0], (list, tuple)) and len(tmp[0]) >= 2:
                values_iter = [e[1] for e in tmp[::-1]]
            else:
                values_iter = tmp[::-1]
        else:
            values_iter = [entries]

        for raw in values_iter:
            data = self.normalize_entry(raw)
            self.current_results.append((0.0, data))
            index = len(self.current_results) - 1
            self.create_result_card(index, 0.0, data)

        self._scroll_to_top()

    def add_url(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Erreur", "Veuillez entrer une URL.")
            return
        existing = get_entry(url)
        if existing:
            if not messagebox.askyesno(
                "Déjà indexé",
                "Cette URL existe déjà. Mettre à jour ?",
            ):
                return
        data = scrape(url)
        if not data:
            messagebox.showerror("Erreur", "Impossible de scraper l'URL.")
            return
        add_or_update_entry(data)
        self.url_entry.delete(0, "end")
        query = self.search_entry.get().strip()
        if query:
            self.search_query()
        else:
            self.refresh_list()

    def search_query(self):
        query = self.search_entry.get().strip()
        if not query:
            self.refresh_list()
            return
        results = search(query)
        self.clear_results()
        for score, entry in results:
            data = self.normalize_entry(entry)
            self.current_results.append((score, data))
            index = len(self.current_results) - 1
            self.create_result_card(index, score, data)
        self._scroll_to_top()

    def get_selected_url(self):
        if self.selected_index is None:
            messagebox.showwarning("Erreur", "Aucun élément sélectionné.")
            return None
        if self.selected_index < 0 or self.selected_index >= len(self.current_results):
            messagebox.showerror("Erreur", "Sélection invalide.")
            return None
        _, entry = self.current_results[self.selected_index]
        url = entry.get("url")
        if not url:
            messagebox.showerror("Erreur", "URL introuvable pour cette entrée.")
            return None
        return url

    def open_selected(self, event=None):
        url = self.get_selected_url()
        if not url:
            return
        webbrowser.open(url)

    def ask_delete_url(self, url: str):
        if not url:
            return

        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Confirmation")
        dialog.resizable(False, False)

        try:
            dialog._apply_appearance_mode()
            dialog._corner_radius = 8
            dialog._border_width = 0
        except:
            pass

        dialog.update_idletasks()
        dialog.geometry("300x120")

        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 150
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 60
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
            command=lambda: self._confirm_delete(dialog, url),
        )
        delete_button.pack(side="right", padx=(10, 40), pady=(0, 15))

    def _confirm_delete(self, dialog: ctk.CTkToplevel, url: str):
        try:
            if delete_entry(url):
                query = self.search_entry.get().strip()
                if query:
                    self.search_query()
                else:
                    self.refresh_list()
            else:
                messagebox.showerror("Erreur", "Impossible de supprimer.")
        finally:
            dialog.destroy()

    def delete_selected(self):
        url = self.get_selected_url()
        if not url:
            return
        self.ask_delete_url(url)


if __name__ == "__main__":
    root = ctk.CTk()
    app = LinkediaApp(root)
    root.mainloop()
