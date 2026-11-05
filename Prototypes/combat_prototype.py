#!/usr/bin/env python3
"""
Hangout Area - Combat Prototype
A tiny top-down action-RPG combat slice built with tkinter only.

Run:
    python Prototypes/combat_prototype.py

Controls:
    WASD / Arrow Keys - move
    Q, E, R, Space    - abilities
    H                 - help / pause
    Enter (on end screen) - restart
    M (on end screen) - back to hero select
"""

import math
import random
import sys
import time
import tkinter as tk
from dataclasses import dataclass, field

WIDTH = 1100
HEIGHT = 700
ARENA_LEFT = 38
ARENA_TOP = 96
ARENA_RIGHT = WIDTH - 38
ARENA_BOTTOM = HEIGHT - 88
ARENA_W = ARENA_RIGHT - ARENA_LEFT
ARENA_H = ARENA_BOTTOM - ARENA_TOP

BG = "#0b1020"
PANEL = "#111a33"
PANEL_2 = "#162242"
GRID = "#1b2b4d"
TEXT = "#e8eefc"
MUTED = "#8da2c8"
ACCENT = "#62e6c8"
GOLD = "#ffd166"
RED = "#ff5d73"
BLUE = "#63b3ff"
PURPLE = "#b388ff"


@dataclass
class Ability:
    name: str
    key: str
    cost: int
    cooldown: float
    desc: str


@dataclass
class Player:
    name: str
    role: str
    color: str
    accent: str
    signature: str
    max_hp: float
    max_mana: float
    hp_regen: float
    mana_regen: float
    speed: float
    atk: float
    armor: float
    attack_range: float
    attack_cd: float
    basic_kind: str
    abilities: list = field(default_factory=list)
    x: float = WIDTH / 2
    y: float = HEIGHT / 2
    hp: float = 0
    mana: float = 0
    attack_timer: float = 0
    facing_x: float = 1
    facing_y: float = 0
    level: int = 1
    xp: int = 0
    xp_next: int = 100
    cooldowns: list = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])
    invisible: float = 0
    speed_buff: float = 0
    speed_mult: float = 1
    attack_speed_buff: float = 0
    attack_speed_mult: float = 1
    damage_reduction: float = 0
    damage_reduction_timer: float = 0
    regen_buff: float = 0
    regen_buff_timer: float = 0
    hurt_flash: float = 0

    def __post_init__(self):
        self.hp = self.max_hp
        self.mana = self.max_mana

    @property
    def radius(self):
        return 18


@dataclass
class Enemy:
    kind: str
    name: str
    x: float
    y: float
    hp: float
    max_hp: float
    speed: float
    damage: float
    radius: float
    xp: int
    gold: int
    color: str
    attack_timer: float = 0
    stun: float = 0
    taunt: float = 0
    weak: float = 0
    hit_flash: float = 0
    boss: bool = False
    special_timer: float = 0
    summon_done: bool = False


@dataclass
class Projectile:
    x: float
    y: float
    vx: float
    vy: float
    radius: float
    damage: float
    color: str
    team: str
    life: float = 3.0


@dataclass
class Effect:
    kind: str
    x: float
    y: float
    radius: float
    max_radius: float
    life: float
    max_life: float
    color: str


@dataclass
class FloatText:
    x: float
    y: float
    text: str
    color: str
    life: float = 0.9
    max_life: float = 0.9


@dataclass
class Pickup:
    kind: str
    x: float
    y: float
    value: int
    radius: float = 9
    life: float = 24


@dataclass
class Clone:
    x: float
    y: float
    timer: float = 8.0
    attack_timer: float = 0


def make_characters():
    return [
        {
            "name": "Anon User",
            "role": "Burst / Stealth",
            "color": "#8b5cf6",
            "accent": "#c4b5fd",
            "signature": "Sacred Switchblade",
            "max_hp": 180,
            "max_mana": 120,
            "hp_regen": 1.5,
            "mana_regen": 4.0,
            "speed": 235,
            "atk": 22,
            "armor": 12,
            "attack_range": 270,
            "attack_cd": 0.45,
            "basic_kind": "projectile",
            "abilities": [
                Ability("Shuriken Throw", "Q", 25, 3.2, "Throw shurikens at up to 3 nearby enemies."),
                Ability("Blinding Light", "E", 35, 7.0, "Blind and damage enemies around you."),
                Ability("Staying Anonymous", "R", 40, 12.0, "Vanish for 3s and move faster."),
                Ability("Clone Warfare", "SPACE", 60, 20.0, "Summon 2 clones that fight for you."),
            ],
        },
        {
            "name": "OPmonkey",
            "role": "Vanguard / Bruiser",
            "color": "#c77b30",
            "accent": "#ffd7a8",
            "signature": "Bonking Stick",
            "max_hp": 285,
            "max_mana": 100,
            "hp_regen": 2.8,
            "mana_regen": 3.0,
            "speed": 195,
            "atk": 20,
            "armor": 30,
            "attack_range": 78,
            "attack_cd": 0.7,
            "basic_kind": "melee",
            "abilities": [
                Ability("Bone Breaker", "Q", 20, 4.0, "A heavy strike that stuns a nearby enemy."),
                Ability("Sickening Scream", "E", 30, 8.0, "Taunt nearby enemies and weaken them."),
                Ability("Rest Break", "R", 25, 12.0, "Regenerate and take reduced damage for 3s."),
                Ability("Plushie Storm", "SPACE", 50, 18.0, "Damage nearby enemies and heal yourself."),
            ],
        },
        {
            "name": "CrushedExpert14",
            "role": "Support / Skirmisher",
            "color": "#2fb98d",
            "accent": "#b8ffe8",
            "signature": "Aether Harp",
            "max_hp": 205,
            "max_mana": 155,
            "hp_regen": 1.6,
            "mana_regen": 6.0,
            "speed": 215,
            "atk": 18,
            "armor": 18,
            "attack_range": 300,
            "attack_cd": 0.6,
            "basic_kind": "projectile",
            "abilities": [
                Ability("Crushing Blow", "Q", 25, 5.0, "Dash to a target area and deal damage."),
                Ability("Energy Drink", "E", 30, 10.0, "Gain movement and attack speed for 6s."),
                Ability("Jamming", "R", 35, 12.0, "Charm enemies around you, stunning them."),
                Ability("Party Time", "SPACE", 60, 20.0, "Heal yourself and damage nearby enemies."),
            ],
        },
    ]


class Game:
    def __init__(self, root, smoke=False):
        self.root = root
        self.smoke = smoke
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.characters = make_characters()
        self.state = "menu"
        self.help_return = "menu"
        self.last_time = time.perf_counter()
        self.menu_time = 0.0
        self.keys = set()
        self.cards = []
        self.toasts = []
        self.player = None
        self.enemies = []
        self.projectiles = []
        self.effects = []
        self.texts = []
        self.pickups = []
        self.clones = []
        self.wave = 0
        self.next_wave_timer = 0
        self.kills = 0
        self.gold = 0
        self.elapsed = 0
        self.boss_spawned = False
        self.boss_defeated = False
        self.chest_spawned = False
        self.victory_signature = ""
        self.rng = random.Random()

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
                self.start_run(int(key) - 1)
            elif key == "h":
                self.open_help()
        elif self.state == "help":
            if key in ("h", "escape", "space"):
                self.close_help()
        elif self.state == "playing":
            if key == "h":
                self.open_help()
            elif key == "q":
                self.use_ability(0)
            elif key == "e":
                self.use_ability(1)
            elif key == "r":
                self.use_ability(2)
            elif key == "space":
                self.use_ability(3)
        else:  # victory / defeat
            if key in ("return", "kp_enter"):
                self.start_run(self.player_index)
            elif key == "m":
                self.state = "menu"

    def on_key_release(self, event):
        self.keys.discard(event.keysym.lower())

    def on_click(self, event):
        if self.state == "menu":
            for index, (x1, y1, x2, y2) in enumerate(self.cards):
                if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                    self.start_run(index)
                    return
        elif self.state == "help":
            self.close_help()

    # ------------------------------------------------------------------ state
    def start_run(self, index):
        self.player_index = index
        data = self.characters[index]
        self.player = Player(
            name=data["name"],
            role=data["role"],
            color=data["color"],
            accent=data["accent"],
            signature=data["signature"],
            max_hp=data["max_hp"],
            max_mana=data["max_mana"],
            hp_regen=data["hp_regen"],
            mana_regen=data["mana_regen"],
            speed=data["speed"],
            atk=data["atk"],
            armor=data["armor"],
            attack_range=data["attack_range"],
            attack_cd=data["attack_cd"],
            basic_kind=data["basic_kind"],
            abilities=data["abilities"],
            x=WIDTH / 2,
            y=(ARENA_TOP + ARENA_BOTTOM) / 2,
        )
        self.state = "playing"
        self.enemies.clear()
        self.projectiles.clear()
        self.effects.clear()
        self.texts.clear()
        self.pickups.clear()
        self.clones.clear()
        self.toasts.clear()
        self.wave = 0
        self.next_wave_timer = 1.4
        self.kills = 0
        self.gold = 0
        self.elapsed = 0
        self.boss_spawned = False
        self.boss_defeated = False
        self.chest_spawned = False
        self.victory_signature = data["signature"]
        self.last_time = time.perf_counter()
        self.toast(f"{self.player.name} enters the arena", self.player.accent)

    def open_help(self):
        self.help_return = self.state
        self.state = "help"

    def close_help(self):
        self.state = self.help_return

    def toast(self, text, color=TEXT):
        self.toasts.append({"text": text, "color": color, "life": 2.8})
        if len(self.toasts) > 4:
            self.toasts.pop(0)

    # ------------------------------------------------------------------ update
    def update(self, dt):
        self.menu_time += dt
        for toast in self.toasts:
            toast["life"] -= dt
        self.toasts = [t for t in self.toasts if t["life"] > 0]

        if self.state != "playing":
            return

        self.elapsed += dt
        p = self.player
        p.hurt_flash = max(0, p.hurt_flash - dt)
        p.invisible = max(0, p.invisible - dt)
        p.speed_buff = max(0, p.speed_buff - dt)
        p.attack_speed_buff = max(0, p.attack_speed_buff - dt)
        p.damage_reduction_timer = max(0, p.damage_reduction_timer - dt)
        p.regen_buff_timer = max(0, p.regen_buff_timer - dt)
        if p.speed_buff <= 0:
            p.speed_mult = 1
        if p.attack_speed_buff <= 0:
            p.attack_speed_mult = 1
        if p.damage_reduction_timer <= 0:
            p.damage_reduction = 0

        regen = p.hp_regen
        if p.regen_buff_timer > 0:
            regen += p.regen_buff
        p.hp = min(p.max_hp, p.hp + regen * dt)
        p.mana = min(p.max_mana, p.mana + p.mana_regen * dt)
        p.cooldowns = [max(0, c - dt) for c in p.cooldowns]

        # movement
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
            p.facing_x, p.facing_y = mx, my
            speed = p.speed * (p.speed_mult if p.speed_buff > 0 else 1)
            p.x += mx * speed * dt
            p.y += my * speed * dt
            p.x = max(ARENA_LEFT + p.radius, min(ARENA_RIGHT - p.radius, p.x))
            p.y = max(ARENA_TOP + p.radius, min(ARENA_BOTTOM - p.radius, p.y))

        # auto basic attack
        p.attack_timer -= dt * (p.attack_speed_mult if p.attack_speed_buff > 0 else 1)
        if p.attack_timer <= 0:
            target = self.nearest_enemy(p.x, p.y, p.attack_range)
            if target:
                p.attack_timer = p.attack_cd
                if p.basic_kind == "melee":
                    self.damage_enemy(target, p.atk)
                    self.effects.append(Effect("slash", p.x, p.y, 0, 34, 0.16, 0.16, p.accent))
                else:
                    self.fire_projectile(p.x, p.y, target.x, target.y, 320, p.atk, p.accent, "player", 7)

        self.update_waves(dt)
        self.update_enemies(dt)
        self.update_projectiles(dt)
        self.update_clones(dt)
        self.update_pickups(dt)

        for effect in self.effects:
            effect.life -= dt
        self.effects = [e for e in self.effects if e.life > 0]
        for text in self.texts:
            text.life -= dt
            text.y -= 38 * dt
        self.texts = [t for t in self.texts if t.life > 0]

        if p.hp <= 0:
            self.state = "defeat"

    def update_waves(self, dt):
        if self.chest_spawned and self.boss_defeated:
            return
        if self.next_wave_timer > 0:
            self.next_wave_timer -= dt
            if self.next_wave_timer <= 0:
                self.start_wave(self.wave + 1)
        elif not self.enemies and not self.boss_defeated:
            self.next_wave_timer = 2.2

    def start_wave(self, number):
        self.wave = number
        self.next_wave_timer = 0
        if number == 1:
            self.toast("WAVE 1 - The gate opens", ACCENT)
            for _ in range(4):
                self.spawn_enemy("grunt")
            for _ in range(2):
                self.spawn_enemy("runner")
        elif number == 2:
            self.toast("WAVE 2 - Something bigger stirs", GOLD)
            for _ in range(5):
                self.spawn_enemy("grunt")
            for _ in range(2):
                self.spawn_enemy("brute")
            for _ in range(2):
                self.spawn_enemy("runner")
        else:
            self.toast("BOSS - Dungeon Warden", RED)
            self.boss_spawned = True
            self.spawn_enemy("boss")
            for _ in range(2):
                self.spawn_enemy("grunt")

    def spawn_enemy(self, kind):
        side = self.rng.choice(["top", "bottom", "left", "right"])
        margin = 28
        if side == "top":
            x = self.rng.uniform(ARENA_LEFT + 40, ARENA_RIGHT - 40)
            y = ARENA_TOP + margin
        elif side == "bottom":
            x = self.rng.uniform(ARENA_LEFT + 40, ARENA_RIGHT - 40)
            y = ARENA_BOTTOM - margin
        elif side == "left":
            x = ARENA_LEFT + margin
            y = self.rng.uniform(ARENA_TOP + 40, ARENA_BOTTOM - 40)
        else:
            x = ARENA_RIGHT - margin
            y = self.rng.uniform(ARENA_TOP + 40, ARENA_BOTTOM - 40)

        if kind == "grunt":
            enemy = Enemy("grunt", "Hollow Grunt", x, y, 64, 64, 88, 8, 14, 20, 6, "#e05a6b")
        elif kind == "runner":
            enemy = Enemy("runner", "Skitterer", x, y, 44, 44, 145, 6, 11, 16, 4, "#ff9f43")
        elif kind == "brute":
            enemy = Enemy("brute", "Beach Brute", x, y, 160, 160, 64, 15, 21, 42, 12, "#b03a55")
        else:
            enemy = Enemy(
                "boss", "Dungeon Warden", x, y, 950, 950, 56, 22, 38, 300, 120,
                PURPLE, boss=True, special_timer=2.5,
            )
        self.enemies.append(enemy)
        self.effects.append(Effect("ring", x, y, 12, 44, 0.35, 0.35, enemy.color))

    def update_enemies(self, dt):
        p = self.player
        for enemy in list(self.enemies):
            if enemy not in self.enemies:
                continue
            enemy.hit_flash = max(0, enemy.hit_flash - dt)
            enemy.stun = max(0, enemy.stun - dt)
            enemy.taunt = max(0, enemy.taunt - dt)
            enemy.weak = max(0, enemy.weak - dt)
            enemy.attack_timer = max(0, enemy.attack_timer - dt)
            if enemy.stun > 0:
                continue

            dx = p.x - enemy.x
            dy = p.y - enemy.y
            dist = max(1, math.hypot(dx, dy))
            nx, ny = dx / dist, dy / dist

            if p.invisible > 0 and not enemy.boss:
                # Confused enemies drift away while Anon is hidden.
                enemy.x -= nx * enemy.speed * 0.45 * dt
                enemy.y -= ny * enemy.speed * 0.45 * dt
            elif dist > enemy.radius + p.radius + 8:
                enemy.x += nx * enemy.speed * dt
                enemy.y += ny * enemy.speed * dt
            elif enemy.attack_timer <= 0:
                enemy.attack_timer = 1.0
                dmg = enemy.damage * (0.75 if enemy.weak > 0 else 1.0)
                self.damage_player(dmg)
                self.effects.append(Effect("slash", enemy.x, enemy.y, 0, enemy.radius + 16, 0.14, 0.14, enemy.color))

            enemy.x = max(ARENA_LEFT + enemy.radius, min(ARENA_RIGHT - enemy.radius, enemy.x))
            enemy.y = max(ARENA_TOP + enemy.radius, min(ARENA_BOTTOM - enemy.radius, enemy.y))

            if enemy.boss:
                enemy.special_timer -= dt
                if enemy.special_timer <= 0:
                    enemy.special_timer = 3.4
                    self.boss_radial(enemy)
                if enemy.hp <= enemy.max_hp * 0.5 and not enemy.summon_done:
                    enemy.summon_done = True
                    self.toast("The Warden calls for aid!", RED)
                    for _ in range(4):
                        self.spawn_enemy("runner")

    def boss_radial(self, boss):
        for i in range(10):
            angle = (math.tau / 10) * i + self.elapsed * 0.3
            vx = math.cos(angle) * 190
            vy = math.sin(angle) * 190
            self.projectiles.append(Projectile(boss.x, boss.y, vx, vy, 7, 14, RED, "enemy", 3.5))
        self.effects.append(Effect("ring", boss.x, boss.y, 20, 90, 0.3, 0.3, RED))

    def update_projectiles(self, dt):
        p = self.player
        for projectile in list(self.projectiles):
            projectile.x += projectile.vx * dt
            projectile.y += projectile.vy * dt
            projectile.life -= dt
            if projectile.life <= 0 or not (
                ARENA_LEFT <= projectile.x <= ARENA_RIGHT and ARENA_TOP <= projectile.y <= ARENA_BOTTOM
            ):
                if projectile in self.projectiles:
                    self.projectiles.remove(projectile)
                continue

            if projectile.team == "player":
                for enemy in list(self.enemies):
                    if enemy in self.enemies and math.hypot(enemy.x - projectile.x, enemy.y - projectile.y) < enemy.radius + projectile.radius:
                        self.damage_enemy(enemy, projectile.damage)
                        if projectile in self.projectiles:
                            self.projectiles.remove(projectile)
                        break
            else:
                if math.hypot(p.x - projectile.x, p.y - projectile.y) < p.radius + projectile.radius:
                    self.damage_player(projectile.damage)
                    if projectile in self.projectiles:
                        self.projectiles.remove(projectile)

    def update_clones(self, dt):
        for clone in list(self.clones):
            clone.timer -= dt
            clone.attack_timer -= dt
            if clone.timer <= 0:
                self.clones.remove(clone)
                continue
            target = self.nearest_enemy(clone.x, clone.y, 330)
            if target and clone.attack_timer <= 0:
                clone.attack_timer = 0.72
                self.fire_projectile(clone.x, clone.y, target.x, target.y, 340, 13, self.player.accent, "player", 7)

    def update_pickups(self, dt):
        p = self.player
        for pickup in list(self.pickups):
            pickup.life -= dt
            if pickup.life <= 0:
                self.pickups.remove(pickup)
                continue
            dist = math.hypot(p.x - pickup.x, p.y - pickup.y)
            if dist < 120:
                speed = 300 * dt
                if dist > 1:
                    pickup.x += (p.x - pickup.x) / dist * speed
                    pickup.y += (p.y - pickup.y) / dist * speed
            if dist < p.radius + pickup.radius + 6:
                self.collect_pickup(pickup)
                if pickup in self.pickups:
                    self.pickups.remove(pickup)

    def collect_pickup(self, pickup):
        p = self.player
        if pickup.kind == "gold":
            self.gold += pickup.value
            self.texts.append(FloatText(pickup.x, pickup.y - 8, f"+{pickup.value}g", GOLD))
        elif pickup.kind == "health":
            healed = min(pickup.value, p.max_hp - p.hp)
            p.hp += healed
            self.texts.append(FloatText(pickup.x, pickup.y - 8, f"+{int(healed)} HP", ACCENT))
        elif pickup.kind == "mana":
            restored = min(pickup.value, p.max_mana - p.mana)
            p.mana += restored
            self.texts.append(FloatText(pickup.x, pickup.y - 8, f"+{int(restored)} MP", BLUE))
        elif pickup.kind == "chest":
            self.state = "victory"
            self.toast("Signature cache claimed!", GOLD)

    # ------------------------------------------------------------------ combat
    def nearest_enemy(self, x, y, max_range):
        best = None
        best_dist = max_range
        for enemy in self.enemies:
            dist = math.hypot(enemy.x - x, enemy.y - y)
            if dist < best_dist:
                best = enemy
                best_dist = dist
        return best

    def fire_projectile(self, x, y, tx, ty, speed, damage, color, team, radius):
        dx = tx - x
        dy = ty - y
        dist = max(1, math.hypot(dx, dy))
        self.projectiles.append(Projectile(x, y, dx / dist * speed, dy / dist * speed, radius, damage, color, team))

    def damage_enemy(self, enemy, amount):
        if enemy not in self.enemies:
            return
        enemy.hp -= amount
        enemy.hit_flash = 0.1
        self.texts.append(FloatText(enemy.x + self.rng.uniform(-8, 8), enemy.y - enemy.radius, str(round(amount)), GOLD))
        if enemy.hp <= 0:
            self.enemies.remove(enemy)
            self.kills += 1
            self.gold += enemy.gold
            self.gain_xp(enemy.xp)
            self.effects.append(Effect("ring", enemy.x, enemy.y, 10, enemy.radius * 2.6, 0.4, 0.4, enemy.color))
            self.drop_loot(enemy)
            if enemy.boss:
                self.on_boss_death(enemy)

    def damage_player(self, amount):
        p = self.player
        if p.invisible > 0:
            amount *= 0.45
        if p.damage_reduction > 0:
            amount *= 1 - p.damage_reduction
        amount *= 1 - p.armor / (p.armor + 100)
        p.hp -= amount
        p.hurt_flash = 0.12
        self.texts.append(FloatText(p.x, p.y - 22, f"-{round(amount)}", RED))
        if p.hp <= 0:
            p.hp = 0
            self.state = "defeat"

    def drop_loot(self, enemy):
        roll = self.rng.random()
        if enemy.boss:
            self.pickups.append(Pickup("chest", enemy.x, enemy.y, 0, 22, 120))
            self.pickups.append(Pickup("health", enemy.x - 30, enemy.y + 10, 45, 10, 60))
            self.pickups.append(Pickup("mana", enemy.x + 30, enemy.y + 10, 45, 10, 60))
            self.chest_spawned = True
        elif roll < 0.55:
            self.pickups.append(Pickup("gold", enemy.x, enemy.y, enemy.gold, 8))
        elif roll < 0.72:
            self.pickups.append(Pickup("health", enemy.x, enemy.y, 20, 10))
        elif roll < 0.86:
            self.pickups.append(Pickup("mana", enemy.x, enemy.y, 18, 10))

    def on_boss_death(self, boss):
        self.boss_defeated = True
        self.toast("The Dungeon Warden falls!", GOLD)
        self.effects.append(Effect("ring", boss.x, boss.y, 20, 280, 0.9, 0.9, GOLD))

    def gain_xp(self, amount):
        p = self.player
        p.xp += amount
        while p.xp >= p.xp_next:
            p.xp -= p.xp_next
            p.level += 1
            p.xp_next = int(p.xp_next * 1.3)
            p.max_hp += 14
            p.max_mana += 7
            p.atk += 2
            p.hp = min(p.max_hp, p.hp + p.max_hp * 0.35)
            p.mana = min(p.max_mana, p.mana + p.max_mana * 0.35)
            self.toast(f"LEVEL {p.level}! Stats increased.", ACCENT)
            self.effects.append(Effect("ring", p.x, p.y, 16, 90, 0.6, 0.6, ACCENT))

    # ------------------------------------------------------------------ abilities
    def use_ability(self, index):
        if self.state != "playing" or not self.player:
            return
        p = self.player
        ability = p.abilities[index]
        if p.cooldowns[index] > 0:
            self.toast(f"{ability.name} is on cooldown", MUTED)
            return
        if p.mana < ability.cost:
            self.toast("Not enough mana", BLUE)
            return
        p.mana -= ability.cost
        p.cooldowns[index] = ability.cooldown
        name = p.name
        if name == "Anon User":
            self.ability_anon(index)
        elif name == "OPmonkey":
            self.ability_opmonkey(index)
        else:
            self.ability_crushed(index)

    def ability_anon(self, index):
        p = self.player
        if index == 0:
            targets = sorted(self.enemies, key=lambda e: math.hypot(e.x - p.x, e.y - p.y))[:3]
            if targets:
                for enemy in targets:
                    self.fire_projectile(p.x, p.y, enemy.x, enemy.y, 430, 24, p.accent, "player", 7)
            else:
                for spread in (-0.2, 0, 0.2):
                    angle = math.atan2(p.facing_y, p.facing_x) + spread
                    self.fire_projectile(p.x, p.y, p.x + math.cos(angle) * 100, p.y + math.sin(angle) * 100, 430, 24, p.accent, "player", 7)
            self.effects.append(Effect("ring", p.x, p.y, 8, 45, 0.2, 0.2, p.accent))
        elif index == 1:
            self.effects.append(Effect("ring", p.x, p.y, 20, 205, 0.4, 0.4, p.accent))
            for enemy in list(self.enemies):
                if math.hypot(enemy.x - p.x, enemy.y - p.y) <= 205:
                    self.damage_enemy(enemy, 30)
                    if enemy in self.enemies and not enemy.boss:
                        enemy.stun = 1.5
                    elif enemy in self.enemies:
                        enemy.stun = 0.3
        elif index == 2:
            p.invisible = 3.0
            p.speed_buff = 3.0
            p.speed_mult = 1.55
            self.effects.append(Effect("ring", p.x, p.y, 20, 90, 0.5, 0.5, p.accent))
            self.toast("Anon vanishes into smoke", p.accent)
        else:
            for offset in (-36, 36):
                self.clones.append(Clone(p.x + offset, p.y + 18))
            self.effects.append(Effect("ring", p.x, p.y, 12, 80, 0.5, 0.5, p.accent))
            self.toast("Clone Warfare!", p.accent)

    def ability_opmonkey(self, index):
        p = self.player
        if index == 0:
            target = self.nearest_enemy(p.x, p.y, 125)
            if target:
                self.damage_enemy(target, 62)
                if target in self.enemies:
                    target.stun = 1.0
                self.effects.append(Effect("slash", target.x, target.y, 0, 60, 0.25, 0.25, p.accent))
            else:
                self.effects.append(Effect("ring", p.x, p.y, 10, 70, 0.25, 0.25, p.accent))
        elif index == 1:
            self.effects.append(Effect("ring", p.x, p.y, 20, 235, 0.45, 0.45, p.accent))
            for enemy in self.enemies:
                if math.hypot(enemy.x - p.x, enemy.y - p.y) <= 235:
                    enemy.taunt = 3.0
                    enemy.weak = 3.0
            self.toast("Sickening Scream - enemies taunted", p.accent)
        elif index == 2:
            p.regen_buff = 9
            p.regen_buff_timer = 3.0
            p.damage_reduction = 0.6
            p.damage_reduction_timer = 3.0
            self.effects.append(Effect("ring", p.x, p.y, 16, 90, 0.5, 0.5, ACCENT))
            self.toast("Rest Break", ACCENT)
        else:
            self.effects.append(Effect("ring", p.x, p.y, 20, 270, 0.55, 0.55, GOLD))
            for enemy in list(self.enemies):
                if math.hypot(enemy.x - p.x, enemy.y - p.y) <= 270:
                    self.damage_enemy(enemy, 52)
            p.hp = min(p.max_hp, p.hp + 48)
            self.texts.append(FloatText(p.x, p.y - 26, "+48 HP", ACCENT))
            self.toast("Plushie Storm!", GOLD)

    def ability_crushed(self, index):
        p = self.player
        if index == 0:
            target = self.nearest_enemy(p.x, p.y, 360)
            if target:
                dx = target.x - p.x
                dy = target.y - p.y
                dist = max(1, math.hypot(dx, dy))
                p.x = max(ARENA_LEFT + p.radius, min(ARENA_RIGHT - p.radius, target.x - dx / dist * 52))
                p.y = max(ARENA_TOP + p.radius, min(ARENA_BOTTOM - p.radius, target.y - dy / dist * 52))
            else:
                p.x = max(ARENA_LEFT + p.radius, min(ARENA_RIGHT - p.radius, p.x + p.facing_x * 150))
                p.y = max(ARENA_TOP + p.radius, min(ARENA_BOTTOM - p.radius, p.y + p.facing_y * 150))
            self.effects.append(Effect("ring", p.x, p.y, 25, 145, 0.4, 0.4, p.accent))
            for enemy in list(self.enemies):
                if math.hypot(enemy.x - p.x, enemy.y - p.y) <= 145:
                    self.damage_enemy(enemy, 56)
        elif index == 1:
            p.speed_buff = 6.0
            p.speed_mult = 1.45
            p.attack_speed_buff = 6.0
            p.attack_speed_mult = 1.65
            self.effects.append(Effect("ring", p.x, p.y, 12, 70, 0.45, 0.45, p.accent))
            self.toast("Energy Drink!", p.accent)
        elif index == 2:
            self.effects.append(Effect("ring", p.x, p.y, 18, 245, 0.5, 0.5, p.accent))
            for enemy in list(self.enemies):
                if math.hypot(enemy.x - p.x, enemy.y - p.y) <= 245:
                    self.damage_enemy(enemy, 24)
                    if enemy in self.enemies and not enemy.boss:
                        enemy.stun = 2.0
            self.toast("Jamming - enemies charmed", p.accent)
        else:
            p.hp = min(p.max_hp, p.hp + 78)
            self.effects.append(Effect("ring", p.x, p.y, 24, 300, 0.7, 0.7, GOLD))
            for enemy in list(self.enemies):
                if math.hypot(enemy.x - p.x, enemy.y - p.y) <= 300:
                    self.damage_enemy(enemy, 46)
            self.texts.append(FloatText(p.x, p.y - 28, "+78 HP", ACCENT))
            self.toast("Party Time!", GOLD)

    # ------------------------------------------------------------------ draw
    def draw(self):
        self.canvas.delete("all")
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "help":
            self.draw_help()
        else:
            self.draw_game()
            if self.state == "victory":
                self.draw_end_screen(True)
            elif self.state == "defeat":
                self.draw_end_screen(False)

    def draw_background(self):
        c = self.canvas
        c.create_rectangle(0, 0, WIDTH, HEIGHT, fill=BG, outline="")
        for x in range(0, WIDTH, 44):
            c.create_line(x, 0, x, HEIGHT, fill=GRID)
        for y in range(0, HEIGHT, 44):
            c.create_line(0, y, WIDTH, y, fill=GRID)
        c.create_rectangle(ARENA_LEFT, ARENA_TOP, ARENA_RIGHT, ARENA_BOTTOM, outline="#29446f", width=2)
        for i in range(6):
            x = ARENA_LEFT + 90 + i * 165
            c.create_oval(x - 3, ARENA_TOP + 30 - 3, x + 3, ARENA_TOP + 30 + 3, fill="#29446f", outline="")
            c.create_oval(x - 3, ARENA_BOTTOM - 30 - 3, x + 3, ARENA_BOTTOM - 30 + 3, fill="#29446f", outline="")

    def draw_menu(self):
        self.draw_background()
        c = self.canvas
        c.create_text(WIDTH / 2, 58, text="HANGOUT AREA", fill=TEXT, font=("Segoe UI", 30, "bold"))
        c.create_text(WIDTH / 2, 92, text="Combat Prototype  •  Choose your hero", fill=MUTED, font=("Segoe UI", 13))
        self.cards = []
        card_w, card_h = 310, 470
        gap = 26
        start_x = (WIDTH - (card_w * 3 + gap * 2)) / 2
        top = 135
        for i, data in enumerate(self.characters):
            x1 = start_x + i * (card_w + gap)
            y1 = top
            x2 = x1 + card_w
            y2 = y1 + card_h
            self.cards.append((x1, y1, x2, y2))
            c.create_rectangle(x1, y1, x2, y2, fill=PANEL, outline=data["color"], width=2)
            c.create_rectangle(x1, y1, x2, y1 + 84, fill=data["color"], outline="")
            c.create_text(x1 + 20, y1 + 22, text=f"{i + 1}", fill=BG, font=("Segoe UI", 15, "bold"), anchor="w")
            c.create_text(x1 + 20, y1 + 48, text=data["name"], fill=BG, font=("Segoe UI", 18, "bold"), anchor="w")
            c.create_text(x1 + 20, y1 + 70, text=data["role"], fill=BG, font=("Segoe UI", 10), anchor="w")
            c.create_text(x1 + 20, y1 + 104, text="COMBAT PROFILE", fill=MUTED, font=("Segoe UI", 9, "bold"), anchor="w")
            stats = [
                f"HP {data['max_hp']}    Mana {data['max_mana']}",
                f"ATK {data['atk']}     Armour {data['armor']}",
                f"Range {data['attack_range']}    Speed {data['speed']}",
            ]
            for n, line in enumerate(stats):
                c.create_text(x1 + 20, y1 + 128 + n * 19, text=line, fill=TEXT, font=("Consolas", 10), anchor="w")
            c.create_text(x1 + 20, y1 + 196, text="ABILITIES", fill=MUTED, font=("Segoe UI", 9, "bold"), anchor="w")
            for n, ability in enumerate(data["abilities"]):
                c.create_text(x1 + 20, y1 + 220 + n * 25, text=f"{ability.key:>5}", fill=data["accent"], font=("Consolas", 10, "bold"), anchor="w")
                c.create_text(x1 + 72, y1 + 220 + n * 25, text=ability.name, fill=TEXT, font=("Segoe UI", 10), anchor="w")
            c.create_text(x1 + 20, y1 + 336, text="SIGNATURE", fill=MUTED, font=("Segoe UI", 9, "bold"), anchor="w")
            c.create_text(x1 + 20, y1 + 356, text=data["signature"], fill=GOLD, font=("Segoe UI", 10, "bold"), anchor="w")
            c.create_text(x1 + 20, y1 + 392, text="Auto-attacks automatically.", fill=MUTED, font=("Segoe UI", 9), anchor="w")
            c.create_text(x1 + 20, y1 + 410, text="Use Q / E / R / Space.", fill=MUTED, font=("Segoe UI", 9), anchor="w")
            c.create_text(x1 + 20, y1 + 432, text="Click card or press number.", fill=data["accent"], font=("Segoe UI", 9), anchor="w")
        c.create_text(WIDTH / 2, HEIGHT - 28, text="WASD / Arrows to move   •   H for help", fill=MUTED, font=("Segoe UI", 11))

    def draw_help(self):
        self.draw_background()
        c = self.canvas
        c.create_rectangle(170, 90, WIDTH - 170, HEIGHT - 90, fill=PANEL, outline=ACCENT, width=2)
        c.create_text(WIDTH / 2, 130, text="HOW TO PLAY", fill=ACCENT, font=("Segoe UI", 24, "bold"))
        lines = [
            ("WASD / Arrow Keys", "Move your hero."),
            ("Basic attacks", "Automatic. Your hero attacks the nearest enemy in range."),
            ("Q / E / R / Space", "Use your four abilities. They cost mana and have cooldowns."),
            ("H", "Open or close this help screen."),
            ("Goal", "Survive two waves, defeat the Dungeon Warden, and claim the signature cache."),
            ("Loot", "Walk over gold, health and mana orbs. The boss drops the chest."),
            ("Tips", "Kiting works. Save mana for the boss. Use crowd control to survive."),
        ]
        y = 190
        for label, text in lines:
            c.create_text(210, y, text=label, fill=GOLD, font=("Segoe UI", 12, "bold"), anchor="w")
            c.create_text(410, y, text=text, fill=TEXT, font=("Segoe UI", 11), anchor="w")
            y += 48
        c.create_text(WIDTH / 2, HEIGHT - 130, text="Press H or Esc to close", fill=MUTED, font=("Segoe UI", 12))

    def draw_game(self):
        self.draw_background()
        c = self.canvas
        p = self.player
        if not p:
            return

        # arena decor
        c.create_text(ARENA_LEFT + 18, ARENA_TOP + 16, text=f"WAVE {max(1, self.wave)}", fill=MUTED, font=("Consolas", 10), anchor="w")
        c.create_text(ARENA_RIGHT - 18, ARENA_TOP + 16, text=f"KILLS {self.kills}", fill=MUTED, font=("Consolas", 10), anchor="e")

        # pickups
        for pickup in self.pickups:
            color = {"gold": GOLD, "health": ACCENT, "mana": BLUE, "chest": GOLD}[pickup.kind]
            if pickup.kind == "chest":
                c.create_rectangle(pickup.x - 18, pickup.y - 14, pickup.x + 18, pickup.y + 14, fill="#5c3d12", outline=color, width=2)
                c.create_line(pickup.x - 18, pickup.y - 8, pickup.x + 18, pickup.y - 8, fill=color, width=2)
                c.create_text(pickup.x, pickup.y + 24, text="SIGNATURE CACHE", fill=GOLD, font=("Consolas", 8, "bold"))
            else:
                c.create_oval(pickup.x - pickup.radius, pickup.y - pickup.radius, pickup.x + pickup.radius, pickup.y + pickup.radius, fill=color, outline="")
                label = {"gold": "G", "health": "+", "mana": "M"}[pickup.kind]
                c.create_text(pickup.x, pickup.y, text=label, fill=BG, font=("Consolas", 8, "bold"))

        # effects
        for effect in self.effects:
            frac = max(0, effect.life / effect.max_life)
            radius = effect.radius + (effect.max_radius - effect.radius) * (1 - frac)
            if effect.kind == "ring":
                c.create_oval(effect.x - radius, effect.y - radius, effect.x + radius, effect.y + radius, outline=effect.color, width=2)
            else:
                c.create_line(effect.x - radius, effect.y, effect.x + radius, effect.y, fill=effect.color, width=3)
                c.create_line(effect.x, effect.y - radius, effect.x, effect.y + radius, fill=effect.color, width=3)

        # enemies
        for enemy in self.enemies:
            color = "#ffffff" if enemy.hit_flash > 0 else enemy.color
            if enemy.kind == "runner":
                c.create_polygon(
                    enemy.x, enemy.y - enemy.radius,
                    enemy.x + enemy.radius, enemy.y + enemy.radius,
                    enemy.x - enemy.radius, enemy.y + enemy.radius,
                    fill=color, outline="",
                )
            else:
                c.create_oval(
                    enemy.x - enemy.radius, enemy.y - enemy.radius,
                    enemy.x + enemy.radius, enemy.y + enemy.radius,
                    fill=color, outline="#ffd7dd" if enemy.boss else "",
                    width=2 if enemy.boss else 1,
                )
                if enemy.boss:
                    c.create_text(enemy.x, enemy.y, text="W", fill=BG, font=("Segoe UI", 18, "bold"))
            if enemy.stun > 0:
                c.create_text(enemy.x, enemy.y - enemy.radius - 14, text="STUN", fill=GOLD, font=("Consolas", 8, "bold"))
            elif enemy.taunt > 0:
                c.create_text(enemy.x, enemy.y - enemy.radius - 14, text="TAUNT", fill=RED, font=("Consolas", 8, "bold"))
            if not enemy.boss:
                bar_w = enemy.radius * 2
                hp_frac = max(0, enemy.hp / enemy.max_hp)
                c.create_rectangle(enemy.x - bar_w / 2, enemy.y - enemy.radius - 8, enemy.x + bar_w / 2, enemy.y - enemy.radius - 4, fill="#2a1620", outline="")
                c.create_rectangle(enemy.x - bar_w / 2, enemy.y - enemy.radius - 8, enemy.x - bar_w / 2 + bar_w * hp_frac, enemy.y - enemy.radius - 4, fill=RED, outline="")

        # clones
        for clone in self.clones:
            c.create_oval(clone.x - 14, clone.y - 14, clone.x + 14, clone.y + 14, outline=p.accent, width=2)
            c.create_text(clone.x, clone.y, text="C", fill=p.accent, font=("Consolas", 9, "bold"))

        # player
        pulse = 2 + math.sin(self.menu_time * 5) * 1.5
        if p.invisible > 0:
            c.create_oval(p.x - 24 - pulse, p.y - 24 - pulse, p.x + 24 + pulse, p.y + 24 + pulse, outline=p.accent, width=1)
        c.create_oval(p.x - p.radius, p.y - p.radius, p.x + p.radius, p.y + p.radius, fill="#ffffff" if p.hurt_flash > 0 else p.color, outline=p.accent, width=3)
        c.create_text(p.x, p.y, text=p.name[0], fill=BG, font=("Segoe UI", 14, "bold"))
        c.create_text(p.x, p.y + 30, text=p.name, fill=p.accent, font=("Segoe UI", 9, "bold"))

        # projectiles
        for projectile in self.projectiles:
            c.create_oval(
                projectile.x - projectile.radius, projectile.y - projectile.radius,
                projectile.x + projectile.radius, projectile.y + projectile.radius,
                fill=projectile.color, outline="",
            )

        # floating text
        for text in self.texts:
            frac = max(0, text.life / text.max_life)
            c.create_text(text.x, text.y, text=text.text, fill=text.color, font=("Segoe UI", 10, "bold"))

        self.draw_hud()

    def draw_hud(self):
        c = self.canvas
        p = self.player
        c.create_rectangle(0, 0, WIDTH, 82, fill=PANEL, outline="")
        c.create_text(24, 18, text=f"{p.name}  •  Lv {p.level}", fill=p.accent, font=("Segoe UI", 14, "bold"), anchor="w")
        self.bar(24, 40, 290, 12, p.hp / p.max_hp, RED, f"HP {int(p.hp)}/{int(p.max_hp)}")
        self.bar(24, 58, 290, 10, p.mana / p.max_mana, BLUE, f"MP {int(p.mana)}/{int(p.max_mana)}")
        self.bar(340, 58, 180, 10, p.xp / p.xp_next, GOLD, f"XP {p.xp}/{p.xp_next}")
        c.create_text(344, 40, text=f"ATK {int(p.atk)}   ARM {int(p.armor)}", fill=MUTED, font=("Consolas", 10), anchor="w")

        c.create_text(WIDTH - 24, 18, text=f"WAVE {max(1, self.wave)}   KILLS {self.kills}", fill=TEXT, font=("Consolas", 11, "bold"), anchor="e")
        c.create_text(WIDTH - 24, 38, text=f"GOLD {self.gold}   TIME {self.elapsed:0.1f}s", fill=GOLD, font=("Consolas", 10), anchor="e")
        c.create_text(WIDTH - 24, 58, text="H  Help / Pause", fill=MUTED, font=("Segoe UI", 9), anchor="e")

        boss = next((e for e in self.enemies if e.boss), None)
        if boss:
            bw = 520
            bx = (WIDTH - bw) / 2
            c.create_text(WIDTH / 2, 92, text="DUNGEON WARDEN", fill=RED, font=("Segoe UI", 11, "bold"))
            c.create_rectangle(bx, 102, bx + bw, 112, fill="#2a1620", outline="")
            c.create_rectangle(bx, 102, bx + bw * max(0, boss.hp / boss.max_hp), 112, fill=RED, outline="")

        # ability bar
        bar_y = HEIGHT - 70
        box_w = 250
        gap = 8
        start = (WIDTH - (box_w * 4 + gap * 3)) / 2
        for i, ability in enumerate(p.abilities):
            x = start + i * (box_w + gap)
            ready = p.cooldowns[i] <= 0 and p.mana >= ability.cost
            outline = p.accent if ready else "#33456a"
            c.create_rectangle(x, bar_y, x + box_w, bar_y + 52, fill=PANEL_2, outline=outline, width=2)
            c.create_text(x + 12, bar_y + 15, text=ability.key, fill=p.accent if ready else MUTED, font=("Consolas", 10, "bold"), anchor="w")
            c.create_text(x + 62, bar_y + 15, text=ability.name, fill=TEXT if ready else MUTED, font=("Segoe UI", 10, "bold"), anchor="w")
            c.create_text(x + 12, bar_y + 36, text=f"{ability.cost} mana", fill=BLUE if p.mana >= ability.cost else RED, font=("Consolas", 9), anchor="w")
            if p.cooldowns[i] > 0:
                frac = p.cooldowns[i] / ability.cooldown
                c.create_rectangle(x + 1, bar_y + 1, x + box_w - 1, bar_y + 1 + 50 * frac, fill="#050914", outline="")
                c.create_text(x + box_w - 12, bar_y + 36, text=f"{p.cooldowns[i]:0.1f}s", fill=MUTED, font=("Consolas", 9), anchor="e")
            else:
                c.create_text(x + box_w - 12, bar_y + 36, text="READY", fill=ACCENT, font=("Consolas", 8, "bold"), anchor="e")

        # toasts
        y = 132
        for toast in self.toasts:
            c.create_text(WIDTH / 2, y, text=toast["text"], fill=toast["color"], font=("Segoe UI", 11, "bold"))
            y += 22

    def bar(self, x, y, w, h, frac, color, label):
        c = self.canvas
        c.create_rectangle(x, y, x + w, y + h, fill="#1b1020", outline="#2e3550")
        c.create_rectangle(x, y, x + w * max(0, min(1, frac)), y + h, fill=color, outline="")
        c.create_text(x + 6, y + h / 2, text=label, fill=TEXT, font=("Consolas", 8, "bold"), anchor="w")

    def draw_end_screen(self, victory):
        c = self.canvas
        c.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#050914", stipple="gray50", outline="")
        c.create_rectangle(220, 150, WIDTH - 220, HEIGHT - 150, fill=PANEL, outline=ACCENT if victory else RED, width=2)
        title = "VICTORY" if victory else "DEFEAT"
        color = ACCENT if victory else RED
        c.create_text(WIDTH / 2, 210, text=title, fill=color, font=("Segoe UI", 34, "bold"))
        if victory:
            c.create_text(WIDTH / 2, 260, text="The Dungeon Warden has fallen.", fill=TEXT, font=("Segoe UI", 14))
            c.create_text(WIDTH / 2, 300, text="SIGNATURE CACHE", fill=MUTED, font=("Segoe UI", 10, "bold"))
            c.create_text(WIDTH / 2, 332, text=self.victory_signature, fill=GOLD, font=("Segoe UI", 20, "bold"))
        else:
            c.create_text(WIDTH / 2, 260, text="Your run ends here... for now.", fill=TEXT, font=("Segoe UI", 14))
        p = self.player
        lines = [
            f"Hero: {p.name}",
            f"Level: {p.level}",
            f"Kills: {self.kills}",
            f"Gold: {self.gold}",
            f"Time: {self.elapsed:0.1f}s",
        ]
        for i, line in enumerate(lines):
            c.create_text(WIDTH / 2, 390 + i * 26, text=line, fill=TEXT, font=("Consolas", 12))
        c.create_text(WIDTH / 2, HEIGHT - 205, text="Press Enter to play again   •   M for hero select", fill=MUTED, font=("Segoe UI", 12))

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
    game = Game(root, smoke=True)
    for index in range(3):
        game.start_run(index)
        for _ in range(360):
            game.update(1 / 60)
        for ability in range(4):
            game.use_ability(ability)
            game.update(1 / 60)
    print("Combat prototype smoke test passed.")
    root.destroy()


def main():
    if "--smoke-test" in sys.argv:
        smoke_test()
        return
    root = tk.Tk()
    root.title("Hangout Area - Combat Prototype")
    root.resizable(False, False)
    game = Game(root)
    game.run()


if __name__ == "__main__":
    main()
