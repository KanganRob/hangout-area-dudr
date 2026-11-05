#!/usr/bin/env python3
"""
Hangout Area - Hub & Expedition Prototype
A small out-of-combat RPG slice built with tkinter only.

Run:
    python Prototypes/hub_prototype.py

Controls:
    WASD / Arrow Keys  - move around the hub
    E                  - interact with a nearby NPC or object
    C                  - character sheet (spend stat points)
    H                  - help
    1 / 2 / 3          - pick cards, contracts, options or shop items
    Esc                - close the current panel
"""

import math
import random
import sys
import time
import tkinter as tk
from dataclasses import dataclass

WIDTH = 1100
HEIGHT = 700
WORLD_LEFT = 24
WORLD_TOP = 96
WORLD_RIGHT = 804
WORLD_BOTTOM = 684

BG = "#0b1020"
PANEL = "#111a33"
PANEL_2 = "#162242"
PANEL_3 = "#1b2b4d"
GRID = "#1b2b4d"
TEXT = "#e8eefc"
MUTED = "#8da2c8"
ACCENT = "#62e6c8"
GOLD = "#ffd166"
RED = "#ff5d73"
BLUE = "#63b3ff"
PURPLE = "#b388ff"
GREEN = "#7ee081"
ORANGE = "#ff9f43"

STAT_KEYS = [
    "Agility",
    "Charisma",
    "Endurance",
    "Intelligence",
    "Luck",
    "Perception",
    "Strength",
]

STAT_BLURB = {
    "Agility": "+5% movement speed per point",
    "Charisma": "+5% NPC trust per point",
    "Endurance": "+1 pack slot, +20 carry weight, +4 expedition vitality",
    "Intelligence": "+2% XP gain per point",
    "Luck": "+5% better loot per point",
    "Perception": "+5% critical-hit chance per point",
    "Strength": "+5% damage multiplier per point",
}

SHOP = [
    {
        "id": "oil",
        "name": "Weapon Oil",
        "desc": "+2% success chance on expedition stat checks. Permanent.",
        "base": 120,
        "step": 100,
        "max": 10,
    },
    {
        "id": "rations",
        "name": "Trail Rations",
        "desc": "+5 maximum expedition vitality. Permanent.",
        "base": 90,
        "step": 80,
        "max": 10,
    },
    {
        "id": "coin",
        "name": "Lucky Coin",
        "desc": "+1 Luck for loot rolls. Permanent.",
        "base": 160,
        "step": 140,
        "max": 3,
    },
]

SIGNATURE_GEAR = {
    "YoboyTazza": [
        "Fate's Dart",
        "Nightstalker Hood",
        "Nightstalker Claws",
        "Nightstalker Vest",
        "Nightstalker Leggings",
        "Nightstalker Boots",
    ],
    "CrushedExpert14": [
        "Aether Harp",
        "Oracle's Circlet",
        "Oracle's Gloves",
        "Oracle's Vestments",
        "Oracle's Skirt",
        "Oracle's Sandals",
    ],
    "OPmonkey": [
        "Bonking Stick",
        "Auroran Helm",
        "Auroran Gauntlets",
        "Auroran Cuirass",
        "Auroran Tassets",
        "Auroran Greaves",
    ],
}

STAGES = [
    {
        "name": "The Collapsed Gate",
        "prompt": (
            "A wall of rubble blocks the only dry entrance into the ruin. "
            "Something inside scrapes against stone, waiting."
        ),
        "options": [
            {
                "label": "Heave the slabs aside",
                "stat": "Strength",
                "text": "Brute force. Loud, but it gets the job done.",
            },
            {
                "label": "Climb the broken arch",
                "stat": "Agility",
                "text": "A quick route over the rubble and through the gap.",
            },
            {
                "label": "Decode the old seal",
                "stat": "Intelligence",
                "text": "Find the mechanism that the last explorers missed.",
            },
        ],
    },
    {
        "name": "The Flooded Hall",
        "prompt": (
            "Knee-deep water fills a hall lined with sealed doors. "
            "A pale shape moves beneath the surface."
        ),
        "options": [
            {
                "label": "Parley with the echo",
                "stat": "Charisma",
                "text": "Convince the guardian that you mean no harm.",
            },
            {
                "label": "Scout a safe path",
                "stat": "Perception",
                "text": "Watch the water and pick out the solid stones.",
            },
            {
                "label": "Swim for the far door",
                "stat": "Endurance",
                "text": "Hold your breath and push straight through.",
            },
        ],
    },
    {
        "name": "The Heart of the Ruin",
        "prompt": (
            "The archive chamber opens before you. A hulking warden "
            "guards the prize, and the room is starting to collapse."
        ),
        "options": [
            {
                "label": "Strike at the weak point",
                "stat": "Luck",
                "text": "Trust your instincts and take the one clean shot.",
            },
            {
                "label": "Break the binding ritual",
                "stat": "Intelligence",
                "text": "Untangle the runes empowering the warden.",
            },
            {
                "label": "Meet it head-on",
                "stat": "Strength",
                "text": "A straight fight. Exactly what it wants.",
            },
        ],
    },
]


def make_heroes():
    return [
        {
            "name": "YoboyTazza",
            "role": "Assassin / Trickster",
            "color": "#8b5cf6",
            "accent": "#c4b5fd",
            "quest": "A Whisper in the Dark",
            "zone": "Nightmarket Rooftops",
            "hook": "Blink and you'll miss him. Literally.",
            "stats": {
                "Agility": 5,
                "Charisma": 4,
                "Endurance": 3,
                "Intelligence": 8,
                "Luck": 4,
                "Perception": 7,
                "Strength": 4,
            },
            "level": 1,
            "xp": 0,
            "xp_next": 120,
            "stat_points": 0,
            "gold": 120,
            "trust": 10,
            "loot_index": 0,
            "completed": 0,
            "inventory": ["Traveller's Pack", "Wayfarer's Hood"],
            "upgrades": {"oil": 0, "rations": 0, "coin": 0},
        },
        {
            "name": "CrushedExpert14",
            "role": "Support / Skirmisher",
            "color": "#2fb98d",
            "accent": "#b8ffe8",
            "quest": "The Crying Chord",
            "zone": "Resonance Halls",
            "hook": "That one insane guy who heals and buffs his allies.",
            "stats": {
                "Agility": 4,
                "Charisma": 3,
                "Endurance": 5,
                "Intelligence": 4,
                "Luck": 10,
                "Perception": 3,
                "Strength": 6,
            },
            "level": 1,
            "xp": 0,
            "xp_next": 120,
            "stat_points": 0,
            "gold": 120,
            "trust": 10,
            "loot_index": 0,
            "completed": 0,
            "inventory": ["Traveller's Pack", "Wayfarer's Hood"],
            "upgrades": {"oil": 0, "rations": 0, "coin": 0},
        },
        {
            "name": "OPmonkey",
            "role": "Vanguard / Bruiser",
            "color": "#c77b30",
            "accent": "#ffd7a8",
            "quest": "The Old Master's Debt",
            "zone": "Bamboo Graveyard",
            "hook": "A real old fella with a bone to pick.",
            "stats": {
                "Agility": 2,
                "Charisma": 2,
                "Endurance": 10,
                "Intelligence": 2,
                "Luck": 5,
                "Perception": 4,
                "Strength": 10,
            },
            "level": 1,
            "xp": 0,
            "xp_next": 120,
            "stat_points": 0,
            "gold": 120,
            "trust": 10,
            "loot_index": 0,
            "completed": 0,
            "inventory": ["Traveller's Pack", "Wayfarer's Hood"],
            "upgrades": {"oil": 0, "rations": 0, "coin": 0},
        },
    ]


@dataclass
class Toast:
    text: str
    color: str = TEXT
    life: float = 3.0


@dataclass
class Interactable:
    kind: str
    name: str
    x: float
    y: float
    color: str


class Game:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.heroes = make_heroes()
        self.hero = None
        self.hero_index = 0
        self.rng = random.Random()

        self.state = "menu"
        self.prev_state = "hub"
        self.time = 0.0
        self.last_time = time.perf_counter()
        self.keys = set()
        self.toasts = []
        self.menu_cards = []
        self.option_cards = []

        self.player_x = 400
        self.player_y = 560
        self.facing_x = 0
        self.facing_y = -1

        self.active_contract_id = None
        self.quest_message = ""

        self.dialogue_lines = []
        self.dialogue_index = 0
        self.dialogue_name = ""
        self.dialogue_color = ACCENT

        self.stage_index = 0
        self.successes = 0
        self.crits = 0
        self.vitality = 100
        self.stage_result = None
        self.stage_log = []
        self.expedition_gold = 0
        self.expedition_xp = 0
        self.expedition_loot = []
        self.debrief = None
        self.shop_message = ""
        self.help_return = "hub"

        self.interactables = [
            Interactable("board", "Quest Board", 145, 255, GOLD),
            Interactable("miko", "Archivist Miko", 300, 238, BLUE),
            Interactable("bram", "Blacksmith Bram", 560, 238, ORANGE),
            Interactable("portal", "Expedition Portal", 650, 520, PURPLE),
        ]

        root.bind("<KeyPress>", self.on_key_press)
        root.bind("<KeyRelease>", self.on_key_release)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.focus_set()

    # ------------------------------------------------------------------ input
    def on_key_press(self, event):
        key = event.keysym.lower()
        if key in self.keys:
            return
        self.keys.add(key)

        if self.state == "menu":
            if key in ("1", "2", "3"):
                self.start_hero(int(key) - 1)
            elif key == "h":
                self.help_return = "menu"
                self.state = "help"
        elif self.state == "hub":
            if key == "e":
                self.interact()
            elif key == "c":
                self.open_sheet()
            elif key == "h":
                self.help_return = "hub"
                self.state = "help"
            elif key == "escape":
                self.state = "menu"
        elif self.state == "help":
            if key in ("h", "escape", "space", "return"):
                self.state = self.help_return
        elif self.state == "dialogue":
            if key in ("e", "space", "return"):
                self.advance_dialogue()
            elif key == "escape":
                self.close_dialogue()
        elif self.state == "board":
            if key in ("1", "2"):
                self.accept_contract(int(key) - 1)
            elif key in ("escape", "e"):
                self.state = "hub"
        elif self.state == "shop":
            if key in ("1", "2", "3"):
                self.buy_upgrade(int(key) - 1)
            elif key in ("escape", "e"):
                self.state = "hub"
        elif self.state == "sheet":
            if key in ("1", "2", "3", "4", "5", "6", "7"):
                self.allocate_stat(int(key) - 1)
            elif key in ("escape", "c"):
                self.state = "hub"
        elif self.state == "prep":
            if key in ("e", "space", "return"):
                self.begin_expedition()
            elif key == "escape":
                self.state = "hub"
        elif self.state == "expedition":
            if self.stage_result:
                if key in ("e", "space", "return"):
                    self.continue_expedition()
            elif key in ("1", "2", "3"):
                self.choose_option(int(key) - 1)
        elif self.state == "debrief":
            if key in ("e", "space", "return", "escape"):
                self.leave_debrief()

    def on_key_release(self, event):
        self.keys.discard(event.keysym.lower())

    def on_click(self, event):
        if self.state == "menu":
            for index, (x1, y1, x2, y2) in enumerate(self.menu_cards):
                if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                    self.start_hero(index)
                    return
        elif self.state == "expedition":
            if self.stage_result:
                self.continue_expedition()
                return
            for index, (x1, y1, x2, y2) in enumerate(self.option_cards):
                if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                    self.choose_option(index)
                    return

    # ------------------------------------------------------------------ helpers
    def toast(self, text, color=TEXT):
        self.toasts.append(Toast(text, color))
        if len(self.toasts) > 5:
            self.toasts.pop(0)

    def current_contract(self):
        if not self.hero or not self.active_contract_id:
            return None
        if self.active_contract_id == "signature":
            return {
                "id": "signature",
                "title": self.hero["quest"],
                "zone": self.hero["zone"],
                "desc": "Recover the signature cache. Each success awards the next piece of your 5-star gear.",
                "reward": "1 signature piece + 120 gold + 80 XP",
            }
        return {
            "id": "bounty",
            "title": "Bounty: Bandit Tide",
            "zone": "Shoreline Caves",
            "desc": "A repeatable contract with easier checks and a flat payout.",
            "reward": "150 gold + 60 XP",
        }

    def upgrade_count(self, upgrade_id):
        return self.hero["upgrades"][upgrade_id]

    def success_bonus(self):
        return self.upgrade_count("oil") * 0.02

    def luck_bonus(self):
        return self.upgrade_count("coin")

    def max_vitality(self):
        return 100 + self.hero["stats"]["Endurance"] * 4 + self.upgrade_count("rations") * 5

    def success_chance(self, stat, extra=0.0):
        value = self.hero["stats"].get(stat, 0)
        chance = 0.28 + value * 0.06 + self.success_bonus() + extra
        return max(0.15, min(0.95, chance))

    def nearest_interactable(self):
        best = None
        best_dist = 76
        for item in self.interactables:
            dist = math.hypot(item.x - self.player_x, item.y - self.player_y)
            if dist < best_dist:
                best = item
                best_dist = dist
        return best

    # ------------------------------------------------------------------ states
    def start_hero(self, index):
        self.hero_index = index
        self.hero = self.heroes[index]
        self.state = "hub"
        self.player_x = 400
        self.player_y = 560
        self.active_contract_id = None
        self.stage_result = None
        self.debrief = None
        self.shop_message = ""
        self.toasts.clear()
        self.toast(f"{self.hero['name']} arrives at the Hangout Area", self.hero["accent"])

    def open_board(self):
        self.state = "board"

    def accept_contract(self, index):
        if index == 0:
            self.active_contract_id = "signature"
            self.quest_message = f"Accepted: {self.hero['quest']}"
            self.toast(self.quest_message, GOLD)
        elif index == 1:
            self.active_contract_id = "bounty"
            self.quest_message = "Accepted: Bounty - Bandit Tide"
            self.toast(self.quest_message, GOLD)
        self.state = "hub"

    def open_dialogue(self):
        self.dialogue_name = "Archivist Miko"
        self.dialogue_color = BLUE
        self.dialogue_lines = [
            "Ah, another face from the Hangout Area. Come to poke at the old ruins?",
            "The place you're headed to is older than the guild's records. The wards react to whoever walks in.",
            "Talk to me between expeditions. Trust opens doors that a crowbar never will.",
        ]
        self.dialogue_index = 0
        self.state = "dialogue"

    def advance_dialogue(self):
        self.dialogue_index += 1
        if self.dialogue_index >= len(self.dialogue_lines):
            self.close_dialogue()

    def close_dialogue(self):
        gain = 2 + self.hero["stats"]["Charisma"] // 3
        self.hero["trust"] = min(100, self.hero["trust"] + gain)
        self.toast(f"Miko's trust +{gain} (now {self.hero['trust']})", BLUE)
        self.state = "hub"

    def open_shop(self):
        self.shop_message = "Bram grunts. 'Coin first. Then I'll make it worth your while.'"
        self.state = "shop"

    def buy_upgrade(self, index):
        item = SHOP[index]
        count = self.upgrade_count(item["id"])
        if count >= item["max"]:
            self.shop_message = f"{item['name']} is already fully upgraded."
            return
        cost = item["base"] + count * item["step"]
        if self.hero["gold"] < cost:
            self.shop_message = f"Not enough gold. {item['name']} costs {cost}."
            return
        self.hero["gold"] -= cost
        self.hero["upgrades"][item["id"]] += 1
        self.shop_message = f"Bought {item['name']} for {cost} gold."
        self.toast(f"{item['name']} upgraded", ORANGE)

    def open_sheet(self):
        self.state = "sheet"

    def allocate_stat(self, index):
        if self.hero["stat_points"] <= 0:
            self.toast("No stat points available. Complete expeditions to level up.", MUTED)
            return
        stat = STAT_KEYS[index]
        if self.hero["stats"][stat] >= 10:
            self.toast(f"{stat} is already at its cap of 10.", MUTED)
            return
        self.hero["stats"][stat] += 1
        self.hero["stat_points"] -= 1
        self.toast(f"{stat} increased to {self.hero['stats'][stat]}", ACCENT)

    def open_portal(self):
        if not self.active_contract_id:
            self.toast("The portal is dormant. Accept a contract at the board first.", MUTED)
            return
        self.state = "prep"

    def begin_expedition(self):
        self.stage_index = 0
        self.successes = 0
        self.crits = 0
        self.vitality = self.max_vitality()
        self.stage_result = None
        self.stage_log = []
        self.expedition_gold = 0
        self.expedition_xp = 0
        self.expedition_loot = []
        self.debrief = None
        self.state = "expedition"
        self.toast(f"Expedition started: {self.current_contract()['zone']}", PURPLE)

    def choose_option(self, index):
        if self.stage_result:
            return
        stage = STAGES[self.stage_index]
        if index >= len(stage["options"]):
            return
        option = stage["options"][index]
        extra = 0.08 if self.active_contract_id == "bounty" else 0.0
        chance = self.success_chance(option["stat"], extra)
        roll = self.rng.random()

        endurance = self.hero["stats"]["Endurance"]
        luck = self.hero["stats"]["Luck"] + self.luck_bonus()
        intel = self.hero["stats"]["Intelligence"]

        if roll < chance * 0.3:
            outcome = "critical"
            self.successes += 1
            self.crits += 1
            gold = (self.rng.randint(34, 56) + luck * 5) * 2
            xp = (18 + intel + self.rng.randint(0, 10)) * 2
            headline = "CRITICAL SUCCESS"
            body = f"{option['label']} goes better than anyone could have hoped."
            tone = GOLD
            damage = 0
        elif roll < chance:
            outcome = "success"
            self.successes += 1
            gold = self.rng.randint(28, 48) + luck * 5
            xp = 18 + intel + self.rng.randint(0, 10)
            headline = "SUCCESS"
            body = f"{option['label']} works. You press deeper into the ruin."
            tone = GREEN
            damage = 0
        else:
            outcome = "failure"
            gold = self.rng.randint(6, 14)
            xp = 6
            damage = max(12, 28 - endurance)
            self.vitality = max(0, self.vitality - damage)
            headline = "SETBACK"
            body = f"{option['label']} fails, and the ruin makes you pay for it."
            tone = RED

        if self.active_contract_id == "bounty":
            gold = int(gold * 1.2)

        self.expedition_gold += gold
        self.expedition_xp += xp
        self.stage_result = {
            "status": outcome,
            "headline": headline,
            "body": body,
            "tone": tone,
            "gold": gold,
            "xp": xp,
            "damage": damage,
            "chance": chance,
            "option": option,
        }
        self.stage_log.append(
            {
                "stage": stage["name"],
                "status": outcome,
                "gold": gold,
                "xp": xp,
                "damage": damage,
                "text": f"{stage['name']}: {headline.lower()} (+{gold}g, +{xp} XP)",
            }
        )

    def continue_expedition(self):
        if not self.stage_result:
            return
        self.stage_result = None
        if self.stage_index < len(STAGES) - 1:
            self.stage_index += 1
        else:
            self.finish_expedition()

    def finish_expedition(self):
        contract = self.current_contract()
        success = self.vitality > 0 and self.successes >= 2
        bonus_gold = 0
        bonus_xp = 0
        loot = []

        if success:
            if contract["id"] == "bounty":
                bonus_gold = 150
                bonus_xp = 60
            else:
                bonus_gold = 120
                bonus_xp = 80
                loot.append(self.grant_signature_piece())
                self.hero["completed"] += 1

        total_gold = self.expedition_gold + bonus_gold
        total_xp = self.expedition_xp + bonus_xp
        self.hero["gold"] += total_gold
        self.gain_xp(total_xp)

        if contract["id"] == "signature" and success:
            self.expedition_loot = loot
        else:
            self.expedition_loot = []

        self.debrief = {
            "success": success,
            "title": contract["title"],
            "zone": contract["zone"],
            "score": f"{self.successes}/{len(STAGES)} checks passed",
            "gold": total_gold,
            "xp": total_xp,
            "loot": loot,
            "log": list(self.stage_log),
            "vitality": self.vitality,
        }
        self.state = "debrief"
        if success:
            self.toast("Expedition complete!", GOLD)
        else:
            self.toast("Expedition failed. The contract remains open.", RED)

    def grant_signature_piece(self):
        hero = self.hero
        gear = SIGNATURE_GEAR[hero["name"]]
        if hero["loot_index"] < len(gear):
            item = gear[hero["loot_index"]]
            hero["loot_index"] += 1
            hero["inventory"].append(item)
            return item
        hero["gold"] += 300
        return "300 gold (signature set complete)"

    def gain_xp(self, amount):
        hero = self.hero
        hero["xp"] += amount
        while hero["xp"] >= hero["xp_next"]:
            hero["xp"] -= hero["xp_next"]
            hero["level"] += 1
            hero["xp_next"] = int(hero["xp_next"] * 1.35)
            hero["stat_points"] += 1
            self.toast(f"LEVEL {hero['level']}! +1 stat point", ACCENT)

    def leave_debrief(self):
        self.state = "hub"
        self.player_x = 650
        self.player_y = 585
        self.debrief = None
        self.stage_result = None

    def interact(self):
        item = self.nearest_interactable()
        if not item:
            self.toast("Nothing close enough to interact with.", MUTED)
            return
        if item.kind == "board":
            self.open_board()
        elif item.kind == "miko":
            self.open_dialogue()
        elif item.kind == "bram":
            self.open_shop()
        elif item.kind == "portal":
            self.open_portal()

    # ------------------------------------------------------------------ update
    def update(self, dt):
        self.time += dt
        for toast in self.toasts:
            toast.life -= dt
        self.toasts = [t for t in self.toasts if t.life > 0]

        if self.state != "hub":
            return

        mx = 0
        my = 0
        if "a" in self.keys or "left" in self.keys:
            mx -= 1
        if "d" in self.keys or "right" in self.keys:
            mx += 1
        if "w" in self.keys or "up" in self.keys:
            my -= 1
        if "s" in self.keys or "down" in self.keys:
            my += 1
        if mx or my:
            length = math.hypot(mx, my)
            mx /= length
            my /= length
            self.facing_x, self.facing_y = mx, my
            speed = 220 + self.hero["stats"]["Agility"] * 10
            self.player_x += mx * speed * dt
            self.player_y += my * speed * dt
            self.player_x = max(WORLD_LEFT + 18, min(WORLD_RIGHT - 18, self.player_x))
            self.player_y = max(WORLD_TOP + 18, min(WORLD_BOTTOM - 18, self.player_y))

    # ------------------------------------------------------------------ draw
    def draw(self):
        self.canvas.delete("all")
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "hub":
            self.draw_hub()
        elif self.state == "help":
            self.draw_help()
        elif self.state == "dialogue":
            self.draw_dialogue()
        elif self.state == "board":
            self.draw_board()
        elif self.state == "shop":
            self.draw_shop()
        elif self.state == "sheet":
            self.draw_sheet()
        elif self.state == "prep":
            self.draw_prep()
        elif self.state == "expedition":
            self.draw_expedition()
        elif self.state == "debrief":
            self.draw_debrief()
        self.draw_toasts()

    def draw_background(self):
        c = self.canvas
        c.create_rectangle(0, 0, WIDTH, HEIGHT, fill=BG, outline="")
        for x in range(0, WIDTH, 44):
            c.create_line(x, 0, x, HEIGHT, fill="#131c31")
        for y in range(0, HEIGHT, 44):
            c.create_line(0, y, WIDTH, y, fill="#131c31")

    def draw_menu(self):
        self.draw_background()
        c = self.canvas
        c.create_text(WIDTH / 2, 54, text="HANGOUT AREA", fill=TEXT, font=("Segoe UI", 30, "bold"))
        c.create_text(
            WIDTH / 2,
            88,
            text="Hub & Expedition Prototype  -  Choose your hero",
            fill=MUTED,
            font=("Segoe UI", 13),
        )

        self.menu_cards = []
        card_w, card_h = 310, 500
        gap = 26
        start_x = (WIDTH - (card_w * 3 + gap * 2)) / 2
        top = 122
        for i, data in enumerate(self.heroes):
            x1 = start_x + i * (card_w + gap)
            y1 = top
            x2 = x1 + card_w
            y2 = y1 + card_h
            self.menu_cards.append((x1, y1, x2, y2))
            gear = SIGNATURE_GEAR[data["name"]]
            c.create_rectangle(x1, y1, x2, y2, fill=PANEL, outline=data["color"], width=2)
            c.create_rectangle(x1, y1, x2, y1 + 92, fill=data["color"], outline="")
            c.create_text(x1 + 20, y1 + 22, text=f"{i + 1}", fill=BG, font=("Segoe UI", 15, "bold"), anchor="w")
            c.create_text(x1 + 20, y1 + 50, text=data["name"], fill=BG, font=("Segoe UI", 18, "bold"), anchor="w")
            c.create_text(x1 + 20, y1 + 73, text=data["role"], fill=BG, font=("Segoe UI", 10), anchor="w")

            c.create_text(x1 + 20, y1 + 114, text=data["hook"], fill=MUTED, font=("Segoe UI", 9), anchor="w", width=card_w - 40)
            c.create_text(x1 + 20, y1 + 152, text="OUT-OF-COMBAT STATS", fill=MUTED, font=("Segoe UI", 9, "bold"), anchor="w")
            for n, stat in enumerate(STAT_KEYS):
                y = y1 + 178 + n * 23
                value = data["stats"][stat]
                c.create_text(x1 + 20, y, text=stat, fill=TEXT, font=("Segoe UI", 10), anchor="w")
                c.create_rectangle(x1 + 128, y - 5, x1 + 262, y + 5, fill="#22304f", outline="")
                c.create_rectangle(x1 + 128, y - 5, x1 + 128 + 134 * (value / 10), y + 5, fill=data["accent"], outline="")
                c.create_text(x1 + 282, y, text=str(value), fill=data["accent"], font=("Consolas", 10, "bold"), anchor="e")

            c.create_text(x1 + 20, y1 + 366, text="SIGNATURE QUEST", fill=MUTED, font=("Segoe UI", 9, "bold"), anchor="w")
            c.create_text(x1 + 20, y1 + 388, text=data["quest"], fill=GOLD, font=("Segoe UI", 11, "bold"), anchor="w", width=card_w - 40)
            c.create_text(x1 + 20, y1 + 410, text=data["zone"], fill=MUTED, font=("Segoe UI", 9), anchor="w")
            c.create_text(x1 + 20, y1 + 438, text=f"Signature weapon: {gear[0]}", fill=GOLD, font=("Segoe UI", 9), anchor="w", width=card_w - 40)
            c.create_text(x1 + 20, y1 + 466, text="Click or press number to begin", fill=data["accent"], font=("Segoe UI", 9), anchor="w")

        c.create_text(
            WIDTH / 2,
            HEIGHT - 28,
            text="WASD / Arrows to move  -  E to interact  -  C character sheet  -  H help",
            fill=MUTED,
            font=("Segoe UI", 11),
        )

    def draw_hub(self):
        self.draw_background()
        c = self.canvas
        hero = self.hero

        c.create_rectangle(WORLD_LEFT, WORLD_TOP, WORLD_RIGHT, WORLD_BOTTOM, fill="#122029", outline="#28405a", width=2)
        # paths
        for target in [(145, 255), (300, 238), (560, 238), (650, 520), (400, 560)]:
            c.create_line(400, 430, target[0], target[1], fill="#1b3143", width=38, capstyle="round")
        c.create_oval(320, 350, 480, 510, fill="#1b3143", outline="#2c4a63", width=2)
        c.create_oval(345, 375, 455, 485, fill="#0e1b27", outline="#2c4a63", width=2)
        c.create_oval(375, 405, 425, 455, fill="#1b3143", outline="")

        # trees
        for tx, ty in [(70, 140), (90, 330), (70, 610), (720, 150), (760, 320), (240, 620), (720, 640)]:
            c.create_oval(tx - 18, ty, tx + 18, ty + 36, fill="#173a2f", outline="")
            c.create_oval(tx - 20, ty - 22, tx + 20, ty + 10, fill="#1e4a3a", outline="")

        # library + forge
        self.draw_building(220, 120, 380, 195, "#233a63", "#2f4d80", BLUE, "ARCHIVE")
        self.draw_building(480, 120, 640, 195, "#4a2c1c", "#673d25", ORANGE, "FORGE")
        c.create_text(300, 213, text="Archivist Miko", fill=BLUE, font=("Segoe UI", 9, "bold"))
        c.create_text(560, 213, text="Blacksmith Bram", fill=ORANGE, font=("Segoe UI", 9, "bold"))

        # quest board
        c.create_rectangle(112, 186, 178, 246, fill="#5b3d22", outline="#8a6136", width=2)
        c.create_rectangle(120, 194, 170, 238, fill="#2e4560", outline="")
        c.create_text(145, 202, text="!", fill=GOLD, font=("Segoe UI", 14, "bold"))
        c.create_line(145, 246, 145, 266, fill="#8a6136", width=3)
        c.create_text(145, 276, text="Quest Board", fill=GOLD, font=("Segoe UI", 9, "bold"))

        # portal
        pulse = math.sin(self.time * 3) * 3
        c.create_oval(650 - 48 - pulse, 520 - 48 - pulse, 650 + 48 + pulse, 520 + 48 + pulse, outline="#3b2a66", width=4)
        c.create_oval(650 - 34, 520 - 34, 650 + 34, 520 + 34, fill="#231243", outline=PURPLE, width=2)
        c.create_oval(650 - 20, 520 - 20, 650 + 20, 520 + 20, fill="#3a2170", outline="")
        c.create_text(650, 520, text="RIFT", fill="#e2d4ff", font=("Segoe UI", 9, "bold"))
        c.create_text(650, 580, text="Expedition Portal", fill=PURPLE, font=("Segoe UI", 9, "bold"))
        if self.active_contract_id:
            c.create_text(650, 596, text=self.current_contract()["zone"], fill=MUTED, font=("Segoe UI", 8))

        # NPCs
        self.draw_npc(300, 238, BLUE, "M")
        self.draw_npc(560, 238, ORANGE, "B")

        # player
        px, py = self.player_x, self.player_y
        c.create_oval(px - 19, py - 19, px + 19, py + 19, fill=hero["color"], outline=hero["accent"], width=3)
        c.create_text(px, py, text=hero["name"][0], fill=BG, font=("Segoe UI", 14, "bold"))
        c.create_text(px, py + 30, text=hero["name"], fill=hero["accent"], font=("Segoe UI", 9, "bold"))

        near = self.nearest_interactable()
        if near:
            c.create_rectangle(WORLD_LEFT + 150, WORLD_BOTTOM - 54, WORLD_RIGHT - 150, WORLD_BOTTOM - 18, fill=PANEL_2, outline=near.color, width=2)
            c.create_text(
                (WORLD_LEFT + WORLD_RIGHT) / 2,
                WORLD_BOTTOM - 36,
                text=f"E  -  Talk to {near.name}" if near.kind in ("miko",) else f"E  -  {near.name}",
                fill=near.color,
                font=("Segoe UI", 11, "bold"),
            )

        self.draw_top_bar()
        self.draw_sidebar()

    def draw_building(self, x1, y1, x2, y2, base, roof, accent, label):
        c = self.canvas
        c.create_rectangle(x1, y1 + 28, x2, y2, fill=base, outline=accent, width=1)
        c.create_polygon(x1 - 8, y1 + 30, (x1 + x2) / 2, y1 - 6, x2 + 8, y1 + 30, fill=roof, outline="")
        c.create_rectangle((x1 + x2) / 2 - 16, y2 - 30, (x1 + x2) / 2 + 16, y2, fill="#101a2a", outline=accent, width=1)
        c.create_text((x1 + x2) / 2, y1 + 50, text=label, fill=TEXT, font=("Segoe UI", 10, "bold"))

    def draw_npc(self, x, y, color, letter):
        c = self.canvas
        c.create_oval(x - 16, y + 18, x + 16, y + 24, fill="#0a121c", outline="")
        c.create_oval(x - 16, y - 16, x + 16, y + 16, fill=color, outline="#f4f8ff", width=1)
        c.create_text(x, y, text=letter, fill=BG, font=("Segoe UI", 12, "bold"))

    def draw_top_bar(self):
        c = self.canvas
        hero = self.hero
        c.create_rectangle(0, 0, WIDTH, 84, fill=PANEL, outline="")
        c.create_text(24, 20, text=f"HANGOUT AREA  -  {hero['name']}", fill=hero["accent"], font=("Segoe UI", 15, "bold"), anchor="w")
        c.create_text(24, 43, text=f"{hero['role']}  -  Level {hero['level']}", fill=MUTED, font=("Segoe UI", 9), anchor="w")
        self.bar(24, 58, 250, 10, hero["xp"] / hero["xp_next"], GOLD, f"XP {hero['xp']}/{hero['xp_next']}")
        c.create_text(300, 20, text=f"GOLD {hero['gold']}", fill=GOLD, font=("Consolas", 11, "bold"), anchor="w")
        c.create_text(300, 40, text=f"TRUST {hero['trust']}/100", fill=BLUE, font=("Consolas", 10), anchor="w")
        contract = self.current_contract()
        if contract:
            c.create_text(480, 20, text=f"CONTRACT: {contract['title']}", fill=ACCENT, font=("Segoe UI", 10, "bold"), anchor="w")
            c.create_text(480, 40, text=f"Zone: {contract['zone']}", fill=MUTED, font=("Segoe UI", 9), anchor="w")
        else:
            c.create_text(480, 20, text="NO ACTIVE CONTRACT", fill=MUTED, font=("Segoe UI", 10, "bold"), anchor="w")
            c.create_text(480, 40, text="Visit the Quest Board to accept one.", fill=MUTED, font=("Segoe UI", 9), anchor="w")
        c.create_text(WIDTH - 24, 20, text="H  Help", fill=MUTED, font=("Segoe UI", 9), anchor="e")
        c.create_text(WIDTH - 24, 40, text="Esc  Hero select", fill=MUTED, font=("Segoe UI", 9), anchor="e")

    def draw_sidebar(self):
        c = self.canvas
        hero = self.hero
        x = 812
        y = WORLD_TOP
        c.create_rectangle(x, y, WIDTH - 8, WORLD_BOTTOM, fill=PANEL, outline="#25405f", width=1)
        c.create_text(x + 14, y + 20, text=hero["name"], fill=hero["accent"], font=("Segoe UI", 13, "bold"), anchor="w")
        c.create_text(x + 14, y + 40, text=f"Level {hero['level']}  -  {hero['role']}", fill=MUTED, font=("Segoe UI", 8), anchor="w")

        c.create_text(x + 14, y + 66, text="OUT-OF-COMBAT STATS", fill=MUTED, font=("Segoe UI", 8, "bold"), anchor="w")
        for n, stat in enumerate(STAT_KEYS):
            row_y = y + 88 + n * 21
            value = hero["stats"][stat]
            c.create_text(x + 14, row_y, text=stat[:4], fill=TEXT, font=("Segoe UI", 9), anchor="w")
            c.create_rectangle(x + 54, row_y - 4, x + 186, row_y + 4, fill="#22304f", outline="")
            c.create_rectangle(x + 54, row_y - 4, x + 54 + 132 * (value / 10), row_y + 4, fill=hero["accent"], outline="")
            c.create_text(x + 262, row_y, text=str(value), fill=hero["accent"], font=("Consolas", 9, "bold"), anchor="e")

        points_y = y + 244
        c.create_text(x + 14, points_y, text=f"STAT POINTS: {hero['stat_points']}", fill=GOLD if hero["stat_points"] else MUTED, font=("Consolas", 9, "bold"), anchor="w")
        c.create_text(x + 14, points_y + 17, text="Press C to spend points", fill=MUTED, font=("Segoe UI", 8), anchor="w")

        c.create_text(x + 14, y + 282, text="SIGNATURE SET", fill=MUTED, font=("Segoe UI", 8, "bold"), anchor="w")
        gear = SIGNATURE_GEAR[hero["name"]]
        piece = gear[min(hero["loot_index"], len(gear) - 1)] if hero["loot_index"] < len(gear) else "Set complete"
        c.create_text(x + 14, y + 302, text=f"{hero['loot_index']}/6 collected", fill=GOLD, font=("Segoe UI", 9, "bold"), anchor="w")
        c.create_text(x + 14, y + 320, text=f"Next: {piece}", fill=TEXT, font=("Segoe UI", 8), anchor="w", width=260)

        c.create_text(x + 14, y + 346, text="PACK", fill=MUTED, font=("Segoe UI", 8, "bold"), anchor="w")
        shown = hero["inventory"][-5:][::-1]
        for n, item in enumerate(shown):
            color = GOLD if item in gear else TEXT
            c.create_text(x + 14, y + 364 + n * 16, text=f"- {item}", fill=color, font=("Segoe UI", 8), anchor="w", width=260)

        c.create_text(x + 14, y + 452, text="FIELD NOTES", fill=MUTED, font=("Segoe UI", 8, "bold"), anchor="w")
        notes = [
            f"Quest completions: {hero['completed']}",
            f"Expedition vitality: {self.max_vitality()}",
            f"Check bonus: +{int(self.success_bonus() * 100)}%   Luck +{self.luck_bonus()}",
        ]
        for n, line in enumerate(notes):
            c.create_text(x + 14, y + 470 + n * 17, text=line, fill=TEXT, font=("Segoe UI", 8), anchor="w")

        c.create_text(x + 14, y + 522, text="CONTROLS", fill=MUTED, font=("Segoe UI", 8, "bold"), anchor="w")
        controls = ["WASD / Arrows  move", "E  interact   -   C  sheet", "H  help   -   Esc  hero select"]
        for n, line in enumerate(controls):
            c.create_text(x + 14, y + 540 + n * 15, text=line, fill=MUTED, font=("Segoe UI", 8), anchor="w")

    def draw_help(self):
        self.draw_background()
        c = self.canvas
        c.create_rectangle(150, 84, WIDTH - 150, HEIGHT - 84, fill=PANEL, outline=ACCENT, width=2)
        c.create_text(WIDTH / 2, 124, text="HOW TO PLAY", fill=ACCENT, font=("Segoe UI", 24, "bold"))
        lines = [
            ("WASD / Arrows", "Move around the Hangout Area hub."),
            ("E", "Interact with the Quest Board, NPCs and the Expedition Portal."),
            ("Quest Board", "Accept your signature quest or a repeatable bounty."),
            ("Expedition Portal", "Start an expedition once you have a contract."),
            ("Stat checks", "Each expedition stage offers three approaches. The chance depends on the linked stat."),
            ("Vitality", "Failed checks cost vitality. Reach the end with 2+ successes to clear the expedition."),
            ("Rewards", "Gold, XP and - for signature quests - the next piece of your 5-star set."),
            ("Character sheet", "Press C to spend stat points earned from levelling up."),
            ("Blacksmith Bram", "Spend gold on permanent expedition upgrades."),
            ("Archivist Miko", "Talk to her to raise trust. Charisma makes trust grow faster."),
            ("C / Esc", "Close panels and return to the hub."),
        ]
        y = 166
        for label, text in lines:
            c.create_text(200, y, text=label, fill=GOLD, font=("Segoe UI", 10, "bold"), anchor="w")
            c.create_text(360, y, text=text, fill=TEXT, font=("Segoe UI", 9), anchor="w", width=560)
            y += 38
        c.create_text(WIDTH / 2, HEIGHT - 104, text="Press H, Space or Esc to close", fill=MUTED, font=("Segoe UI", 10))

    def draw_dialogue(self):
        self.draw_hub()
        c = self.canvas
        c.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#050914", stipple="gray50", outline="")
        c.create_rectangle(120, 400, WIDTH - 120, 620, fill=PANEL, outline=self.dialogue_color, width=2)
        c.create_rectangle(140, 380, 300, 420, fill=PANEL_2, outline=self.dialogue_color, width=2)
        c.create_text(220, 400, text=self.dialogue_name, fill=self.dialogue_color, font=("Segoe UI", 13, "bold"))
        line = self.dialogue_lines[self.dialogue_index]
        c.create_text(160, 452, text=line, fill=TEXT, font=("Segoe UI", 13), anchor="w", width=WIDTH - 320)
        c.create_text(WIDTH - 150, 588, text="E / Space  continue   -   Esc  leave", fill=MUTED, font=("Segoe UI", 9), anchor="e")
        c.create_text(150, 588, text=f"Trust: {self.hero['trust']}/100", fill=BLUE, font=("Segoe UI", 9), anchor="w")

    def draw_panel_title(self, title, subtitle=""):
        c = self.canvas
        c.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#050914", stipple="gray50", outline="")
        c.create_rectangle(120, 78, WIDTH - 120, HEIGHT - 78, fill=PANEL, outline="#2c4a70", width=2)
        c.create_text(WIDTH / 2, 116, text=title, fill=TEXT, font=("Segoe UI", 22, "bold"))
        if subtitle:
            c.create_text(WIDTH / 2, 146, text=subtitle, fill=MUTED, font=("Segoe UI", 10))

    def draw_board(self):
        self.draw_hub()
        self.draw_panel_title("QUEST BOARD", "Choose a contract. You can change it before entering the portal.")
        c = self.canvas
        contracts = [
            self.current_contract() if self.active_contract_id == "signature" else {
                "id": "signature",
                "title": self.hero["quest"],
                "zone": self.hero["zone"],
                "desc": "Recover your signature cache. Rewards the next piece of your 5-star set on success.",
                "reward": "1 signature piece + 120 gold + 80 XP",
            },
            {
                "id": "bounty",
                "title": "Bounty: Bandit Tide",
                "zone": "Shoreline Caves",
                "desc": "A repeatable contract with slightly easier checks and a flat payout.",
                "reward": "150 gold + 60 XP",
            },
        ]
        for i, contract in enumerate(contracts):
            x1 = 180 + i * 370
            y1 = 200
            x2 = x1 + 340
            y2 = 510
            selected = contract["id"] == self.active_contract_id
            outline = GOLD if selected else "#2c4a70"
            c.create_rectangle(x1, y1, x2, y2, fill=PANEL_2, outline=outline, width=2 if selected else 1)
            c.create_text(x1 + 18, y1 + 24, text=f"{i + 1}", fill=GOLD, font=("Segoe UI", 15, "bold"), anchor="w")
            c.create_text(x1 + 46, y1 + 24, text="SIGNATURE QUEST" if contract["id"] == "signature" else "REPEATABLE", fill=MUTED, font=("Segoe UI", 8, "bold"), anchor="w")
            c.create_text(x1 + 18, y1 + 62, text=contract["title"], fill=GOLD if contract["id"] == "signature" else ACCENT, font=("Segoe UI", 15, "bold"), anchor="w", width=300)
            c.create_text(x1 + 18, y1 + 98, text=f"Zone: {contract['zone']}", fill=BLUE, font=("Segoe UI", 10), anchor="w")
            c.create_text(x1 + 18, y1 + 138, text=contract["desc"], fill=TEXT, font=("Segoe UI", 10), anchor="w", width=300)
            c.create_text(x1 + 18, y1 + 222, text="REWARD", fill=MUTED, font=("Segoe UI", 8, "bold"), anchor="w")
            c.create_text(x1 + 18, y1 + 244, text=contract["reward"], fill=GOLD, font=("Segoe UI", 10), anchor="w", width=300)
            c.create_text(x1 + 18, y1 + 286, text=f"Signature progress: {self.hero['loot_index']}/6", fill=MUTED, font=("Segoe UI", 9), anchor="w")
            if selected:
                c.create_text(x1 + 18, y2 - 48, text="ACTIVE CONTRACT", fill=ACCENT, font=("Segoe UI", 8, "bold"), anchor="w")
            c.create_text(x1 + 18, y2 - 24, text="Press " + str(i + 1) + " to accept", fill=ACCENT, font=("Segoe UI", 9, "bold"), anchor="w")
        c.create_text(WIDTH / 2, HEIGHT - 112, text="Esc  close", fill=MUTED, font=("Segoe UI", 10))

    def draw_shop(self):
        self.draw_hub()
        self.draw_panel_title("BLACKSMITH BRAM", "Permanent expedition upgrades. Gold is spent immediately.")
        c = self.canvas
        c.create_text(WIDTH / 2, 180, text=self.shop_message, fill=MUTED, font=("Segoe UI", 10))
        c.create_text(880, 118, text=f"GOLD {self.hero['gold']}", fill=GOLD, font=("Consolas", 12, "bold"), anchor="e")
        for i, item in enumerate(SHOP):
            y = 214 + i * 108
            count = self.upgrade_count(item["id"])
            cost = item["base"] + count * item["step"]
            maxed = count >= item["max"]
            c.create_rectangle(180, y, WIDTH - 180, y + 88, fill=PANEL_2, outline="#2c4a70", width=1)
            c.create_text(204, y + 24, text=str(i + 1), fill=GOLD, font=("Segoe UI", 14, "bold"), anchor="w")
            c.create_text(232, y + 24, text=item["name"], fill=TEXT, font=("Segoe UI", 13, "bold"), anchor="w")
            c.create_text(232, y + 48, text=item["desc"], fill=MUTED, font=("Segoe UI", 9), anchor="w", width=540)
            c.create_text(232, y + 68, text=f"Owned: {count}/{item['max']}", fill=BLUE, font=("Segoe UI", 9), anchor="w")
            c.create_text(WIDTH - 204, y + 34, text="MAXED" if maxed else f"{cost}g", fill=MUTED if maxed else GOLD, font=("Consolas", 13, "bold"), anchor="e")
            c.create_text(WIDTH - 204, y + 58, text="-" if maxed else "Press to buy", fill=MUTED, font=("Segoe UI", 8), anchor="e")
        c.create_text(WIDTH / 2, HEIGHT - 112, text="Esc  leave the forge", fill=MUTED, font=("Segoe UI", 10))

    def draw_sheet(self):
        self.draw_hub()
        self.draw_panel_title("CHARACTER SHEET", "Press 1-7 to spend a stat point. Stats cap at 10.")
        c = self.canvas
        hero = self.hero
        c.create_text(210, 186, text=f"Stat points available: {hero['stat_points']}", fill=GOLD, font=("Segoe UI", 12, "bold"), anchor="w")
        for i, stat in enumerate(STAT_KEYS):
            y = 228 + i * 48
            c.create_text(190, y, text=f"{i + 1}", fill=GOLD, font=("Consolas", 11, "bold"), anchor="w")
            c.create_text(220, y, text=stat, fill=TEXT, font=("Segoe UI", 12, "bold"), anchor="w")
            c.create_text(220, y + 19, text=STAT_BLURB[stat], fill=MUTED, font=("Segoe UI", 8), anchor="w")
            value = hero["stats"][stat]
            c.create_rectangle(640, y - 7, 830, y + 7, fill="#22304f", outline="")
            c.create_rectangle(640, y - 7, 640 + 190 * (value / 10), y + 7, fill=hero["accent"], outline="")
            c.create_text(874, y, text=str(value), fill=hero["accent"], font=("Consolas", 12, "bold"), anchor="e")

        c.create_text(640, 200, text="SIGNATURE SET", fill=MUTED, font=("Segoe UI", 9, "bold"), anchor="w")
        gear = SIGNATURE_GEAR[hero["name"]]
        for i, item in enumerate(gear):
            owned = i < hero["loot_index"]
            c.create_text(640, 224 + i * 20, text=("+ " if owned else "- ") + item, fill=GOLD if owned else MUTED, font=("Segoe UI", 9), anchor="w")
        c.create_text(880, 200, text="PACK", fill=MUTED, font=("Segoe UI", 9, "bold"), anchor="w")
        for i, item in enumerate(hero["inventory"][-9:][::-1]):
            c.create_text(880, 224 + i * 20, text=f"- {item}", fill=TEXT, font=("Segoe UI", 9), anchor="w", width=190)

        c.create_text(WIDTH / 2, HEIGHT - 112, text="C / Esc  close", fill=MUTED, font=("Segoe UI", 10))

    def draw_prep(self):
        self.draw_hub()
        self.draw_panel_title("EXPEDITION BRIEFING", "Three stages. Two successes clear the contract.")
        c = self.canvas
        contract = self.current_contract()
        c.create_text(200, 190, text=contract["title"], fill=GOLD, font=("Segoe UI", 18, "bold"), anchor="w")
        c.create_text(200, 218, text=f"Zone: {contract['zone']}", fill=BLUE, font=("Segoe UI", 11), anchor="w")
        c.create_text(200, 246, text=contract["desc"], fill=MUTED, font=("Segoe UI", 10), anchor="w", width=680)

        c.create_text(200, 296, text="STAGES", fill=MUTED, font=("Segoe UI", 9, "bold"), anchor="w")
        for i, stage in enumerate(STAGES):
            y = 320 + i * 54
            c.create_oval(202, y - 12, 226, y + 12, fill=PANEL_2, outline=ACCENT, width=1)
            c.create_text(214, y, text=str(i + 1), fill=ACCENT, font=("Consolas", 9, "bold"))
            c.create_text(246, y - 8, text=stage["name"], fill=TEXT, font=("Segoe UI", 12, "bold"), anchor="w")
            stats = ", ".join(option["stat"] for option in stage["options"])
            c.create_text(246, y + 12, text=f"Approaches: {stats}", fill=MUTED, font=("Segoe UI", 8), anchor="w")

        c.create_text(200, 502, text="YOUR RUN", fill=MUTED, font=("Segoe UI", 9, "bold"), anchor="w")
        c.create_text(200, 528, text=f"Vitality: {self.max_vitality()}  (100 + 4 per Endurance, plus upgrades)", fill=TEXT, font=("Segoe UI", 10), anchor="w")
        c.create_text(200, 552, text=f"Stat-check bonus: +{int(self.success_bonus() * 100)}%", fill=TEXT, font=("Segoe UI", 10), anchor="w")
        c.create_text(200, 576, text=f"Bonus Luck for loot: +{self.luck_bonus()}", fill=TEXT, font=("Segoe UI", 10), anchor="w")
        c.create_text(200, 600, text="Press E / Space to enter the portal   -   Esc to cancel", fill=ACCENT, font=("Segoe UI", 10, "bold"), anchor="w")

    def draw_expedition(self):
        self.draw_background()
        c = self.canvas
        contract = self.current_contract()
        stage = STAGES[self.stage_index]

        c.create_rectangle(0, 0, WIDTH, 96, fill=PANEL, outline="")
        c.create_text(30, 24, text=contract["title"].upper(), fill=GOLD, font=("Segoe UI", 15, "bold"), anchor="w")
        c.create_text(30, 50, text=f"{contract['zone']}  -  Stage {self.stage_index + 1} of {len(STAGES)}", fill=MUTED, font=("Segoe UI", 10), anchor="w")
        for i in range(len(STAGES)):
            x = 30 + i * 34
            if i < self.stage_index:
                color = GREEN if any(entry["status"] != "failure" for entry in self.stage_log[i : i + 1]) else RED
            elif i == self.stage_index:
                color = ACCENT
            else:
                color = "#33456a"
            c.create_oval(x, 72, x + 22, 94, fill=color, outline="")
            c.create_text(x + 11, 83, text=str(i + 1), fill=BG, font=("Consolas", 9, "bold"))

        c.create_text(WIDTH - 30, 24, text=f"VITALITY {self.vitality}/{self.max_vitality()}", fill=RED if self.vitality < 50 else TEXT, font=("Consolas", 12, "bold"), anchor="e")
        self.bar(WIDTH - 330, 48, 300, 12, self.vitality / max(1, self.max_vitality()), RED, "")
        c.create_text(WIDTH - 30, 76, text=f"Checks passed: {self.successes}   Criticals: {self.crits}", fill=MUTED, font=("Consolas", 9), anchor="e")

        c.create_text(60, 132, text=stage["name"], fill=ACCENT, font=("Segoe UI", 20, "bold"), anchor="w")
        c.create_text(60, 166, text=stage["prompt"], fill=TEXT, font=("Segoe UI", 11), anchor="w", width=980)

        self.option_cards = []
        if self.stage_result:
            result = self.stage_result
            c.create_rectangle(150, 228, WIDTH - 150, 470, fill=PANEL, outline=result["tone"], width=2)
            c.create_text(WIDTH / 2, 270, text=result["headline"], fill=result["tone"], font=("Segoe UI", 24, "bold"))
            c.create_text(WIDTH / 2, 314, text=result["body"], fill=TEXT, font=("Segoe UI", 12), width=760)
            c.create_text(WIDTH / 2, 352, text=f"Chance was {int(result['chance'] * 100)}%  -  {result['option']['stat']}", fill=MUTED, font=("Segoe UI", 9))
            c.create_text(WIDTH / 2, 388, text=f"+{result['gold']} gold    +{result['xp']} XP", fill=GOLD, font=("Segoe UI", 13, "bold"))
            if result["damage"]:
                c.create_text(WIDTH / 2, 420, text=f"-{result['damage']} vitality", fill=RED, font=("Segoe UI", 11, "bold"))
            c.create_text(WIDTH / 2, 500, text="Press E / Space to continue", fill=ACCENT, font=("Segoe UI", 11, "bold"))
        else:
            extra = 0.08 if contract["id"] == "bounty" else 0.0
            for i, option in enumerate(stage["options"]):
                x1 = 70 + i * 327
                y1 = 228
                x2 = x1 + 300
                y2 = 470
                self.option_cards.append((x1, y1, x2, y2))
                chance = self.success_chance(option["stat"], extra)
                value = self.hero["stats"][option["stat"]]
                c.create_rectangle(x1, y1, x2, y2, fill=PANEL_2, outline="#2c4a70", width=1)
                c.create_text(x1 + 18, y1 + 22, text=str(i + 1), fill=GOLD, font=("Segoe UI", 15, "bold"), anchor="w")
                c.create_text(x1 + 18, y1 + 56, text=option["label"], fill=TEXT, font=("Segoe UI", 13, "bold"), anchor="w", width=264)
                c.create_text(x1 + 18, y1 + 108, text=option["text"], fill=MUTED, font=("Segoe UI", 9), anchor="w", width=264)
                c.create_text(x1 + 18, y1 + 168, text=f"{option['stat']} {value}", fill=ACCENT, font=("Segoe UI", 11, "bold"), anchor="w")
                c.create_text(x1 + 18, y1 + 194, text=f"{int(chance * 100)}% success chance", fill=GOLD, font=("Segoe UI", 10), anchor="w")
                c.create_rectangle(x1 + 18, y1 + 210, x2 - 18, y1 + 222, fill="#22304f", outline="")
                c.create_rectangle(x1 + 18, y1 + 210, x1 + 18 + (x2 - x1 - 36) * chance, y1 + 222, fill=GOLD, outline="")
                c.create_text(x1 + 18, y2 - 22, text="Press to attempt", fill=ACCENT, font=("Segoe UI", 9), anchor="w")

        # log
        c.create_rectangle(60, 522, WIDTH - 60, 650, fill=PANEL, outline="#25405f", width=1)
        c.create_text(78, 540, text="EXPEDITION LOG", fill=MUTED, font=("Segoe UI", 8, "bold"), anchor="w")
        entries = self.stage_log[-4:]
        for i, entry in enumerate(entries):
            color = {"critical": GOLD, "success": GREEN, "failure": RED}[entry["status"]]
            c.create_text(78, 562 + i * 20, text=entry["text"], fill=color, font=("Segoe UI", 9), anchor="w")
        if not entries:
            c.create_text(78, 562, text="No checks made yet. Pick an approach above.", fill=MUTED, font=("Segoe UI", 9), anchor="w")

    def draw_debrief(self):
        self.draw_background()
        c = self.canvas
        data = self.debrief
        success = data["success"]
        tone = ACCENT if success else RED
        c.create_rectangle(120, 70, WIDTH - 120, HEIGHT - 70, fill=PANEL, outline=tone, width=2)
        c.create_text(WIDTH / 2, 112, text="EXPEDITION COMPLETE" if success else "EXPEDITION FAILED", fill=tone, font=("Segoe UI", 26, "bold"))
        c.create_text(WIDTH / 2, 146, text=f"{data['title']}  -  {data['zone']}", fill=MUTED, font=("Segoe UI", 10))
        c.create_text(WIDTH / 2, 184, text=data["score"], fill=TEXT, font=("Segoe UI", 12))
        c.create_text(WIDTH / 2, 210, text=f"Vitality remaining: {data['vitality']}/{self.max_vitality()}", fill=RED if data["vitality"] < 50 else TEXT, font=("Segoe UI", 10))

        c.create_text(180, 250, text="STAGE RESULTS", fill=MUTED, font=("Segoe UI", 9, "bold"), anchor="w")
        for i, entry in enumerate(data["log"]):
            color = {"critical": GOLD, "success": GREEN, "failure": RED}[entry["status"]]
            c.create_text(180, 276 + i * 26, text=entry["text"], fill=color, font=("Segoe UI", 10), anchor="w")

        c.create_text(180, 376, text="REWARDS", fill=MUTED, font=("Segoe UI", 9, "bold"), anchor="w")
        c.create_text(180, 402, text=f"{data['gold']} gold", fill=GOLD, font=("Segoe UI", 12, "bold"), anchor="w")
        c.create_text(180, 426, text=f"{data['xp']} XP", fill=BLUE, font=("Segoe UI", 12, "bold"), anchor="w")
        if data["loot"]:
            c.create_text(180, 462, text="SIGNATURE CACHE", fill=MUTED, font=("Segoe UI", 9, "bold"), anchor="w")
            for i, item in enumerate(data["loot"]):
                c.create_text(180, 488 + i * 24, text=item, fill=GOLD, font=("Segoe UI", 12, "bold"), anchor="w")
        elif success:
            c.create_text(180, 462, text="Bounty paid. No signature cache on repeatable contracts.", fill=MUTED, font=("Segoe UI", 9), anchor="w")
        else:
            c.create_text(180, 462, text="No signature cache. The contract remains open - try again.", fill=MUTED, font=("Segoe UI", 9), anchor="w")

        c.create_text(WIDTH - 200, 250, text="AFTERMATH", fill=MUTED, font=("Segoe UI", 9, "bold"), anchor="e")
        lines = [
            f"Level {self.hero['level']}",
            f"{self.hero['stat_points']} stat point(s) available",
            f"Signature set: {self.hero['loot_index']}/6",
            f"Gold: {self.hero['gold']}",
        ]
        for i, line in enumerate(lines):
            c.create_text(WIDTH - 200, 278 + i * 24, text=line, fill=TEXT, font=("Segoe UI", 10), anchor="e")

        c.create_text(WIDTH / 2, HEIGHT - 112, text="Press E / Space to return to the Hangout Area", fill=ACCENT, font=("Segoe UI", 11, "bold"))

    def draw_toasts(self):
        c = self.canvas
        y = 100 if self.state != "menu" else HEIGHT - 90
        for toast in self.toasts[-4:]:
            c.create_text(WIDTH / 2, y, text=toast.text, fill=toast.color, font=("Segoe UI", 10, "bold"))
            y += 20

    def bar(self, x, y, w, h, frac, color, label):
        c = self.canvas
        c.create_rectangle(x, y, x + w, y + h, fill="#1b1020", outline="#2e3550")
        c.create_rectangle(x, y, x + w * max(0, min(1, frac)), y + h, fill=color, outline="")
        if label:
            c.create_text(x + 6, y + h / 2, text=label, fill=TEXT, font=("Consolas", 8, "bold"), anchor="w")

    # ------------------------------------------------------------------ loop
    def tick(self):
        now = time.perf_counter()
        dt = min(0.05, now - self.last_time)
        self.last_time = now
        self.update(dt)
        self.draw()
        self.root.after(16, self.tick)

    def run(self):
        self.last_time = time.perf_counter()
        self.tick()
        self.root.mainloop()


def smoke_test():
    root = tk.Tk()
    root.withdraw()
    game = Game(root)
    game.rng = random.Random(7)

    game.draw()

    for hero_index in range(3):
        game.start_hero(hero_index)
        game.draw()

        game.open_board()
        game.draw()
        game.accept_contract(0)
        game.draw()
        assert game.active_contract_id == "signature"

        game.open_portal()
        game.draw()
        assert game.state == "prep"
        game.begin_expedition()
        game.draw()
        assert game.state == "expedition"

        for _ in range(len(STAGES)):
            stage = STAGES[game.stage_index]
            best = max(
                range(len(stage["options"])),
                key=lambda i: game.success_chance(stage["options"][i]["stat"]),
            )
            game.choose_option(best)
            game.draw()
            assert game.stage_result is not None
            game.continue_expedition()
            game.draw()

        assert game.state == "debrief", game.state
        game.leave_debrief()
        game.draw()
        assert game.state == "hub"

        # Character sheet and stat allocation.
        game.hero["stat_points"] = 1
        before = game.hero["stats"]["Agility"]
        game.open_sheet()
        game.draw()
        game.allocate_stat(0)
        game.draw()
        assert game.hero["stats"]["Agility"] == before + 1
        game.state = "hub"

        # Shop purchase.
        game.hero["gold"] = 1000
        game.open_shop()
        game.draw()
        game.buy_upgrade(0)
        game.draw()
        assert game.upgrade_count("oil") == 1
        game.state = "hub"

        # Dialogue and help.
        game.open_dialogue()
        game.draw()
        game.advance_dialogue()
        game.advance_dialogue()
        game.advance_dialogue()
        game.draw()
        assert game.state == "hub"
        game.help_return = "hub"
        game.state = "help"
        game.draw()
        game.state = "hub"

    # Force a successful signature clear and confirm loot is granted.
    game.start_hero(0)
    game.active_contract_id = "signature"
    game.successes = 3
    game.vitality = 100
    game.expedition_gold = 10
    game.expedition_xp = 10
    game.stage_log = []
    before_loot = game.hero["loot_index"]
    game.finish_expedition()
    game.draw()
    assert game.hero["loot_index"] == before_loot + 1
    assert game.hero["inventory"][-1] == SIGNATURE_GEAR[game.hero["name"]][before_loot]

    print("Hub prototype smoke test passed.")
    root.destroy()


def main():
    if "--smoke-test" in sys.argv:
        smoke_test()
        return
    root = tk.Tk()
    root.title("Hangout Area - Hub & Expedition Prototype")
    root.resizable(False, False)
    game = Game(root)
    game.run()


if __name__ == "__main__":
    main()
