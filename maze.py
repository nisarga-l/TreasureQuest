import tkinter as tk
from tkinter import messagebox
import random

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

    if not level_data:
        messagebox.showerror(
            "Level Error",
            f"Level {level} was not found.",
            parent=root
        )
        from game import level_selection
        level_selection(root, hero)
        return

    maze = [list(row) for row in level_data["maze"]]

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

    ice_hits = {}

    # Power-up uses available in this level
    shield_uses = 1
    speed_uses = 3
    icebreaker_uses = 3

    # Activated power-ups
    shield_active = False
    speed_active = False
    icebreaker_active = False

    ai_maze = ["".join(row) for row in maze]
    ai = QLearningAgent(ai_maze)

    coins = set()
    traps = set()

    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == "C":
                coins.add((x, y))
            elif cell == "T":
                traps.add((x, y))

    # Moving enemies are placed only on open floor tiles.
    open_tiles = []

    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == "." and (x, y) != (1, 1):
                open_tiles.append((x, y))

    random.shuffle(open_tiles)

    monster_count = min(1 + (level // 4), 4)
    monster_positions = [
        list(pos) for pos in open_tiles[:monster_count]
    ]

    # Every fifth level has a special guardian.
    guardian_position = None

    if level % 5 == 0 and len(open_tiles) > monster_count:
        guardian_position = list(open_tiles[monster_count])

    monster_tick = 0

    panel = tk.Frame(
        root,
        bg="#140B2D",
        padx=15,
        pady=8,
        highlightbackground="#FFD700",
        highlightthickness=2
    )
    panel.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        panel,
        text=f"LEVEL {level}: {level_data['name'].upper()}",
        font=("Georgia", 21, "bold"),
        bg="#140B2D",
        fg="#FFD700"
    ).pack(pady=5)

    status = tk.Label(
        panel,
        bg="#140B2D",
        fg="white",
        font=("Arial", 10, "bold")
    )
    status.pack(pady=4)

    canvas = tk.Canvas(
        panel,
        width=len(maze[0]) * SIZE,
        height=len(maze) * SIZE,
        bg="#30264D",
        highlightthickness=0
    )
    canvas.pack(pady=5)

    message = tk.Label(
        panel,
        text="Find the purple relic and reach the golden portal!",
        bg="#140B2D",
        fg="#D9B9FF",
        font=("Arial", 10)
    )
    message.pack(pady=4)

    power_status = tk.Label(
        panel,
        text="",
        bg="#140B2D",
        fg="#65FF9D",
        font=("Arial", 10, "bold")
    )
    power_status.pack(pady=3)

    legend = tk.Label(
        panel,
        text="👾 = Moving Monster     G = Guardian (defeat after relic)     B = Breakable Ice",
        bg="#140B2D",
        fg="#AEEBFF",
        font=("Arial", 9, "bold")
    )
    legend.pack(pady=2)

    def update_status():

        status.config(
            text=(
                f"{hero} | Score: {score} | Lives: {lives} "
                f"| Steps: {steps} | Coins: {collected_coins} "
                f"| Relic: {'YES' if relic_found else 'NO'}"
            )
        )

        power_status.config(
            text=(
                f"🛡 Shield: {shield_uses}   "
                f"⚡ Speed: {speed_uses}   "
                f"❄ Ice Breaker: {icebreaker_uses}"
            )
        )

    def draw():

        canvas.delete("all")

        for y, row in enumerate(maze):
            for x, cell in enumerate(row):

                x1 = x * SIZE
                y1 = y * SIZE
                x2 = x1 + SIZE
                y2 = y1 + SIZE

                if cell == "#":
                    canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill="#211935",
                        outline="#100B20",
                        width=2
                    )
                else:
                    canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill="#65518A",
                        outline="#211935"
                    )

                if cell == "B":

                    hits = ice_hits.get((x, y), 0)

                    canvas.create_rectangle(
                        x1 + 4, y1 + 4,
                        x2 - 4, y2 - 4,
                        fill="#75DFFF" if hits == 0 else "#B8F3FF",
                        outline="#E9FCFF",
                        width=3
                    )

                    canvas.create_line(
                        x1 + 11, y1 + 9,
                        x1 + 20, y1 + 20,
                        x1 + 15, y1 + 32,
                        fill="#278EBB",
                        width=2
                    )

                    canvas.create_text(
                        x1 + 30, y1 + 12,
                        text=str(2 - hits),
                        fill="#123B61",
                        font=("Arial", 11, "bold")
                    )

                elif cell == "I":

                    canvas.create_polygon(
                        x1 + 21, y1 + 3,
                        x2 - 4, y1 + 23,
                        x1 + 29, y2 - 3,
                        x1 + 10, y2 - 8,
                        x1 + 4, y1 + 20,
                        fill="#53C9EE",
                        outline="#E6FAFF",
                        width=2
                    )

                    canvas.create_text(
                        x1 + 21, y1 + 28,
                        text="❄",
                        fill="white",
                        font=("Arial", 12, "bold")
                    )

                if (x, y) in coins:

                    canvas.create_oval(
                        x1 + 12, y1 + 12,
                        x2 - 12, y2 - 12,
                        fill="#FFD700",
                        outline="white"
                    )

                if (x, y) in traps:

                    canvas.create_text(
                        x1 + 21, y1 + 21,
                        text="!",
                        fill="#FF4D6D",
                        font=("Arial", 24, "bold")
                    )

                if cell == "R" and not relic_found:

                    canvas.create_polygon(
                        x1 + 21, y1 + 5,
                        x2 - 5, y1 + 21,
                        x1 + 21, y2 - 5,
                        x1 + 5, y1 + 21,
                        fill="#D15CFF"
                    )

                if cell == "G":

                    canvas.create_oval(
                        x1 + 5, y1 + 5,
                        x2 - 5, y2 - 5,
                        fill="#F6B93B",
                        outline="white",
                        width=2
                    )

        # Moving monsters - 👾 symbol
        for mx, my in monster_positions:

            cx = mx * SIZE + SIZE // 2
            cy = my * SIZE + SIZE // 2

            canvas.create_oval(
                cx - 14, cy - 14,
                cx + 14, cy + 14,
                fill="#E84A5F",
                outline="#FFD6DC",
                width=2
            )

            canvas.create_text(
                cx,
                cy,
                text="👾",
                fill="white",
                font=("Segoe UI Emoji", 20)
            )

        # Special guardian appears on every fifth level.
        if guardian_position is not None:

            gx, gy = guardian_position

            cx = gx * SIZE + SIZE // 2
            cy = gy * SIZE + SIZE // 2

            canvas.create_oval(
                cx - 17, cy - 17,
                cx + 17, cy + 17,
                fill="#8B2BE2",
                outline="#FFD700",
                width=3
            )

            canvas.create_text(
                cx, cy,
                text="G",
                fill="white",
                font=("Arial", 12, "bold")
            )

        # AI companion
        ax, ay = ai_position

        canvas.create_oval(
            ax * SIZE + 13,
            ay * SIZE + 13,
            ax * SIZE + SIZE - 13,
            ay * SIZE + SIZE - 13,
            fill="#32FF91",
            outline="white"
        )

        # Player
        x, y = player

        canvas.create_oval(
            x * SIZE + 7,
            y * SIZE + 7,
            x * SIZE + SIZE - 7,
            y * SIZE + SIZE - 7,
            fill=HERO_COLORS.get(hero, "#37D8FF"),
            outline="white",
            width=2
        )

        update_status()

    def finish(won):

        nonlocal game_over

        if game_over:
            return

        game_over = True
        root.unbind("<KeyPress>")

        from victory import show_result

        show_result(
            root,
            hero,
            score,
            steps,
            lives,
            won,
            level,
            collected_coins
        )

    def handle_tile(nx, ny):

        nonlocal score, lives
        nonlocal relic_found, collected_coins
        nonlocal shield_active, guardian_position

        # Guardian can only be defeated after collecting the relic.
        if guardian_position == [nx, ny]:

            if relic_found:

                guardian_position = None
                score += 150

                message.config(
                    text="Guardian defeated! +150 bonus points!"
                )

            else:

                lives -= 1
                player[:] = [1, 1]

                message.config(
                    text="The Guardian is too strong! Find the relic first."
                )

                if lives <= 0:
                    finish(False)
                    return False

                return True

        # Ordinary monsters cost one life on contact.
        for monster in list(monster_positions):

            if monster == [nx, ny]:

                if shield_active:

                    monster_positions.remove(monster)
                    shield_active = False

                    message.config(
                        text="Magic Shield blocked a monster!"
                    )

                    break

                lives -= 1
                player[:] = [1, 1]

                message.config(
                    text="A monster caught you! You lost one life."
                )

                if lives <= 0:
                    finish(False)
                    return False

                return True

        cell = maze[ny][nx]

        if (nx, ny) in coins:

            coins.remove((nx, ny))
            collected_coins += 1
            score += 15

            message.config(text="Golden coin collected!")

        if cell == "R" and not relic_found:

            relic_found = True
            score += 50

            message.config(text="Purple relic collected!")

        if (nx, ny) in traps:

            if shield_active:

                traps.remove((nx, ny))
                shield_active = False

                message.config(
                    text="Magic Shield protected you from the trap!"
                )

                return True

            lives -= 1
            score = max(0, score - 25)
            player[:] = [1, 1]

            message.config(
                text="Trap! You lost one life."
            )

            if lives <= 0:
                finish(False)
                return False

        if cell == "G":

            if relic_found:

                score += 100
                finish(True)

                return False

            message.config(
                text="Portal locked! Collect the relic first."
            )

        return True

    def attempt_step(dx, dy):

        nonlocal steps
        nonlocal icebreaker_uses, icebreaker_active

        nx = player[0] + dx
        ny = player[1] + dy

        if not (
            0 <= ny < len(maze)
            and 0 <= nx < len(maze[ny])
        ):

            message.config(
                text="You cannot move outside the maze!"
            )

            return False

        cell = maze[ny][nx]

        if cell == "#":

            message.config(text="You hit a wall!")
            return False

        if cell == "I":

            message.config(
                text="A giant iceberg blocks your path!"
            )

            return False

        if cell == "B":

            position = (nx, ny)

            if icebreaker_active and icebreaker_uses > 0:

                maze[ny][nx] = "."
                ice_hits.pop(position, None)

                icebreaker_uses -= 1
                icebreaker_active = False

                message.config(
                    text="Magic Ice Breaker destroyed the ice!"
                )

            else:

                ice_hits[position] = ice_hits.get(position, 0) + 1

                if ice_hits[position] < 2:

                    message.config(
                        text="Crack! Hit the ice block one more time!"
                    )

                    draw()
                    return False

                maze[ny][nx] = "."
                del ice_hits[position]

                message.config(
                    text="Ice block broken! The path is clear!"
                )

        player[:] = [nx, ny]
        steps += 1

        if not handle_tile(nx, ny):
            return False

        return True

    def move(event):

        nonlocal speed_active

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

        number_of_steps = 2 if speed_active else 1

        if speed_active:
            speed_active = False

        moved = False

        for _ in range(number_of_steps):

            if game_over:
                return

            success = attempt_step(dx, dy)

            if success:
                moved = True
            else:
                break

        if moved:
            draw()

    # POWER-UP BUTTON ACTIONS

    def use_shield():

        nonlocal shield_uses, shield_active

        if shield_active:

            message.config(
                text="Your Magic Shield is already active!"
            )

            return

        if shield_uses <= 0:

            message.config(
                text="No Magic Shield uses remaining!"
            )

            return

        shield_uses -= 1
        shield_active = True

        message.config(
            text="Magic Shield activated! It will protect you from one collision."
        )

        draw()

    def use_speed():

        nonlocal speed_uses, speed_active

        if speed_active:

            message.config(
                text="Speed Boost is already active!"
            )

            return

        if speed_uses <= 0:

            message.config(
                text="No Speed Boost uses remaining!"
            )

            return

        speed_uses -= 1
        speed_active = True

        message.config(
            text="Speed Boost activated! Your next move can travel two tiles."
        )

        draw()

    def use_icebreaker():

        nonlocal icebreaker_active

        if icebreaker_uses <= 0:

            message.config(
                text="No Ice Breaker uses remaining!"
            )

            return

        icebreaker_active = True

        message.config(
            text="Ice Breaker ready! Move into a breakable ice block."
        )

        draw()

    # AI TRAINING

    def train_ai():

        nonlocal ai_trained
        nonlocal ai_has_relic
        nonlocal ai_finished

        message.config(
            text="Training AI, please wait..."
        )

        root.update_idletasks()

        try:

            states = ai.train(3000)

        except Exception as error:

            messagebox.showerror(
                "AI Error",
                str(error),
                parent=root
            )

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

        nonlocal ai_has_relic
        nonlocal ai_finished

        if not ai_trained:

            message.config(
                text="Click TRAIN AI first!"
            )

            return

        if ai_finished:

            message.config(
                text="AI completed this maze!"
            )

            return

        dx, dy = ai.next_move(
            ai_position,
            ai_has_relic
        )

        nx = ai_position[0] + dx
        ny = ai_position[1] + dy

        if not (
            0 <= ny < len(maze)
            and 0 <= nx < len(maze[ny])
        ):

            return

        cell = maze[ny][nx]

        if cell in ("#", "B", "I"):

            message.config(
                text="AI encountered an obstacle!"
            )

            return

        ai_position[:] = [nx, ny]

        if cell == "R":
            ai_has_relic = True

        if cell == "T":

            ai_position[:] = [1, 1]

            message.config(
                text="AI hit a trap!"
            )

        elif cell == "G" and ai_has_relic:

            ai_finished = True

            message.config(
                text="AI reached the portal!"
            )

        else:

            message.config(
                text="AI moved!"
            )

        draw()

    # CHANGE HERO

    def change_hero():

        unlocked = load_progress()["unlocked_characters"]

        window = tk.Toplevel(root)
        window.title("Change Hero")
        window.geometry("360x300")
        window.configure(bg="#140B2D")

        tk.Label(
            window,
            text="CHANGE HERO",
            font=("Georgia", 20, "bold"),
            bg="#140B2D",
            fg="#FFD700"
        ).pack(pady=15)

        def select(name):

            nonlocal hero

            hero = name
            window.destroy()

            draw()

        for name in HERO_COLORS:

            tk.Button(
                window,
                text=(
                    name if name in unlocked
                    else f"{name} - LOCKED"
                ),
                state=(
                    "normal" if name in unlocked
                    else "disabled"
                ),
                command=lambda n=name: select(n),
                bg="#7545D8",
                fg="white",
                width=25
            ).pack(pady=7)

    # MOVING MONSTERS AND GUARDIAN

    def move_enemies():

        nonlocal monster_tick, lives, score
        nonlocal guardian_position, shield_active

        if game_over:
            return

        monster_tick += 1

        def move_one(position, is_guardian=False):

            x, y = position
            choices = []

            for dx, dy in (
                (0, -1),
                (0, 1),
                (-1, 0),
                (1, 0)
            ):

                nx, ny = x + dx, y + dy

                if not (
                    0 <= ny < len(maze)
                    and 0 <= nx < len(maze[ny])
                ):
                    continue

                if maze[ny][nx] in (
                    "#", "B", "I", "G", "R"
                ):
                    continue

                if [nx, ny] == ai_position:
                    continue

                choices.append([nx, ny])

            if choices:

                # Guardians move more slowly than ordinary monsters.
                if not is_guardian or monster_tick % 2 == 0:

                    position[:] = random.choice(choices)

        # Move ordinary monsters
        for monster in monster_positions:
            move_one(monster)

        # Guardian moves more slowly
        if guardian_position is not None:

            move_one(
                guardian_position,
                is_guardian=True
            )

        # Check if an enemy reaches the player
        player_pos = list(player)

        if guardian_position == player_pos:

            if relic_found:

                guardian_position = None
                score += 150

                message.config(
                    text="Guardian defeated! +150 bonus points!"
                )

            else:

                lives -= 1
                player[:] = [1, 1]

                message.config(
                    text="The Guardian caught you! Find the relic first."
                )

        else:

            hit_monster = next(
                (
                    monster for monster in monster_positions
                    if monster == player_pos
                ),
                None
            )

            if hit_monster is not None:

                if shield_active:

                    monster_positions.remove(hit_monster)
                    shield_active = False

                    message.config(
                        text="Magic Shield blocked a monster!"
                    )

                else:

                    lives -= 1
                    player[:] = [1, 1]

                    message.config(
                        text="A monster caught you! You lost one life."
                    )

        if lives <= 0:

            finish(False)
            return

        draw()

        root.after(1100, move_enemies)

    # POWER-UP BUTTONS

    power_buttons = tk.Frame(
        panel,
        bg="#140B2D"
    )
    power_buttons.pack(pady=5)

    tk.Button(
        power_buttons,
        text="🛡 MAGIC SHIELD",
        command=use_shield,
        bg="#286AAB",
        fg="white",
        width=15
    ).pack(side="left", padx=3)

    tk.Button(
        power_buttons,
        text="⚡ SPEED BOOST",
        command=use_speed,
        bg="#A36A18",
        fg="white",
        width=15
    ).pack(side="left", padx=3)

    tk.Button(
        power_buttons,
        text="❄ ICE BREAKER",
        command=use_icebreaker,
        bg="#2585C5",
        fg="white",
        width=15
    ).pack(side="left", padx=3)

    # AI AND HERO BUTTONS

    buttons = tk.Frame(
        panel,
        bg="#140B2D"
    )
    buttons.pack(pady=5)

    tk.Button(
        buttons,
        text="TRAIN AI",
        bg="#7545D8",
        fg="white",
        width=12,
        command=train_ai
    ).pack(side="left", padx=3)

    tk.Button(
        buttons,
        text="AI NEXT MOVE",
        bg="#2585C5",
        fg="white",
        width=13,
        command=ai_next_move
    ).pack(side="left", padx=3)

    tk.Button(
        buttons,
        text="CHANGE HERO",
        bg="#C43C68",
        fg="white",
        width=13,
        command=change_hero
    ).pack(side="left", padx=3)

    def go_to_levels():

        from game import level_selection

        level_selection(root, hero)

    tk.Button(
        panel,
        text="LEVEL SELECTION",
        bg="#605086",
        fg="white",
        width=22,
        command=go_to_levels
    ).pack(pady=4)

    root.bind("<KeyPress>", move)

    draw()

    # Start automatic monster movement
    root.after(1100, move_enemies)