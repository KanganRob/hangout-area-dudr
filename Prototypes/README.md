# Hangout Area - Python Prototypes

These two small prototypes test the recommended game format: a **co-op open-world action RPG** with a social hub, short expeditions/dungeons, and signature loot.

They are **gameplay prototypes**, not production code. Everything is drawn with tkinter Canvas shapes, so there are no external assets, downloads, or dependencies.

## Requirements

- Python 3.10 or newer (tested on Python 3.14)
- tkinter, which ships with the standard Python installer on Windows

No `pip install` is needed.

## Running

From the repository root:

```powershell
python Prototypes/combat_prototype.py
python Prototypes/hub_prototype.py
```

Headless smoke tests (no window stays open):

```powershell
python Prototypes/combat_prototype.py --smoke-test
python Prototypes/hub_prototype.py --smoke-test
```

---

## 1. Combat Prototype

**File:** `combat_prototype.py`

**What it demonstrates:** the moment-to-moment combat slice - hero selection, role differences, real-time movement, basic attacks, four abilities per hero, mana and cooldowns, enemy waves, a boss, loot pickups, XP, levelling, and win/loss states.

**Heroes:** Anon User (burst/stealth), OPmonkey (vanguard/bruiser), CrushedExpert14 (support/skirmisher).

| Key | Action |
|-|-|
| WASD / Arrow Keys | Move |
| Q / E / R / Space | Use abilities 1-4 |
| H | Help / pause |
| Enter (end screen) | Restart with the same hero |
| M (end screen) | Return to hero select |

**Loop:** pick a hero -> survive two waves -> defeat the Dungeon Warden -> collect the signature cache.

**What to watch for:**

- Do the three heroes feel meaningfully different?
- Is there a reason to move and kite, rather than stand still?
- Are mana costs and cooldowns creating decisions?
- Does the boss fight feel like a step up from the waves?
- Does the signature cache at the end feel like a reward?

**Not included:** co-op networking, final art, animation, equipment inventory, difficulty options.

---

## 2. Hub & Expedition Prototype

**File:** `hub_prototype.py`

**What it demonstrates:** the out-of-combat RPG loop - a walkable hub, NPCs, contracts, trust, permanent shop upgrades, stat checks, expedition risk/reward, signature gear progression, XP, stat points, and inventory.

**Heroes:** YoboyTazza, CrushedExpert14, and OPmonkey, using the out-of-combat stats from their character kits.

| Key | Action |
|-|-|
| WASD / Arrow Keys | Move around the hub |
| E | Interact with the Quest Board, NPCs, or the Expedition Portal |
| C | Character sheet / spend stat points |
| H | Help |
| 1 / 2 / 3 | Pick contracts, expedition approaches, and shop items |
| Esc | Close panels, cancel a briefing, or return to hero select |

### The loop

1. Choose a hero.
2. Walk to the **Quest Board** and accept the signature quest or a repeatable bounty.
3. Talk to **Archivist Miko** to raise trust (Charisma increases the gain).
4. Buy permanent expedition upgrades from **Blacksmith Bram** with gold.
5. Enter the **Expedition Portal**.
6. Clear three stages by choosing an approach tied to an out-of-combat stat.
7. Earn gold, XP, and - on a successful signature expedition - the next piece of your 5-star signature set.
8. Spend stat points, upgrade gear, and go again.

### Expedition rules

- Each stage offers three approaches. The success chance is based on the linked stat.
- A failed check costs vitality. Vitality starts at `100 + 4 x Endurance`, plus shop upgrades.
- Reach the end with **at least 2 of 3 successes** and any vitality left to clear the expedition.
- **Signature quests** award the next signature item: weapon first, then helmet, gloves, chestplate, pants, and boots.
- **Bounties** are repeatable gold/XP contracts with slightly easier checks.
- After all six signature pieces are collected, further signature clears pay bonus gold instead.

### Stat checks

The prototype uses:

```text
success chance = 28% + (stat x 6%) + 2% per Weapon Oil + bounty bonus
```

This is deliberately simple. It is meant to answer: **does choosing an approach based on your character's stats feel good?**

### Signature rewards

| Hero | Signature Weapon | Signature Set |
|-|-|-|
| YoboyTazza | Fate's Dart | Nightstalker |
| CrushedExpert14 | Aether Harp | Oracle's |
| OPmonkey | Bonking Stick | Auroran |

The item names and set structure match [item-list.md](../item-list.md).

**Not included:** real open-world zones, real NPC schedules, co-op, combat inside expeditions, and final art.

---

## Design Notes

### Why two prototypes?

The recommended format has two very different halves:

- **Combat:** fast, real-time, skill-based.
- **Hub/progression:** slower, choice-based, stat-driven.

Building them separately makes it easier to judge each half before combining them into one vertical slice.

### How this maps to the full game

| Prototype | Full game equivalent |
|-|-|
| Combat arena | Open zone, dungeon room, or boss arena |
| Wave timer | Enemy camps, patrols, and dungeon encounters |
| Signature cache | Quest reward or dungeon chest |
| Hub map | Hangout Area social hub |
| Quest Board | Contract and main-story quest givers |
| Expedition Portal | Zone/dungeon selection |
| Three-stage expedition | Short dungeon run with skippable encounters |
| Blacksmith upgrades | Permanent account/character progression |
| Miko trust | NPC trust and dialogue unlocks |

### Deliberate simplifications

- Single-player only; co-op is not implemented yet.
- No real collision, pathfinding, or navmesh in the hub.
- Placeholder shapes and colours instead of characters and environments.
- Expedition stages are abstract stat checks, not playable combat rooms.
- Balance numbers are first-pass guesses, not tuned values.
- No save system; closing the window resets progress.

### Suggested next step

Build a **combined vertical slice**:

- One hub.
- One playable zone connected to the hub.
- One dungeon with a boss.
- Three heroes.
- Loot that drops in combat and is equipped in the hub.
- One signature quest that spans the zone and the dungeon.

That would test whether the combat loop and the hub/progression loop actually support each other. If they do, the next decision is the production engine and art pipeline (for example Godot or Unity) rather than expanding the Python prototypes further.
