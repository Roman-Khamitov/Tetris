import pygame
from menu import main_menu

def main():
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    pygame.display.set_caption("Multiplayer Tetris")
    main_menu(screen)
    pygame.mixer.music.stop()
if __name__ == "__main__":
    main()
