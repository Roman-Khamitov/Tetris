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
BLUE = (0, 100, 255)
DARK_BLUE = (0, 50, 150)
LIGHT_GRAY = (60, 60, 60)
HIGHLIGHT_COLOR = (255, 255, 150)

# Градиент для фона
def draw_gradient_background(screen):
    width, height = screen.get_size()
    for y in range(height):
        # Интерполяция между темно-серым и почти черным
        color = [max(10, 30 - y//30), max(10, 30 - y//30), max(10, 30 - y//30)]
        pygame.draw.line(screen, color, (0, y), (width, y))

def draw_text(screen, text, size, x, y, color=WHITE, align="center", font_name=FONT_NAME, bold=True):
    font = pygame.font.SysFont(font_name, size, bold=bold)
    label = font.render(text, True, color)
    if align == "center":
        rect = label.get_rect(center=(x, y))
    elif align == "left":
        rect = label.get_rect(topleft=(x, y))
    elif align == "right":
        rect = label.get_rect(topright=(x, y))
    screen.blit(label, rect)

def draw_button(screen, text, rect, color, hover=False, text_color=BLACK):
    base_color = tuple(min(255, c + 40) for c in color) if hover else color
    # Кнопка с тенью и скругленными углами
    pygame.draw.rect(screen, (0, 0, 0), rect.inflate(8, 8), border_radius=15)
    pygame.draw.rect(screen, base_color, rect, border_radius=12)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=12)  # Обводка
    
    # Текст кнопки
    draw_text(screen, text, 30, rect.centerx, rect.centery, text_color)

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
    
    # Загрузка и сортировка рекордов
    highscores = load_highscores()
    highscores.sort(key=lambda x: x["score"], reverse=True)
    highscores = highscores[:100]
    
    # Адаптивные размеры
    table_width = min(width * 0.9, 1000)  # Максимальная ширина таблицы
    table_x = (width - table_width) // 2
    table_y = height * 0.15
    row_height = max(35, height // 25)  # Минимальная высота строки
    
    # Адаптивные ширины колонок
    col_widths = [
        table_width * 0.07,  # №
        table_width * 0.25,  # Ник
        table_width * 0.15,  # Очки
        table_width * 0.12,  # Уровень
        table_width * 0.12,  # Линии
        table_width * 0.29   # Дата
    ]
    
    headers = ["№", "Ник", "Очки", "Уровень", "Линии", "Дата"]
    
    # Кнопка "Назад"
    button_width = min(200, width * 0.3)
    button_height = min(50, height * 0.08)
    back_button_rect = pygame.Rect((width - button_width) // 2, height - 100, button_width, button_height)
    
    # Прокрутка
    scroll_offset = 0
    max_scroll = max(0, len(highscores) * row_height - height * 0.5)
    
    # Анимация появления
    alpha_surface = pygame.Surface((width, height))
    alpha_surface.fill(BLACK)
    for alpha in range(255, 0, -10):
        alpha_surface.set_alpha(alpha)
        draw_gradient_background(screen)
        pygame.display.flip()
        screen.blit(alpha_surface, (0, 0))
        pygame.time.delay(30)
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        # Обработка событий прокрутки
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_DOWN:
                    scroll_offset = min(scroll_offset + row_height, max_scroll)
                elif event.key == pygame.K_UP:
                    scroll_offset = max(scroll_offset - row_height, 0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button_rect.collidepoint(event.pos):
                    running = False
                elif event.button == 4:  # Колесо вверх
                    scroll_offset = max(scroll_offset - row_height * 2, 0)
                elif event.button == 5:  # Колесо вниз
                    scroll_offset = min(scroll_offset + row_height * 2, max_scroll)
            elif event.type == pygame.MOUSEMOTION:
                if mouse_pressed and max_scroll > 0:
                    scroll_offset = min(max(0, scroll_offset - event.rel[1]), max_scroll)
        
        # Отрисовка
        draw_gradient_background(screen)
        
        # Заголовок с эффектом свечения
        draw_text(screen, "Таблица рекордов", min(60, width // 15), width // 2, table_y * 0.7, YELLOW)
        pygame.draw.line(screen, YELLOW, (width * 0.25, table_y * 0.9), (width * 0.75, table_y * 0.9), 3)
        
        # Область таблицы с тенью
        table_rect = pygame.Rect(table_x - 10, table_y - 10, table_width + 20, 
                                min(height * 0.6, (len(highscores) + 2) * row_height) + 20)
        pygame.draw.rect(screen, (20, 20, 20), table_rect, border_radius=15)
        pygame.draw.rect(screen, (80, 80, 80), table_rect, 2, border_radius=15)
        
        # Заголовки таблицы
        x = table_x
        for i, header in enumerate(headers):
            header_rect = pygame.Rect(x, table_y - scroll_offset, col_widths[i], row_height)
            if header_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, DARK_BLUE, header_rect)
            else:
                pygame.draw.rect(screen, BLUE, header_rect)
            
            draw_text(screen, header, min(28, width // 40), 
                     x + col_widths[i] // 2, table_y + row_height // 2 - scroll_offset, 
                     WHITE, align="center", bold=True)
            x += col_widths[i]
        
        # Строки таблицы
        visible_rows = range(len(highscores))  # Все строки, прокрутка обрабатывается через offset
        for i in visible_rows:
            y_pos = table_y + (i + 1) * row_height - scroll_offset
            
            # Пропускаем строки, которые не видны
            if y_pos + row_height < table_y or y_pos > height - 100:
                continue
            
            entry = highscores[i]
            date = datetime.fromtimestamp(entry["date"] / 1000).strftime("%d.%m.%Y %H:%M")
            row_data = [
                str(i + 1),
                entry["nickname"][:15],  # Ограничение длины ника
                f"{entry['score']:,}".replace(",", " "),
                str(entry["level"]),
                str(entry["lines"]),
                date
            ]
            
            # Подсветка строки при наведении
            row_rect = pygame.Rect(table_x, y_pos, table_width, row_height)
            if row_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, HIGHLIGHT_COLOR, row_rect)
                text_color = BLACK
            else:
                # Чередование цвета строк
                bg_color = LIGHT_GRAY if i % 2 == 0 else (50, 50, 50)
                pygame.draw.rect(screen, bg_color, row_rect)
                text_color = WHITE
            
            # Отрисовка данных строки
            x = table_x
            for j, data in enumerate(row_data):
                cell_rect = pygame.Rect(x, y_pos, col_widths[j], row_height)
                pygame.draw.rect(screen, (40, 40, 40), cell_rect, 1)  # Разделители
                
                draw_text(screen, data, min(24, width // 50), 
                         x + col_widths[j] // 2, y_pos + row_height // 2, 
                         text_color, align="center", bold=(j == 2))  # Жирный шрифт для очков
                x += col_widths[j]
        
        # Полоса прокрутки
        if max_scroll > 0:
            scroll_ratio = scroll_offset / max_scroll
            scrollbar_height = height * 0.5 * (height * 0.5 / (len(highscores) * row_height))
            scrollbar_height = max(scrollbar_height, 40)
            scrollbar_y = table_y + (height * 0.5 - scrollbar_height) * scroll_ratio
            
            pygame.draw.rect(screen, (100, 100, 100), 
                            (width - 20, table_y, 10, height * 0.5), border_radius=5)
            pygame.draw.rect(screen, WHITE, 
                            (width - 20, scrollbar_y, 10, scrollbar_height), border_radius=5)
        
        # Кнопка "Назад"
        draw_button(screen, "Назад", back_button_rect, YELLOW, 
                  back_button_rect.collidepoint(mouse_pos))
        
        # Информация о количестве записей
        draw_text(screen, f"Всего записей: {len(highscores)}", min(24, width // 50), 
                 width // 2, height - 50, (200, 200, 200))
        
        pygame.display.flip()
        clock.tick(60)
    
    # Анимация исчезновения
    for alpha in range(0, 255, 15):
        alpha_surface.set_alpha(alpha)
        draw_gradient_background(screen)
        pygame.display.flip()
        screen.blit(alpha_surface, (0, 0))
        pygame.time.delay(30)
    
    return False