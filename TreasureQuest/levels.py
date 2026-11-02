from copy import deepcopy

# The first three levels are the original mazes. Later levels use the same
# temple tile system, with increasingly challenging coin and trap layouts.
_BASE_MAZES = {
    1: [
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
    ],
    2: [
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
    ],
    3: [
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

_LEVEL_NAMES = [
    "Crystal Entrance", "Moonlight Maze", "Royal Temple",
    "Starlight Passage", "Golden Hall", "Mystic Garden",
    "Emerald Corridor", "Whispering Cavern", "Silver Bridge",
    "Luna's Sanctuary", "Ancient Library", "Sapphire Vault",
    "Twilight Tunnel", "Enchanted Courtyard", "Ruby Chamber",
    "Celestial Steps", "Hidden Observatory", "Dragon's Gate",
    "Frozen Gallery", "Sunfire Hall", "Crystal Catacombs",
    "Moonstone Keep", "Phantom Passage", "Golden Observatory",
    "Starfall Fortress", "Eternal Labyrinth", "Crown of Shadows",
    "Astral Palace", "Legendary Vault", "Starlight Throne"
]

LEVELS = {}

for level_number in range(1, 31):
    template_number = ((level_number - 1) % 3) + 1
    maze = [list(row) for row in _BASE_MAZES[template_number]]

    # Add a different set of extra coins and traps to later levels.
    # Walls, start, relic and exit positions remain unchanged.
    if level_number > 3:
        candidates = [
            (x, y)
            for y in range(1, len(maze) - 1)
            for x in range(1, len(maze[y]) - 1)
            if maze[y][x] == '.'
        ]
        # A deterministic level-specific ordering gives each level a
        # different collectible/challenge arrangement.
        candidates.sort(key=lambda point: ((point[0] * 7 + point[1] * 11 + level_number * 5) % 97,
                                           point[1], point[0]))
        extra_coins = min(1 + level_number // 6, 5)
        extra_traps = min((level_number - 2) // 5, 5)
        for x, y in candidates[:extra_coins]:
            maze[y][x] = 'C'
        for x, y in candidates[extra_coins:extra_coins + extra_traps]:
            maze[y][x] = 'T'

    LEVELS[level_number] = {
        "name": _LEVEL_NAMES[level_number - 1],
        "reward": 100 + (level_number - 1) * 50,
        "maze": ["".join(row) for row in maze]
    }


def get_level(number):
    return LEVELS[number]
