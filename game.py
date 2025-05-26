import pygame
import random

# Инициализация
pygame.init()

# Константы
CELL_SIZE = 30
COLUMNS = 10
ROWS = 20
WIDTH = CELL_SIZE * COLUMNS + 150
HEIGHT = CELL_SIZE * ROWS
FPS = 60

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
        self.font = pygame.font.SysFont('Arial', 24)
        self.over_alpha = 0
        self.over_font_size = 40
        self.over_anim_time = 0

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

    def draw_game_over(self, dt):
        self.over_anim_time += dt
        if self.over_alpha < 255:
            self.over_alpha += dt // 2
        if self.over_font_size < 80:
            self.over_font_size += dt * 0.05

        font = pygame.font.SysFont("Arial", int(self.over_font_size))
        text = font.render("GAME OVER", True, RED)
        text.set_alpha(min(255, int(self.over_alpha)))
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text, rect)

    def draw_board(self):
        # Поле
        for y in range(ROWS):
            for x in range(COLUMNS):
                val = self.board[y][x]
                if val:
                    pygame.draw.rect(self.screen, val,
                                     (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, BLACK,
                                     (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)

        # Текущая фигура
        for y, row in enumerate(self.current.shape):
            for x, cell in enumerate(row):
                if cell:
                    px = (self.current.x + x) * CELL_SIZE
                    py = (self.current.y + y) * CELL_SIZE
                    pygame.draw.rect(self.screen, self.current.color, (px, py, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, BLACK, (px, py, CELL_SIZE, CELL_SIZE), 2)

        # Сетка
        for x in range(COLUMNS):
            for y in range(ROWS):
                pygame.draw.rect(self.screen, GRAY,
                                 (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

        # Панель справа
        pygame.draw.rect(self.screen, PANEL_BG, (CELL_SIZE * COLUMNS, 0, 150, HEIGHT))

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (CELL_SIZE * COLUMNS + 20, 20))

        # Следующая фигура
        pygame.draw.rect(self.screen, WHITE, (CELL_SIZE * COLUMNS + 10, 65, 130, 110), 2)
        next_label = self.font.render("Next:", True, WHITE)
        self.screen.blit(next_label, (CELL_SIZE * COLUMNS + 20, 70))
        for y, row in enumerate(self.next.shape):
            for x, cell in enumerate(row):
                if cell:
                    px = CELL_SIZE * COLUMNS + 30 + x * CELL_SIZE
                    py = 100 + y * CELL_SIZE
                    pygame.draw.rect(self.screen, self.next.color, (px, py, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, BLACK, (px, py, CELL_SIZE, CELL_SIZE), 2)


def run_game(screen):
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    game = Game(screen)

    running = True
    while running:
        dt = clock.tick(FPS)
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game.game_over:
                    if event.key == pygame.K_SPACE:
                        game.restart()
                    elif event.key == pygame.K_ESCAPE:
                        return
                    continue
                if event.key == pygame.K_LEFT:
                    game.move(-1)
                elif event.key == pygame.K_RIGHT:
                    game.move(1)
                elif event.key == pygame.K_DOWN:
                    game.update(100)
                elif event.key == pygame.K_UP:
                    game.rotate()
                elif event.key == pygame.K_SPACE:
                    game.drop()
                elif event.key == pygame.K_ESCAPE:
                    return  # выход в меню

        if not game.game_over:
            game.update(dt)

        game.draw_board()
        if game.game_over:
            game.draw_game_over(dt)

        pygame.display.flip()

    pygame.quit()



