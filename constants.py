# screen settings
SCREEN_WIDTH = 1280 # in px
SCREEN_HEIGHT = 720 # in px
RUNNING = True
TILE_SIZE = 32 # in px
CHUNK_SIZE = 16 # in px

# Game settings
ZOOM_LEVEL = 1.0
FPS = 60
START_CHUNKS_NUM = 5

# Enemy
SEPARATION_STRENGTH = 1.5 # strength that defines how strong enemies will push nearby enemies
ENEMY_SIZE = TILE_SIZE//2
ENEMY_SPEED = 100 # in px
ENEMY_HEALTH = 10

# Path finding
PATH_RECALC_DELAY = 1000 # in ms

# Player
PLAYER_SPEED = 200 # in px
PLAYER_RADIUS = TILE_SIZE // 2.5
PLAYER_HEALTH = 100
PLATER_SHOOT_DELAY = 150

# Bullet
BULLET_SIZE = 4 # in px
BULLET_SPEED = 700
BULLET_LIFETIME = 2.0 # how long bullet will live, when below 0 bullet is beeng destroyed

# Colors
GREEN = (40, 120, 40)
BROWN = (100, 80, 50)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (50, 50, 200)
