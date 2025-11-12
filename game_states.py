from enum import Enum, auto

class GameState(Enum):
    PLAYING = auto()
    PAUSED = auto()
    INVENTORY = auto()
    CRAFTING = auto()