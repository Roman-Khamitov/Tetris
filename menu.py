import pygame
import sys

# Цвета
WHITE = (255, 255, 255)
GRAY = (30, 30, 30)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLACK = (0, 0, 0)

# Цвета фигур тетриса
TETRIS_COLORS = [
    (0, 255, 255),     # I
    (255, 255, 0),     # O
    (128, 0, 128),     # T
    (0, 255, 0),       # S
    (255, 0, 0),       # Z
    (0, 0, 255),       # J
    (255, 165, 0),     # L
]

# Буквы "TETRIS" как пиксельные схемы (5x5 каждая)
TETRIS_LETTERS = {
    'T': ["#####",
          "  #  ",
          "  #  ",
          "  #  ",
          "  #  "],
    'E': ["#####",
          "#    ",
          "###  ",
          "#    ",
          "#####"],
    'R': ["#### ",
          "#   #",
          "#### ",
          "#  # ",
          "#   #"],
    'I': [" ### ",
          "  #  ",
          "  #  ",
          "  #  ",
          " ### "],
    'S': [" ####",
          "#    ",
          " ### ",
          "    #",
          "#### "],
}

def draw_text(screen, text, size, x, y, color=WHITE):
    font = pygame.font.SysFont("Arial", size, bold=True)
    label = font.render(text, True, color)
    rect = label.get_rect(center=(x, y))
    screen.blit(label, rect)

def draw_button(screen, text, x, y, width, height, color):
    pygame.draw.rect(screen, color, (x, y, width, height), border_radius=12)
    draw_text(screen, text, 30, x + width // 2, y + height // 2)

def draw_tetris_logo(screen, start_x, start_y, block_size):
    x = start_x
    color_idx = 0

    for letter in "TETRIS":
        pattern = TETRIS_LETTERS[letter]
        color = TETRIS_COLORS[color_idx % len(TETRIS_COLORS)]
        color_idx += 1

        for row_idx, row in enumerate(pattern):
            for col_idx, char in enumerate(row):
                if char == "#":
                    rect = pygame.Rect(
                        x + col_idx * block_size,
                        start_y + row_idx * block_size,
                        block_size,
                        block_size
                    )
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, BLACK, rect, 2)  # обводка

        x += (len(pattern[0]) + 1) * block_size  # Отступ между буквами

def main_menu(screen):
    clock = pygame.time.Clock()

    while True:
        screen.fill(GRAY)

        # Рисуем логотип TETRIS из фигур
        draw_tetris_logo(screen, 50, 50, 20)

        # Кнопки
        draw_button(screen, "1. Начать игру", 200, 250, 200, 60, GREEN)
        draw_button(screen, "2. Выйти",        200, 330, 200, 60, RED)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    from game import run_game
                    run_game(screen)  # заменить на свою игру
                elif event.key == pygame.K_2 or event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        clock.tick(60)

