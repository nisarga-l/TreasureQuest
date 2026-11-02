
import tkinter as tk
from tkinter import messagebox

from theme import apply_background
from progress import complete_level, load_progress, get_total_coins
from levels import LEVELS


def show_result(root, hero, score, steps, lives,
                won, level=1, collected_coins=0):

    root.unbind_all("<MouseWheel>")
    root.unbind_all("<Button-4>")
    root.unbind_all("<Button-5>")
    root.unbind("<KeyPress>")

    for widget in root.winfo_children():
        widget.destroy()

    apply_background(root)

    stars = 3 if lives >= 3 else (2 if lives == 2 else 1)

    reward = 0
    unlocked = []

    if won:
        try:
            reward, unlocked = complete_level(
                level, collected_coins, stars
            )
        except Exception as error:
            messagebox.showerror(
                "Progress Error", str(error), parent=root
            )
            return

    panel = tk.Frame(
        root,
        bg="#140B2D",
        highlightbackground="#FFD875",
        highlightthickness=3,
        padx=20,
        pady=10
    )

    panel.place(
        relx=0.5,
        rely=0.5,
        anchor="center",
        width=590,
        height=700
    )

    def heading(text, size, color):
        tk.Label(
            panel,
            text=text,
            font=("Georgia", size, "bold"),
            fg=color,
            bg="#140B2D"
        ).pack(pady=4)

    def crystal_button(text, command, color, hover):
        button = tk.Canvas(
            panel,
            width=350,
            height=44,
            bg="#140B2D",
            highlightthickness=0,
            cursor="hand2"
        )
        button.pack(pady=4)

        shape = button.create_polygon(
            12, 2, 338, 2, 350, 22,
            338, 42, 12, 42, 0, 22,
            fill=color,
            outline="#FFD875",
            width=2
        )

        button.create_text(
            175, 22,
            text=text,
            fill="white",
            font=("Georgia", 12, "bold")
        )

        button.bind(
            "<Enter>",
            lambda event: button.itemconfig(
                shape, fill=hover, outline="#FFF0B0", width=3
            )
        )

        button.bind(
            "<Leave>",
            lambda event: button.itemconfig(
                shape, fill=color, outline="#FFD875", width=2
            )
        )

        button.bind(
            "<Button-1>",
            lambda event: command()
        )

    heading(
        "✦ LEVEL COMPLETED! ✦" if won else "GAME OVER",
        26,
        "#FFD875" if won else "#FF6688"
    )

    level_info = LEVELS.get(level, {"name": "Unknown Level"})

    heading(
        f"LEVEL {level}: {level_info['name']}",
        15,
        "#D5A7FF"
    )

    if won:
        heading("★ " * stars, 23, "#FFD875")

    # Game statistics
    info = tk.Frame(
        panel,
        bg="#30204F",
        highlightbackground="#9D72D1",
        highlightthickness=2,
        padx=12,
        pady=8
    )
    info.pack(fill="x", pady=7)

    tk.Label(
        info,
        text=f"✧ HERO: {hero}",
        font=("Arial", 11, "bold"),
        fg="#FFD875",
        bg="#30204F"
    ).pack(pady=2)

    tk.Label(
        info,
        text=(
            f"FINAL SCORE       : {score}\n"
            f"STEPS TAKEN       : {steps}\n"
            f"LIVES REMAINING   : {lives}\n"
            f"MAZE COINS        : {collected_coins}"
        ),
        font=("Arial", 10),
        fg="white",
        bg="#30204F",
        justify="left"
    ).pack(pady=3)

    if won:

        heading(
            "✦ YOU FOUND THE TREASURE! ✦",
            14,
            "#FFD875"
        )

        # Treasure chest animation area
        chest_frame = tk.Frame(
            panel,
            bg="#140B2D"
        )
        chest_frame.pack(pady=2)

        chest = tk.Canvas(
            chest_frame,
            width=280,
            height=112,
            bg="#140B2D",
            highlightthickness=0
        )
        chest.pack()

        reward_label = tk.Label(
            chest_frame,
            text="A mysterious treasure awaits...",
            font=("Georgia", 11, "bold"),
            fg="#FFD875",
            bg="#140B2D"
        )
        reward_label.pack(pady=2)

        total_label = tk.Label(
            chest_frame,
            text=f"TOTAL WALLET: {get_total_coins():,} COINS",
            font=("Arial", 10, "bold"),
            fg="#65FF9D",
            bg="#140B2D"
        )
        total_label.pack(pady=2)

        chest_state = {
            "opened": False,
            "glow": False
        }

        def draw_chest(opening=0):
            chest.delete("all")

            # Magical glow behind the chest
            glow_color = (
                "#FFE98A" if chest_state["glow"]
                else "#9D65DB"
            )

            chest.create_oval(
                65, 5, 215, 110,
                fill="#38205C",
                outline=glow_color,
                width=3
            )

            # Floating stars
            chest.create_text(
                35, 25, text="✦",
                fill="#FFD875",
                font=("Georgia", 17, "bold")
            )

            chest.create_text(
                245, 22, text="✧",
                fill="#D5A7FF",
                font=("Georgia", 18, "bold")
            )

            chest.create_text(
                45, 83, text="✧",
                fill="#FFD875",
                font=("Georgia", 13, "bold")
            )

            chest.create_text(
                235, 80, text="✦",
                fill="#FFD875",
                font=("Georgia", 15, "bold")
            )

            # Magical light when the chest opens
            if opening > 0:
                chest.create_oval(
                    100, 12, 180, 83,
                    fill="#FFF0A8",
                    outline="#FFFFFF",
                    width=2
                )

                for x, y in [
                    (110, 18), (175, 24), (90, 43),
                    (190, 45), (130, 5), (155, 8)
                ]:
                    chest.create_text(
                        x, y,
                        text="✦",
                        fill="#FFD875",
                        font=("Georgia", 15, "bold")
                    )

            # Chest bottom
            chest.create_rectangle(
                85, 55, 195, 100,
                fill="#A95D19",
                outline="#FFD875",
                width=3
            )

            chest.create_rectangle(
                85, 68, 195, 78,
                fill="#D99A32",
                outline="#FFD875",
                width=2
            )

            # Chest golden lock
            chest.create_rectangle(
                132, 64, 148, 87,
                fill="#FFE58A",
                outline="#8B5018",
                width=2
            )

            chest.create_oval(
                137, 70, 143, 76,
                fill="#75421A",
                outline=""
            )

            # Chest lid: moves upward as opening increases
            lift = int(opening * 32)

            chest.create_polygon(
                85, 55 - lift,
                95, 27 - lift,
                185, 27 - lift,
                195, 55 - lift,
                fill="#C47A24",
                outline="#FFD875",
                width=3
            )

            chest.create_line(
                95, 38 - lift,
                185, 38 - lift,
                fill="#FFE58A",
                width=3
            )

            chest.create_line(
                140, 28 - lift,
                140, 52 - lift,
                fill="#FFE58A",
                width=2
            )

            # Coins appear when the chest opens
            if opening > 0.35:
                for x, y in [
                    (105, 40), (125, 20),
                    (155, 16), (175, 38),
                    (115, 5), (165, 2)
                ]:
                    chest.create_oval(
                        x, y, x + 13, y + 13,
                        fill="#FFD700",
                        outline="#FFF3A0",
                        width=2
                    )

        def glow_animation():
            if not chest.winfo_exists():
                return

            if chest_state["opened"]:
                return

            chest_state["glow"] = not chest_state["glow"]
            draw_chest()

            root.after(450, glow_animation)

        def open_treasure():
            if chest_state["opened"]:
                return

            chest_state["opened"] = True
            open_button.config(
                text="✦ TREASURE OPENED ✦",
                state="disabled"
            )

            reward_label.config(
                text="MAGIC TREASURE UNLOCKED!",
                fg="#FFE98A"
            )

            def animate_open(frame=0):
                if not chest.winfo_exists():
                    return

                progress = min(frame / 10, 1)
                draw_chest(progress)

                if frame < 10:
                    root.after(
                        65,
                        lambda: animate_open(frame + 1)
                    )
                else:
                    reward_label.config(
                        text="COUNTING YOUR GOLDEN REWARD...",
                        fg="#FFD875"
                    )
                    animate_coins()

            def animate_coins(current=0):
                if not reward_label.winfo_exists():
                    return

                if reward <= 0:
                    reward_label.config(
                        text="NO NEW COINS THIS TIME!",
                        fg="#FFD875"
                    )
                    return

                current = min(current + max(1, reward // 30), reward)

                reward_label.config(
                    text=f"✦ +{current:,} COINS ✦",
                    fg="#65FF9D"
                )

                if current < reward:
                    root.after(
                        35,
                        lambda: animate_coins(current)
                    )
                else:
                    reward_label.config(
                        text=f"✦ YOU RECEIVED {reward:,} COINS! ✦",
                        fg="#65FF9D"
                    )

            animate_open()

        draw_chest()

        # Button to open treasure
        open_button = tk.Button(
            chest_frame,
            text="✦ OPEN TREASURE ✦",
            command=open_treasure,
            font=("Georgia", 11, "bold"),
            bg="#9A5A16",
            fg="white",
            activebackground="#D99A32",
            activeforeground="white",
            relief="raised",
            bd=3,
            padx=20,
            pady=5,
            cursor="hand2"
        )
        open_button.pack(pady=4)

        glow_animation()

        if unlocked:
            tk.Label(
                panel,
                text="NEW HERO UNLOCKED: LUNA THE STAR MAGE!",
                font=("Arial", 9, "bold"),
                fg="#FFB6E6",
                bg="#140B2D"
            ).pack(pady=2)

        heading(
            "✧ YOUR NEXT ADVENTURE AWAITS ✧",
            10,
            "#D5A7FF"
        )

        def play_again():
            from maze import start_maze
            start_maze(root, hero, level)

        def next_level():
            from maze import start_maze

            if level + 1 in LEVELS:
                start_maze(root, hero, level + 1)
            else:
                from game import level_selection
                level_selection(root, hero)

        def level_map():
            from game import level_selection
            level_selection(root, hero)

        def main_menu():
            from main import show_welcome
            show_welcome(root)

        crystal_button(
            "✦ PLAY AGAIN ✦",
            play_again,
            "#7545D8",
            "#A77BFF"
        )

        if level + 1 in LEVELS:
            crystal_button(
                f"✧ NEXT LEVEL ({level + 1}) ✧",
                next_level,
                "#218B64",
                "#35B88A"
            )

        crystal_button(
            "💎 LEVEL MAP",
            level_map,
            "#2585C5",
            "#48B5F0"
        )

        crystal_button(
            "⌂ MAIN MENU",
            main_menu,
            "#C43C68",
            "#EE648C"
        )

    else:
        heading("✧ DON'T GIVE UP! ✧", 13, "#D5A7FF")

        def play_again():
            from maze import start_maze
            start_maze(root, hero, level)

        def level_map():
            from game import level_selection
            level_selection(root, hero)

        def main_menu():
            from main import show_welcome
            show_welcome(root)

        crystal_button(
            "✦ TRY AGAIN ✦",
            play_again,
            "#7545D8",
            "#A77BFF"
        )

        crystal_button(
            "💎 LEVEL MAP",
            level_map,
            "#2585C5",
            "#48B5F0"
        )

        crystal_button(
            "⌂ MAIN MENU",
            main_menu,
            "#C43C68",
            "#EE648C"
        )

    tk.Label(
        panel,
        text="✦ STARLIGHT TEMPLE ✦",
        font=("Georgia", 9, "bold"),
        fg="#FFD875",
        bg="#140B2D"
    ).pack(pady=3)
