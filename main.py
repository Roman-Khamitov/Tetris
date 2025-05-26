import pygame
from menu import main_menu

def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 700))
    pygame.display.set_caption("Multiplayer Tetris")
    main_menu(screen)

if __name__ == "__main__":
    main()
