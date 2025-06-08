import pygame
import sys
import math

# Цвета
WHITE = (255, 255, 255)
GRAY = (30, 30, 30)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
PURPLE = (128, 0, 255)
YELLOW = (255, 200, 0)

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
          " ### ",
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
                    pygame.draw.rect(screen, BLACK, rect, 2)

        x += (len(pattern[0]) + 1) * block_size * pulse_scale

def main_menu(screen):
    pygame.mixer.music.load("assets/MenuTheme.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    clock = pygame.time.Clock()
    width, height = screen.get_size()

    button_width = width // 3
    button_height = 60
    button_x = (width - button_width) // 2
    button_spacing = 80
    
    first_button_y = height // 2 - button_spacing

    button1_rect = pygame.Rect(button_x, first_button_y, button_width, button_height)
    button2_rect = pygame.Rect(button_x, first_button_y + button_spacing, button_width, button_height)
    button3_rect = pygame.Rect(button_x, first_button_y + button_spacing * 2, button_width, button_height)
    button4_rect = pygame.Rect(button_x, first_button_y + button_spacing * 3, button_width, button_height)
    button5_rect = pygame.Rect(button_x, first_button_y + button_spacing * 4, button_width, button_height)
    button6_rect = pygame.Rect(button_x, first_button_y + button_spacing * 5, button_width, button_height)

    frame = 0

    while True:
        screen.fill(GRAY)

        pulse = 1.0 + 0.05 * math.sin(frame * 0.1)
        block_size = min(width, height) // 25
        logo_x = (width - block_size * 6 * 6) // 2
        logo_y = height // 8

        draw_tetris_logo(screen, logo_x, logo_y, block_size, pulse)

        mouse_pos = pygame.mouse.get_pos()

        draw_button(screen, "1. Начать игру", button1_rect, GREEN, button1_rect.collidepoint(mouse_pos))
        draw_button(screen, "2. Для двух игроков", button2_rect, BLUE, button2_rect.collidepoint(mouse_pos))
        draw_button(screen, "3. Рейтинговая игра", button3_rect, PURPLE, button3_rect.collidepoint(mouse_pos))
        draw_button(screen, "4. Таблица рейтинга", button4_rect, YELLOW, button4_rect.collidepoint(mouse_pos))
        draw_button(screen, "5. Настройки", button5_rect, (100, 100, 255), button5_rect.collidepoint(mouse_pos))
        draw_button(screen, "6. Выйти", button6_rect, RED, button6_rect.collidepoint(mouse_pos))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    pygame.mixer.music.stop()
                    from game import run_game
                    run_game(screen)
                elif event.key == pygame.K_2:
                    pygame.mixer.music.stop()
                    from game import run_game
                    run_game(screen, multiplayer=True)
                elif event.key == pygame.K_3:
                    pygame.mixer.music.stop()
                    from rating import start_rating_game
                    start_rating_game(screen)
                elif event.key == pygame.K_4:
                    pygame.mixer.music.stop()
                    from toptable import show_highscores
                    show_highscores(screen)
                    pygame.mixer.music.play(-1)  # Возобновляем музыку после возврата
                elif event.key == pygame.K_5:
                    print("Настройки")
                elif event.key == pygame.K_6 or event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button1_rect.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    from game import run_game
                    run_game(screen)
                elif button2_rect.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    from game import run_game
                    run_game(screen, multiplayer=True)
                elif button3_rect.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    from rating import start_rating_game
                    start_rating_game(screen)
                elif button4_rect.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    from toptable import show_highscores
                    show_highscores(screen)
                    pygame.mixer.music.play(-1)  # Возобновляем музыку после возврата
                elif button5_rect.collidepoint(event.pos):
                    print("Настройки")
                elif button6_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        frame += 1
        clock.tick(60)