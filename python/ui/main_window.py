import webbrowser
from tkinter import messagebox
import threading
import customtkinter as ctk

from services.scraper_service import scrape
from core.data_manager import add_or_update_entry, list_entries, get_entry, delete_entry
from core.search_engine import search
from core.normalization import normalize_entry
from core.paths import ICON_DIR

from ui.cards import ResultCard
from ui.dialogs import ask_delete_dialog, ask_error_dialog

WINDOW_GEOMETRY = "1100x580"

class LinkediaApp:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("Linkedia")
        self.root.geometry(WINDOW_GEOMETRY)

        self.current_results = []
        self.result_cards = []
        self.selected_index = None

        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure((0, 1, 2), weight=1)

        self.sidebar_frame = ctk.CTkFrame(self.root, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Linkedia",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.rescrape_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Re-scraper tous",
            command=self.rescrape_all
        )
        self.rescrape_button.grid(row=1, column=0, padx=20, pady=(10, 10), sticky="ew")

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
        self.content_frame.grid_rowconfigure(3, weight=0)
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

        self.spinner = ctk.CTkProgressBar(self.content_frame, mode="indeterminate")
        self.spinner.grid(row=3, column=0, pady=10)
        self.spinner.grid_remove()

        self.refresh_list()

    def run_async(self, fn):
        thread = threading.Thread(target=fn)
        thread.daemon = True
        thread.start()

    def start_loading(self):
        self.spinner.grid()
        self.spinner.start()
        self.add_button.configure(state="disabled")
        self.search_button.configure(state="disabled")
        self.rescrape_button.configure(state="disabled")

    def stop_loading(self):
        self.spinner.stop()
        self.spinner.grid_remove()
        self.add_button.configure(state="normal")
        self.search_button.configure(state="normal")
        self.rescrape_button.configure(state="normal")

    def rescrape_all(self):
        def task():
            try:
                entries = list_entries()  # {hash: entry}
                for entry in entries.values():
                    real_url = entry.get("url")
                    if not real_url:
                        continue
                    real_url = self.normalize_url(real_url)
                    data = scrape(real_url)
                    add_or_update_entry(data)
                self.root.after(0, self.refresh_list)
            finally:
                self.root.after(0, self.stop_loading)

        self.start_loading()
        self.run_async(task)

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
        except:
            pass

    def refresh_list(self):
        entries = list_entries()
        self.clear_results()

        items = list(entries.values())[::-1]
        for raw in items:
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

    def normalize_url(self, url: str) -> str:
        url = url.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        return url

    def add_url(self):
        def task():
            try:
                self._add_url_internal()
            finally:
                self.root.after(0, self.stop_loading)

        self.start_loading()
        self.run_async(task)

    def _add_url_internal(self):
        url = self.url_entry.get().strip()
        if not url:
            self.root.after(0, lambda: messagebox.showwarning("Erreur", "Veuillez entrer une URL."))
            return

        url = self.normalize_url(url)
        data = scrape(url)

        if isinstance(data, dict) and "error" in data:
            if data["error"] == "not_found":
                self.root.after(0, lambda: ask_error_dialog(self.root, "L’URL n’existe pas ou est inaccessible."))
                return
            if data["error"] == "scrape_failed":
                self.root.after(0, lambda: ask_error_dialog(self.root, "Impossible de scraper cette URL."))
                return

        add_or_update_entry(data)
        self.root.after(0, lambda: self.url_entry.delete(0, "end"))

        query = self.search_entry.get().strip()
        self.root.after(0, self.search_query if query else self.refresh_list)

    def search_query(self):
        def task():
            try:
                q = self.search_entry.get().strip()
                if not q:
                    self.root.after(0, self.refresh_list)
                    return
                results = search(q)
                self.root.after(0, lambda: self._display_search_results(results))
            finally:
                self.root.after(0, self.stop_loading)

        self.start_loading()
        self.run_async(task)

    def _display_search_results(self, results):
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
        return entry.get("url")

    def open_selected_from_card(self, index: int):
        self.select_card(index)
        self.open_selected()

    def open_selected(self, event=None):
        url = self.get_selected_url()
        if url:
            webbrowser.open(url)

    def select_card(self, index: int):
        if 0 <= index < len(self.current_results):
            self.selected_index = index
            self.update_card_styles()

    def ask_delete_url(self, url: str):
        if url:
            ask_delete_dialog(self.root, url, self._confirm_delete)

    def _confirm_delete(self, url: str):
        entry = get_entry(url)

        if delete_entry(url):
            if entry:
                icon_path = entry.get("icon")
                if icon_path:
                    filename = icon_path.split("/")[-1]
                    abs_icon = ICON_DIR / filename
                    try:
                        if abs_icon.exists():
                            abs_icon.unlink()
                    except:
                        pass

            q = self.search_entry.get().strip()
            self.search_query() if q else self.refresh_list()
        else:
            messagebox.showerror("Erreur", "Impossible de supprimer.")
