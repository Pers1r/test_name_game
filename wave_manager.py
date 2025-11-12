import pygame
import random
import pygame
import math
from enemy import Enemy


class WaveManager:
    def __init__(self):
        self.wave_number = 0
        self.wave_active = False
        self.enemies_to_spawn_this_wave = 0
        self.spawn_timer = 0
        self.spawn_delay = 1000

    def start_next_wave(self):
        if self.wave_active:
            print("Cannot start wave: a wave is already active.")
            return

        self.wave_number += 1
        self.wave_active = True
        self.enemies_to_spawn_this_wave = 5 + (self.wave_number * 3)
        self.spawn_timer = pygame.time.get_ticks()
        print(f"--- STARTING WAVE {self.wave_number} ---")

    def _spawn_enemy(self, player, world_surface_width, current_world):
        spawn_radius = (world_surface_width / 2) + random.randint(50, 150)
        angle = random.uniform(0, 2 * math.pi)

        spawn_x = player.pos.x + math.cos(angle) * spawn_radius
        spawn_y = player.pos.y + math.sin(angle) * spawn_radius

        current_world.enemy_list.append(Enemy(spawn_x, spawn_y))

    def update(self, current_time, player, current_world):
        if self.wave_active and self.enemies_to_spawn_this_wave > 0:
            if current_time - self.spawn_timer > self.spawn_delay:
                self.spawn_timer = current_time
                # Use a dummy surface width for now, or pass from Game
                # TODO: This logic might need player's camera width
                self._spawn_enemy(player, 1280 / 1.0, current_world)
                self.enemies_to_spawn_this_wave -= 1

        if self.wave_active and self.enemies_to_spawn_this_wave == 0:
            if not current_world.enemy_list:
                self.wave_active = False
                print(f"--- WAVE {self.wave_number} COMPLETE! ---")
                print("Press 'N' to start next wave.")

    def get_debug_info(self):
        wave_text = f"Wave: {self.wave_number} (Active: {self.wave_active})"
        spawning_text = f"To Spawn: {self.enemies_to_spawn_this_wave}"
        return wave_text, spawning_text
