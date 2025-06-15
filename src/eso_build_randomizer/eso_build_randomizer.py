#!/usr/bin/env python3
"""Elder Scrolls Online Build Randomizer
========================================
Generates random skill line combinations following the new subclassing system rules.
"""  # noqa: D415

from __future__ import annotations

import argparse
import random
import sys
import termios
import tty
from typing import Any


class QuitRequested(Exception):  # noqa: N818
    """Exception raised when user presses Q to quit."""


# ESO Classes and their skill lines
CLASSES = {
    "Arcanist": ["Herald of the Tome", "Soldier of Apocrypha", "Curative Runeforms"],
    "Dragonknight": ["Ardent Flame", "Draconic Power", "Earthen Heart"],
    "Nightblade": ["Assassination", "Shadow", "Siphoning"],
    "Sorcerer": ["Daedric Summoning", "Dark Magic", "Storm Calling"],
    "Templar": ["Aedric Spear", "Dawn's Wrath", "Restoring Light"],
    "Necromancer": ["Grave Lord", "Bone Tyrant", "Living Death"],
    "Warden": ["Animal Companions", "Green Balance", "Winter's Embrace"],
}


def generate_random_build(
    base_class: str | None = None, num_lines: int | None = None
) -> dict[str, Any]:
    """Generate a random build following ESO subclassing rules.

    1. Must keep at least one original skill line.
    2. Can only subclass one skill from another class.
    3. Can trade out 1 or 2 skill lines.

    Args:
        base_class: The base class to generate a build for.
        num_lines: The number of skill lines to replace.

    Returns:
        A dictionary containing the base class, skill lines, subclassed from, and description.

    Raises:
        ValueError: If num_lines is not 1 or 2.
    """
    if base_class is None:
        base_class = random.choice(list(CLASSES.keys()))

    original_skills = CLASSES[base_class].copy()
    available_classes = [cls for cls in CLASSES if cls != base_class]

    # Decide how many skill lines to replace
    if num_lines is not None:
        if not 1 <= num_lines <= 2:
            msg = "num_lines must be 1 or 2"
            raise ValueError(msg)
        num_replacements = num_lines
    else:
        num_replacements = random.choice([1, 2])

    # Select which original skills to replace
    skills_to_replace = random.sample(original_skills, num_replacements)
    remaining_original_skills = [
        skill for skill in original_skills if skill not in skills_to_replace
    ]

    # Select replacement classes (must be different for each replacement)
    replacement_classes = random.sample(available_classes, num_replacements)

    # Build the final skill line combination
    final_skills = remaining_original_skills.copy()
    subclassed_from = []

    for replacement_class in replacement_classes:
        # Pick a random skill from the replacement class
        replacement_skill = random.choice(CLASSES[replacement_class])
        final_skills.append(replacement_skill)
        subclassed_from.append(replacement_class)

    return {
        "base_class": base_class,
        "skill_lines": final_skills,
        "subclassed_from": subclassed_from,
        "description": f"{base_class} with {', '.join(subclassed_from)} subclassing",
    }


def print_build(build: dict[str, Any]):
    """Pretty print a build configuration."""
    print(f"🏛️  {build['base_class']} Build")
    print("=" * 50)
    print("📜 Skill Lines:")

    original_skills = CLASSES[build["base_class"]]

    for skill in build["skill_lines"]:
        if skill in original_skills:
            print(f"   • {skill}")
        else:
            # Find which class this skill belongs to
            source_class = None
            for cls, skills in CLASSES.items():
                if skill in skills:
                    source_class = cls
                    break
            print(f"   • {skill} (from {source_class})")

    if build["subclassed_from"]:
        print(f"\n🔄 Subclassed from: {', '.join(build['subclassed_from'])}")

    print(f"💡 {build['description']}")
    print("-" * 50)


def generate_multiple_builds(
    count: int = 5, base_class: str | None = None, num_lines: int | None = None
):
    """Generate multiple random builds."""
    print(f"🎲 Generating {count} Random ESO Builds")
    print("=" * 50)

    for i in range(count):
        build = generate_random_build(base_class, num_lines)
        print_build(build)

        if i < count - 1:  # Don't print extra newline after last build
            print()


def ask_for_retry(
    last_class: str | None = None, was_random: bool = False
) -> tuple[bool, str | None, bool]:
    """Ask user if they want to retry with same class or start over."""
    if last_class:
        print("\nWhat would you like to do next?")
        if was_random:
            print("1. Generate another random build")
        else:
            print(f"1. Generate another {last_class} build")
        print("2. Start over (back to main menu)")
        print("\nPress 1 or 2...")
        choice = get_single_key()
        if choice == "1":
            return True, last_class if not was_random else None, was_random
        if choice == "2":
            return False, None, False
        print("❌ Invalid choice! Returning to main menu.")
        return False, None, False
    return False, None, False


def handle_random_build():
    """Handle random build generation with retry logic."""
    clear_screen()
    build = generate_random_build()
    print_build(build)

    # Ask if they want to retry
    retry, retry_class, _was_random = ask_for_retry(build["base_class"], was_random=True)
    while retry:
        clear_screen()
        build = generate_random_build(retry_class)  # retry_class will be None for random
        print_build(build)
        retry, retry_class, _was_random = ask_for_retry(build["base_class"], was_random=True)
    clear_screen()


def handle_class_selection():
    """Handle class-specific build generation with retry logic."""
    clear_screen()
    print("🎮 ESO Build Randomizer - Class Selection")
    print("=" * 50)
    print("\nAvailable classes:")
    for i, cls in enumerate(CLASSES.keys(), 1):
        print(f"{i}. {cls}")
    print("\nChoose a class...")

    class_choice = get_single_key()
    try:
        class_index = int(class_choice) - 1
        class_names = list(CLASSES.keys())
        if 0 <= class_index < len(class_names):
            selected_class = class_names[class_index]
            clear_screen()
            build = generate_random_build(selected_class)
            print_build(build)

            # Ask if they want to retry with the same class
            retry, retry_class, _ = ask_for_retry(selected_class, was_random=False)
            while retry:
                clear_screen()
                build = generate_random_build(retry_class)
                print_build(build)
                retry, retry_class, _ = ask_for_retry(retry_class, was_random=False)
            clear_screen()
        else:
            clear_screen()
            print("❌ Invalid class selection!")
            print("Press any key to continue...")
            get_single_key()
            clear_screen()
    except ValueError:
        clear_screen()
        print("❌ Please enter a valid number!")
        print("Press any key to continue...")
        get_single_key()
        clear_screen()


def handle_multiple_builds():
    """Handle multiple build generation."""
    clear_screen()
    print("🎮 ESO Build Randomizer - Multiple Builds")
    print("=" * 50)
    try:
        count = int(input("How many builds to generate? (default 5): ") or "5")
        num_lines = input("How many skill lines to replace? (default random): ")
        lines: int | None = int(num_lines) if num_lines else None
        clear_screen()
        generate_multiple_builds(count, num_lines=lines)
        print("\nPress any key to continue...")
        get_single_key()
        clear_screen()
    except ValueError:
        clear_screen()
        print("❌ Please enter a valid number!")
        print("Press any key to continue...")
        get_single_key()
        clear_screen()


def interactive_mode() -> None:
    """Interactive mode for generating builds.

    Raises:
        QuitRequested: If user presses Q at any point.
    """
    clear_screen()

    while True:
        print("🎮 ESO Build Randomizer - Interactive Mode")
        print("=" * 50)
        print("\nOptions:")
        print("1. Generate random build (any class)")
        print("2. Generate build for specific class")
        print("3. Generate multiple builds")
        print("Q. Quit")
        print("\nChoose an option...")

        choice = get_single_key()

        if choice == "1":
            handle_random_build()
        elif choice == "2":
            handle_class_selection()
        elif choice == "3":
            handle_multiple_builds()
        elif choice == "q":
            raise QuitRequested
        else:
            clear_screen()
            print("❌ Invalid choice! Please press 1, 2, 3, or Q.")
            print("Press any key to continue...")
            get_single_key()
            clear_screen()


def clear_screen():
    """Clear the terminal screen and position cursor at top-left."""
    # Check if we're in a real terminal that supports ANSI codes
    if sys.stdout.isatty() and sys.stdin.isatty():
        try:  # Use ANSI escape codes for real terminals
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.flush()
            return
        except Exception:
            pass

    # Fallback to system clear command
    import os

    os.system("cls" if os.name == "nt" else "clear")

    # After system clear, try to position cursor at top-left if possible
    if sys.stdout.isatty():
        try:
            sys.stdout.write("\033[H")
            sys.stdout.flush()
        except Exception:
            pass


def get_single_key() -> str:
    """Get a single keypress without requiring Enter.

    Raises:
        QuitRequested: If Q is pressed.
        KeyboardInterrupt: If Ctrl+C is pressed.
    """
    try:
        # Save terminal settings
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        # Set terminal to raw mode
        tty.setraw(sys.stdin.fileno())

        # Read single character
        key = sys.stdin.read(1)

        # Restore terminal settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        # Handle Ctrl+C
        if ord(key) == 3:  # Ctrl+C
            raise KeyboardInterrupt

        # Handle Q
        if key.lower() == "q":
            raise QuitRequested

        return key.lower()
    except (ImportError, AttributeError):
        # Fallback for systems without termios (like Windows)
        return input().strip().lower()


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="ESO Build Randomizer")
    parser.add_argument(
        "-n", "--number", type=int, default=3, help="Number of builds to generate (default: 3)"
    )
    parser.add_argument(
        "-c",
        "--class",
        dest="base_class",
        choices=list(CLASSES.keys()),
        help="Generate builds for specific class only",
    )
    parser.add_argument(
        "-l",
        "--lines",
        type=int,
        help="Number of skill lines to replace (default: random)",
    )
    parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode")

    args = parser.parse_args()

    try:
        if args.interactive:
            interactive_mode()
        else:
            print("🎲 ESO Build Randomizer")
            if args.base_class:
                print(f"Generating builds for {args.base_class}...\n")
            else:
                print("Generating random builds...\n")

            if args.lines and not 1 <= args.lines <= 2:
                print("❌ Invalid number of lines to replace. Must be 1 or 2.")
                return

            generate_multiple_builds(args.number, args.base_class, args.lines)

            print("\n💡 Tip: Use --help to see all options, or -i for interactive mode!")
    except QuitRequested:
        clear_screen()
        print("👋 Happy theorycrafting!")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ An error occurred: {e}")


if __name__ == "__main__":
    main()
