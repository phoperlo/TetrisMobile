import pygame
import random
import sys

# Инициализация
pygame.init()

# Размеры экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 10

# Адаптивные размеры
GRID_SIZE = min(SCREEN_HEIGHT // 24, SCREEN_WIDTH // 30, 30)
GRID_WIDTH = 10
GRID_HEIGHT = 20

# Цвета
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (180, 70, 230)
DARK_BLUE = (20, 20, 40)
DARK_GRAY = (40, 40, 60)

# Цвета фигур
COLORS = [CYAN, YELLOW, PURPLE, BLUE, ORANGE, GREEN, RED]

# Фигуры
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]]
]

class MobileButton:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.pressed = False
        font_size = max(20, min(width // 3, height // 2))
        self.font = pygame.font.SysFont(None, font_size)
    
    def draw(self, screen):
        # Цвет при нажатии
        if self.pressed:
            color = tuple(min(255, c + 50) for c in self.color)
        else:
            color = self.color
        
        # Кнопка
        pygame.draw.rect(screen, color, self.rect, border_radius=15)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=15)
        
        # Текст
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def check_touch(self, pos):
        return self.rect.collidepoint(pos)

class TetrisMobile:
    def __init__(self):
        # Окно
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Тетрис Mobile")
        self.clock = pygame.time.Clock()
        
        # Шрифты
        self.font_small = pygame.font.SysFont(None, 24)
        self.font_medium = pygame.font.SysFont(None, 32)
        self.font_large = pygame.font.SysFont(None, 48)
        
        # Игровые переменные
        self.reset_game()
        self.game_state = "MENU"  # MENU, PLAYING, PAUSED, GAME_OVER
        self.last_fall = pygame.time.get_ticks()
        self.fall_speed = 500
        
        # Кнопки управления
        self.create_buttons()
    
    def create_buttons(self):
        # Размеры кнопок
        btn_w = SCREEN_WIDTH // 8
        btn_h = SCREEN_HEIGHT // 12
        
        # Кнопки управления в игре
        y_pos = SCREEN_HEIGHT - btn_h - 20
        
        self.btn_left = MobileButton(20, y_pos, btn_w, btn_h, "←", BLUE)
        self.btn_right = MobileButton(40 + btn_w, y_pos, btn_w, btn_h, "→", BLUE)
        self.btn_rotate = MobileButton(60 + 2*btn_w, y_pos, btn_w, btn_h, "↻", GREEN)
        self.btn_down = MobileButton(80 + 3*btn_w, y_pos, btn_w, btn_h, "↓", ORANGE)
        
        # Кнопки действий
        action_w = SCREEN_WIDTH // 6
        self.btn_pause = MobileButton(SCREEN_WIDTH - action_w - 20, 20, action_w, btn_h, "Пауза", PURPLE)
        self.btn_drop = MobileButton(SCREEN_WIDTH - action_w - 20, 40 + btn_h, action_w, btn_h, "Сброс", RED)
        
        # Кнопки меню
        menu_w = SCREEN_WIDTH // 3
        menu_h = SCREEN_HEIGHT // 10
        center_x = SCREEN_WIDTH // 2 - menu_w // 2
        
        self.btn_new = MobileButton(center_x, 200, menu_w, menu_h, "Новая игра", GREEN)
        self.btn_continue = MobileButton(center_x, 250 + menu_h, menu_w, menu_h, "Продолжить", BLUE)
        self.btn_exit = MobileButton(center_x, 300 + 2*menu_h, menu_w, menu_h, "Выйти", RED)
    
    def reset_game(self):
        self.board = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.level = 1
        self.lines = 0
        self.game_over = False
        self.next_piece = random.randint(0, len(SHAPES) - 1)
        self.spawn_piece()
    
    def spawn_piece(self):
        self.current_piece = SHAPES[self.next_piece]
        self.current_color = COLORS[self.next_piece]
        self.next_piece = random.randint(0, len(SHAPES) - 1)
        self.piece_x = GRID_WIDTH // 2 - len(self.current_piece[0]) // 2
        self.piece_y = 0
        
        if self.check_collision():
            self.game_over = True
    
    def check_collision(self, dx=0, dy=0):
        for y, row in enumerate(self.current_piece):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.piece_x + x + dx
                    new_y = self.piece_y + y + dy
                    
                    if (new_x < 0 or new_x >= GRID_WIDTH or 
                        new_y >= GRID_HEIGHT or 
                        (new_y >= 0 and self.board[new_y][new_x])):
                        return True
        return False
    
    def lock_piece(self):
        for y, row in enumerate(self.current_piece):
            for x, cell in enumerate(row):
                if cell:
                    if self.piece_y + y >= 0:
                        self.board[self.piece_y + y][self.piece_x + x] = self.current_color
        
        self.clear_lines()
        self.spawn_piece()
    
    def clear_lines(self):
        lines_to_remove = []
        for y in range(GRID_HEIGHT):
            if all(self.board[y]):
                lines_to_remove.append(y)
        
        for line in lines_to_remove:
            del self.board[line]
            self.board.insert(0, [0] * GRID_WIDTH)
        
        if lines_to_remove:
            self.lines += len(lines_to_remove)
            self.score += len(lines_to_remove) * 100 * self.level
            self.level = self.lines // 10 + 1
            self.fall_speed = max(100, 500 - (self.level - 1) * 40)
    
    def move(self, dx, dy):
        if not self.game_over and self.current_piece:
            if not self.check_collision(dx, dy):
                self.piece_x += dx
                self.piece_y += dy
                return True
            elif dy > 0:  # Не можем двигаться вниз
                self.lock_piece()
        return False
    
    def rotate(self):
        if not self.game_over and self.current_piece:
            original = self.current_piece
            rotated = list(zip(*self.current_piece[::-1]))
            self.current_piece = [list(row) for row in rotated]
            
            if self.check_collision():
                self.current_piece = original
    
    def drop(self):
        if not self.game_over:
            while self.move(0, 1):
                pass
    
    def draw_board(self):
        # Позиция доски
        board_x = 20
        board_y = 20
        
        # Фон доски
        pygame.draw.rect(self.screen, DARK_GRAY, 
                        (board_x - 5, board_y - 5,
                         GRID_WIDTH * GRID_SIZE + 10,
                         GRID_HEIGHT * GRID_SIZE + 10))
        
        # Сетка
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(
                    board_x + x * GRID_SIZE,
                    board_y + y * GRID_SIZE,
                    GRID_SIZE - 1, GRID_SIZE - 1
                )
                if self.board[y][x]:
                    pygame.draw.rect(self.screen, self.board[y][x], rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
                else:
                    pygame.draw.rect(self.screen, (50, 50, 70), rect)
                    pygame.draw.rect(self.screen, (40, 40, 60), rect, 1)
        
        # Текущая фигура
        if not self.game_over and self.current_piece:
            for y, row in enumerate(self.current_piece):
                for x, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(
                            board_x + (self.piece_x + x) * GRID_SIZE,
                            board_y + (self.piece_y + y) * GRID_SIZE,
                            GRID_SIZE - 1, GRID_SIZE - 1
                        )
                        pygame.draw.rect(self.screen, self.current_color, rect)
                        pygame.draw.rect(self.screen, WHITE, rect, 2)
    
    def draw_sidebar(self):
        # Позиция боковой панели
        sidebar_x = 30 + GRID_WIDTH * GRID_SIZE + 20
        sidebar_width = SCREEN_WIDTH - sidebar_x - 20
        
        # Фон
        pygame.draw.rect(self.screen, (30, 30, 50),
                        (sidebar_x, 0, sidebar_width, SCREEN_HEIGHT))
        
        y = 20
        
        # Заголовок
        title = self.font_medium.render("ТЕТРИС", True, CYAN)
        self.screen.blit(title, (sidebar_x + 10, y))
        y += 40
        
        # Статистика
        stats = [
            f"Счет: {self.score}",
            f"Уровень: {self.level}",
            f"Линии: {self.lines}",
            f"Скорость: {self.fall_speed}мс"
        ]
        
        for stat in stats:
            text = self.font_small.render(stat, True, WHITE)
            self.screen.blit(text, (sidebar_x + 10, y))
            y += 30
        
        y += 20
        
        # Следующая фигура
        next_text = self.font_small.render("Следующая:", True, WHITE)
        self.screen.blit(next_text, (sidebar_x + 10, y))
        y += 30
        
        if self.next_piece is not None:
            next_shape = SHAPES[self.next_piece]
            next_color = COLORS[self.next_piece]
            
            # Центрирование
            shape_w = len(next_shape[0]) * (GRID_SIZE - 5)
            shape_x = sidebar_x + (sidebar_width - shape_w) // 2
            
            for py, row in enumerate(next_shape):
                for px, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(
                            shape_x + px * (GRID_SIZE - 5),
                            y + py * (GRID_SIZE - 5),
                            GRID_SIZE - 6, GRID_SIZE - 6
                        )
                        pygame.draw.rect(self.screen, next_color, rect)
                        pygame.draw.rect(self.screen, WHITE, rect, 1)
    
    def draw_menu(self):
        # Полупрозрачный фон
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Заголовок
        title = self.font_large.render("ТЕТРИС MOBILE", True, CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Кнопки меню
        self.btn_new.draw(self.screen)
        
        # Кнопка "Продолжить" только если игра была на паузе
        if self.game_state == "PAUSED":
            self.btn_continue.draw(self.screen)
        else:
            # Неактивная кнопка
            saved_color = self.btn_continue.color
            self.btn_continue.color = GRAY
            self.btn_continue.draw(self.screen)
            self.btn_continue.color = saved_color
        
        self.btn_exit.draw(self.screen)
        
        # Инструкция
        instr = self.font_small.render("Касайтесь кнопок для управления", True, WHITE)
        instr_rect = instr.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(instr, instr_rect)
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Текст
        game_over = self.font_large.render("ИГРА ОКОНЧЕНА!", True, RED)
        game_over_rect = game_over.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(game_over, game_over_rect)
        
        score_text = self.font_medium.render(f"Счет: {self.score}", True, YELLOW)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(score_text, score_rect)
        
        # Кнопки
        btn_w = SCREEN_WIDTH // 4
        center_x = SCREEN_WIDTH // 2 - btn_w // 2
        
        restart_btn = MobileButton(center_x, 280, btn_w, 50, "Новая игра", GREEN)
        menu_btn = MobileButton(center_x, 350, btn_w, 50, "В меню", BLUE)
        
        restart_btn.draw(self.screen)
        menu_btn.draw(self.screen)
        
        return restart_btn, menu_btn
    
    def draw_pause(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font_large.render("ПАУЗА", True, YELLOW)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(pause_text, pause_rect)
        
        continue_text = self.font_medium.render("Коснитесь экрана для продолжения", True, WHITE)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, 260))
        self.screen.blit(continue_text, continue_rect)
    
    def draw_controls(self):
        if self.game_state == "PLAYING":
            self.btn_left.draw(self.screen)
            self.btn_right.draw(self.screen)
            self.btn_rotate.draw(self.screen)
            self.btn_down.draw(self.screen)
            self.btn_pause.draw(self.screen)
            self.btn_drop.draw(self.screen)
    
    def draw(self):
        # Фон
        self.screen.fill(DARK_BLUE)
        
        if self.game_state in ["PLAYING", "PAUSED", "GAME_OVER"]:
            self.draw_board()
            self.draw_sidebar()
            self.draw_controls()
            
            if self.game_state == "PAUSED":
                self.draw_pause()
            elif self.game_over:
                return self.draw_game_over()
        
        elif self.game_state == "MENU":
            self.draw_board()
            self.draw_sidebar()
            self.draw_menu()
        
        return None
    
    def handle_touch(self, pos):
        if self.game_state == "PLAYING":
            # Кнопки управления
            if self.btn_left.check_touch(pos):
                self.btn_left.pressed = True
                self.move(-1, 0)
                return True
            elif self.btn_right.check_touch(pos):
                self.btn_right.pressed = True
                self.move(1, 0)
                return True
            elif self.btn_rotate.check_touch(pos):
                self.btn_rotate.pressed = True
                self.rotate()
                return True
            elif self.btn_down.check_touch(pos):
                self.btn_down.pressed = True
                self.move(0, 1)
                return True
            elif self.btn_pause.check_touch(pos):
                self.btn_pause.pressed = True
                self.game_state = "PAUSED"
                return True
            elif self.btn_drop.check_touch(pos):
                self.btn_drop.pressed = True
                self.drop()
                return True
        
        elif self.game_state == "MENU":
            if self.btn_new.check_touch(pos):
                self.reset_game()
                self.game_state = "PLAYING"
                return True
            elif self.btn_continue.check_touch(pos) and self.game_state == "PAUSED":
                self.game_state = "PLAYING"
                return True
            elif self.btn_exit.check_touch(pos):
                return False
        
        elif self.game_state == "PAUSED":
            # Любое касание продолжает игру
            self.game_state = "PLAYING"
            return True
        
        elif self.game_over:
            buttons = self.draw()
            if buttons:
                restart_btn, menu_btn = buttons
                if restart_btn.check_touch(pos):
                    self.reset_game()
                    self.game_state = "PLAYING"
                    return True
                elif menu_btn.check_touch(pos):
                    self.game_state = "MENU"
                    return True
        
        return False
    
    def run(self):
        running = True
        
        while running:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif self.game_state == "PLAYING" and not self.game_over:
                        if event.key == pygame.K_LEFT:
                            self.move(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move(1, 0)
                        elif event.key == pygame.K_UP:
                            self.rotate()
                        elif event.key == pygame.K_DOWN:
                            self.fall_speed = 100
                        elif event.key == pygame.K_SPACE:
                            self.drop()
                        elif event.key == pygame.K_p:
                            self.game_state = "PAUSED"
                    elif event.key == pygame.K_m:
                        self.game_state = "MENU"
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Левая кнопка (касание)
                        if not self.handle_touch(event.pos):
                            if self.game_state == "PAUSED":
                                self.game_state = "PLAYING"
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    # Сбрасываем все кнопки
                    for btn in [self.btn_left, self.btn_right, self.btn_rotate,
                              self.btn_down, self.btn_pause, self.btn_drop,
                              self.btn_new, self.btn_continue, self.btn_exit]:
                        btn.pressed = False
            
            # Автоматическое падение
            if self.game_state == "PLAYING" and not self.game_over:
                if current_time - self.last_fall > self.fall_speed:
                    self.move(0, 1)
                    self.last_fall = current_time
            
            # Отрисовка
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    print("Тетрис Mobile")
    print("Управление:")
    print("  Кнопки на экране - мобильное управление")
    print("  Стрелки - движение/поворот (для ПК)")
    print("  P - пауза")
    print("  M - меню")
    print("  ESC - выход")
    
    try:
        game = TetrisMobile()
        game.run()
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()
