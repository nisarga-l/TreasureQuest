
import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk
from game import character_selection

BASE_DIR = Path(__file__).parent
BACKGROUND = BASE_DIR / "assets" / "temple_bg.png"


def show_welcome(root):
    root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))
    root.unbind("<KeyPress>")

    for widget in root.winfo_children():
        widget.destroy()

    root.title("Treasure Quest: Starlight Temple")
    root.resizable(True, True)
    root.attributes("-fullscreen", True)

    # Load temple background
    image = Image.open(BACKGROUND)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    image = image.resize((screen_width, screen_height))
    background_photo = ImageTk.PhotoImage(image)

    background = tk.Label(
        root,
        image=background_photo,
        borderwidth=0
    )
    background.image = background_photo
    background.place(x=0, y=0, relwidth=1, relheight=1)

    # Dark panel
    panel = tk.Frame(
        root,
        bg="#140B2D",
        highlightbackground="#C89B48",
        highlightthickness=2
    )
    panel.place(
        relx=0.5,
        rely=0.5,
        anchor="center",
        width=620,
        height=530
    )

    tk.Label(
        panel,
        text="TREASURE QUEST",
        font=("Georgia", 37, "bold"),
        fg="#FFD875",
        bg="#140B2D"
    ).pack(pady=(38, 5))

    tk.Label(
        panel,
        text="STARLIGHT TEMPLE",
        font=("Georgia", 23, "bold"),
        fg="#D5A7FF",
        bg="#140B2D"
    ).pack(pady=5)

    tk.Label(
        panel,
        text="Explore the magical maze and find the hidden treasure!",
        font=("Arial", 12),
        fg="white",
        bg="#140B2D"
    ).pack(pady=25)

    def how_to_play():
        window = tk.Toplevel(root)
        window.title("How to Play")
        window.geometry("500x370")
        window.configure(bg="#140B2D")

        tk.Label(
            window,
            text="HOW TO PLAY",
            font=("Georgia", 24, "bold"),
            fg="#FFD875",
            bg="#140B2D"
        ).pack(pady=25)

        tk.Label(
            window,
            text=(
                "Use Arrow Keys or WASD to move.\n\n"
                "Collect golden coins for points.\n\n"
                "Avoid dangerous traps.\n\n"
                "Find the magical purple relic.\n\n"
                "Reach the golden portal to win!\n\n"
                "Train your AI companion using Q-learning."
            ),
            font=("Arial", 13),
            fg="white",
            bg="#140B2D",
            justify="center"
        ).pack()

    # NEW CRYSTAL-STYLE BUTTON DESIGN
    def make_button(text, command, color):

        button = tk.Canvas(
            panel,
            width=370,
            height=62,
            bg="#140B2D",
            highlightthickness=0,
            cursor="hand2"
        )

        button.pack(pady=7)

        # Button colours
        normal_colors = {
            "#60218D": ("#321052", "#9B54D6", "#E4B5FF"),
            "#174C94": ("#102D59", "#347ED0", "#A6D9FF"),
            "#831B51": ("#48102E", "#B63875", "#FFB4D9")
        }

        dark, bright, border = normal_colors[color]

        def draw_button(hover=False):

            button.delete("all")

            if hover:
                fill = bright
                outline = "#FFF0A8"
                border_width = 4
            else:
                fill = dark
                outline = border
                border_width = 3

            # Crystal-shaped background
            button.create_polygon(
                20, 3,
                350, 3,
                367, 31,
                350, 59,
                20, 59,
                3, 31,
                fill=fill,
                outline=outline,
                width=border_width,
                smooth=True
            )

            # Inner crystal border
            button.create_polygon(
                25, 9,
                345, 9,
                358, 31,
                345, 53,
                25, 53,
                12, 31,
                outline="#FFFFFF",
                width=1,
                fill=""
            )

            # Crystal decoration
            button.create_text(
                48, 31,
                text="✧",
                font=("Georgia", 24, "bold"),
                fill="#FFE99B"
            )

            button.create_text(
                185, 31,
                text=text,
                font=("Georgia", 16, "bold"),
                fill="white"
            )

            button.create_text(
                320, 31,
                text="✦",
                font=("Georgia", 20, "bold"),
                fill="#FFE99B"
            )

        draw_button()

        button.bind(
            "<Enter>",
            lambda event: draw_button(True)
        )

        button.bind(
            "<Leave>",
            lambda event: draw_button(False)
        )

        button.bind(
            "<Button-1>",
            lambda event: command()
        )

    make_button(
        "START GAME",
        lambda: character_selection(root),
        "#60218D"
    )

    make_button(
        "HOW TO PLAY",
        how_to_play,
        "#174C94"
    )

    make_button(
        "EXIT GAME",
        root.destroy,
        "#831B51"
    )


if __name__ == "__main__":
    root = tk.Tk()
    show_welcome(root)
    root.mainloop()
