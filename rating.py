import pygame
import json
import os
import hashlib
from datetime import datetime
from game import run_game
from toptable import load_highscores, show_highscores

# Константы
USER_DB_FILE = "assets/users.json"
HIGHSCORES_FILE = "assets/highscores.json"
FONT_NAME = "Arial"
COLORS = {
    "background": (30, 30, 40),
    "primary": (70, 130, 180),
    "secondary": (100, 150, 200),
    "accent": (255, 215, 0),
    "text": (240, 240, 240),
    "error": (220, 60, 60),
    "success": (60, 220, 60),
    "input_bg": (20, 20, 30),
    "input_active": (50, 50, 70)
}

class AuthSystem:
    @staticmethod
    def load_users():
        if not os.path.exists(USER_DB_FILE):
            return {}
        try:
            with open(USER_DB_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    @staticmethod
    def save_users(users):
        os.makedirs(os.path.dirname(USER_DB_FILE), exist_ok=True)
        with open(USER_DB_FILE, "w") as f:
            json.dump(users, f, indent=2)

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
        highscores.append(new_entry)
        highscores.sort(key=lambda x: x["score"], reverse=True)
        highscores = highscores[:100]
        os.makedirs(os.path.dirname(HIGHSCORES_FILE), exist_ok=True)
        with open(HIGHSCORES_FILE, "w") as f:
            json.dump(highscores, f, indent=2)

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def add_particles(self, pos, color, count=10):
        for _ in range(count):
            angle = pygame.time.get_ticks() % 360  # Упрощаем расчет угла
            velocity = pygame.math.Vector2(0, 1).rotate(angle)  # Создаем вектор и поворачиваем
            velocity.x += (pygame.time.get_ticks() % 10) - 5  # Добавляем случайное отклонение
            
            self.particles.append({
                "pos": [pos[0], pos[1]],
                "velocity": [velocity.x, velocity.y],
                "size": pygame.time.get_ticks() % 5 + 2,
                "color": color,
                "life": 60 + (pygame.time.get_ticks() % 40)
            })

    def update(self):
        for particle in self.particles[:]:
            particle["pos"][0] += particle["velocity"][0] * 0.1
            particle["pos"][1] += particle["velocity"][1] * 0.1
            particle["life"] -= 1
            if particle["life"] <= 0:
                self.particles.remove(particle)

    def draw(self, screen):
        for particle in self.particles:
            pygame.draw.circle(
                screen,
                particle["color"],
                (int(particle["pos"][0]), int(particle["pos"][1])),
                int(particle["size"])
            )

class LoginScreen:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.clock = pygame.time.Clock()
        self.particles = ParticleSystem()
        self.font_large = pygame.font.SysFont(FONT_NAME, 40, bold=True)
        self.font_medium = pygame.font.SysFont(FONT_NAME, 30, bold=True)
        self.font_small = pygame.font.SysFont(FONT_NAME, 24)
        
        # Анимационные переменные
        self.title_offset = 0
        self.title_direction = 1
        self.bg_offset = 0
        
        # Звуковые эффекты
        self.sounds = {
            "click": None,
            "error": None,
            "success": None
        }
        
        try:
            self.sounds["click"] = pygame.mixer.Sound("assets/sounds/click.wav")
            self.sounds["error"] = pygame.mixer.Sound("assets/sounds/error.wav")
            self.sounds["success"] = pygame.mixer.Sound("assets/sounds/success.wav")
        except:
            print("Звуковые эффекты не загружены")

    def draw_text(self, text, font, color, pos, align="center", shadow=False):
        text_surface = font.render(text, True, color)
        if align == "center":
            text_rect = text_surface.get_rect(center=pos)
        elif align == "left":
            text_rect = text_surface.get_rect(topleft=pos)
        elif align == "right":
            text_rect = text_surface.get_rect(topright=pos)
        
        if shadow:
            shadow_surface = font.render(text, True, (0, 0, 0))
            shadow_rect = shadow_surface.get_rect(center=(pos[0]+2, pos[1]+2))
            self.screen.blit(shadow_surface, shadow_rect)
        
        self.screen.blit(text_surface, text_rect)
        return text_rect

    def draw_button(self, rect, text, is_hovered):
        color = COLORS["primary"] if not is_hovered else COLORS["secondary"]
        border_color = COLORS["accent"] if is_hovered else COLORS["primary"]
        
        # Тень
        shadow_rect = rect.copy()
        shadow_rect.x += 5
        shadow_rect.y += 5
        pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow_rect, border_radius=10)
        
        # Основная кнопка
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=8)
        
        # Текст кнопки
        text_color = COLORS["text"] if not is_hovered else COLORS["accent"]
        self.draw_text(text, self.font_medium, text_color, rect.center, "center", True)
        
        return rect

    def draw_input_field(self, rect, text, is_active, is_password=False):
        bg_color = COLORS["input_active"] if is_active else COLORS["input_bg"]
        border_color = COLORS["accent"] if is_active else COLORS["primary"]
        
        # Тень
        shadow_rect = rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow_rect, border_radius=5)
        
        # Поле ввода
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=5)
        pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=5)
        
        # Текст
        display_text = "*" * len(text) if is_password else text
        if display_text:
            text_surface = self.font_medium.render(display_text, True, COLORS["text"])
            text_rect = text_surface.get_rect(midleft=(rect.x + 15, rect.centery))
            self.screen.blit(text_surface, text_rect)
        
        # Подсказка курсора
        if is_active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = text_rect.right + 5 if display_text else rect.x + 15
            pygame.draw.line(
                self.screen, COLORS["text"], 
                (cursor_x, rect.y + 10), 
                (cursor_x, rect.y + rect.height - 10), 
                2
            )
        
        return rect

    def show_message(self, text, color=COLORS["error"], duration=2000):
        message_rect = pygame.Rect(0, self.height - 80, self.width, 60)
        pygame.draw.rect(self.screen, (0, 0, 0, 150), message_rect, border_radius=10)
        
        text_rect = self.draw_text(
            text, self.font_small, color, 
            (self.width // 2, self.height - 50), 
            "center", True
        )
        
        pygame.display.flip()
        pygame.time.delay(duration)
        return text_rect

    def animate_background(self):
        self.bg_offset = (self.bg_offset + 0.2) % self.width
        for i in range(-1, 2):
            pygame.draw.rect(
                self.screen, (40, 40, 50),
                (i * self.width + self.bg_offset, 0, self.width, self.height)
            )
        
        # Звезды
        for i in range(20):
            x = (pygame.time.get_ticks() * 0.1 + i * 100) % self.width
            y = (i * 50 + pygame.time.get_ticks() * 0.05) % self.height
            size = 1 + (i % 3)
            pygame.draw.circle(
                self.screen, 
                (100 + i * 5, 100 + i * 5, 150 + i * 5),
                (int(x), int(y)), size
            )

    def input_credentials(self):
        nickname = ""
        password = ""
        active_field = None  # "nickname", "password" или None
        error_message = ""
        
        input_width = min(400, self.width * 0.8)
        input_height = 50
        nickname_rect = pygame.Rect(
            (self.width - input_width) // 2, 
            self.height // 2 - 80, 
            input_width, 
            input_height
        )
        password_rect = pygame.Rect(
            (self.width - input_width) // 2, 
            self.height // 2, 
            input_width, 
            input_height
        )
        login_button_rect = pygame.Rect(
            (self.width - 200) // 2, 
            self.height // 2 + 80, 
            200, 
            50
        )
        back_button_rect = pygame.Rect(
            20, 20, 
            100, 
            40
        )
        
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            login_hovered = login_button_rect.collidepoint(mouse_pos)
            back_hovered = back_button_rect.collidepoint(mouse_pos)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "menu"
                    
                    elif active_field and event.key == pygame.K_RETURN:
                        if nickname.strip() and password.strip():
                            return nickname.strip(), password.strip()
                        else:
                            error_message = "Заполните все поля!"
                            if self.sounds["error"]:
                                self.sounds["error"].play()
                    
                    elif active_field and event.key == pygame.K_BACKSPACE:
                        if active_field == "nickname":
                            nickname = nickname[:-1]
                        elif active_field == "password":
                            password = password[:-1]
                    
                    elif active_field and event.key == pygame.K_TAB:
                        active_field = "password" if active_field == "nickname" else "nickname"
                    
                    elif active_field:
                        char = event.unicode
                        if char.isprintable():
                            if active_field == "nickname" and len(nickname) < 15:
                                nickname += char
                            elif active_field == "password" and len(password) < 20:
                                password += char
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Левая кнопка мыши
                        if nickname_rect.collidepoint(event.pos):
                            active_field = "nickname"
                            if self.sounds["click"]:
                                self.sounds["click"].play()
                        
                        elif password_rect.collidepoint(event.pos):
                            active_field = "password"
                            if self.sounds["click"]:
                                self.sounds["click"].play()
                        
                        elif login_button_rect.collidepoint(event.pos):
                            if nickname.strip() and password.strip():
                                return nickname.strip(), password.strip()
                            else:
                                error_message = "Заполните все поля!"
                                if self.sounds["error"]:
                                    self.sounds["error"].play()
                        
                        elif back_button_rect.collidepoint(event.pos):
                            if self.sounds["click"]:
                                self.sounds["click"].play()
                            return "menu"
                        
                        else:
                            active_field = None
            
            # Отрисовка
            self.animate_background()
            self.particles.update()
            self.particles.draw(self.screen)
            
            # Анимированный заголовок
            self.title_offset += 0.1 * self.title_direction
            if abs(self.title_offset) > 5:
                self.title_direction *= -1
            
            title_y = self.height // 4 + self.title_offset
            self.draw_text(
                "РЕЙТИНГОВЫЙ РЕЖИМ", 
                self.font_large, 
                COLORS["accent"], 
                (self.width // 2, title_y), 
                "center", 
                True
            )
            
            # Поля ввода
            self.draw_text(
                "Никнейм:", 
                self.font_small, 
                COLORS["text"], 
                (nickname_rect.x, nickname_rect.y - 30), 
                "left"
            )
            self.draw_input_field(
                nickname_rect, 
                nickname, 
                active_field == "nickname"
            )
            
            self.draw_text(
                "Пароль:", 
                self.font_small, 
                COLORS["text"], 
                (password_rect.x, password_rect.y - 30), 
                "left"
            )
            self.draw_input_field(
                password_rect, 
                password, 
                active_field == "password", 
                True
            )
            
            # Кнопки
            self.draw_button(
                login_button_rect, 
                "ВОЙТИ", 
                login_hovered
            )
            
            self.draw_button(
                back_button_rect, 
                "НАЗАД", 
                back_hovered
            )
            
            # Сообщение об ошибке
            if error_message:
                self.show_message(error_message)
                error_message = ""
            
            pygame.display.flip()
            self.clock.tick(60)

def start_rating_game(screen):
    auth = AuthSystem()
    login_screen = LoginScreen(screen)
    
    while True:
        credentials = login_screen.input_credentials()
        
        if credentials == "menu":
            return  # Выход в главное меню
        if credentials is None:
            return  # Выход из игры
        
        nickname, password = credentials
        
        # Проверка учетных данных
        users = auth.load_users()
        hashed_password = auth.hash_password(password)
        
        if nickname in users:
            if users[nickname] != hashed_password:
                login_screen.show_message("Неверный пароль!", COLORS["error"])
                continue
            else:
                login_screen.show_message(f"С возвращением, {nickname}!", COLORS["success"])
        else:
            users[nickname] = hashed_password
            auth.save_users(users)
            login_screen.show_message(f"Новый аккаунт создан!", COLORS["success"])
            pygame.time.delay(1000)
            login_screen.show_message(f"Добро пожаловать, {nickname}!", COLORS["success"])
        
        # Запуск игры
        game_result = run_game(screen, mode="rating")
        
        # Обработка результатов игры
        if game_result and game_result.get("game_over"):
            RatingSystem.save_highscore(
                nickname,
                game_result["score"],
                game_result["level"],
                game_result["lines"]
            )
            
            # Показ таблицы рекордов
            if not show_highscores(screen):
                return  # Выход в меню, если пользователь нажал ESC
            
        elif game_result and game_result.get("menu"):
            return  # Выход в меню из игры