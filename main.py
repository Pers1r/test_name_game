import pygame
import sys
import os

from game import Game

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    # --- Setup Asset Path ---
    # We set the global asset path *before* initializing the game
    # This assumes your main.py is in the root and assets are in root/assets
    # If not, adjust as needed.
    ASSET_PATH = resource_path("assets")

    # --- Parse CLI Arguments ---
    debug = "--debug" in sys.argv
    performance = "--perf" in sys.argv

    # --- Create and Run the Game ---
    try:
        game_instance = Game(debug=debug, performance=performance, asset_path=ASSET_PATH)
        game_instance.run()
    except Exception as e:
        print(f"\n--- FATAL ERROR ---")
        print(f"An unhandled exception occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()