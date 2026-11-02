
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from PIL import Image, ImageTk

from theme import apply_background
from progress import (
    load_progress,
    CHARACTER_REQUIREMENTS,
    unlock_character,
)
from levels import LEVELS

IMAGE_FOLDER = Path(__file__).parent / "assets" / "characters"

HEROES = [
    ("Mira the Explorer", "mira.png", "#2BADE0"),
    ("Luna the Star Mage", "luna.png", "#974BE0"),
    ("Ruby the Brave", "ruby.png", "#E04B75"),
]


def clear_screen(root):
    root.unbind_all("<MouseWheel>")
    root.unbind_all("<Button-4>")
    root.unbind_all("<Button-5>")
    root.unbind("<KeyPress>")

    for widget in root.winfo_children():
        widget.destroy()

    apply_background(root)


# --------------------------------------------------
# CHARACTER SELECTION
# --------------------------------------------------

def character_selection(root):
    clear_screen(root)

    data = load_progress()
    root.hero_images = []

    panel = tk.Frame(
        root,
        bg="#140B2D",
        padx=25,
        pady=15
    )
    panel.place(
        relx=0.5,
        rely=0.5,
        anchor="center"
    )

    tk.Label(
        panel,
        text="✦ CHOOSE YOUR HERO ✦",
        font=("Georgia", 29, "bold"),
        bg="#140B2D",
        fg="#FFD875"
    ).pack(pady=8)

    tk.Label(
        panel,
        text=f"✧ COIN WALLET: {data['coins']:,} ✧",
        font=("Arial", 14, "bold"),
        bg="#140B2D",
        fg="#FFD875"
    ).pack(pady=5)

    tk.Label(
        panel,
        text="Choose your magical adventure companion",
        font=("Georgia", 12, "italic"),
        bg="#140B2D",
        fg="#D5A7FF"
    ).pack(pady=8)

    cards = tk.Frame(panel, bg="#140B2D")
    cards.pack(pady=15)

    for name, filename, color in HEROES:

        unlocked = name in data["unlocked_characters"]
        price = CHARACTER_REQUIREMENTS[name]

        # Separate character card with its own border
        card = tk.Frame(
            cards,
            bg="#24143F",
            padx=12,
            pady=12,
            highlightbackground=color,
            highlightthickness=3
        )
        card.pack(side="left", padx=12, pady=8)

        image_path = IMAGE_FOLDER / filename

        try:
            image = Image.open(image_path)
            image.thumbnail((145, 175))

            photo = ImageTk.PhotoImage(image)
            root.hero_images.append(photo)

            tk.Label(
                card,
                image=photo,
                bg="#24143F"
            ).pack(pady=8)

        except (OSError, ValueError):
            tk.Label(
                card,
                text="Image not found",
                bg="#24143F",
                fg="white",
                width=17,
                height=8
            ).pack()

        tk.Label(
            card,
            text=name,
            bg="#24143F",
            fg="#FFD875",
            font=("Georgia", 11, "bold"),
            wraplength=155
        ).pack(pady=8)

        if unlocked:
            status = "✦ UNLOCKED ✦"
            button_text = "SELECT HERO"
            button_color = color
            button_state = "normal"

        elif name == "Luna the Star Mage":
            status = "UNLOCK AT LEVEL 10"
            button_text = "LOCKED"
            button_color = "#51485F"
            button_state = "disabled"

        else:
            status = f"PRICE: {price:,} COINS"
            button_text = f"UNLOCK ({price:,})"
            button_color = "#A66A18"
            button_state = "normal"

        tk.Label(
            card,
            text=status,
            bg="#24143F",
            fg="#65FF9D" if unlocked else "#FFB6C8",
            font=("Arial", 10, "bold")
        ).pack(pady=7)

        def choose_character(hero=name):
            latest = load_progress()

            if hero in latest["unlocked_characters"]:
                level_selection(root, hero)
                return

            if hero == "Luna the Star Mage":
                messagebox.showinfo(
                    "Hero Locked",
                    "Complete Level 10 to unlock Luna!",
                    parent=root
                )
                return

            price_needed = CHARACTER_REQUIREMENTS[hero]

            if latest["coins"] < price_needed:
                messagebox.showinfo(
                    "Not Enough Coins",
                    f"You need {price_needed - latest['coins']:,} "
                    "more coins.",
                    parent=root
                )
                return

            confirm = messagebox.askyesno(
                "Unlock Hero",
                f"Unlock {hero} for {price_needed:,} coins?",
                parent=root
            )

            if confirm:
                success, message, _ = unlock_character(hero)

                messagebox.showinfo(
                    "Character",
                    message,
                    parent=root
                )

                if success:
                    character_selection(root)

        tk.Button(
            card,
            text=button_text,
            bg=button_color,
            activebackground="#A77BFF",
            fg="white",
            activeforeground="white",
            font=("Georgia", 10, "bold"),
            width=16,
            height=2,
            relief="raised",
            bd=2,
            cursor="hand2",
            state=button_state,
            command=choose_character
        ).pack(pady=10)

    tk.Button(
        panel,
        text="✦ MAIN MENU ✦",
        width=20,
        bg="#7545D8",
        fg="white",
        font=("Georgia", 11, "bold"),
        relief="raised",
        bd=3,
        command=lambda: back_to_menu(root),
        cursor="hand2"
    ).pack(pady=10)


# --------------------------------------------------
# CANDY CRUSH STYLE LEVEL MAP
# --------------------------------------------------

def level_selection(root, hero):
    clear_screen(root)

    data = load_progress()

    highest = max(
        1,
        int(data.get("highest_level", 1))
    )

    completed = set(data.get("completed_levels", []))
    stars_data = data.get("level_stars", {})

    items = sorted(LEVELS.items())

    panel = tk.Frame(
        root,
        bg="#140B2D",
        highlightbackground="#FFD700",
        highlightthickness=3,
        padx=14,
        pady=10
    )

    panel.place(
        relx=0.5,
        rely=0.5,
        anchor="center",
        relwidth=0.78,
        relheight=0.88
    )

    tk.Label(
        panel,
        text="✦ STARLIGHT ADVENTURE ✦",
        font=("Georgia", 25, "bold"),
        bg="#140B2D",
        fg="#FFD875"
    ).pack(pady=(8, 2))

    tk.Label(
        panel,
        text=f"Hero: {hero}     ✦     Coins: {data['coins']:,}",
        font=("Arial", 12, "bold"),
        bg="#140B2D",
        fg="white"
    ).pack(pady=3)

    tk.Label(
        panel,
        text="Follow the magical path to your next treasure!",
        font=("Georgia", 11, "italic"),
        bg="#140B2D",
        fg="#D5A7FF"
    ).pack(pady=4)

    map_area = tk.Frame(panel, bg="#140B2D")
    map_area.pack(
        fill="both",
        expand=True,
        padx=8,
        pady=5
    )

    canvas = tk.Canvas(
        map_area,
        bg="#1C1040",
        highlightthickness=2,
        highlightbackground="#A879DB",
        borderwidth=0,
        yscrollincrement=20
    )

    scrollbar = tk.Scrollbar(
        map_area,
        orient="vertical",
        command=canvas.yview
    )

    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    spacing = 155
    map_width = 760
    map_height = 130 + len(items) * spacing

    canvas.configure(
        scrollregion=(0, 0, map_width, map_height)
    )

    # Mouse-wheel scrolling
    def wheel_scroll(event):
        if event.delta:
            direction = -1 if event.delta > 0 else 1
            canvas.yview_scroll(direction * 3, "units")
        return "break"

    root.bind_all("<MouseWheel>", wheel_scroll)

    root.bind_all(
        "<Button-4>",
        lambda event: (
            canvas.yview_scroll(-3, "units"), "break"
        )[1]
    )

    root.bind_all(
        "<Button-5>",
        lambda event: (
            canvas.yview_scroll(3, "units"), "break"
        )[1]
    )

    # Winding path positions
    positions = []

    for index, (number, details) in enumerate(items):
        x = 220 if index % 2 == 0 else 520
        y = 75 + index * spacing
        positions.append((x, y))

    # Draw path
    for index in range(len(positions) - 1):
        x1, y1 = positions[index]
        x2, y2 = positions[index + 1]

        canvas.create_line(
            x1, y1, x2, y2,
            fill="#7650A9",
            width=20,
            smooth=True
        )

        canvas.create_line(
            x1, y1, x2, y2,
            fill="#FFD875",
            width=5,
            smooth=True
        )

    # Draw levels
    for index, (number, details) in enumerate(items):

        x, y = positions[index]

        unlocked = number <= highest
        done = number in completed
        current = number == highest and not done

        tag = f"level_{number}"

        if done:
            fill = "#247A69"
            status = "COMPLETED"
            earned_stars = int(
                stars_data.get(str(number), 3)
            )
            star_text = "★ " * max(1, earned_stars)

        elif unlocked:
            fill = "#7545D8"
            status = "TAP TO PLAY"
            star_text = "✦"

        else:
            fill = "#51485F"
            status = "LOCKED"
            star_text = "LOCK"

        if current:
            canvas.create_oval(
                x - 53, y - 53,
                x + 53, y + 53,
                fill="#FFD875",
                outline="#FFF2B5",
                width=3
            )

        # Main level circle
        canvas.create_oval(
            x - 43, y - 43,
            x + 43, y + 43,
            fill=fill,
            outline="#FFD875",
            width=4,
            tags=(tag,)
        )

        canvas.create_text(
            x, y - 9,
            text=str(number),
            fill="white",
            font=("Georgia", 22, "bold"),
            tags=(tag,)
        )

        canvas.create_text(
            x, y + 18,
            text=star_text,
            fill="#FFE7A0",
            font=("Arial", 10, "bold"),
            tags=(tag,)
        )

        canvas.create_text(
            x, y + 61,
            text=details["name"],
            fill="#FFD875",
            font=("Georgia", 12, "bold"),
            tags=(tag,)
        )

        if number == 10:
            canvas.create_text(
                x, y + 84,
                text="UNLOCK LUNA THE STAR MAGE!",
                fill="#FFB6E6",
                font=("Arial", 10, "bold")
            )

            canvas.create_text(
                x, y + 105,
                text=status,
                fill="white",
                font=("Arial", 9, "bold")
            )
        else:
            canvas.create_text(
                x, y + 84,
                text=status,
                fill="white",
                font=("Arial", 9, "bold")
            )

        # Current level marker
        if current:
            canvas.create_text(
                x + 67, y - 2,
                text="➤",
                fill="white",
                font=("Arial", 26, "bold")
            )

        # Bind click to the entire level circle.
        if unlocked:

            def open_level(event, level_number=number):
                from maze import start_maze
                start_maze(root, hero, level_number)
                return "break"

            canvas.tag_bind(
                tag,
                "<Button-1>",
                open_level
            )

            canvas.tag_bind(
                tag,
                "<Enter>",
                lambda event: canvas.config(cursor="hand2")
            )

            canvas.tag_bind(
                tag,
                "<Leave>",
                lambda event: canvas.config(cursor="")
            )

    # Scroll to the current level
    canvas.update_idletasks()

    current_index = next(
        (
            index for index, (number, details)
            in enumerate(items)
            if number == highest
        ),
        0
    )

    target_y = 75 + current_index * spacing

    visible_height = max(1, canvas.winfo_height())
    scrollable_height = max(
        1, map_height - visible_height
    )

    scroll_position = (
        target_y - visible_height * 0.40
    ) / scrollable_height

    canvas.yview_moveto(
        max(0.0, min(1.0, scroll_position))
    )

    buttons = tk.Frame(panel, bg="#140B2D")
    buttons.pack(pady=(4, 7))

    tk.Button(
        buttons,
        text="CHANGE HERO",
        font=("Arial", 11, "bold"),
        bg="#2585C5",
        fg="white",
        width=16,
        command=lambda: character_selection(root),
        cursor="hand2"
    ).pack(side="left", padx=8)

    tk.Button(
        buttons,
        text="MAIN MENU",
        font=("Arial", 11, "bold"),
        bg="#7545D8",
        fg="white",
        width=16,
        command=lambda: back_to_menu(root),
        cursor="hand2"
    ).pack(side="left", padx=8)


# --------------------------------------------------
# MAIN MENU
# --------------------------------------------------

def back_to_menu(root):
    from main import show_welcome
    show_welcome(root)
