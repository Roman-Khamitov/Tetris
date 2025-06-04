import pygame
import random

pygame.init()

# Цвета
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
WHITE = (255, 255, 255)
RED = (220, 20, 60)
PANEL_BG = (20, 20, 20)

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
PANEL_WIDTH_RATIO = 0.25  # Увеличим панель для лучшего отображения


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
        hint_text.set_alpha(min(255, int(self.over_alpha)))
        hint_rect = hint_text.get_rect(center=(width // 2, height // 2 + 30))
        self.screen.blit(hint_text, hint_rect)

    def draw_board(self, width, height, player_num=None):
        cell_size = min(width * (1 - PANEL_WIDTH_RATIO) // COLUMNS, height // ROWS)
        panel_width = int(width * PANEL_WIDTH_RATIO)
        offset_x = 0
        offset_y = 0

        # Игровое поле
        for y in range(ROWS):
            for x in range(COLUMNS):
                val = self.board[y][x]
                if val:
                    pygame.draw.rect(self.screen, val,
                                     (offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size))
                    pygame.draw.rect(self.screen, BLACK,
                                     (offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size), 2)

        # Текущая фигура
        for y, row in enumerate(self.current.shape):
            for x, cell in enumerate(row):
                if cell:
                    px = offset_x + (self.current.x + x) * cell_size
                    py = offset_y + (self.current.y + y) * cell_size
                    pygame.draw.rect(self.screen, self.current.color, (px, py, cell_size, cell_size))
                    pygame.draw.rect(self.screen, BLACK, (px, py, cell_size, cell_size), 2)

        # Сетка
        for x in range(COLUMNS):
            for y in range(ROWS):
                pygame.draw.rect(self.screen, GRAY,
                                 (offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size), 1)

        # Боковая панель
        panel_x = offset_x + COLUMNS * cell_size
        pygame.draw.rect(self.screen, PANEL_BG, (panel_x, 0, panel_width, height))

        # Очки
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (panel_x + 20, 20))

        # Следующая фигура
        next_panel_height = 150  # Увеличим высоту панели для следующей фигуры
        pygame.draw.rect(self.screen, WHITE, (panel_x + 10, 60, panel_width - 20, next_panel_height), 2)
        next_label = self.font.render("Next:", True, WHITE)
        self.screen.blit(next_label, (panel_x + 20, 65))
        
        # Центрируем следующую фигуру
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

        # Управление (перенесем под следующую фигуру)
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
            # Single-player default (assume WASD)
            control_line1 = self.font.render("Move: A / D", True, RED)
            control_line2 = self.font.render("Rotate: W   Drop: Shift", True, RED)

        self.screen.blit(control_line1, (panel_x + 20, controls_y + 35))
        self.screen.blit(control_line2, (panel_x + 20, controls_y + 65))


def run_game(screen, multiplayer=False):
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()

    game1 = Game(screen)
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

            elif event.type == pygame.KEYDOWN:
                # Управление первым игроком (WASD + LShift)
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

                # Управление вторым игроком (Arrow keys + Space)
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

                # Перезапуск/выход
                if event.key == pygame.K_ESCAPE:
                    return
                if (game1.game_over or (multiplayer and game2 and game2.game_over)) and event.key == pygame.K_r:
                    game1.restart()
                    if multiplayer:
                        game2.restart()
                    winner_declared = False
                    winner_alpha = 0
                    winner_font_size = 40

        # Обновление (только если игра не закончена)
        if not multiplayer:
            if not game1.game_over:
                game1.update(dt)
            game1.draw_board(width, height, player_num=1)
            if game1.game_over:
                game1.draw_game_over(dt, width, height)
        else:
            half_width = width // 2

            # Игрок 1 (WASD)
            surface1 = pygame.Surface((half_width, height))
            game1.screen = surface1
            game1.draw_board(half_width, height)
    
            
            # Игрок 2 (Arrows)
            surface2 = pygame.Surface((half_width, height))
            game2.screen = surface2
            game2.draw_board(half_width, height, player_num=2)


            screen.blit(surface1, (0, 0))
            screen.blit(surface2, (half_width, 0))

            pygame.draw.line(screen, WHITE, (half_width, 0), (half_width, height), 2)

            # Обновление игр только если нет победителя
            if not winner_declared:
                if not game1.game_over:
                    game1.update(dt)
                if not game2.game_over:
                    game2.update(dt)

            # Проверка на окончание игры
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

            # Отображение сообщения о победе
            if winner_declared:
                winner_anim_time += dt
                if winner_alpha < 255:
                    winner_alpha += dt // 2
                if winner_font_size < 80:
                    winner_font_size += dt * 0.05

                # Затемнение экрана
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

        pygame.display.flip()

    pygame.quit()


def draw_label(surface, text, size, color, x, y):
    font = pygame.font.SysFont("Arial", size)
    label = font.render(text, True, color)
    rect = label.get_rect(center=(x, y + label.get_height() // 2))
    surface.blit(label, rect)