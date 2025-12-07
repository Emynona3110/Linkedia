import customtkinter as ctk
from PIL import Image

from utils.theme import get_mode

CARD_CORNER_RADIUS = 10
CARD_PADDING_X = 4
CARD_PADDING_Y = 4
ICON_SIZE = (20, 20)
DESCRIPTION_MAX_LENGTH = 140
SCORE_PREFIX = "Score : "
CLOSE_TEXT = "×"
CLOSE_FONT_SIZE = 20


class ResultCard:
    def __init__(self, parent, row: int, index: int, score: float, entry: dict,
                 on_open, on_delete, on_select):
        self.index = index
        self.entry = entry
        self.score = score
        self.on_open = on_open
        self.on_delete = on_delete
        self.on_select = on_select

        self.frame = ctk.CTkFrame(parent, corner_radius=CARD_CORNER_RADIUS)
        self.frame.grid(row=row, column=0, padx=CARD_PADDING_X, pady=CARD_PADDING_Y, sticky="ew")
        self.frame.grid_columnconfigure(0, weight=1)

        self.icon_image = None
        icon_path = entry.get("icon")

        if icon_path:
            try:
                img = Image.open(icon_path).convert("RGBA")
                self.icon_image = ctk.CTkImage(
                    light_image=img,
                    dark_image=img,
                    size=ICON_SIZE,
                )
            except Exception:
                self.icon_image = None

        title = entry.get("title") or entry.get("url") or ""
        description = entry.get("description") or ""

        self.title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.title_frame.grid(row=0, column=0, padx=10, pady=(6, 0), sticky="w")
        self.title_frame.grid_columnconfigure(1, weight=1)

        if self.icon_image:
            self.icon_label = ctk.CTkLabel(
                self.title_frame,
                image=self.icon_image,
                text="",
                width=ICON_SIZE[0],
                height=ICON_SIZE[1],
            )
            self.icon_label.grid(row=0, column=0, padx=(0, 8), sticky="w")

        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text=title,
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.title_label.grid(row=0, column=1, sticky="w")

        self.desc_label = None
        if description:
            short_desc = description.strip()
            if len(short_desc) > DESCRIPTION_MAX_LENGTH:
                short_desc = short_desc[: DESCRIPTION_MAX_LENGTH - 3] + "..."
            self.desc_label = ctk.CTkLabel(
                self.frame,
                text=short_desc,
                anchor="w",
                font=ctk.CTkFont(size=10),
            )
            self.desc_label.grid(row=1, column=0, padx=10, pady=(0, 6), sticky="w")

        self.score_label = ctk.CTkLabel(
            self.frame,
            text=f"{SCORE_PREFIX}{score:.1f}",
            anchor="w",
            font=ctk.CTkFont(size=10),
        )
        self.score_label.grid(row=2, column=0, padx=10, pady=(0, 6), sticky="w")

        self.close_label = ctk.CTkLabel(
            self.frame,
            text=CLOSE_TEXT,
            width=12,
            font=ctk.CTkFont(size=CLOSE_FONT_SIZE),
            text_color=("gray50", "gray50"),
        )
        self.close_label.grid(row=0, column=1, padx=8, pady=6, sticky="ne")

        def on_enter(e):
            mode = get_mode()
            self.close_label.configure(text_color="white" if mode == "Dark" else "black")

        def on_leave(e):
            self.close_label.configure(text_color=("gray50", "gray50"))

        self.close_label.bind("<Enter>", on_enter)
        self.close_label.bind("<Leave>", on_leave)
        self.close_label.bind("<Button-1>", lambda e: self.on_delete(self.entry["url"]))

        def on_click(event):
            self.on_open(self.index)

        binds = [
            self.frame,
            self.title_frame,
            self.title_label,
            self.score_label,
        ]

        for w in binds:
            w.bind("<Button-1>", on_click)
            w.bind("<Double-Button-1>", on_click)

        if self.icon_image:
            self.icon_label.bind("<Button-1>", on_click)
            self.icon_label.bind("<Double-Button-1>", on_click)

        if self.desc_label:
            self.desc_label.bind("<Button-1>", on_click)
            self.desc_label.bind("<Double-Button-1>", on_click)

    def set_selected(self, selected: bool):
        if selected:
            self.frame.configure(fg_color=("gray80", "gray25"))
        else:
            self.frame.configure(fg_color=("gray90", "gray15"))
