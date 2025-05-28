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
PANEL_WIDTH_RATIO = 0.2


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
        rect = text.get_rect(center=(width // 2, height // 2))
        self.screen.blit(text, rect)

    def draw_board(self, width, height):
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

        # Grid
        for x in range(COLUMNS):
            for y in range(ROWS):
                pygame.draw.rect(self.screen, GRAY,
                                 (offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size), 1)

        # Right panel
        panel_x = offset_x + COLUMNS * cell_size
        pygame.draw.rect(self.screen, PANEL_BG, (panel_x, 0, panel_width, height))

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (panel_x + 20, 20))

        # Next piece
        pygame.draw.rect(self.screen, WHITE, (panel_x + 10, 65, panel_width - 20, 110), 2)
        next_label = self.font.render("Next:", True, WHITE)
        self.screen.blit(next_label, (panel_x + 20, 70))
        for y, row in enumerate(self.next.shape):
            for x, cell in enumerate(row):
                if cell:
                    px = panel_x + 30 + x * cell_size
                    py = 100 + y * cell_size
                    pygame.draw.rect(self.screen, self.next.color, (px, py, cell_size, cell_size))
                    pygame.draw.rect(self.screen, BLACK, (px, py, cell_size, cell_size), 2)


def run_game(screen, multiplayer=False):
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()

    game1 = Game(screen)
    game2 = Game(screen) if multiplayer else None

    running = True
    while running:
        dt = clock.tick(60)
        screen.fill(BLACK)

        width, height = screen.get_size()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # Управление первым игроком
                if not game1.game_over:
                    if event.key == pygame.K_LEFT:
                        game1.move(-1)
                    elif event.key == pygame.K_RIGHT:
                        game1.move(1)
                    elif event.key == pygame.K_DOWN:
                        game1.update(100)
                    elif event.key == pygame.K_UP:
                        game1.rotate()
                    elif event.key == pygame.K_SPACE:
                        game1.drop()

                # Управление вторым игроком
                if multiplayer and game2 and not game2.game_over:
                    if event.key == pygame.K_a:
                        game2.move(-1)
                    elif event.key == pygame.K_d:
                        game2.move(1)
                    elif event.key == pygame.K_s:
                        game2.update(100)
                    elif event.key == pygame.K_w:
                        game2.rotate()
                    elif event.key == pygame.K_LSHIFT:
                        game2.drop()

                # Перезапуск/выход
                if event.key == pygame.K_ESCAPE:
                    return
                if game1.game_over and event.key == pygame.K_r:
                    game1.restart()
                if multiplayer and game2 and game2.game_over and event.key == pygame.K_r:
                    game2.restart()

        # Обновление
        if not game1.game_over:
            game1.update(dt)
        if multiplayer and game2 and not game2.game_over:
            game2.update(dt)

        # Рисуем
        half_width = width // 2 if multiplayer else width
        game1.draw_board(half_width, height)
        if multiplayer and game2:
            # Сдвиг отрисовки второго игрока вправо
            pygame.draw.line(screen, WHITE, (half_width, 0), (half_width, height), 2)
            offset_surface = pygame.Surface((half_width, height))
            game2.screen = offset_surface
            game2.draw_board(half_width, height)
            screen.blit(offset_surface, (half_width, 0))

        if game1.game_over:
            game1.draw_game_over(dt, half_width, height)
        if multiplayer and game2 and game2.game_over:
            game2.draw_game_over(dt, half_width, height)

        pygame.display.flip()

    pygame.quit()
