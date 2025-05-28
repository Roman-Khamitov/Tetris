import pygame
import sys
import math

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

# Пиксельные схемы букв "TETRIS" (5x5)
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

def draw_button(screen, text, rect, color, hover=False):
    base_color = tuple(min(255, c + 30) for c in color) if hover else color
    pygame.draw.rect(screen, base_color, rect, border_radius=12)
    draw_text(screen, text, 30, rect.centerx, rect.centery)

def draw_tetris_logo(screen, start_x, start_y, block_size, pulse_scale=1.0):
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
                        x + col_idx * block_size * pulse_scale,
                        start_y + row_idx * block_size * pulse_scale,
                        block_size * pulse_scale,
                        block_size * pulse_scale
                    )
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, BLACK, rect, 2)  # обводка

        x += (len(pattern[0]) + 1) * block_size * pulse_scale

def main_menu(screen):
    clock = pygame.time.Clock()
    width, height = screen.get_size()

    button_width = width // 3
    button_height = 60
    button_x = (width - button_width) // 2
    button1_y = height // 2
    button2_y = button1_y + 90
    button3_y = button2_y + 90

    # Прямоугольники кнопок
    button1_rect = pygame.Rect(button_x, button1_y, button_width, button_height)
    button2_rect = pygame.Rect(button_x, button2_y, button_width, button_height)
    button3_rect = pygame.Rect(button_x, button3_y, button_width, button_height)

    frame = 0

    while True:
        screen.fill(GRAY)

        # Пульсация логотипа
        pulse = 1.0 + 0.05 * math.sin(frame * 0.1)
        block_size = min(width, height) // 25
        logo_x = (width - block_size * 6 * 6) // 2
        logo_y = height // 8

        draw_tetris_logo(screen, logo_x, logo_y, block_size, pulse)

        mouse_pos = pygame.mouse.get_pos()

        # Кнопки
        draw_button(screen, "1. Начать игру",       button1_rect, GREEN, button1_rect.collidepoint(mouse_pos))
        draw_button(screen, "2. Выйти",             button2_rect, RED,   button2_rect.collidepoint(mouse_pos))
        draw_button(screen, "3. Для двух игроков",  button3_rect, (0, 100, 255), button3_rect.collidepoint(mouse_pos))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    from game import run_game
                    run_game(screen)
                elif event.key == pygame.K_2 or event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_3:
                    from game import run_game
                    run_game(screen, multiplayer=True)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button1_rect.collidepoint(event.pos):
                    from game import run_game
                    run_game(screen)
                elif button2_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                elif button3_rect.collidepoint(event.pos):
                    from game import run_game
                    run_game(screen, multiplayer=True)

        frame += 1
        clock.tick(60)
