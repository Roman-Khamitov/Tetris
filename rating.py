import pygame
import json
import os
import hashlib
from game import run_game
from toptable import load_highscores, show_highscores

# Константы
USER_DB_FILE = "assets/users.json"
HIGHSCORES_FILE = "assets/highscores.json"
FONT_NAME = "Arial"

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
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "menu"  # Возвращаем сигнал для выхода в меню
                    elif active_field and event.key == pygame.K_RETURN:
                        if nickname.strip() and password.strip():
                            return nickname.strip(), password.strip()
                        else:
                            error_message = "Ник и пароль не могут быть пустыми!"
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
                            if active_field == "nickname" and len(nickname) < 20:
                                nickname += char
                            elif active_field == "password" and len(password) < 20:
                                password += char
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

            self.draw_text("Введите ник:", self.font_large, pygame.Color("white"), nickname_rect.x, nickname_rect.y - 40)
            self.draw_input_box(nickname_rect, nickname, active_field == "nickname")
            
            self.draw_text("Введите пароль:", self.font_large, pygame.Color("white"), password_rect.x, password_rect.y - 40)
            self.draw_input_box(password_rect, password, active_field == "password", is_password=True)
            
            self.draw_button(button_rect, "Подтвердить", button_hovered)

            if error_message:
                self.draw_text(error_message, self.font_small, pygame.Color("red"), 50, self.screen_height - 50)

            pygame.display.flip()
            self.clock.tick(30)

def start_rating_game(screen):
    auth = AuthSystem()
    login_screen = LoginScreen(screen)
    
    while True:
        credentials = login_screen.input_credentials()
        if credentials == "menu":  # Выход в меню
            print("Выход в главное меню")
            return
        if credentials is None or len(credentials) != 2:  # Окно закрыто
            print("Ввод отменён или окно закрыто")
            return
        
        nickname, password = credentials  # Распаковываем только если уверены, что это кортеж
        
        users = auth.load_users()
        hashed_password = auth.hash_password(password)
        
        if nickname in users:
            if users[nickname] != hashed_password:
                login_screen.show_message("Неверный пароль!")
                continue
        else:
            users[nickname] = hashed_password
            auth.save_users(users)
            login_screen.show_message(f"Добро пожаловать, {nickname}!", pygame.Color("green"))
        
        result = run_game(screen, mode="rating")
        print(f"Результат игры: {result}")
        
        if result and result.get("menu"):  # Выход в меню из игры
            print("Выход в главное меню из игры")
            return
        if result and result.get("game_over"):
            RatingSystem.save_highscore(
                nickname,
                result["score"],
                result["level"],
                result["lines"]
            )
            if not show_highscores(screen):  # Если show_highscores возвращает False (Esc pressed)
                print("Выход в главное меню из таблицы рейтинга")
                return
        else:
            print("Игра завершена без сохранения результата")
        
        login_screen.show_message("Игра окончена. Введите ник и пароль для новой игры.", pygame.Color("white"))