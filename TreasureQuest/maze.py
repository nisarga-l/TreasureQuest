
import tkinter as tk
from tkinter import messagebox

from theme import apply_background
from levels import get_level
from progress import load_progress
from q_learning import QLearningAgent

SIZE = 42

HERO_COLORS = {
    "Mira the Explorer": "#37D8FF",
    "Luna the Star Mage": "#C66BFF",
    "Ruby the Brave": "#FF6688"
}


def start_maze(root, hero, level=1):
    root.unbind("<KeyPress>")

    for widget in root.winfo_children():
        widget.destroy()

    apply_background(root)

    level_data = get_level(level)
    maze = level_data["maze"]

    player = [1, 1]
    ai_position = [1, 1]

    score = 0
    lives = 3
    steps = 0
    collected_coins = 0
    relic_found = False
    game_over = False

    ai_has_relic = False
    ai_trained = False
    ai_finished = False

    ai = QLearningAgent(maze)

    coins = set()
    traps = set()

    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == "C":
                coins.add((x, y))
            elif cell == "T":
                traps.add((x, y))

    panel = tk.Frame(
        root,
        bg="#140B2D",
        padx=20,
        pady=10,
        highlightbackground="#FFD700",
        highlightthickness=2
    )
    panel.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        panel,
        text=f"LEVEL {level}: {level_data['name'].upper()}",
        font=("Georgia", 23, "bold"),
        bg="#140B2D",
        fg="#FFD700"
    ).pack(pady=7)

    status = tk.Label(
        panel,
        bg="#140B2D",
        fg="white",
        font=("Arial", 12, "bold")
    )
    status.pack(pady=5)

    canvas = tk.Canvas(
        panel,
        width=len(maze[0]) * SIZE,
        height=len(maze) * SIZE,
        bg="#30264D",
        highlightthickness=0
    )
    canvas.pack(pady=6)

    message = tk.Label(
        panel,
        text="Find the purple relic and reach the golden portal!",
        bg="#140B2D",
        fg="#D9B9FF",
        font=("Arial", 12)
    )
    message.pack(pady=6)

    def draw():
        canvas.delete("all")

        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                x1 = x * SIZE
                y1 = y * SIZE
                x2 = x1 + SIZE
                y2 = y1 + SIZE

                canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill="#30264D" if cell == "#" else "#65518A",
                    outline="#211935"
                )

                if (x, y) in coins:
                    canvas.create_oval(
                        x1+12, y1+12, x2-12, y2-12,
                        fill="#FFD700", outline="white"
                    )

                if (x, y) in traps:
                    canvas.create_text(
                        x1+21, y1+21, text="!",
                        fill="#FF4D6D",
                        font=("Arial", 24, "bold")
                    )

                if cell == "R" and not relic_found:
                    canvas.create_polygon(
                        x1+21, y1+5,
                        x2-5, y1+21,
                        x1+21, y2-5,
                        x1+5, y1+21,
                        fill="#D15CFF"
                    )

                if cell == "G":
                    canvas.create_oval(
                        x1+5, y1+5,
                        x2-5, y2-5,
                        fill="#F6B93B",
                        outline="white",
                        width=2
                    )

        ax, ay = ai_position
        canvas.create_oval(
            ax*SIZE+13, ay*SIZE+13,
            ax*SIZE+SIZE-13, ay*SIZE+SIZE-13,
            fill="#32FF91", outline="white"
        )

        x, y = player
        canvas.create_oval(
            x*SIZE+7, y*SIZE+7,
            x*SIZE+SIZE-7, y*SIZE+SIZE-7,
            fill=HERO_COLORS.get(hero, "#37D8FF"),
            outline="white", width=2
        )

        status.config(
            text=(
                f"{hero} | Score: {score} | Lives: {lives} "
                f"| Steps: {steps} | Coins: {collected_coins} "
                f"| Relic: {'YES' if relic_found else 'NO'}"
            )
        )

    def finish(won):
        nonlocal game_over
        game_over = True
        root.unbind("<KeyPress>")

        from victory import show_result
        show_result(
            root, hero, score, steps, lives,
            won, level, collected_coins
        )

    def move(event):
        nonlocal score, lives, steps
        nonlocal relic_found, collected_coins

        if game_over:
            return

        directions = {
            "Up": (0, -1),
            "Down": (0, 1),
            "Left": (-1, 0),
            "Right": (1, 0),
            "w": (0, -1),
            "s": (0, 1),
            "a": (-1, 0),
            "d": (1, 0)
        }

        key = event.keysym
        if key not in directions:
            return

        dx, dy = directions[key]
        nx = player[0] + dx
        ny = player[1] + dy

        if not (
            0 <= ny < len(maze)
            and 0 <= nx < len(maze[ny])
        ):
            return

        if maze[ny][nx] == "#":
            message.config(text="You hit a wall!")
            return

        player[:] = [nx, ny]
        steps += 1

        if (nx, ny) in coins:
            coins.remove((nx, ny))
            collected_coins += 1
            score += 15
            message.config(text="Golden coin collected!")

        if maze[ny][nx] == "R" and not relic_found:
            relic_found = True
            score += 50
            message.config(text="Purple relic collected!")

        if (nx, ny) in traps:
            lives -= 1
            score = max(0, score - 25)
            player[:] = [1, 1]
            message.config(text="Trap! You lost one life.")

            if lives <= 0:
                finish(False)
                return

        if maze[ny][nx] == "G":
            if relic_found:
                score += 100
                finish(True)
                return
            else:
                message.config(
                    text="Portal locked! Collect the relic first."
                )

        draw()

    def train_ai():
        nonlocal ai_trained, ai_has_relic, ai_finished

        message.config(text="Training AI, please wait...")
        root.update_idletasks()

        try:
            states = ai.train(3000)
        except Exception as error:
            messagebox.showerror("AI Error", str(error))
            return

        ai_trained = True
        ai_has_relic = False
        ai_finished = False
        ai_position[:] = [1, 1]

        message.config(
            text=f"AI training completed! States: {states}"
        )
        draw()

    def ai_next_move():
        nonlocal ai_has_relic, ai_finished

        if not ai_trained:
            message.config(text="Click TRAIN AI first!")
            return

        if ai_finished:
            message.config(text="AI completed this maze!")
            return

        dx, dy = ai.next_move(ai_position, ai_has_relic)
        nx = ai_position[0] + dx
        ny = ai_position[1] + dy

        if not (
            0 <= ny < len(maze)
            and 0 <= nx < len(maze[ny])
        ):
            return

        if maze[ny][nx] == "#":
            message.config(text="AI encountered a wall.")
            return

        ai_position[:] = [nx, ny]

        if maze[ny][nx] == "R":
            ai_has_relic = True

        if maze[ny][nx] == "T":
            ai_position[:] = [1, 1]
            message.config(text="AI hit a trap!")

        elif maze[ny][nx] == "G" and ai_has_relic:
            ai_finished = True
            message.config(text="AI reached the portal!")

        else:
            message.config(text="AI moved!")

        draw()

    def change_hero():
        nonlocal hero
        unlocked = load_progress()["unlocked_characters"]

        window = tk.Toplevel(root)
        window.title("Change Hero")
        window.geometry("360x300")
        window.configure(bg="#140B2D")

        tk.Label(
            window, text="CHANGE HERO",
            font=("Georgia", 20, "bold"),
            bg="#140B2D", fg="#FFD700"
        ).pack(pady=15)

        def select(name):
            nonlocal hero
            hero = name
            window.destroy()
            draw()

        for name in HERO_COLORS:
            tk.Button(
                window,
                text=name if name in unlocked else f"{name} - LOCKED",
                state="normal" if name in unlocked else "disabled",
                command=lambda n=name: select(n),
                bg="#7545D8",
                fg="white",
                width=25
            ).pack(pady=7)

    buttons = tk.Frame(panel, bg="#140B2D")
    buttons.pack(pady=7)

    tk.Button(
        buttons, text="TRAIN AI",
        bg="#7545D8", fg="white",
        width=13, command=train_ai
    ).pack(side="left", padx=5)

    tk.Button(
        buttons, text="AI NEXT MOVE",
        bg="#2585C5", fg="white",
        width=15, command=ai_next_move
    ).pack(side="left", padx=5)

    tk.Button(
        buttons, text="CHANGE HERO",
        bg="#C43C68", fg="white",
        width=15, command=change_hero
    ).pack(side="left", padx=5)

    tk.Button(
        panel, text="LEVEL SELECTION",
        bg="#605086", fg="white",
        width=22,
        command=lambda: go_to_levels(root, hero)
    ).pack(pady=5)

    root.bind("<KeyPress>", move)
    draw()


def go_to_levels(root, hero):
    from game import level_selection
    level_selection(root, hero)
