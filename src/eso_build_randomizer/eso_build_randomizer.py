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
import time
import tty
from typing import Any

from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text


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
    """Pretty print a build configuration using Rich."""
    console = Console()

    # Create skill lines content
    skill_lines_content = []
    original_skills = CLASSES[build["base_class"]]

    for skill in build["skill_lines"]:
        if skill in original_skills:
            skill_lines_content.append(f"   [cyan]• {skill}[/cyan]")
        else:
            # Find which class this skill belongs to
            source_class = None
            for cls, skills in CLASSES.items():
                if skill in skills:
                    source_class = cls
                    break
            skill_lines_content.append(
                f"   [cyan]• {skill}[/cyan] [yellow](from {source_class})[/yellow]"
            )

    # Build the panel content as a string
    panel_content_lines = []
    panel_content_lines.extend((f"[bold blue]{build['base_class']} with Skill Lines:[/bold blue]",))
    panel_content_lines.extend(skill_lines_content)

    if build["subclassed_from"]:
        panel_content_lines.append("")
        # Create a single line with highlighted class names
        subclass_names = [f"[bold yellow]{cls}[/bold yellow]" for cls in build["subclassed_from"]]
        panel_content_lines.append(f"[bold cyan]Subclasses {', '.join(subclass_names)}[/bold cyan]")
    else:
        panel_content_lines.extend((
            "",
            f"[bold green]Pure {build['base_class']} build[/bold green]",
        ))

    panel_content = "\n".join(panel_content_lines)

    # Create the panel with shorter title
    panel = Panel(
        panel_content,
        border_style="bright_cyan",
        padding=(1, 2),
        title=f"[bold white]{build['base_class']} Build[/bold white]",
        title_align="center",
    )

    console.print(panel)


def generate_multiple_builds(
    count: int = 5, base_class: str | None = None, num_lines: int | None = None
):
    """Generate multiple random builds using Rich layout."""
    console = Console()

    # Header
    header = Panel(
        Align.center(Text(f"{count} Random ESO Builds", style="bold magenta")),
        border_style="magenta",
        padding=(1, 2),
    )
    console.print(header)
    console.print()

    for i in range(count):
        build = generate_random_build(base_class, num_lines)
        print_build(build)

        if i < count - 1:  # Don't print extra space after last build
            console.print()


def ask_for_retry(
    last_class: str | None = None, was_random: bool = False
) -> tuple[bool, str | None]:
    """Ask user if they want to retry with same class or start over using Rich.

    Raises:
        QuitRequested: If the user presses Q to quit.
    """
    console = Console()

    if last_class:
        console.print()

        # Create options panel
        options_text = []
        if was_random:
            options_text.append("[bold cyan]1.[/bold cyan] Generate another random build")
        else:
            options_text.append(f"[bold cyan]1.[/bold cyan] Generate another {last_class} build")
        options_text.extend((
            "[bold cyan]2.[/bold cyan] Start over (back to main menu)",
            "[bold cyan]Q.[/bold cyan] Quit",
        ))

        options_panel = Panel(
            "\n".join(options_text),
            title="[bold blue]What's next?[/bold blue]",
            border_style="blue",
            padding=(1, 2),
        )
        console.print(options_panel)

        console.print("\n[dim]Press 1, 2, or Q...[/dim]")
        choice = get_single_key()

        if choice == "1":
            return True, last_class if not was_random else None
        if choice == "2":
            return False, None
        if choice == "q":
            raise QuitRequested

        console.print("[yellow]Sorry, that's not a valid option. Please try again.[/yellow]")
        return False, None
    return False, None


def handle_random_build():
    """Handle random build generation with retry logic."""
    clear_screen()
    build = generate_random_build()
    print_build(build)

    # Ask if they want to retry
    retry, retry_class = ask_for_retry(build["base_class"], was_random=True)
    while retry:
        clear_screen()
        build = generate_random_build(retry_class)  # retry_class will be None for random
        print_build(build)
        retry, retry_class = ask_for_retry(build["base_class"], was_random=True)
    clear_screen()


def handle_class_selection():
    """Handle class-specific build generation with retry logic.

    Raises:
        QuitRequested: If the user presses Q to quit.
    """
    console = Console()
    clear_screen()

    while True:
        # Create class selection panel
        class_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        class_table.add_column("Option", style="bold cyan", width=4)
        class_table.add_column("Class", style="white")

        for i, cls in enumerate(CLASSES.keys(), 1):
            class_table.add_row(str(i), cls)

        class_table.add_row("Q", "Quit")

        class_panel = Panel(
            class_table,
            title="[bold yellow]Choose Your Class[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        )

        console.print(class_panel)
        console.print("\n[dim]Choose a class or Q to quit...[/dim]")

        class_choice = get_single_key()
        try:
            if class_choice.lower() == "q":
                raise QuitRequested
            class_index = int(class_choice) - 1
            if 0 <= class_index < len(CLASSES):
                selected_class = list(CLASSES.keys())[class_index]
                clear_screen()
                build = generate_random_build(selected_class)
                print_build(build)

                # Ask if they want to retry
                retry, retry_class = ask_for_retry(selected_class, was_random=False)
                while retry:
                    clear_screen()
                    build = generate_random_build(retry_class)
                    print_build(build)
                    retry, retry_class = ask_for_retry(retry_class, was_random=False)
                break
            # Don't clear screen - show error with context
            error_panel = Panel(
                "[yellow]Sorry, that's not a valid class number. Please try again![/yellow]",
                border_style="yellow",
                padding=(1, 2),
            )
            console.print(error_panel)
            console.print()
        except ValueError:
            # Don't clear screen - show error with context
            error_panel = Panel(
                "[yellow]Please enter a number for the class selection.[/yellow]",
                border_style="yellow",
                padding=(1, 2),
            )
            console.print(error_panel)
            console.print()


def handle_multiple_builds():
    """Handle multiple build generation.

    Raises:
        QuitRequested: If the user presses Q to quit.
    """
    console = Console()
    clear_screen()

    while True:
        # Create input panel
        input_panel = Panel(
            "[bold cyan]Multiple Build Generator[/bold cyan]\n\n"
            + "Configure your batch generation settings:\n\n"
            + "[dim]Press Q at any prompt to quit[/dim]",
            title="[bold yellow]Batch Settings[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        )
        console.print(input_panel)
        console.print()

        try:
            count = Prompt.ask("[cyan]How many builds to generate?[/cyan]", default="5")
            if count.lower() == "q":
                raise QuitRequested
            count = int(count)
            num_lines_input = Prompt.ask(
                "[cyan]How many skill lines to replace?[/cyan] [dim](1, 2, or leave blank for random)[/dim]",
                default="",
            )
            if num_lines_input.lower() == "q":
                raise QuitRequested
            lines: int | None = int(num_lines_input) if num_lines_input else None

            clear_screen()
            generate_multiple_builds(count, num_lines=lines)
            console.print("\n[dim]Press any key to continue...[/dim]")
            get_single_key()
            break
        except ValueError:
            # Don't clear screen - show error with context
            error_panel = Panel(
                "[yellow]Please enter a valid number.[/yellow]",
                border_style="yellow",
                padding=(1, 2),
            )
            console.print(error_panel)
            console.print()


def interactive_mode() -> None:
    """Interactive mode for generating builds using Rich UI.

    Raises:
        QuitRequested: If user presses Q at any point.
    """
    console = Console()
    clear_screen()

    while True:
        try:
            # Create the main menu
            title = Text("ESO Build Randomizer", style="bold magenta")
            subtitle = Text("Interactive Mode", style="dim cyan")

            # Create menu options table
            menu_table = Table(show_header=False, box=None, padding=(0, 2))
            menu_table.add_column("Option", style="bold cyan", width=1)
            menu_table.add_column("Description", style="white")

            menu_table.add_row("1", "Generate random build (any class)")
            menu_table.add_row("2", "Generate build for specific class")
            menu_table.add_row("3", "Generate multiple builds")
            menu_table.add_row("Q", "Quit")

            # Display the menu
            console.print(Align.center(title))
            console.print(Align.center(subtitle))
            console.print()
            console.print(menu_table)
            console.print("\n[dim]Choose an option...[/dim]")

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
                # Don't clear screen - show error with context
                error_panel = Panel(
                    "[yellow]Sorry, that's not a valid option. Try 1, 2, 3, or Q.[/yellow]",
                    border_style="yellow",
                    padding=(0, 2),
                )
                console.print(error_panel)
                console.print()
        except QuitRequested:
            clear_screen()
            break
        except Exception as e:
            console = Console()
            console.print(f"[red]An error occurred: {e}[/red]")
            console.print("\n[dim]Press any key to continue...[/dim]")
            get_single_key()
            clear_screen()


def clear_screen():
    """Clear the terminal screen and position cursor at top-left."""
    console = Console()
    console.clear()
    # Add a small delay to ensure the clear operation completes
    time.sleep(0.05)
    # Force flush to ensure immediate clearing
    sys.stdout.flush()


def get_single_key() -> str:
    """Get a single keypress without requiring Enter.

    Raises:
        QuitRequested: If Q is pressed.
        KeyboardInterrupt: If Ctrl+C is pressed.
    """
    try:
        # Try Unix-style terminal input first
        if hasattr(sys.stdin, "fileno") and sys.stdout.isatty():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                key = sys.stdin.read(1)
                if key == "\x03":  # Ctrl+C
                    raise KeyboardInterrupt
                if key.lower() == "q":
                    raise QuitRequested
                return key.lower()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        else:
            # Fallback when not in a proper terminal
            key = Prompt.ask("Press a key", default="").strip().lower()
            if key == "q":
                raise QuitRequested from None
            return key
    except (ImportError, AttributeError, OSError):
        # Fallback for systems without termios or when not in a proper terminal
        key = Prompt.ask("Press a key", default="").strip().lower()
        if key == "q":
            raise QuitRequested from None
        return key


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
            console = Console()
            console.print("ESO Build Randomizer")
            if args.base_class:
                console.print(f"Generating builds for {args.base_class}...\n")
            else:
                console.print("Generating random builds...\n")

            if args.lines and not 1 <= args.lines <= 2:
                console.print("[yellow]Number of lines to replace should be 1 or 2.[/yellow]")
                return

            generate_multiple_builds(args.number, args.base_class, args.lines)

            console.print(
                "\n[dim]Tip: Use --help to see all options, or -i for interactive mode![/dim]"
            )
    except QuitRequested:
        clear_screen()
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[cyan]Goodbye![/cyan]")
    except Exception as e:
        console = Console()
        console.print(f"[red]An error occurred: {e}[/red]")


if __name__ == "__main__":
    main()
