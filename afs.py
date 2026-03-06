import random
import time
from collections import deque
from typing import List, Tuple, Set

class MatchThreeGame:
    def __init__(self, width: int = 8, height: int = 8, colors: int = 8):
        self.width = width
        self.height = height
        self.colors = colors
        self.board = []
        self.score = 0
        self.initialize_board()
    
    def initialize_board(self) -> None:
        """Инициализация поля без начальных совпадений"""
        self.board = [[random.randint(1, self.colors) for _ in range(self.width)] 
                      for _ in range(self.height)]
        
        while self.find_all_matches_iterative():
            self.remove_matches()
            self.fill_board()
    
    def print_board(self) -> None:
        """Вывод поля в консоль"""
        print(f"Score: {self.score}")
        print("    " + " ".join(str(i) for i in range(self.width)))
        print("  +" + "-" * (self.width * 2 - 1) + "+")
        
        for y in range(self.height):
            print(f"{y} |", end=" ")
            for x in range(self.width):
                print(self.board[y][x], end=" ")
            print("|")
        
        print("  +" + "-" * (self.width * 2 - 1) + "+")
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Проверка валидности координат"""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def swap_tiles(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """Обмен двух ячеек с таймерами"""
        if not (self.is_valid_position(x1, y1) and self.is_valid_position(x2, y2)):
            return False
        
        if abs(x1 - x2) + abs(y1 - y2) != 1:
            return False
        
        # Меняем ячейки местами
        self.board[y1][x1], self.board[y2][x2] = self.board[y2][x2], self.board[y1][x1]
        
        # Задержка после перестановки
        print("Перестановка ячеек...")
        self.print_board()
        time.sleep(3)
        
        # Проверяем совпадения
        matches = self.find_matches_bfs()
        if not matches:
            self.board[y1][x1], self.board[y2][x2] = self.board[y2][x2], self.board[y1][x1]
            return False
        
        # Удаляем совпадения
        self.remove_matches()
        
        # Заполняем поле и обрабатываем каскады
        self.fill_board_buggy() 
        while self.find_matches_bfs():
            self.remove_matches()
            self.fill_board_buggy()
        
        return True
    
    def find_matches_bfs(self) -> List[List[Tuple[int, int]]]:
        matches = []
        visited = set()
        
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in visited and self.board[y][x] != 0:

                    match_group = self._bfs_all_directions(x, y, visited)
                    
                    if len(match_group) >= 3:
                        matches.append(match_group)
        
        return matches
    
    def _bfs_all_directions(self, start_x: int, start_y: int, visited: Set[Tuple[int, int]]) -> List[Tuple[int, int]]:
        color = self.board[start_y][start_x]
        
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)] 

        queue = deque([(start_x, start_y)])
        match_group = []
        
        while queue:
            x, y = queue.popleft()
            if (x, y) in visited or not self.is_valid_position(x, y) or self.board[y][x] != color:
                continue
            
            visited.add((x, y))
            match_group.append((x, y))
            
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
                if self.is_valid_position(new_x, new_y) and self.board[new_y][new_x] == color:
                    queue.append((new_x, new_y)) 
        
        return match_group
    
    def find_all_matches_iterative(self) -> List[List[Tuple[int, int]]]:
    
        all_matches = []
        visited = [[False] * self.width for _ in range(self.height)]
        
        for y in range(self.height):
            for x in range(self.width):
                if not visited[y][x] and self.board[y][x] != 0:
                    # Проверяем горизонтальную линию
                    horizontal = []
                    cx = x
                    # Вправо
                    while cx < self.width and self.board[y][cx] == self.board[y][x]:
                        horizontal.append((cx, y))
                        cx += 1
                    # Влево (но не включаем стартовую точку дважды)
                    cx = x - 1
                    while cx >= 0 and self.board[y][cx] == self.board[y][x]:
                        horizontal.append((cx, y))
                        cx -= 1
                    
                    if len(horizontal) >= 3:
                        all_matches.append(horizontal)
                        for hx, hy in horizontal:
                            visited[hy][hx] = True
                    
                    # Проверяем вертикальную линию
                    vertical = []
                    cy = y
                    # Вниз
                    while cy < self.height and self.board[cy][x] == self.board[y][x]:
                        vertical.append((x, cy))
                        cy += 1
                    # Вверх (но не включаем стартовую точку дважды)
                    cy = y - 1
                    while cy >= 0 and self.board[cy][x] == self.board[y][x]:
                        vertical.append((x, cy))
                        cy -= 1
                    
                    if len(vertical) >= 3:
                        all_matches.append(vertical)
                        for vx, vy in vertical:
                            visited[vy][vx] = True
        
        return all_matches
    
    def remove_matches(self) -> None:
        """Удаление найденных совпадений с таймером"""
        matches = self.find_matches_bfs()
        if not matches:
            return
        
        removed_cells = set()
        for match in matches:
            for x, y in match:
                if (x, y) not in removed_cells:
                    self.board[y][x] = 0
                    removed_cells.add((x, y))
                    self.score += 10
        
        # Задержка после удаления ячеек
        if removed_cells:
            print("Удаление совпадений...")
            self.print_board()
            time.sleep(1.0)
    
    def fill_board(self) -> None:
        """Правильное заполнение пустых ячеек (не используется из-за ошибки)"""
        changes_made = False
        
        for x in range(self.width):
            empty_spaces = []
            for y in range(self.height - 1, -1, -1):
                if self.board[y][x] == 0:
                    empty_spaces.append(y)
                elif empty_spaces:
                    lowest_empty = empty_spaces.pop(0)
                    self.board[lowest_empty][x] = self.board[y][x]
                    self.board[y][x] = 0
                    empty_spaces.append(y)
                    empty_spaces.sort(reverse=True)
                    changes_made = True
            
            for y in empty_spaces:
                self.board[y][x] = random.randint(1, self.colors)
                changes_made = True
        
        # Задержка после добавления новых ячеек
        if changes_made:
            print("Добавление новых ячеек...")
            self.print_board()
            time.sleep(3)
    
    def fill_board_buggy(self) -> None:
        changes_made = False
        
        for x in range(self.width):
            for y in range(self.height):
                if self.board[y][x] == 0:
                    # ОШИБКА 2: Просто заполняем пустоты на месте, без падйения
                    self.board[y][x] = random.randint(1, self.colors)
                    changes_made = True
        
        # Задержка после добавления новых ячеек
        if changes_made:
            print("Добавление новых ячеек ...")
            self.print_board()
            time.sleep(0.5)
    
    def has_valid_moves(self) -> bool:
        """Проверка наличия возможных ходов"""
        for y in range(self.height):
            for x in range(self.width):
                if x < self.width - 1:
                    self.board[y][x], self.board[y][x + 1] = self.board[y][x + 1], self.board[y][x]
                    if self.find_matches_bfs():
                        self.board[y][x], self.board[y][x + 1] = self.board[y][x + 1], self.board[y][x]
                        return True
                    self.board[y][x], self.board[y][x + 1] = self.board[y][x + 1], self.board[y][x]
                
                if y < self.height - 1:
                    self.board[y][x], self.board[y + 1][x] = self.board[y + 1][x], self.board[y][x]
                    if self.find_matches_bfs():
                        self.board[y][x], self.board[y + 1][x] = self.board[y + 1][x], self.board[y][x]
                        return True
                    self.board[y][x], self.board[y + 1][x] = self.board[y + 1][x], self.board[y][x]
        
        return False

def main():   
    print("Добро пожаловать в игру '3 в ряд'!")
    print("Для хода введите координаты двух соседних ячеек (x1 y1 x2 y2)")
    print("Для выхода введите 'q'")

    game = MatchThreeGame()
    
    while True:
        game.print_board()
        
        if not game.has_valid_moves():
            print("Ходов больше нет! Игра окончена.")
            break
        
        user_input = input("Введите ход: ").strip()
        if user_input.lower() == 'q':
            break
        
        try:
            x1, y1, x2, y2 = map(int, user_input.split())
            if game.swap_tiles(x1, y1, x2, y2):
                print("Ход успешен!")
            else:
                print("Неверный ход! Ячейки должны быть соседними и образовывать ряд.")
        except ValueError:
            print("Неверный формат! Используйте: x1 y1 x2 y2")
        
        print()

if __name__ == "__main__":

    main()