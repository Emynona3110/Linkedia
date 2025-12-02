import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

from scraper import scrape
from storage import add_or_update_entry, delete_entry, list_entries, get_entry
from search import search

class LinkediaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Linkedia")
        self.root.geometry("900x600")

        add_frame = ttk.LabelFrame(root, text="Ajouter / Mettre à jour un site")
        add_frame.pack(fill="x", padx=10, pady=10)

        self.url_entry = ttk.Entry(add_frame)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        add_button = ttk.Button(add_frame, text="Ajouter", command=self.add_url)
        add_button.pack(side="left", padx=5)

        search_frame = ttk.LabelFrame(root, text="Recherche")
        search_frame.pack(fill="x", padx=10, pady=10)

        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        search_button = ttk.Button(search_frame, text="Chercher", command=self.search_query)
        search_button.pack(side="left", padx=5)

        results_frame = ttk.LabelFrame(root, text="Résultats")
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.results_list = tk.Listbox(results_frame, font=("Segoe UI", 11))
        self.results_list.pack(fill="both", expand=True, padx=5, pady=5)
        self.results_list.bind("<Double-Button-1>", self.open_selected)

        delete_btn = ttk.Button(root, text="Supprimer le site sélectionné", command=self.delete_selected)
        delete_btn.pack(pady=5)

    def add_url(self):
        url = self.url_entry.get().strip()
        if not url:
            return messagebox.showwarning("Erreur", "Veuillez entrer une URL.")
        existing = get_entry(url)
        if existing:
            if not messagebox.askyesno("Déjà indexé", "Cette URL existe déjà. Mettre à jour ?"):
                return
        data = scrape(url)
        if not data:
            return messagebox.showerror("Erreur", "Impossible de scraper l'URL.")
        add_or_update_entry(data)
        messagebox.showinfo("Succès", "Site ajouté / mis à jour.")

    def search_query(self):
        query = self.search_entry.get().strip()
        if not query:
            return
        results = search(query)
        self.results_list.delete(0, tk.END)
        for score, entry in results:
            title = entry["title"] or entry["url"]
            self.results_list.insert(tk.END, f"{score}% │ {title} │ {entry['url']}")

    def open_selected(self, event=None):
        selection = self.results_list.curselection()
        if not selection:
            return
        text = self.results_list.get(selection[0])
        url = text.split("│")[-1].strip()
        webbrowser.open(url)

    def delete_selected(self):
        selection = self.results_list.curselection()
        if not selection:
            return messagebox.showwarning("Erreur", "Aucun élément sélectionné.")
        text = self.results_list.get(selection[0])
        url = text.split("│")[-1].strip()
        if delete_entry(url):
            messagebox.showinfo("Supprimé", "Entrée supprimée.")
            self.search_query()
        else:
            messagebox.showerror("Erreur", "Impossible de supprimer.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LinkediaApp(root)
    root.mainloop()
