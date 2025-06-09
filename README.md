# ESO Build Randomizer 🎲

A Python script that generates random Elder Scrolls Online build combinations following the new subclassing system rules introduced in the game.

## Features

- **Rule-compliant generation**: Follows all ESO subclassing rules
- **Multiple generation modes**: Generate single builds, multiple builds, or use interactive mode
- **Class-specific builds**: Focus on specific classes if desired
- **Beautiful output**: Clean, emoji-enhanced display of build information

## ESO Subclassing Rules

The script follows these official ESO subclassing rules:

1. **Must keep at least one original skill line** - Can't replace all three class skill lines
2. **One skill per other class** - Can't take multiple skills from the same external class
3. **Always subclass** - Every build will have 1 or 2 subclassed skill lines (no pure builds)

## Usage

### Basic Usage

```bash
# Generate 3 random builds (default)
esobuild

# Generate 5 random builds
esobuild -n 5

# Generate builds for a specific class only
esobuild -c Necromancer -n 3
```

### Interactive Mode

```bash
esobuild -i
```

### Command Line Options

- `-n, --number`: Number of builds to generate (default: 3)
- `-c, --class`: Generate builds for specific class only
- `-i, --interactive`: Run in interactive mode
- `-h, --help`: Show help message

## Available Classes & Skill Lines

- **Arcanist**: Herald of the Tome, Soldier of Apocrypha, Curative Runeforms
- **Dragonknight**: Ardent Flame, Draconic Power, Earthen Heart
- **Nightblade**: Assassination, Shadow, Siphoning
- **Sorcerer**: Daedric Summoning, Dark Magic, Storm Calling
- **Templar**: Aedric Spear, Dawn's Wrath, Restoring Light
- **Necromancer**: Grave Lord, Bone Tyrant, Living Death
- **Warden**: Animal Companions, Green Balance, Winter's Embrace

## Example Output

```text
🏛️  Dragonknight Build
==================================================
📜 Skill Lines:
   • Earthen Heart
   • Soldier of Apocrypha (from Arcanist)
   • Siphoning (from Nightblade)

🔄 Subclassed from: Arcanist, Nightblade
💡 Dragonknight with Arcanist, Nightblade subclassing
```

## Tips for Theorycrafting

The randomizer can help you discover unexpected synergies:

- **Tank builds**: Try combining defensive skill lines from different classes
- **Hybrid damage**: Mix magical and physical damage skill lines
- **Support builds**: Combine healing and utility skills from various classes
- **Unique combinations**: Let the randomizer surprise you with combinations you wouldn't normally consider!

Happy theorycrafting! 🎮
