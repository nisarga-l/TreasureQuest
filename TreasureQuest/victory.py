import tkinter as tk
from tkinter import messagebox

from theme import apply_background
from progress import complete_level, get_total_coins, load_progress
from levels import LEVELS


def show_result(root, hero, score, steps, lives,
                won, level=1, collected_coins=0):
    root.unbind("<KeyPress>")
    for widget in root.winfo_children():
        widget.destroy()
    # Preserve the project's original temple background.
    apply_background(root)

    panel = tk.Frame(root, bg="#140B2D", padx=30, pady=15,
                     highlightbackground="#FFD700", highlightthickness=3)
    panel.place(relx=0.5, rely=0.5, anchor="center")

    heading = "LEVEL COMPLETED!" if won else "GAME OVER"
    tk.Label(panel, text=heading, font=("Georgia", 27, "bold"),
             fg="#FFD700" if won else "#FF6688",
             bg="#140B2D").pack(pady=7)
    tk.Label(panel, text=f"LEVEL {level}: {LEVELS[level]['name']}",
             font=("Georgia", 17, "bold"), fg="#D9B9FF",
             bg="#140B2D").pack(pady=5)

    stars = 3 if lives >= 3 else (2 if lives == 2 else 1)
    if won:
        tk.Label(panel, text="★ " * stars, font=("Georgia", 28, "bold"),
                 fg="#FFD875", bg="#140B2D").pack(pady=1)

    tk.Label(
        panel,
        text=(f"Hero: {hero}\nFinal Score: {score}\nSteps Taken: {steps}\n"
              f"Lives Remaining: {lives}\nMaze Coins Collected: {collected_coins}"),
        font=("Arial", 13), fg="white", bg="#140B2D",
        justify="center"
    ).pack(pady=8)

    def play_again():
        from maze import start_maze
        start_maze(root, hero, level)

    def change_hero():
        from game import character_selection
        character_selection(root)

    def main_menu():
        from main import show_welcome
        show_welcome(root)

    def level_map():
        from game import level_selection
        level_selection(root, hero)

    def make_button(text, command, color, state="normal"):
        return tk.Button(panel, text=text, command=command,
                         font=("Arial", 11, "bold"), bg=color,
                         fg="white", width=25, height=2,
                         cursor="hand2", state=state,
                         disabledforeground="#D0C7DA")

    next_button = None

    if won:
        tk.Label(panel, text="A MAGICAL TREASURE CHEST APPEARS!",
                 font=("Arial", 12, "bold"), fg="#FFD875",
                 bg="#140B2D").pack(pady=5)
        chest_icon = tk.Label(panel, text="🎁",
                              font=("Segoe UI Emoji", 38),
                              fg="#FFD700", bg="#140B2D")
        chest_icon.pack(pady=2)

        chest_claimed = level in load_progress()["completed_levels"]

        def open_chest():
            nonlocal chest_claimed
            if chest_claimed:
                messagebox.showinfo(
                    "TREASURE CHEST",
                    "This level's treasure has already been claimed.",
                    parent=root)
                return
            try:
                reward, unlocked = complete_level(
                    level, collected_coins, stars)
            except Exception as error:
                messagebox.showerror("REWARD ERROR", str(error), parent=root)
                return

            chest_claimed = True
            chest_button.config(text="REWARD CLAIMED", state="disabled")
            chest_icon.config(text="✨")
            text = (f"You opened the treasure chest!\n\n"
                    f"Coins earned: {reward}\n"
                    f"Total wallet coins: {get_total_coins():,}")
            if unlocked:
                text += "\n\nNEW HERO UNLOCKED!\n" + "\n".join(unlocked)
            messagebox.showinfo("TREASURE REWARD", text, parent=root)
            next_button.config(state="normal")

        chest_button = make_button(
            "OPEN TREASURE CHEST", open_chest, "#A87516",
            state="disabled" if chest_claimed else "normal")
        chest_button.pack(pady=5)

        if chest_claimed:
            chest_icon.config(text="✨")

        if level < max(LEVELS):
            next_button = make_button(
                f"NEXT LEVEL ({level + 1})", level_map, "#218B64",
                state="normal" if chest_claimed else "disabled")
            next_button.pack(pady=5)
        else:
            next_button = make_button(
                "BACK TO LEVEL MAP", level_map, "#218B64",
                state="normal" if chest_claimed else "disabled")
            next_button.pack(pady=5)

        # If the chest was already claimed on an earlier playthrough,
        # the next level/map remains available.
        if chest_claimed:
            chest_button.config(text="REWARD ALREADY CLAIMED")
            chest_button.config(state="disabled")

    make_button("PLAY AGAIN", play_again, "#7545D8").pack(pady=4)
    make_button("LEVEL MAP", level_map, "#2585C5").pack(pady=4)
    make_button("CHANGE HERO", change_hero, "#426FAE").pack(pady=4)
    make_button("MAIN MENU", main_menu, "#C43C68").pack(pady=4)
