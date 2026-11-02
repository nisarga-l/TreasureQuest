
import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk, ImageOps

BACKGROUND = Path(__file__).parent / "assets" / "temple_bg.png"


def apply_background(root):
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()

    root.attributes("-fullscreen", True)
    root.configure(bg="#160d30")

    if BACKGROUND.exists():
        image = Image.open(BACKGROUND).convert("RGB")
        image = ImageOps.fit(
            image,
            (width, height),
            method=Image.Resampling.LANCZOS
        )

        photo = ImageTk.PhotoImage(image)

        label = tk.Label(
            root,
            image=photo,
            borderwidth=0
        )
        label.image = photo
    else:
        label = tk.Label(
            root,
            bg="#160d30"
        )

    label.place(
        x=0,
        y=0,
        relwidth=1,
        relheight=1
    )

    return label
