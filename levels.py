
# TREASURE QUEST: STARLIGHT TEMPLE
# 30 PROGRESSIVELY DIFFICULT LEVELS

import random
from collections import deque


LEVELS = {
    1: {
        "name": "Crystal Entrance",
        "reward": 100,
        "maze": [
            "############",
            "#P..C......#",
            "#.####.###.#",
            "#....#...C.#",
            "###..#.###.#",
            "#C...#.....#",
            "#.####.###.#",
            "#....R...#.#",
            "#.######.#.#",
            "#...T....G.#",
            "############"
        ]
    },
    2: {
        "name": "Moonlight Maze",
        "reward": 200,
        "maze": [
            "############",
            "#P.C.......#",
            "#.##.#.###.#",
            "#....#...C.#",
            "###....###.#",
            "#C...#.....#",
            "#.##.#.###.#",
            "#...TR...#.#",
            "#.######.#.#",
            "#...C....G.#",
            "############"
        ]
    },
    3: {
        "name": "Royal Temple",
        "reward": 350,
        "maze": [
            "############",
            "#P.C.......#",
            "#.##.#.###.#",
            "#....#...C.#",
            "###....#.#.#",
            "#CT..#.....#",
            "#.##.#.###.#",
            "#...TR...#.#",
            "#.####.#.#.#",
            "#...C.T..G.#",
            "############"
        ]
    }
}


LEVEL_NAMES = [
    "Enchanted Forest",
    "Golden Passage",
    "Emerald Chamber",
    "Mystic Garden",
    "Crystal Cavern",
    "Frozen Kingdom",
    "Shadow Corridor",
    "Diamond Temple",
    "Starlight Bridge",
    "Secret Treasure",
    "Lost Kingdom",
    "Golden Palace",
    "Moon Crystal Cave",
    "Royal Garden",
    "Magic Waterfall",
    "Dragon's Passage",
    "Hidden Sanctuary",
    "Silver Castle",
    "Mystic Mountains",
    "Frozen Palace",
    "Crystal Kingdom",
    "Shadow Temple",
    "Golden Labyrinth",
    "Star Guardian",
    "Ancient Treasure",
    "Luna's Kingdom",
    "Ultimate Temple"
]


def find_position(maze, symbol):

    for y, row in enumerate(maze):
        for x, cell in enumerate(row):

            if cell == symbol:
                return (x, y)

    return None


def can_reach(maze, start, target):

    if start is None or target is None:
        return False

    queue = deque([start])
    visited = {start}

    while queue:

        x, y = queue.popleft()

        if (x, y) == target:
            return True

        for dx, dy in [
            (0, -1),
            (0, 1),
            (-1, 0),
            (1, 0)
        ]:

            nx = x + dx
            ny = y + dy

            if not (
                0 <= ny < len(maze)
                and 0 <= nx < len(maze[ny])
            ):
                continue

            if maze[ny][nx] in ("#", "B", "I"):
                continue

            position = (nx, ny)

            if position not in visited:

                visited.add(position)
                queue.append(position)

    return False


def maze_is_solvable(maze):

    start = find_position(maze, "P")
    relic = find_position(maze, "R")
    goal = find_position(maze, "G")

    return (
        can_reach(maze, start, relic)
        and can_reach(maze, relic, goal)
    )


def add_level_obstacles(maze, level):

    # Keep the original maze layout.
    new_maze = [list(row) for row in maze]

    # Difficulty increases with level.
    ice_blocks = min(1 + level // 3, 9)
    icebergs = min(max(0, (level - 5) // 3), 7)

    candidates = []

    for y in range(1, len(new_maze) - 1):

        for x in range(1, len(new_maze[y]) - 1):

            if new_maze[y][x] == ".":
                candidates.append((x, y))

    # Shuffle positions differently for each level.
    randomizer = random.Random(level * 137)

    randomizer.shuffle(candidates)

    placed_blocks = 0
    placed_icebergs = 0

    for x, y in candidates:

        if placed_blocks >= ice_blocks:
            break

        new_maze[y][x] = "B"

        if maze_is_solvable(new_maze):

            placed_blocks += 1

        else:

            new_maze[y][x] = "."

    for x, y in candidates:

        if placed_icebergs >= icebergs:
            break

        if new_maze[y][x] != ".":
            continue

        new_maze[y][x] = "I"

        if maze_is_solvable(new_maze):

            placed_icebergs += 1

        else:

            new_maze[y][x] = "."

    return ["".join(row) for row in new_maze]


def add_extra_coins(maze, level):

    new_maze = [list(row) for row in maze]

    positions = []

    for y in range(1, len(new_maze) - 1):

        for x in range(1, len(new_maze[y]) - 1):

            if new_maze[y][x] == ".":
                positions.append((x, y))

    randomizer = random.Random(level * 271)

    randomizer.shuffle(positions)

    extra_coins = min(level // 3, len(positions))

    for x, y in positions[:extra_coins]:

        new_maze[y][x] = "C"

    return ["".join(row) for row in new_maze]


# Generate levels 4 to 30.
for number in range(4, 31):

    template_number = ((number - 1) % 3) + 1

    original_maze = LEVELS[template_number]["maze"]

    # Add ice blocks and icebergs.
    maze = add_level_obstacles(
        original_maze,
        number
    )

    # Add additional coins.
    maze = add_extra_coins(
        maze,
        number
    )

    if not maze_is_solvable(maze):

        # Safety fallback: use the original template.
        maze = original_maze[:]

    LEVELS[number] = {
        "name": LEVEL_NAMES[number - 4],
        "reward": 100 + number * 75,
        "difficulty": (
            "Easy" if number <= 5 else
            "Medium" if number <= 10 else
            "Hard" if number <= 15 else
            "Very Hard" if number <= 20 else
            "Expert" if number <= 25 else
            "Ultimate"
        ),
        "maze": maze
    }


def get_level(number):

    return LEVELS.get(number)
