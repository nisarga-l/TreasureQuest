import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from PIL import Image, ImageTk

from theme import apply_background
from progress import load_progress, CHARACTER_REQUIREMENTS, unlock_character
from levels import LEVELS

IMAGE_FOLDER = Path(__file__).parent / "assets" / "characters"

HEROES = [
    ("Mira the Explorer", "mira.png", "#2BADE0"),
    ("Luna the Star Mage", "luna.png", "#974BE0"),
    ("Ruby the Brave", "ruby.png", "#E04B75"),
]


def clear_screen(root):
    root.unbind("<KeyPress>")
    for widget in root.winfo_children():
        widget.destroy()
    # Keep the original temple background unchanged.
    apply_background(root)


def character_selection(root):
    clear_screen(root)
    data = load_progress()
    root.hero_images = []

    panel = tk.Frame(root, bg="#140B2D", padx=20, pady=15,
                     highlightbackground="#FFD700", highlightthickness=2)
    panel.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(panel, text="CHOOSE YOUR HERO", font=("Georgia", 27, "bold"),
             bg="#140B2D", fg="#FFD700").pack(pady=8)
    tk.Label(panel, text=f"COIN WALLET: {data['coins']:,}",
             font=("Arial", 15, "bold"), bg="#140B2D",
             fg="#FFD875").pack(pady=5)

    cards = tk.Frame(panel, bg="#140B2D")
    cards.pack(pady=10)

    for name, filename, color in HEROES:
        unlocked = name in data["unlocked_characters"]
        price = CHARACTER_REQUIREMENTS[name]
        card = tk.Frame(cards, bg="#30264D", padx=8, pady=8)
        card.pack(side="left", padx=8)

        try:
            image = Image.open(IMAGE_FOLDER / filename)
            image.thumbnail((150, 180))
            photo = ImageTk.PhotoImage(image)
            root.hero_images.append(photo)
            tk.Label(card, image=photo, bg="#30264D").pack(pady=5)
        except (OSError, ValueError):
            tk.Label(card, text="Image not found", bg="#30264D",
                     fg="white", width=18, height=8).pack()

        tk.Label(card, text=name, bg="#30264D", fg="white",
                 font=("Arial", 11, "bold"), wraplength=160).pack(pady=5)

        if unlocked:
            status = "FREE CHARACTER" if price == 0 else "UNLOCKED"
            button_text = "SELECT"
        elif name == "Luna the Star Mage":
            status = "UNLOCK AT LEVEL 10"
            button_text = "LOCKED"
        else:
            status = f"PRICE: {price:,} COINS"
            button_text = f"UNLOCK ({price:,})"
        tk.Label(card, text=status, bg="#30264D",
                 fg="#65FF9D" if unlocked else "#FFB6C8",
                 font=("Arial", 10, "bold")).pack(pady=5)

        def choose_character(hero=name):
            latest = load_progress()
            if hero in latest["unlocked_characters"]:
                level_selection(root, hero)
                return
            if hero == "Luna the Star Mage":
                messagebox.showinfo(
                    "Hero Locked",
                    "Complete Level 10 to unlock Luna the Star Mage.",
                    parent=root)
                return
            price_needed = CHARACTER_REQUIREMENTS[hero]
            if latest["coins"] < price_needed:
                messagebox.showinfo(
                    "Not Enough Coins",
                    f"{hero} costs {price_needed:,} coins.\\n"
                    f"You have {latest['coins']:,} coins.\\n\\n"
                    f"You need {price_needed-latest['coins']:,} more coins.",
                    parent=root)
                return
            if not messagebox.askyesno(
                    "Unlock Character",
                    f"Spend {price_needed:,} coins to unlock {hero}?",
                    parent=root):
                return
            success, message, _ = unlock_character(hero)
            messagebox.showinfo("Character Unlock", message, parent=root)
            if success:
                character_selection(root)

        tk.Button(card, text=button_text,
                  bg=color if unlocked else "#A66A18", fg="white",
                  width=15, font=("Arial", 10, "bold"),
                  command=choose_character, cursor="hand2",
                  state=("disabled" if name == "Luna the Star Mage" and not unlocked
                         else "normal")).pack(pady=8)

    tk.Button(panel, text="MAIN MENU", width=20, bg="#7545D8",
              fg="white", font=("Arial", 11, "bold"),
              command=lambda: back_to_menu(root),
              cursor="hand2").pack(pady=8)


def level_selection(root, hero):
    clear_screen(root)
    data = load_progress()
    highest = max(1, int(data.get("highest_level", 1)))
    completed = set(data.get("completed_levels", []))

    panel = tk.Frame(root, bg="#140B2D", highlightbackground="#FFD700",
                     highlightthickness=3, padx=14, pady=10)
    panel.place(relx=0.5, rely=0.5, anchor="center",
                width=850, height=700)

    tk.Label(panel, text="✦ STARLIGHT ADVENTURE ✦",
             font=("Georgia", 25, "bold"), bg="#140B2D",
             fg="#FFD875").pack(pady=(8, 2))
    info = tk.Label(panel, text=f"Hero: {hero}     ✦     Coins: {data['coins']:,}",
                    font=("Arial", 12, "bold"), bg="#140B2D", fg="white")
    info.pack(pady=3)
    tk.Label(panel, text="Follow the magical path to your next treasure!",
             font=("Georgia", 11, "italic"), bg="#140B2D",
             fg="#D5A7FF").pack(pady=4)

    map_area = tk.Frame(panel, bg="#140B2D")
    map_area.pack(fill="both", expand=True, padx=8, pady=5)
    canvas = tk.Canvas(map_area, bg="#1C1040", highlightthickness=2,
                       highlightbackground="#A879DB")
    scrollbar = tk.Scrollbar(map_area, orient="vertical",
                             command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    items = list(LEVELS.items())
    spacing = 155
    map_height = max(540, len(items) * spacing + 100)
    canvas.configure(scrollregion=(0, 0, 700, map_height))

    positions = []
    for index, (number, details) in enumerate(items):
        x = 205 if index % 2 == 0 else 495
        y = 75 + index * spacing
        positions.append((x, y))

    # Winding golden path behind the level crystals.
    for i in range(len(positions) - 1):
        x1, y1 = positions[i]
        x2, y2 = positions[i + 1]
        canvas.create_line(x1, y1, x2, y2, fill="#6D4B9E",
                           width=19, smooth=True)
        canvas.create_line(x1, y1, x2, y2, fill="#FFD875",
                           width=5, smooth=True)

    for index, (number, details) in enumerate(items):
        x, y = positions[index]
        unlocked = number <= highest
        done = number in completed
        current = number == highest and not done

        if done:
            fill, state_text = "#247A69", "COMPLETED"
            stars = "★ ★ ★"
        elif unlocked:
            fill, state_text = "#7545D8", "TAP TO PLAY"
            stars = "✦"
        else:
            fill, state_text = "#51485F", "LOCKED"
            stars = "🔒"

        tags = (f"level_{number}",)
        if current:
            canvas.create_oval(x-54, y-54, x+54, y+54,
                               fill="#FFD875", outline="#FFF2B5",
                               width=3, tags=tags)
        canvas.create_oval(x-43, y-43, x+43, y+43,
                           fill=fill, outline="#FFD875",
                           width=4, tags=tags)
        canvas.create_text(x, y-9, text=str(number), fill="white",
                           font=("Georgia", 22, "bold"), tags=tags)
        canvas.create_text(x, y+18, text=stars, fill="#FFE7A0",
                           font=("Arial", 10, "bold"), tags=tags)
        canvas.create_text(x, y+61, text=details["name"],
                           fill="#FFD875", font=("Georgia", 12, "bold"))
        canvas.create_text(x, y+82, text=state_text,
                           fill="white", font=("Arial", 9, "bold"))

        if current:
            canvas.create_text(x+65, y-2, text="➤",
                               fill="#FFFFFF", font=("Arial", 26, "bold"))

        if unlocked:
            def open_level(event, level_number=number):
                from maze import start_maze
                start_maze(root, hero, level_number)
            canvas.tag_bind(tags[0], "<Button-1>", open_level)
            canvas.tag_bind(tags[0], "<Enter>",
                            lambda event: canvas.config(cursor="hand2"))
            canvas.tag_bind(tags[0], "<Leave>",
                            lambda event: canvas.config(cursor=""))

    # Scroll close to the currently unlocked level when the map opens.
    if highest in LEVELS:
        current_index = list(LEVELS.keys()).index(highest)
        target_y = 75 + current_index * spacing
        canvas.yview_moveto(max(0, min(1, (target_y - 120) / map_height)))

    buttons = tk.Frame(panel, bg="#140B2D")
    buttons.pack(pady=(4, 7))
    tk.Button(buttons, text="CHANGE HERO", font=("Arial", 11, "bold"),
              bg="#2585C5", fg="white", width=16,
              command=lambda: character_selection(root),
              cursor="hand2").pack(side="left", padx=8)
    tk.Button(buttons, text="MAIN MENU", font=("Arial", 11, "bold"),
              bg="#7545D8", fg="white", width=16,
              command=lambda: back_to_menu(root),
              cursor="hand2").pack(side="left", padx=8)


def back_to_menu(root):
    from main import show_welcome
    show_welcome(root)
