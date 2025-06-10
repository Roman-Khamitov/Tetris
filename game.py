import pygame
import random
import json
import os
import hashlib
from toptable import load_highscores, show_highscores

pygame.init()

# Цвета
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
WHITE = (255, 255, 255)
RED = (220, 20, 60)
PANEL_BG = (20, 20, 20)

# Константы для рейтинга
USER_DB_FILE = "assets/users.json"
HIGHSCORES_FILE = "assets/highscores.json"
FONT_NAME = "Arial"

# Фигуры
TETROMINOES = {
    'I': [[1, 1, 1, 1]],
    'J': [[1, 0, 0],
          [1, 1, 1]],
    'L': [[0, 0, 1],
          [1, 1, 1]],
    'O': [[1, 1],
          [1, 1]],
    'S': [[0, 1, 1],
          [1, 1, 0]],
    'T': [[0, 1, 0],
          [1, 1, 1]],
    'Z': [[1, 1, 0],
          [0, 1, 1]],
}

COLORS = {
    'I': (0, 255, 255),
    'J': (0, 0, 255),
    'L': (255, 165, 0),
    'O': (255, 255, 0),
    'S': (0, 255, 0),
    'T': (160, 32, 240),
    'Z': (255, 0, 0),
}

# Постоянные размеры
COLUMNS = 10
ROWS = 20
PANEL_WIDTH_RATIO = 0.25

class AuthSystem:
    @staticmethod
    def load_users():
        if not os.path.exists(USER_DB_FILE):
            print(f"Файл {USER_DB_FILE} не существует")
            return {}
        try:
            with open(USER_DB_FILE, "r") as f:
                data = json.load(f)
                print(f"Загружено {len(data)} пользователей из {USER_DB_FILE}")
                return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Ошибка загрузки {USER_DB_FILE}: {e}")
            return {}

    @staticmethod
    def save_users(users):
        os.makedirs(os.path.dirname(USER_DB_FILE), exist_ok=True)
        with open(USER_DB_FILE, "w") as f:
            json.dump(users, f, indent=2)
        print(f"Сохранено {len(users)} пользователей в {USER_DB_FILE}")

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

class RatingSystem:
    @staticmethod
    def load_highscores():
        return load_highscores()

    @staticmethod
    def save_highscore(nickname, score, level, lines):
        highscores = RatingSystem.load_highscores()
        new_entry = {
            "nickname": nickname,
            "score": score,
            "level": level,
            "lines": lines,
            "date": pygame.time.get_ticks()
        }
        print(f"Сохраняем результат: {new_entry}")
        highscores.append(new_entry)
        highscores.sort(key=lambda x: x["score"], reverse=True)
        highscores = highscores[:100]
        os.makedirs(os.path.dirname(HIGHSCORES_FILE), exist_ok=True)
        with open(HIGHSCORES_FILE, "w") as f:
            json.dump(highscores, f, indent=2)
        print(f"Сохранено {len(highscores)} записей в {HIGHSCORES_FILE}")

class LoginScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.SysFont(FONT_NAME, 40)
        self.font_small = pygame.font.SysFont(FONT_NAME, 24)
        self.clock = pygame.time.Clock()
        self.screen_width, self.screen_height = screen.get_size()
        print(f"Инициализация экрана: {self.screen_width}x{self.screen_height}")

    def draw_text(self, text, font, color, x, y):
        surface = font.render(text, True, color)
        self.screen.blit(surface, (x, y))

    def show_message(self, text, color=pygame.Color("red")):
        self.screen.fill(pygame.Color("dimgray"))
        self.draw_text(text, self.font_small, color, 50, self.screen_height - 50)
        pygame.display.flip()
        pygame.time.delay(2000)

    def draw_input_box(self, rect, text, is_active, is_password=False):
        border_color = pygame.Color("white") if is_active else pygame.Color("gray")
        pygame.draw.rect(self.screen, border_color, rect, 2)
        pygame.draw.rect(self.screen, pygame.Color("black"), rect.inflate(-4, -4))
        display_text = "*" * len(text) if is_password else text
        text_surface = self.font_large.render(display_text, True, pygame.Color("white"))
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def draw_button(self, rect, text, is_hovered):
        color = pygame.Color("green") if is_hovered else pygame.Color("darkgreen")
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, pygame.Color("white"), rect, 2)
        text_surface = self.font_large.render(text, True, pygame.Color("white"))
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def input_credentials(self):
        nickname = ""
        password = ""
        active_field = None
        error_message = ""

        input_width, input_height = 300, 50
        nickname_rect = pygame.Rect((self.screen_width - input_width) // 2, 150, input_width, input_height)
        password_rect = pygame.Rect((self.screen_width - input_width) // 2, 250, input_width, input_height)
        button_rect = pygame.Rect((self.screen_width - 150) // 2, 350, 150, 50)

        while True:
            self.screen.fill(pygame.Color("dimgray"))

            mouse_pos = pygame.mouse.get_pos()
            button_hovered = button_rect.collidepoint(mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None, None

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if nickname_rect.collidepoint(event.pos):
                        active_field = "nickname"
                    elif password_rect.collidepoint(event.pos):
                        active_field = "password"
                    elif button_rect.collidepoint(event.pos):
                        if nickname.strip() and password.strip():
                            return nickname.strip(), password.strip()
                        else:
                            error_message = "Ник и пароль не могут быть пустыми!"
                    else:
                        active_field = None

                elif event.type == pygame.KEYDOWN and active_field:
                    if event.key == pygame.K_RETURN:
                        if nickname.strip() and password.strip():
                            return nickname.strip(), password.strip()
                        else:
                            error_message = "Ник и пароль не могут быть пустыми!"
                    elif event.key == pygame.K_BACKSPACE:
                        if active_field == "nickname":
                            nickname = nickname[:-1]
                        elif active_field == "password":
                            password = password[:-1]
                    elif event.key == pygame.K_TAB:
                        active_field = "password" if active_field == "nickname" else "nickname"
                    else:
                        char = event.unicode
                        if char.isprintable():
                            if active_field == "nickname" and len(nickname) < 20:
                                nickname += char
                            elif active_field == "password" and len(password) < 20:
                                password += char

            self.draw_text("Введите ник:", self.font_large, pygame.Color("white"), nickname_rect.x, nickname_rect.y - 40)
            self.draw_input_box(nickname_rect, nickname, active_field == "nickname")
            
            self.draw_text("Введите пароль:", self.font_large, pygame.Color("white"), password_rect.x, password_rect.y - 40)
            self.draw_input_box(password_rect, password, active_field == "password", is_password=True)
            
            self.draw_button(button_rect, "Подтвердить", button_hovered)

            if error_message:
                self.draw_text(error_message, self.font_small, pygame.Color("red"), 50, self.screen_height - 50)

            pygame.display.flip()
            self.clock.tick(30)

class Tetromino:
    def __init__(self, shape):
        self.shape = TETROMINOES[shape]
        self.color = COLORS[shape]
        self.x = COLUMNS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.board = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.score = 0
        self.current = self.new_tetromino()
        self.next = self.new_tetromino()
        self.fall_time = 0
        self.fall_speed = 500
        self.game_over = False
        self.over_alpha = 0
        self.over_font_size = 40
        self.over_anim_time = 0
        self.font = pygame.font.SysFont('Arial', 24)
        self.base_fall_speed = 500
        self.fall_speed = self.base_fall_speed
        self.level = 1
        self.lines_cleared_total = 0
        self.speed_increase_interval = 10

    def new_tetromino(self):
        return Tetromino(random.choice(list(TETROMINOES.keys())))

    def restart(self):
        self.__init__(self.screen)

    def valid_position(self, shape, offset_x, offset_y):
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = offset_x + x
                    new_y = offset_y + y
                    if new_x < 0 or new_x >= COLUMNS or new_y >= ROWS:
                        return False
                    if new_y >= 0 and self.board[new_y][new_x]:
                        return False
        return True

    def lock(self):
        for y, row in enumerate(self.current.shape):
            for x, cell in enumerate(row):
                if cell:
                    px = self.current.x + x
                    py = self.current.y + y
                    if py >= 0:
                        self.board[py][px] = self.current.color
        self.clear_lines()
        self.current = self.next
        self.next = self.new_tetromino()
        if not self.valid_position(self.current.shape, self.current.x, self.current.y):
            self.game_over = True

    def clear_lines(self):
        new_board = [row for row in self.board if any(cell == 0 for cell in row)]
        lines_cleared = ROWS - len(new_board)
        self.lines_cleared_total += lines_cleared

        new_level = self.lines_cleared_total // self.speed_increase_interval + 1
        if new_level > self.level:
            self.level = new_level
            self.fall_speed = max(100, self.base_fall_speed - (self.level - 1) * 50)

        for _ in range(lines_cleared):
            new_board.insert(0, [0 for _ in range(COLUMNS)])
        self.board = new_board
        self.score += lines_cleared * 100

    def move(self, dx):
        if self.valid_position(self.current.shape, self.current.x + dx, self.current.y):
            self.current.x += dx

    def rotate(self):
        old_shape = self.current.shape
        self.current.rotate()
        if not self.valid_position(self.current.shape, self.current.x, self.current.y):
            self.current.shape = old_shape

    def drop(self):
        while self.valid_position(self.current.shape, self.current.x, self.current.y + 1):
            self.current.y += 1
        self.lock()

    def update(self, dt):
        self.fall_time += dt
        if self.fall_time > self.fall_speed:
            self.fall_time = 0
            if self.valid_position(self.current.shape, self.current.x, self.current.y + 1):
                self.current.y += 1
            else:
                self.lock()

    def draw_game_over(self, dt, width, height):
        self.over_anim_time += dt
        if self.over_alpha < 255:
            self.over_alpha += dt // 2
        if self.over_font_size < 80:
            self.over_font_size += dt * 0.05

        font = pygame.font.SysFont("Arial", int(self.over_font_size))
        text = font.render("GAME OVER", True, RED)
        text.set_alpha(min(255, int(self.over_alpha)))
        rect = text.get_rect(center=(width // 2, height // 2 - 30))
        self.screen.blit(text, rect)
        
        small_font = pygame.font.SysFont("Arial", 24)
        hint_text = small_font.render("Press R to Restart", True, WHITE)
        hint_text.set_alpha(min(255, int(self.over_alpha)))  # Fixed: _forest -> self.over_alpha

        hint_rect = hint_text.get_rect(center=(width // 2, height // 2 + 30))
        self.screen.blit(hint_text, hint_rect)

    def draw_board(self, width, height, player_num=None):
        cell_size = min(width * (1 - PANEL_WIDTH_RATIO) // COLUMNS, height // ROWS)
        panel_width = int(width * PANEL_WIDTH_RATIO)
        offset_x = 0
        offset_y = 0

        for y in range(ROWS):
            for x in range(COLUMNS):
                val = self.board[y][x]
                if val:
                    pygame.draw.rect(self.screen, val,
                                     (offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size))
                    pygame.draw.rect(self.screen, BLACK,
                                     (offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size), 2)

        for y, row in enumerate(self.current.shape):
            for x, cell in enumerate(row):
                if cell:
                    px = offset_x + (self.current.x + x) * cell_size
                    py = offset_y + (self.current.y + y) * cell_size
                    pygame.draw.rect(self.screen, self.current.color, (px, py, cell_size, cell_size))
                    pygame.draw.rect(self.screen, BLACK, (px, py, cell_size, cell_size), 2)

        for x in range(COLUMNS):
            for y in range(ROWS):
                pygame.draw.rect(self.screen, GRAY,
                                 (offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size), 1)

        panel_x = offset_x + COLUMNS * cell_size
        pygame.draw.rect(self.screen, PANEL_BG, (panel_x, 0, panel_width, height))

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (panel_x + 20, 20))

        next_panel_height = 150
        pygame.draw.rect(self.screen, WHITE, (panel_x + 10, 60, panel_width - 20, next_panel_height), 2)
        next_label = self.font.render("Next:", True, WHITE)
        self.screen.blit(next_label, (panel_x + 20, 65))
        
        next_shape_width = len(self.next.shape[0]) * cell_size
        next_shape_height = len(self.next.shape) * cell_size
        start_x = panel_x + (panel_width - next_shape_width) // 2
        start_y = 100 + (next_panel_height - next_shape_height - 40) // 2
        
        for y, row in enumerate(self.next.shape):
            for x, cell in enumerate(row):
                if cell:
                    px = start_x + x * cell_size
                    py = start_y + y * cell_size
                    pygame.draw.rect(self.screen, self.next.color, (px, py, cell_size, cell_size))
                    pygame.draw.rect(self.screen, BLACK, (px, py, cell_size, cell_size), 2)

        controls_y = 60 + next_panel_height + 20
        controls_height = 100
        pygame.draw.rect(self.screen, WHITE, (panel_x + 10, controls_y, panel_width - 20, controls_height), 2)

        control_title = self.font.render("Controls:", True, WHITE)
        self.screen.blit(control_title, (panel_x + 20, controls_y + 5))

        if player_num == 1:
            control_line1 = self.font.render("Move: A / D", True, RED)
            control_line2 = self.font.render("Rotate: W   Drop: Shift", True, RED)
        elif player_num == 2:
            control_line1 = self.font.render("Move: ← / →", True, RED)
            control_line2 = self.font.render("Rotate: ↑   Drop: Space", True, RED)
        else:
            control_line1 = self.font.render("Move: A / D", True, RED)
            control_line2 = self.font.render("Rotate: W   Drop: Shift", True, RED)

        self.screen.blit(control_line1, (panel_x + 20, controls_y + 35))
        self.screen.blit(control_line2, (panel_x + 20, controls_y + 65))

def draw_label(surface, text, size, color, x, y):
    font = pygame.font.SysFont("Arial", size)
    label = font.render(text, True, color)
    rect = label.get_rect(center=(x, y + label.get_height() // 2))
    surface.blit(label, rect)

def run_game(screen, multiplayer=False, mode="normal"):
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    
    game1 = Game(screen)
    if mode == "rating":
        game1.base_fall_speed = 800
        game1.fall_speed = game1.base_fall_speed
        game1.speed_increase_interval = 5
    game2 = Game(screen) if multiplayer else None

    running = True
    winner_declared = False
    winner_text = ""
    winner_alpha = 0
    winner_font_size = 40
    winner_anim_time = 0

    while running:
        dt = clock.tick(60)
        screen.fill(BLACK)
        width, height = screen.get_size()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return {"quit": True}
                
            elif event.type == pygame.KEYDOWN:
                # Обработка управления для игрока 1
                if not game1.game_over and not winner_declared:
                    if event.key == pygame.K_a:
                        game1.move(-1)
                    elif event.key == pygame.K_d:
                        game1.move(1)
                    elif event.key == pygame.K_s:
                        game1.update(100)
                    elif event.key == pygame.K_w:
                        game1.rotate()
                    elif event.key == pygame.K_LSHIFT:
                        game1.drop()
                
                # Обработка управления для игрока 2 (в мультиплеере)
                if multiplayer and game2 and not game2.game_over and not winner_declared:
                    if event.key == pygame.K_LEFT:
                        game2.move(-1)
                    elif event.key == pygame.K_RIGHT:
                        game2.move(1)
                    elif event.key == pygame.K_DOWN:
                        game2.update(100)
                    elif event.key == pygame.K_UP:
                        game2.rotate()
                    elif event.key == pygame.K_SPACE:
                        game2.drop()
                
                # Общие клавиши
                if event.key == pygame.K_ESCAPE:
                    # В рейтинговом режиме возвращаем результат при ESC
                    if mode == "rating" and (game1.game_over or (multiplayer and game2 and game2.game_over)):
                        result = {
                            "game_over": True,
                            "score": game1.score if not multiplayer else max(game1.score, game2.score if game2 else 0),
                            "level": game1.level if not multiplayer else max(game1.level, game2.level if game2 else 0),
                            "lines": game1.lines_cleared_total if not multiplayer else max(game1.lines_cleared_total, game2.lines_cleared_total if game2 else 0)
                        }
                        return result
                    else:
                        return {"menu": True}
                
                # Обработка рестарта
                if (game1.game_over or (multiplayer and game2 and game2.game_over)) and event.key == pygame.K_r:
                    game1.restart()
                    if multiplayer:
                        game2.restart()
                    winner_declared = False
                    winner_alpha = 0
                    winner_font_size = 40

        # Логика игры и отрисовка
        if not multiplayer:
            if not game1.game_over:
                game1.update(dt)
            game1.draw_board(width, height, player_num=1)
            if game1.game_over:
                game1.draw_game_over(dt, width, height)
                
                # Автоматический возврат результата только в рейтинговом режиме
                if mode == "rating":
                    result = {
                        "game_over": True,
                        "score": game1.score,
                        "level": game1.level,
                        "lines": game1.lines_cleared_total
                    }
                    return result
        else:
            # Логика для мультиплеера (остается без изменений)
            half_width = width // 2

            surface1 = pygame.Surface((half_width, height))
            game1.screen = surface1
            game1.draw_board(half_width, height, player_num=1)
            
            surface2 = pygame.Surface((half_width, height))
            game2.screen = surface2
            game2.draw_board(half_width, height, player_num=2)

            screen.blit(surface1, (0, 0))
            screen.blit(surface2, (half_width, 0))

            pygame.draw.line(screen, WHITE, (half_width, 0), (half_width, height), 2)

            if not winner_declared:
                if not game1.game_over:
                    game1.update(dt)
                if not game2.game_over:
                    game2.update(dt)

            if not winner_declared:
                if game1.game_over and not game2.game_over:
                    winner_text = f"Player 2 WINS! Score: {game2.score}"
                    winner_declared = True
                elif game2.game_over and not game1.game_over:
                    winner_text = f"Player 1 WINS! Score: {game1.score}"
                    winner_declared = True
                elif game1.game_over and game2.game_over:
                    if game1.score > game2.score:
                        winner_text = f"Player 1 WINS! {game1.score}-{game2.score}"
                    elif game2.score > game1.score:
                        winner_text = f"Player 2 WINS! {game2.score}-{game1.score}"
                    else:
                        winner_text = f"DRAW! Score: {game1.score}"
                    winner_declared = True

            if winner_declared:
                winner_anim_time += dt
                if winner_alpha < 255:
                    winner_alpha += dt // 2
                if winner_font_size < 80:
                    winner_font_size += dt * 0.05

                overlay = pygame.Surface((width, height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))

                font = pygame.font.SysFont("Arial", int(winner_font_size))
                text = font.render(winner_text, True, RED)
                text.set_alpha(min(255, int(winner_alpha)))
                rect = text.get_rect(center=(width // 2, height // 2 - 30))
                screen.blit(text, rect)
                
                small_font = pygame.font.SysFont("Arial", 24)
                hint = small_font.render("Press R to Restart", True, WHITE)
                hint.set_alpha(min(255, int(winner_alpha)))
                hint_rect = hint.get_rect(center=(width // 2, height // 2 + 30))
                screen.blit(hint, hint_rect)

                # Автоматический возврат результата только в рейтинговом режиме
                if mode == "rating":
                    result = {
                        "game_over": True,
                        "score": max(game1.score, game2.score if game2 else 0),
                        "level": max(game1.level, game2.level if game2 else 0),
                        "lines": max(game1.lines_cleared_total, game2.lines_cleared_total if game2 else 0)
                    }
                    return result

        pygame.display.flip()

    # Возвращаем результат только при явном выходе (не при рестарте)
    return {"quit": True}
