
import json
from pathlib import Path
from levels import LEVELS

SAVE_FILE = Path(__file__).parent / "save_data.json"

CHARACTER_REQUIREMENTS = {
    "Mira the Explorer": 0,
    "Luna the Star Mage": 0,
    "Ruby the Brave": 10000,
}


def load_progress():
    data = {
        "coins": 0,
        "highest_level": 1,
        "completed_levels": [],
        "unlocked_characters": ["Mira the Explorer"],
        "level_stars": {},
    }

    if SAVE_FILE.exists():
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as file:
                saved = json.load(file)

            if isinstance(saved, dict):
                data.update(saved)

        except (OSError, ValueError):
            pass

    if not isinstance(data.get("unlocked_characters"), list):
        data["unlocked_characters"] = ["Mira the Explorer"]

    if "Mira the Explorer" not in data["unlocked_characters"]:
        data["unlocked_characters"].append("Mira the Explorer")

    if not isinstance(data.get("completed_levels"), list):
        data["completed_levels"] = []

    if not isinstance(data.get("level_stars"), dict):
        data["level_stars"] = {}

    data["highest_level"] = max(
        1, int(data.get("highest_level", 1))
    )

    data["coins"] = max(0, int(data.get("coins", 0)))

    return data


def save_progress(data):
    with open(SAVE_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def unlock_character(hero):
    data = load_progress()

    if hero not in CHARACTER_REQUIREMENTS:
        return False, "Unknown character.", data

    if hero in data["unlocked_characters"]:
        return True, f"{hero} is already unlocked!", data

    if hero == "Luna the Star Mage":
        if 10 not in data["completed_levels"]:
            return (
                False,
                "Complete Level 10 to unlock Luna the Star Mage.",
                data,
            )

        data["unlocked_characters"].append(hero)
        save_progress(data)

        return True, "Luna the Star Mage unlocked!", data

    price = CHARACTER_REQUIREMENTS[hero]

    if data["coins"] < price:
        missing = price - data["coins"]

        return (
            False,
            f"You need {missing:,} more coins to unlock {hero}.",
            data,
        )

    data["coins"] -= price
    data["unlocked_characters"].append(hero)

    save_progress(data)

    return True, f"{hero} unlocked successfully!", data


def complete_level(level, collected_coins=0, stars=3):
    data = load_progress()

    if level not in LEVELS:
        return 0, []

    # Do not give the level reward twice.
    if level in data["completed_levels"]:
        old_stars = int(
            data["level_stars"].get(str(level), 0)
        )

        data["level_stars"][str(level)] = max(
            old_stars, stars
        )

        save_progress(data)
        return 0, []

    bonus = LEVELS[level]["reward"]
    extra_coins = collected_coins * 25
    total_reward = bonus + extra_coins

    data["coins"] += total_reward

    data["completed_levels"].append(level)
    data["completed_levels"].sort()

    data["level_stars"][str(level)] = stars

    # Unlock the next level.
    data["highest_level"] = max(
        data["highest_level"], level + 1
    )

    newly_unlocked = []

    # Automatically unlock Luna after Level 10.
    if (
        level == 10
        and "Luna the Star Mage"
        not in data["unlocked_characters"]
    ):
        data["unlocked_characters"].append(
            "Luna the Star Mage"
        )

        newly_unlocked.append("Luna the Star Mage")

    save_progress(data)

    return total_reward, newly_unlocked


def get_total_coins():
    return load_progress()["coins"]
