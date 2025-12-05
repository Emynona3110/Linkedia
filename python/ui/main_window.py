import webbrowser
from tkinter import messagebox

import customtkinter as ctk

from services.scraper_service import scrape
from core.data_manager import add_or_update_entry, list_entries, get_entry, delete_entry
from core.search_engine import search
from core.normalization import normalize_entry
from ui.cards import ResultCard
from ui.dialogs import ask_delete_dialog, ask_error_dialog


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

    def update_card_styles(self):
        for idx, card in enumerate(self.result_cards):
            card.set_selected(idx == self.selected_index)

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
            data = normalize_entry(raw)
            self.current_results.append((0.0, data))
            index = len(self.current_results) - 1
            card = ResultCard(
                parent=self.results_container,
                row=index,
                index=index,
                score=0.0,
                entry=data,
                on_open=self.open_selected_from_card,
                on_delete=self.ask_delete_url,
                on_select=self.select_card,
            )
            self.result_cards.append(card)

        self.update_card_styles()
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

        if isinstance(data, dict) and "error" in data:
            if data["error"] == "not_found":
                ask_error_dialog(self.root, "L’URL n’existe pas ou est inaccessible.")
                return
            if data["error"] == "scrape_failed":
                ask_error_dialog(self.root, "Impossible de scraper cette URL.")
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
            data = normalize_entry(entry)
            self.current_results.append((score, data))
            index = len(self.current_results) - 1
            card = ResultCard(
                parent=self.results_container,
                row=index,
                index=index,
                score=score,
                entry=data,
                on_open=self.open_selected_from_card,
                on_delete=self.ask_delete_url,
                on_select=self.select_card,
            )
            self.result_cards.append(card)
        self.update_card_styles()
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

    def open_selected_from_card(self, index: int):
        self.select_card(index)
        self.open_selected()

    def open_selected(self, event=None):
        url = self.get_selected_url()
        if not url:
            return
        webbrowser.open(url)

    def select_card(self, index: int):
        if index < 0 or index >= len(self.current_results):
            return
        self.selected_index = index
        self.update_card_styles()

    def ask_delete_url(self, url: str):
        if not url:
            return
        ask_delete_dialog(self.root, url, self._confirm_delete)

    def _confirm_delete(self, url: str):
        if delete_entry(url):
            query = self.search_entry.get().strip()
            if query:
                self.search_query()
            else:
                self.refresh_list()
        else:
            messagebox.showerror("Erreur", "Impossible de supprimer.")
