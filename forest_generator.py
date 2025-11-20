# forest_generator.py
import random
import math
from noise import pnoise2

class ForestGenerator:
    def __init__(self, seed):
        self.seed = seed
        self.scale = 0.1  # Controls how "zoomed in" the forest blobs are. Smaller = bigger forests.
        self.octaves = 2
        self.persistence = 0.5
        self.lacunarity = 2.0

    def get_tree_at(self, grid_x, grid_y):
        """
        Returns 'tree_large', 'tree_small', 'bush', or None based on noise.
        """
        # 1. Generate Noise Value (-1.0 to 1.0)
        # We offset x/y by the seed to make every world different
        noise_val = pnoise2(grid_x * self.scale + self.seed,
                            grid_y * self.scale + self.seed,
                            octaves=self.octaves,
                            persistence=self.persistence,
                            lacunarity=self.lacunarity,
                            repeatx=1024, repeaty=1024,
                            base=self.seed)

        # 2. Determine Tree Type based on thresholds
        # Adjust these numbers to change forest density

        # Deep Forest (Center)
        if noise_val > 0.45:
            return 'tree_large'

        # Normal Forest
        elif noise_val > 0.40:
            return 'tree_small'

        # Edge of Forest (Bushes)
        elif noise_val > 0.35:
            return 'bush'

        # Random isolated bushes (outside of forests)
        # 2% chance to spawn a random bush in open fields
        elif random.random() < 0.005:
            return 'bush'

        return None