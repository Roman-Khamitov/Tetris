import pygame
import json
import os
from datetime import datetime

# Константы
HIGHSCORES_FILE = "assets/highscores.json"
FONT_NAME = "Arial"
GRAY = (30, 30, 30)
WHITE = (255, 255, 255)
YELLOW = (255, 200, 0)
BLACK = (0, 0, 0)

def draw_text(screen, text, size, x, y, color=WHITE, align="center"):
    font = pygame.font.SysFont(FONT_NAME, size, bold=True)
    label = font.render(text, True, color)
    if align == "center":
        rect = label.get_rect(center=(x, y))
    elif align == "left":
        rect = label.get_rect(topleft=(x, y))
    screen.blit(label, rect)

def draw_button(screen, text, rect, color, hover=False):
    base_color = tuple(min(255, c + 30) for c in color) if hover else color
    pygame.draw.rect(screen, base_color, rect, border_radius=12)
    draw_text(screen, text, 30, rect.centerx, rect.centery)

def load_highscores():
    if not os.path.exists(HIGHSCORES_FILE):
        return []
    try:
        with open(HIGHSCORES_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def show_highscores(screen):
    clock = pygame.time.Clock()
    width, height = screen.get_size()
    
    highscores = load_highscores()
    highscores.sort(key=lambda x: x["score"], reverse=True)
    highscores = highscores[:100]
    print(f"Отображаем {len(highscores)} записей в таблице рейтинга")

    table_x = width // 8
    table_y = height // 6
    row_height = 40
    col_widths = [50, 200, 100, 100, 100, 200]
    headers = ["№", "Ник", "Очки", "Уровень", "Линии", "Дата"]

    button_width = 150
    button_height = 50
    back_button_rect = pygame.Rect((width - button_width) // 2, height - 100, button_width, button_height)

    while True:
        screen.fill(GRAY)

        draw_text(screen, "Таблица рейтинга", 50, width // 2, table_y - 60)

        x = table_x
        for i, header in enumerate(headers):
            draw_text(screen, header, 30, x + col_widths[i] // 2, table_y, WHITE, align="left")
            x += col_widths[i]

        pygame.draw.line(screen, WHITE, (table_x, table_y + 40), (table_x + sum(col_widths), table_y + 40), 2)
        for i in range(len(highscores) + 1):
            pygame.draw.line(screen, WHITE, (table_x, table_y + (i + 1) * row_height), 
                             (table_x + sum(col_widths), table_y + (i + 1) * row_height), 1)
        for i in range(len(headers) + 1):
            x = table_x + sum(col_widths[:i])
            pygame.draw.line(screen, WHITE, (x, table_y), (x, table_y + (len(highscores) + 1) * row_height), 1)

        for i, entry in enumerate(highscores):
            date = datetime.fromtimestamp(entry["date"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            row_data = [
                str(i + 1),
                entry["nickname"],
                str(entry["score"]),
                str(entry["level"]),
                str(entry["lines"]),
                date
            ]
            x = table_x
            for j, data in enumerate(row_data):
                draw_text(screen, data, 25, x + col_widths[j] // 2, table_y + (i + 1) * row_height + row_height // 2, WHITE, align="left")
                x += col_widths[j]

        mouse_pos = pygame.mouse.get_pos()
        draw_button(screen, "Назад", back_button_rect, YELLOW, back_button_rect.collidepoint(mouse_pos))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False  # Возврат в меню
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button_rect.collidepoint(event.pos):
                    return False  # Возврат в меню

        clock.tick(60)