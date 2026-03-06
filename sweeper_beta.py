import tkinter as tk
from tkinter import messagebox, ttk
from random import shuffle
import time
from collections import deque
import math

class MyButton(tk.Button):
    
    def __init__(self, master, x, y, number=0, *args, **kwargs):
        super(MyButton, self).__init__(master, width=2, height=1, 
                                        font='calibri 8 bold', *args, **kwargs)
        self.x = x
        self.y = y
        self.number = number
        self.is_mine = False
        self.count_bomb = 0
        self.is_open = False
        self.is_flag = False
    
    def __repr__(self):
        return f"MyButton({self.x},{self.y}) - mine:{self.is_mine}"

class Minesweeper:
    
    window = tk.Tk()
    ROW = 9
    COLUMNS = 9
    MINES = 10
    FLAGS = 0
    IS_GAME_OVER = False
    IS_FIRST_CLICK = True
    IS_FIRST_CLICK2 = True  # Добавляем флаг для первого клика игрока 2
    START_TIME = None
    
    # Доступные предметы
    AVAILABLE_ITEMS = {
        "none": {
            "name": "Без предметов",
            "description": "Обычная игра без дополнительных предметов",
            "uses": 0
        },
        "sapper": {
            "name": "Сапер",
            "description": "Проверяет одну клетку на мину. Если мина найдена, ставит флаг",
            "uses": 1
        },
        "sapper_suit": {
            "name": "Костюм сапера",
            "description": "Защищает от одной мины (можно ошибиться один раз)",
            "uses": 1
        },
        "air_invasion": {
            "name": "Воздушное вторжение",
            "description": "Дает 3 дополнительных хода игроку, использовавшему предмет",
            "uses": 1
        },
        "air_defense": {
            "name": "ПВО",
            "description": "Активируется заранее, защищает от воздушного вторжения и БПЛА в течение 5 ходов",
            "uses": 1
        },
        "uav": {
            "name": "БПЛА",
            "description": "Активен 5 ходов. Если противник активирует костюм сапера в этот период, его эффект будет отменен",
            "uses": 1
        },
        "double_move": {
            "name": "Двойной ход",
            "description": "Позволяет сделать два хода подряд",
            "uses": 1
        }
    }
    
    def __init__(self):
        self.buttons = []
        self.buttons2 = []  # Второе поле для двух игроков
        self.current_player = 1  # 1 или 2
        self.game_mode = "single"  # "single" или "multi"
        
        # Предметы для каждого игрока
        self.selected_items = [
            ["none", "none"],  # Игрок 1
            ["none", "none"]   # Игрок 2
        ]
        self.current_item_uses = [
            [0, 0],  # Игрок 1
            [0, 0]   # Игрок 2
        ]
        
        self.active_item_slot = None
        self.active_item_player = None
        self.air_invasion_active = False  # Изменено с air_invasion_blocked
        self.block_timer_label = None
        self.block_remaining_time = 0
        self.block_timer_running = False
        self.triple_moves_left = 0  # Количество оставшихся ходов от воздушного вторжения
        
        # Активные эффекты для каждого игрока
        self.sapper_suit_active = [False, False]  # [игрок1, игрок2]
        self.uav_active = [False, False]
        self.uav_moves_left = [0, 0]
        self.air_defense_active = [False, False]
        self.air_defense_moves_left = [0, 0]
        self.double_move_active = False
        self.double_move_count = 0
        
        self.player1_score = 0
        self.player2_score = 0
        self.player1_moves = 0
        self.player2_moves = 0
        
        self.create_menu()
        self.create_info_panel()
        self.create_widgets()
        self.window.title("Сапер с предметами - Мультиплеер")
        
    def create_menu(self):
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        
        # Меню Игра
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Игра", menu=game_menu)
        game_menu.add_command(label="Новая игра (одиночная)", command=lambda: self.set_game_mode("single"))
        game_menu.add_command(label="Новая игра на двоих", command=lambda: self.set_game_mode("multi"))
        game_menu.add_separator()
        game_menu.add_command(label="Выход", command=self.window.destroy)
        
        # Меню Сложность
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Сложность", menu=settings_menu)
        settings_menu.add_command(label="Новичок (9x9, 10 мин)", 
                                  command=lambda: self.set_difficulty(9, 9, 10))
        settings_menu.add_command(label="Любитель (16x16, 40 мин)", 
                                  command=lambda: self.set_difficulty(16, 16, 40))
        settings_menu.add_command(label="Эксперт (16x30, 99 мин)", 
                                  command=lambda: self.set_difficulty(16, 30, 99))
        
        # Меню Предметы - Игрок 1
        items_menu1 = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Предметы Игрок 1", menu=items_menu1)
        
        # Слот 1 игрока 1
        items_menu1.add_cascade(label="Слот 1", menu=self.create_item_submenu(0, 0))
        # Слот 2 игрока 1
        items_menu1.add_cascade(label="Слот 2", menu=self.create_item_submenu(0, 1))
        
        # Меню Предметы - Игрок 2
        items_menu2 = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Предметы Игрок 2", menu=items_menu2)
        
        # Слот 1 игрока 2
        items_menu2.add_cascade(label="Слот 1", menu=self.create_item_submenu(1, 0))
        # Слот 2 игрока 2
        items_menu2.add_cascade(label="Слот 2", menu=self.create_item_submenu(1, 1))
        
        # Меню справки
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="Об игре", command=self.show_about)
        help_menu.add_command(label="Правила", command=self.show_rules)
        help_menu.add_command(label="Управление предметами", command=self.show_items_help)
    
    def create_item_submenu(self, player, slot):
        """Создает подменю для выбора предмета"""
        submenu = tk.Menu(self.window, tearoff=0)
        
        var = tk.StringVar(value=self.selected_items[player][slot])
        
        for item_id, item_data in self.AVAILABLE_ITEMS.items():
            submenu.add_radiobutton(
                label=f"{item_data['name']} ({item_data['uses']} исп.)",
                variable=var,
                value=item_id,
                command=lambda pid=player, sid=slot, iid=item_id: self.select_item(iid, pid, sid)
            )
        
        return submenu
    
    def set_game_mode(self, mode):
        """Установка режима игры"""
        if not self.IS_GAME_OVER:
            if messagebox.askyesno("Смена режима", 
                                  f"Вы хотите начать игру в режиме {'на двоих' if mode == 'multi' else 'одиночную'}?\nТекущая игра будет перезапущена."):
                self.game_mode = mode
                self.new_game()
        else:
            self.game_mode = mode
            self.new_game()
    
    def select_item(self, item_id, player, slot):
        """Выбор предмета из меню для указанного слота и игрока"""
        if self.IS_GAME_OVER:
            self.selected_items[player][slot] = item_id
            self.current_item_uses[player][slot] = self.AVAILABLE_ITEMS[item_id]["uses"]
            messagebox.showinfo("Предмет выбран", 
                               f"Игрок {player+1}, слот {slot+1}: {self.AVAILABLE_ITEMS[item_id]['name']}\nНачните новую игру, чтобы использовать его.")
        else:
            if messagebox.askyesno("Смена предмета", 
                                  f"Игрок {player+1}, вы хотите сменить предмет в слоте {slot+1} на {self.AVAILABLE_ITEMS[item_id]['name']}?\nТекущая игра будет перезапущена."):
                self.selected_items[player][slot] = item_id
                self.current_item_uses[player][slot] = self.AVAILABLE_ITEMS[item_id]["uses"]
                self.new_game()
    
    def create_info_panel(self):
        self.info_frame = tk.Frame(self.window)
        self.info_frame.grid(row=0, column=0, columnspan=20, pady=10, sticky="ew")
        
        # Левая часть - информация о минах и времени
        left_frame = tk.Frame(self.info_frame)
        left_frame.pack(side=tk.LEFT)
        
        self.mines_label = tk.Label(left_frame, text=f"Мин: {self.MINES}", 
                                     font='calibri 12 bold')
        self.mines_label.pack(side=tk.LEFT, padx=20)
        
        self.time_label = tk.Label(left_frame, text="Время: 0", 
                                    font='calibri 12 bold')
        self.time_label.pack(side=tk.LEFT, padx=20)
        
        self.flags_label = tk.Label(left_frame, text=f"Флагов: {self.FLAGS}/{self.MINES}", 
                                     font='calibri 12 bold')
        self.flags_label.pack(side=tk.LEFT, padx=20)
        
        # Центральная часть - информация об игроках
        self.players_frame = tk.Frame(self.info_frame)
        self.players_frame.pack(side=tk.LEFT, padx=20)
        
        self.player1_indicator = tk.Label(self.players_frame, 
                                         text="🎮 Игрок 1", 
                                         font='calibri 12 bold', 
                                         fg="blue", 
                                         bg="lightblue",
                                         relief=tk.RIDGE,
                                         padx=10)
        self.player1_indicator.pack(side=tk.LEFT, padx=5)
        
        self.player2_indicator = tk.Label(self.players_frame, 
                                         text="Игрок 2", 
                                         font='calibri 12 bold', 
                                         fg="gray", 
                                         bg="lightgray",
                                         relief=tk.RIDGE,
                                         padx=10)
        self.player2_indicator.pack(side=tk.LEFT, padx=5)
        
        self.player1_score_label = tk.Label(self.players_frame, 
                                           text="Очки: 0", 
                                           font='calibri 10')
        self.player1_score_label.pack(side=tk.LEFT, padx=5)
        
        self.player2_score_label = tk.Label(self.players_frame, 
                                           text="Очки: 0", 
                                           font='calibri 10')
        self.player2_score_label.pack(side=tk.LEFT, padx=5)
        
        # Предметы игрока 1
        self.items_frame_player1 = tk.Frame(self.info_frame)
        self.items_frame_player1.pack(side=tk.LEFT, padx=10)
        
        self.item_frame1_player1 = tk.Frame(self.items_frame_player1, relief=tk.RIDGE, borderwidth=2, bg="lightblue")
        self.item_frame1_player1.pack(side=tk.LEFT, padx=5)
        
        self.item_label1_player1 = tk.Label(self.item_frame1_player1, 
                                           text=f"Игрок 1:\nПредмет 1",
                                           font='calibri 9 bold', fg="blue")
        self.item_label1_player1.pack()
        
        self.item_uses_label1_player1 = tk.Label(self.item_frame1_player1,
                                                text=f"Исп.: 0/0",
                                                font='calibri 8', fg="darkblue")
        self.item_uses_label1_player1.pack()
        
        self.use_item_btn1_player1 = tk.Button(self.item_frame1_player1, text="Исп.", 
                                              font='calibri 8 bold', bg="lightblue",
                                              command=lambda: self.activate_item(0, 0),
                                              width=6)
        self.use_item_btn1_player1.pack(pady=2)
        
        self.item_frame2_player1 = tk.Frame(self.items_frame_player1, relief=tk.RIDGE, borderwidth=2, bg="lightblue")
        self.item_frame2_player1.pack(side=tk.LEFT, padx=5)
        
        self.item_label2_player1 = tk.Label(self.item_frame2_player1, 
                                           text=f"Игрок 1:\nПредмет 2",
                                           font='calibri 9 bold', fg="blue")
        self.item_label2_player1.pack()
        
        self.item_uses_label2_player1 = tk.Label(self.item_frame2_player1,
                                                text=f"Исп.: 0/0",
                                                font='calibri 8', fg="darkblue")
        self.item_uses_label2_player1.pack()
        
        self.use_item_btn2_player1 = tk.Button(self.item_frame2_player1, text="Исп.", 
                                              font='calibri 8 bold', bg="lightblue",
                                              command=lambda: self.activate_item(0, 1),
                                              width=6)
        self.use_item_btn2_player1.pack(pady=2)
        
        # Предметы игрока 2
        self.items_frame_player2 = tk.Frame(self.info_frame)
        self.items_frame_player2.pack(side=tk.LEFT, padx=10)
        
        self.item_frame1_player2 = tk.Frame(self.items_frame_player2, relief=tk.RIDGE, borderwidth=2, bg="lightcoral")
        self.item_frame1_player2.pack(side=tk.LEFT, padx=5)
        
        self.item_label1_player2 = tk.Label(self.item_frame1_player2, 
                                           text=f"Игрок 2:\nПредмет 1",
                                           font='calibri 9 bold', fg="red")
        self.item_label1_player2.pack()
        
        self.item_uses_label1_player2 = tk.Label(self.item_frame1_player2,
                                                text=f"Исп.: 0/0",
                                                font='calibri 8', fg="darkred")
        self.item_uses_label1_player2.pack()
        
        self.use_item_btn1_player2 = tk.Button(self.item_frame1_player2, text="Исп.", 
                                              font='calibri 8 bold', bg="lightcoral",
                                              command=lambda: self.activate_item(1, 0),
                                              width=6)
        self.use_item_btn1_player2.pack(pady=2)
        
        self.item_frame2_player2 = tk.Frame(self.items_frame_player2, relief=tk.RIDGE, borderwidth=2, bg="lightcoral")
        self.item_frame2_player2.pack(side=tk.LEFT, padx=5)
        
        self.item_label2_player2 = tk.Label(self.item_frame2_player2, 
                                           text=f"Игрок 2:\nПредмет 2",
                                           font='calibri 9 bold', fg="red")
        self.item_label2_player2.pack()
        
        self.item_uses_label2_player2 = tk.Label(self.item_frame2_player2,
                                                text=f"Исп.: 0/0",
                                                font='calibri 8', fg="darkred")
        self.item_uses_label2_player2.pack()
        
        self.use_item_btn2_player2 = tk.Button(self.item_frame2_player2, text="Исп.", 
                                              font='calibri 8 bold', bg="lightcoral",
                                              command=lambda: self.activate_item(1, 1),
                                              width=6)
        self.use_item_btn2_player2.pack(pady=2)
        
        # Правая часть - кнопка перезапуска и таймер блокировки (теперь не используется)
        right_frame = tk.Frame(self.info_frame)
        right_frame.pack(side=tk.RIGHT)
        
        # Фрейм для таймера воздушного вторжения (изменено назначение)
        self.air_invasion_frame = tk.Frame(right_frame)
        self.air_invasion_frame.pack(side=tk.TOP, pady=5)
        
        self.air_invasion_label = tk.Label(self.air_invasion_frame, 
                                         text="",
                                         font='calibri 11 bold', 
                                         fg="white", 
                                         bg="darkgreen",
                                         width=15,
                                         height=1)
        self.air_invasion_label.pack()
        self.air_invasion_label.pack_forget()  # Скрываем по умолчанию
        
        self.reset_btn = tk.Button(right_frame, text="🔄", font='calibri 15', 
                                   command=self.new_game)
        self.reset_btn.pack(side=tk.BOTTOM, pady=5)
        
        # Индикаторы активных эффектов
        self.indicators_frame = tk.Frame(self.info_frame)
        self.indicators_frame.pack(side=tk.RIGHT, padx=10)
        
        # Индикатор ПВО
        self.air_defense_indicator = tk.Label(self.indicators_frame, 
                                            text="🛡 ПВО: НЕТ",
                                            font='calibri 9', fg="gray", bg="lightgray")
        self.air_defense_indicator.pack()
        
        # Индикатор костюма сапера
        self.sapper_suit_indicator = tk.Label(self.indicators_frame, 
                                            text="🛡 Костюм: НЕТ",
                                            font='calibri 9', fg="gray", bg="lightgray")
        self.sapper_suit_indicator.pack()
        
        # Индикатор БПЛА
        self.uav_indicator = tk.Label(self.indicators_frame, 
                                     text="🚁 БПЛА: НЕТ",
                                     font='calibri 9', fg="gray", bg="lightgray")
        self.uav_indicator.pack()
        
        # Индикатор двойного хода
        self.double_move_indicator = tk.Label(self.indicators_frame, 
                                            text="⚡ Двойной: НЕТ",
                                            font='calibri 9', fg="gray", bg="lightgray")
        self.double_move_indicator.pack()
        
        # Индикатор воздушного вторжения (тройной ход)
        self.air_invasion_indicator = tk.Label(self.indicators_frame, 
                                             text="✈️ Возд.вторж.: НЕТ",
                                             font='calibri 9', fg="gray", bg="lightgray")
        self.air_invasion_indicator.pack()
    
    def update_player_display(self):
        """Обновляет отображение информации об игроках"""
        # Подсвечиваем активного игрока
        if self.current_player == 1:
            self.player1_indicator.config(fg="blue", bg="lightblue", text="🎮 Игрок 1 (ХОДИТ)")
            self.player2_indicator.config(fg="gray", bg="lightgray", text="Игрок 2")
            
            # Подсветка предметов активного игрока
            self.items_frame_player1.config(bg="lightyellow")
            self.items_frame_player2.config(bg="SystemButtonFace")
        else:
            self.player1_indicator.config(fg="gray", bg="lightgray", text="Игрок 1")
            self.player2_indicator.config(fg="red", bg="lightcoral", text="🎮 Игрок 2 (ХОДИТ)")
            
            # Подсветка предметов активного игрока
            self.items_frame_player1.config(bg="SystemButtonFace")
            self.items_frame_player2.config(bg="lightyellow")
        
        # Обновляем очки
        self.player1_score_label.config(text=f"Очки: {self.player1_score}")
        self.player2_score_label.config(text=f"Очки: {self.player2_score}")
        
        # Обновляем индикаторы эффектов
        player_idx = self.current_player - 1
        other_idx = 1 if player_idx == 0 else 0
        
        # ПВО
        if self.air_defense_active[player_idx]:
            color = "lightblue" if player_idx == 0 else "lightcoral"
            text = f"🛡 ПВО: {self.air_defense_moves_left[player_idx]} ход."
            self.air_defense_indicator.config(text=text, fg="darkblue", bg=color)
        elif self.air_defense_active[other_idx]:
            color = "lightcoral" if player_idx == 0 else "lightblue"
            text = f"🛡 ПВО пр-ка: {self.air_defense_moves_left[other_idx]} ход."
            self.air_defense_indicator.config(text=text, fg="darkred", bg=color)
        else:
            self.air_defense_indicator.config(text="🛡 ПВО: НЕТ", fg="gray", bg="lightgray")
        
        # Костюм сапера
        if self.sapper_suit_active[player_idx]:
            color = "lightblue" if player_idx == 0 else "lightcoral"
            self.sapper_suit_indicator.config(text="🛡 Костюм: АКТИВЕН", fg="darkgreen", bg=color)
        else:
            self.sapper_suit_indicator.config(text="🛡 Костюм: НЕТ", fg="gray", bg="lightgray")
        
        # БПЛА
        if self.uav_active[player_idx]:
            color = "lightblue" if player_idx == 0 else "lightcoral"
            text = f"🚁 БПЛА: {self.uav_moves_left[player_idx]} ход."
            self.uav_indicator.config(text=text, fg="darkred", bg=color)
        elif self.uav_active[other_idx]:
            color = "lightcoral" if player_idx == 0 else "lightblue"
            text = f"🚁 БПЛА пр-ка: {self.uav_moves_left[other_idx]} ход."
            self.uav_indicator.config(text=text, fg="darkred", bg=color)
        else:
            self.uav_indicator.config(text="🚁 БПЛА: НЕТ", fg="gray", bg="lightgray")
        
        # Двойной ход
        if self.double_move_active:
            text = f"⚡ Двойной ход: {self.double_move_count} осталось"
            self.double_move_indicator.config(text=text, fg="darkorange", bg="lightyellow")
        else:
            self.double_move_indicator.config(text="⚡ Двойной: НЕТ", fg="gray", bg="lightgray")
        
        # Воздушное вторжение (тройной ход)
        if self.air_invasion_active and self.triple_moves_left > 0:
            player_name = "Игрок 1" if self.current_player == 1 else "Игрок 2"
            color = "lightblue" if self.current_player == 1 else "lightcoral"
            text = f"✈️ Возд.вторж.: {self.triple_moves_left} ход."
            self.air_invasion_indicator.config(text=text, fg="darkgreen", bg=color)
            self.air_invasion_label.config(text=f"✈️ {self.triple_moves_left} ход.", bg="darkgreen")
        else:
            self.air_invasion_indicator.config(text="✈️ Возд.вторж.: НЕТ", fg="gray", bg="lightgray")
            self.air_invasion_label.pack_forget()
    
    def update_item_display(self):
        """Обновляет отображение информации о предметах"""
        for player in range(2):
            for slot in range(2):
                item_id = self.selected_items[player][slot]
                item_data = self.AVAILABLE_ITEMS[item_id]
                
                if player == 0:
                    if slot == 0:
                        self.item_label1_player1.config(text=f"Игрок 1:\n{item_data['name'][:10]}")
                        if self.current_item_uses[player][slot] > 0:
                            self.item_uses_label1_player1.config(text=f"Исп.: {self.current_item_uses[player][slot]}/{item_data['uses']}")
                            self.use_item_btn1_player1.config(state=tk.NORMAL, bg="lightblue")
                        else:
                            self.item_uses_label1_player1.config(text="Использован")
                            self.use_item_btn1_player1.config(state=tk.DISABLED, bg="gray")
                    else:
                        self.item_label2_player1.config(text=f"Игрок 1:\n{item_data['name'][:10]}")
                        if self.current_item_uses[player][slot] > 0:
                            self.item_uses_label2_player1.config(text=f"Исп.: {self.current_item_uses[player][slot]}/{item_data['uses']}")
                            self.use_item_btn2_player1.config(state=tk.NORMAL, bg="lightblue")
                        else:
                            self.item_uses_label2_player1.config(text="Использован")
                            self.use_item_btn2_player1.config(state=tk.DISABLED, bg="gray")
                else:
                    if slot == 0:
                        self.item_label1_player2.config(text=f"Игрок 2:\n{item_data['name'][:10]}")
                        if self.current_item_uses[player][slot] > 0:
                            self.item_uses_label1_player2.config(text=f"Исп.: {self.current_item_uses[player][slot]}/{item_data['uses']}")
                            self.use_item_btn1_player2.config(state=tk.NORMAL, bg="lightcoral")
                        else:
                            self.item_uses_label1_player2.config(text="Использован")
                            self.use_item_btn1_player2.config(state=tk.DISABLED, bg="gray")
                    else:
                        self.item_label2_player2.config(text=f"Игрок 2:\n{item_data['name'][:10]}")
                        if self.current_item_uses[player][slot] > 0:
                            self.item_uses_label2_player2.config(text=f"Исп.: {self.current_item_uses[player][slot]}/{item_data['uses']}")
                            self.use_item_btn2_player2.config(state=tk.NORMAL, bg="lightcoral")
                        else:
                            self.item_uses_label2_player2.config(text="Использован")
                            self.use_item_btn2_player2.config(state=tk.DISABLED, bg="gray")
    
    def show_air_invasion_indicator(self):
        """Показывает индикатор воздушного вторжения"""
        self.air_invasion_label.pack()
        self.air_invasion_label.config(text=f"✈️ {self.triple_moves_left} ход.")
    
    def hide_air_invasion_indicator(self):
        """Скрывает индикатор воздушного вторжения"""
        self.air_invasion_label.pack_forget()
    
    def activate_air_invasion(self, player_num):
        """Активация воздушного вторжения - дает тройной ход"""
        player_idx = player_num - 1
        other_player = 2 if player_num == 1 else 1
        
        # Проверяем ПВО противника
        if self.air_defense_active[1 if player_idx == 0 else 0]:
            other_idx = 1 if player_idx == 0 else 0
            self.air_defense_moves_left[other_idx] -= 1
            self.update_player_display()
            
            messagebox.showinfo("ПВО сработало!", 
                               f"Воздушное вторжение отражено системами ПВО Игрока {other_player}!\n"
                               f"Ходов защиты осталось: {self.air_defense_moves_left[other_idx]}")
            
            self.current_item_uses[player_idx][self.active_item_slot] -= 1
            self.update_item_display()
            
            if self.air_defense_moves_left[other_idx] <= 0:
                self.air_defense_active[other_idx] = False
            
            self.reset_item_frames()
            self.item_mode_active = False
            self.active_item_slot = None
            self.active_item_player = None
            return False
        else:
            self.air_invasion_active = True
            self.triple_moves_left = 3  # Тройной ход вместо 2
            self.show_air_invasion_indicator()
            
            self.current_item_uses[player_idx][self.active_item_slot] -= 1
            self.update_item_display()
            
            messagebox.showinfo("Воздушное вторжение!", 
                               f"✈️ Игрок {player_num} запустил воздушное вторжение!\n"
                               f"Теперь Игрок {player_num} получает 3 дополнительных хода подряд!")
            
            # Сразу делаем первый дополнительный ход
            self.switch_player_with_triple_move()
            
            return True
    
    def switch_player_with_triple_move(self):
        """Переключение игрока с учетом воздушного вторжения"""
        if self.air_invasion_active and self.triple_moves_left > 0:
            # Не меняем игрока, даем дополнительный ход тому же игроку
            self.triple_moves_left -= 1
            
            # Обновляем активные эффекты
            self.update_active_effects()
            
            # Обновляем отображение
            self.update_player_display()
            
            if self.triple_moves_left > 0:
                messagebox.showinfo("Дополнительный ход", 
                                   f"Воздушное вторжение продолжается!\n"
                                   f"Игрок {self.current_player} делает еще ход.\n"
                                   f"Осталось дополнительных ходов: {self.triple_moves_left}")
            else:
                self.air_invasion_active = False
                self.hide_air_invasion_indicator()
                self.update_player_display()
                
                messagebox.showinfo("Воздушное вторжение завершено", 
                                   f"Воздушное вторжение завершено! Теперь ход переходит к другому игроку.")
                # После завершения воздушного вторжения переключаем на другого игрока
                old_player = self.current_player
                self.current_player = 2 if self.current_player == 1 else 1
                
                # Обновляем счетчики ходов
                if old_player == 1:
                    self.player1_moves += 1
                else:
                    self.player2_moves += 1
                
                self.update_player_display()
                messagebox.showinfo("Смена хода", f"Теперь ходит Игрок {self.current_player}!")
        else:
            # Обычное переключение игрока
            self.switch_player()
    
    def disable_field(self, player_num):
        """Отключает поле указанного игрока"""
        if player_num == 1:
            for i in range(self.ROW):
                for j in range(self.COLUMNS):
                    btn = self.buttons[i][j]
                    if not btn.is_open:
                        btn.config(state=tk.DISABLED, cursor="watch")
        else:
            for i in range(self.ROW):
                for j in range(self.COLUMNS):
                    btn = self.buttons2[i][j]
                    if not btn.is_open:
                        btn.config(state=tk.DISABLED, cursor="watch")
    
    def enable_active_field(self):
        """Включает только активное поле"""
        if self.current_player == 1:
            for i in range(self.ROW):
                for j in range(self.COLUMNS):
                    btn = self.buttons[i][j]
                    if not btn.is_open and not btn.is_flag:
                        btn.config(state=tk.NORMAL, cursor="")
        else:
            for i in range(self.ROW):
                for j in range(self.COLUMNS):
                    btn = self.buttons2[i][j]
                    if not btn.is_open and not btn.is_flag:
                        btn.config(state=tk.NORMAL, cursor="")
    
    def switch_player(self):
        """Переключение между игроками"""
        if self.game_mode == "multi" and not self.IS_GAME_OVER:
            # Проверяем воздушное вторжение
            if self.air_invasion_active and self.triple_moves_left > 0:
                # Используем специальный метод для воздушного вторжения
                self.switch_player_with_triple_move()
                return
                
            # Проверяем двойной ход
            if self.double_move_active and self.double_move_count > 0:
                # Делаем дополнительный ход
                self.double_move_count -= 1
                if self.double_move_count <= 0:
                    self.double_move_active = False
                
                messagebox.showinfo("Двойной ход", 
                                  f"Игрок {self.current_player} делает дополнительный ход!\n"
                                  f"Осталось дополнительных ходов: {self.double_move_count}")
                self.update_player_display()
                return
            else:
                # Меняем игрока
                old_player = self.current_player
                self.current_player = 2 if self.current_player == 1 else 1
                
                # Обновляем счетчики ходов
                if old_player == 1:
                    self.player1_moves += 1
                else:
                    self.player2_moves += 1
                
                # Обновляем активные эффекты
                self.update_active_effects()
                
                # Обновляем отображение
                self.update_player_display()
                
                messagebox.showinfo("Смена хода", f"Теперь ходит Игрок {self.current_player}!")
    
    def update_active_effects(self):
        """Обновляет активные эффекты при смене хода"""
        player_idx = self.current_player - 1
        
        # Обновляем БПЛА
        if self.uav_active[player_idx]:
            self.uav_moves_left[player_idx] -= 1
            if self.uav_moves_left[player_idx] <= 0:
                self.uav_active[player_idx] = False
        
        # Обновляем ПВО
        if self.air_defense_active[player_idx]:
            self.air_defense_moves_left[player_idx] -= 1
            if self.air_defense_moves_left[player_idx] <= 0:
                self.air_defense_active[player_idx] = False
    
    def activate_item(self, player, slot):
        """Активация предмета из указанного слота указанным игроком"""
        if self.IS_GAME_OVER:
            messagebox.showwarning("Игра окончена", "Игра уже завершена!")
            return
            
        # Проверяем, что предмет активирует текущий игрок
        if player != self.current_player - 1:
            messagebox.showwarning("Не ваш ход", 
                                  f"Сейчас ходит Игрок {self.current_player}!\nДождитесь своего хода.")
            return
            
        if self.current_item_uses[player][slot] <= 0:
            messagebox.showwarning("Предмет недоступен", "Этот предмет уже использован!")
            return
        
        item_id = self.selected_items[player][slot]
        item_data = self.AVAILABLE_ITEMS[item_id]
        
        if item_id == "none":
            messagebox.showinfo("Без предметов", "В этом слоте не выбран предмет.")
            return
        
        # Особенная обработка для воздушного вторжения
        if item_id == "air_invasion":
            self.active_item_slot = slot
            self.active_item_player = player
            
            # Немедленная активация воздушного вторжения
            success = self.activate_air_invasion(player + 1)
            
            if success:
                self.current_item_uses[player][slot] -= 1
                self.update_item_display()
                
            self.reset_item_frames()
            self.item_mode_active = False
            self.active_item_slot = None
            self.active_item_player = None
            return True
        
        # Особенная обработка для БПЛА - применяем сразу
        if item_id == "uav":
            other_player = 1 if player == 0 else 0
            
            # Проверяем ПВО противника
            if self.air_defense_active[other_player] and self.air_defense_moves_left[other_player] > 0:
                self.air_defense_moves_left[other_player] -= 1
                self.update_player_display()
                
                messagebox.showinfo("ПВО сработало!", 
                                   f"БПЛА сбит системами ПВО Игрока {other_player+1}!\n"
                                   f"Ходов защиты осталось: {self.air_defense_moves_left[other_player]}")
                
                self.current_item_uses[player][slot] -= 1
                self.update_item_display()
                
                if self.air_defense_moves_left[other_player] <= 0:
                    self.air_defense_active[other_player] = False
                    self.update_player_display()
                
                return True
            else:
                self.uav_active[player] = True
                self.uav_moves_left[player] = 5
                self.update_player_display()
                
                self.current_item_uses[player][slot] -= 1
                self.update_item_display()
                
                messagebox.showinfo("БПЛА запущен!", 
                                   f"🚁 Игрок {player+1} запустил БПЛА!\n"
                                   f"БПЛА будет активен в течение 5 ходов.")
                return True
        
        # Для других предметов устанавливаем режим использования предмета
        self.active_item_slot = slot
        self.active_item_player = player
        self.item_mode_active = True
        
        # Подсвечиваем активный предмет
        if player == 0:
            if slot == 0:
                self.item_frame1_player1.config(bg="yellow")
                self.use_item_btn1_player1.config(bg="orange", text="Выбери")
            else:
                self.item_frame2_player1.config(bg="yellow")
                self.use_item_btn2_player1.config(bg="orange", text="Выбери")
        else:
            if slot == 0:
                self.item_frame1_player2.config(bg="yellow")
                self.use_item_btn1_player2.config(bg="orange", text="Выбери")
            else:
                self.item_frame2_player2.config(bg="yellow")
                self.use_item_btn2_player2.config(bg="orange", text="Выбери")
        
        if item_id == "air_defense":
            if self.air_defense_active[player]:
                messagebox.showinfo("ПВО уже активно", 
                                   f"ПВО уже активно!\nХодов защиты: {self.air_defense_moves_left[player]}")
                self.reset_item_frames()
                self.item_mode_active = False
                self.active_item_slot = None
                self.active_item_player = None
                return
            
            messagebox.showinfo("Предмет активирован", 
                               f"Предмет '{item_data['name']}' активирован!\n"
                               f"Выберите любую клетку для активации ПВО.")
        elif item_id == "double_move":
            messagebox.showinfo("Предмет активирован", 
                               f"Предмет '{item_data['name']}' активирован!\n"
                               f"Вы получите 2 дополнительных хода после текущего.")
            
            self.double_move_active = True
            self.double_move_count = 2
            self.current_item_uses[player][slot] -= 1
            self.update_item_display()
            self.update_player_display()
            
            self.reset_item_frames()
            self.item_mode_active = False
            self.active_item_slot = None
            self.active_item_player = None
            return True
        else:
            messagebox.showinfo("Предмет активирован", 
                               f"Предмет '{item_data['name']}' активирован!\nТеперь нажмите на клетку.")
    
    def reset_item_frames(self):
        """Сброс подсветки фреймов предметов"""
        colors = ["lightblue", "lightcoral"]
        for player in range(2):
            for slot in range(2):
                if player == 0:
                    if slot == 0:
                        self.item_frame1_player1.config(bg=colors[player])
                        self.use_item_btn1_player1.config(bg=colors[player], text="Исп.")
                    else:
                        self.item_frame2_player1.config(bg=colors[player])
                        self.use_item_btn2_player1.config(bg=colors[player], text="Исп.")
                else:
                    if slot == 0:
                        self.item_frame1_player2.config(bg=colors[player])
                        self.use_item_btn1_player2.config(bg=colors[player], text="Исп.")
                    else:
                        self.item_frame2_player2.config(bg=colors[player])
                        self.use_item_btn2_player2.config(bg=colors[player], text="Исп.")
    
    def apply_item(self, button, field_num):
        """Применение активного предмета к выбранной клетке"""
        if self.active_item_slot is None or self.active_item_player is None:
            return False
            
        player = self.active_item_player
        slot = self.active_item_slot
        
        # Проверяем, что игрок применяет предмет на правильном поле
        # Игрок 1 применяет предметы на поле игрока 2 и наоборот
        if (player == 0 and field_num != 2) or (player == 1 and field_num != 1):
            messagebox.showwarning("Неверное поле", 
                                 f"Игрок {player+1} должен применять предметы на поле противника!")
            return False
        
        item_id = self.selected_items[player][slot]
        
        if item_id == "none":
            return False
        
        if self.current_item_uses[player][slot] <= 0:
            return False
        
        item_data = self.AVAILABLE_ITEMS[item_id]
        
        # Выбираем поле в зависимости от field_num
        if field_num == 1:
            field = self.buttons
            other_player = 0
        else:
            field = self.buttons2
            other_player = 1
        
        if item_id == "sapper":
            success = self.apply_sapper_item(button, field)
        elif item_id == "sapper_suit":
            success = self.apply_sapper_suit_item(button, player)
        elif item_id == "air_defense":
            success = self.apply_air_defense_item(button, player)
        else:
            success = False
        
        if success:
            self.current_item_uses[player][slot] -= 1
            self.update_item_display()
        
        self.item_mode_active = False
        self.active_item_slot = None
        self.active_item_player = None
        self.reset_item_frames()
        
        return True
    
    def apply_sapper_item(self, button, field):
        """Применение предмета 'Сапер' на поле противника"""
        if button.is_open:
            messagebox.showwarning("Клетка уже открыта", "Эта клетка уже открыта!")
            return False
            
        if button.is_flag:
            messagebox.showwarning("Клетка помечена", "Эта клетка уже помечена флагом!")
            return False
        
        if button.is_mine:
            button.is_flag = True
            button.config(text="🚩", disabledforeground="green", state=tk.DISABLED)
            self.FLAGS += 1
            self.update_labels()
            
            messagebox.showinfo("Сапер нашел мину!", 
                              "Сапер нашел мину на поле противника! Клетка помечена флагом 🚩")
            
            # Проверяем победу
            target_field = self.buttons2 if field is self.buttons else self.buttons
            if self.check_win_multi(target_field):
                winner = 2 if field is self.buttons else 1
                self.multiplayer_win(winner)
        else:
            button.is_open = True
            button.config(relief=tk.SUNKEN, state=tk.DISABLED)
            
            if button.count_bomb:
                colors = {
                    1: "blue", 2: "green", 3: "red", 
                    4: "purple", 5: "maroon", 6: "turquoise",
                    7: "black", 8: "gray"
                }
                button.config(text=str(button.count_bomb), 
                              disabledforeground=colors.get(button.count_bomb, "black"))
                messagebox.showinfo("Сапер проверил клетку", 
                                   f"На поле противника в этой клетке нет мины.\nРядом мин: {button.count_bomb}")
            else:
                button.config(text="")
                messagebox.showinfo("Сапер проверил клетку", 
                                   "На поле противника в этой клетке нет мины.\nРядом мин нет.")
            
            # Открываем соседние пустые клетки
            self.open_cells(button.x, button.y, field)
        
        return True
    
    def apply_sapper_suit_item(self, button, player):
        """Применение предмета 'Костюм сапера' - защищает от одной мины"""
        other_player = 1 if player == 0 else 0
        
        # Проверяем БПЛА противника
        if self.uav_active[other_player] and self.uav_moves_left[other_player] > 0:
            messagebox.showwarning("Костюм сапера уничтожен!", 
                                  f"🚁 Внимание! БПЛА противника засек активацию костюма сапера!\n"
                                  f"Костюм сапера был немедленно уничтожен дроном.")
            
            self.current_item_uses[player][self.active_item_slot] -= 1
            self.update_item_display()
            
            self.item_mode_active = False
            self.active_item_slot = None
            self.active_item_player = None
            self.reset_item_frames()
            
            return True
        else:
            self.sapper_suit_active[player] = True
            self.update_player_display()
            
            messagebox.showinfo("Костюм сапера активирован", 
                               f"Костюм сапера активирован для Игрока {player+1}! "
                               f"Следующая найденная мина будет обезврежена.")
            return True
    
    def apply_air_defense_item(self, button, player):
        """Применение предмета 'ПВО' - активирует защиту"""
        self.air_defense_active[player] = True
        self.air_defense_moves_left[player] = 5
        self.update_player_display()
        
        messagebox.showinfo("ПВО активировано!", 
                           f"Системы ПВО Игрока {player+1} приведены в боевую готовность!\n"
                           f"Защита активна на 5 ходов.")
        return True
    
    def create_widgets(self):
        # Очищаем старые виджеты
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Frame) and widget != self.info_frame:
                widget.destroy()
        
        self.IS_GAME_OVER = False
        self.IS_FIRST_CLICK = True
        self.IS_FIRST_CLICK2 = True  # Сбрасываем флаг для первого клика игрока 2
        self.FLAGS = 0
        self.item_mode_active = False
        self.active_item_slot = None
        self.active_item_player = None
        
        # Сбрасываем все эффекты
        self.sapper_suit_active = [False, False]
        self.uav_active = [False, False]
        self.uav_moves_left = [0, 0]
        self.air_defense_active = [False, False]
        self.air_defense_moves_left = [0, 0]
        self.double_move_active = False
        self.double_move_count = 0
        self.air_invasion_active = False
        self.triple_moves_left = 0
        
        self.player1_score = 0
        self.player2_score = 0
        self.player1_moves = 0
        self.player2_moves = 0
        
        # Убираем блокировку
        self.block_timer_running = False
        
        # Загружаем предметы для каждого игрока
        for player in range(2):
            for slot in range(2):
                self.current_item_uses[player][slot] = self.AVAILABLE_ITEMS[self.selected_items[player][slot]]["uses"]
        
        self.update_labels()
        self.update_item_display()
        self.update_player_display()
        self.reset_item_frames()
        
        if self.game_mode == "single":
            # Одно поле для одиночной игры
            self.main_frame = tk.Frame(self.window)
            self.main_frame.grid(row=1, column=0, columnspan=self.COLUMNS)
            
            self.buttons = []
            for i in range(self.ROW):
                temp = []
                for j in range(self.COLUMNS):
                    btn = MyButton(self.main_frame, x=i, y=j)
                    btn.config(command=lambda button=btn: self.click(button))
                    btn.bind("<Button-3>", self.right_click)
                    btn.grid(row=i, column=j, sticky="nsew")
                    temp.append(btn)
                self.buttons.append(temp)
        else:
            # Два поля для игры на двоих
            self.main_frame = tk.Frame(self.window)
            self.main_frame.grid(row=1, column=0, columnspan=max(self.COLUMNS, 9)*2 + 2, pady=10)
            
            # Поле игрока 1 (слева)
            left_frame = tk.Frame(self.main_frame)
            left_frame.grid(row=0, column=0, padx=10)
            
            player1_label = tk.Label(left_frame, text="Игрок 1", font='calibri 14 bold', fg="blue")
            player1_label.pack()
            
            self.buttons_frame1 = tk.Frame(left_frame)
            self.buttons_frame1.pack()
            
            self.buttons = []
            for i in range(self.ROW):
                temp = []
                for j in range(self.COLUMNS):
                    btn = MyButton(self.buttons_frame1, x=i, y=j)
                    btn.config(command=lambda button=btn: self.click(button))
                    btn.bind("<Button-3>", self.right_click)
                    btn.grid(row=i, column=j, sticky="nsew")
                    temp.append(btn)
                self.buttons.append(temp)
            
            # Разделитель
            separator = tk.Frame(self.main_frame, width=2, bg="black")
            separator.grid(row=0, column=1, sticky="ns", padx=10)
            
            # Поле игрока 2 (справа)
            right_frame = tk.Frame(self.main_frame)
            right_frame.grid(row=0, column=2, padx=10)
            
            player2_label = tk.Label(right_frame, text="Игрок 2", font='calibri 14 bold', fg="red")
            player2_label.pack()
            
            self.buttons_frame2 = tk.Frame(right_frame)
            self.buttons_frame2.pack()
            
            self.buttons2 = []
            for i in range(self.ROW):
                temp = []
                for j in range(self.COLUMNS):
                    btn = MyButton(self.buttons_frame2, x=i, y=j)
                    btn.config(command=lambda button=btn: self.click2(button))
                    btn.bind("<Button-3>", self.right_click2)
                    btn.grid(row=i, column=j, sticky="nsew")
                    temp.append(btn)
                self.buttons2.append(temp)
            
            # Изначально включаем поле текущего игрока
            self.enable_active_field()
    
    def click(self, clicked_button: MyButton):
        """Обработка клика для поля игрока 1"""
        if self.IS_GAME_OVER:
            return
        
        # Проверяем режим предмета
        if self.item_mode_active:
            if self.apply_item(clicked_button, 1):
                self.switch_player()
            return
        
        # Проверяем, что это поле активного игрока
        if self.game_mode == "multi" and self.current_player != 1:
            messagebox.showwarning("Не ваш ход", 
                                  f"Сейчас ходит Игрок {self.current_player}!\nИспользуйте предметы на поле противника.")
            return
            
        if clicked_button.is_open or clicked_button.is_flag:
            return
            
        # Первый клик игрока 1 - генерируем мины для его поля
        if self.IS_FIRST_CLICK:
            self.START_TIME = time.time()
            self.generate_mines(clicked_button)
            self.count_mines_around()
            # Не генерируем мины для игрока 2 здесь - они будут сгенерированы при его первом клике
            self.update_time()
            self.IS_FIRST_CLICK = False
        
        if clicked_button.is_mine:
            player_idx = 0  # Игрок 1
            if self.sapper_suit_active[player_idx]:
                clicked_button.is_mine = False
                clicked_button.is_open = True
                clicked_button.config(relief=tk.SUNKEN, state=tk.DISABLED, text="🛡", bg="lightgreen")
                self.sapper_suit_active[player_idx] = False
                self.update_player_display()
                messagebox.showinfo("Костюм сапера сработал!", "Костюм сапера защитил от мины!")
                
                self.count_mines_around()
                self.open_cells(clicked_button.x, clicked_button.y, self.buttons)
                
                self.player1_score += 1
                self.update_player_display()
                
                # Проверяем победу
                if self.check_win_multi(self.buttons):
                    self.multiplayer_win(1)
                else:
                    self.switch_player()
            else:
                clicked_button.config(text="💣", bg="red", disabledforeground="black")
                self.multiplayer_game_over(1)
            return
        
        self.open_cells(clicked_button.x, clicked_button.y, self.buttons)
        self.player1_score += 1
        self.update_player_display()
        
        # Обновляем активные эффекты
        self.update_active_effects_on_move(0)
        
        if self.check_win_multi(self.buttons):
            self.multiplayer_win(1)
        else:
            self.switch_player()
    
    def click2(self, clicked_button: MyButton):
        """Обработка клика для поля игрока 2"""
        if self.IS_GAME_OVER:
            return
        
        # Проверяем режим предмета
        if self.item_mode_active:
            if self.apply_item(clicked_button, 2):
                self.switch_player()
            return
        
        # Проверяем, что это поле активного игрока
        if self.current_player != 2:
            messagebox.showwarning("Не ваш ход", 
                                  f"Сейчас ходит Игрок {self.current_player}!\nИспользуйте предметы на поле противника.")
            return
            
        if clicked_button.is_open or clicked_button.is_flag:
            return
        
        # Первый клик игрока 2 - генерируем мины для его поля
        if self.IS_FIRST_CLICK2:
            if self.START_TIME is None:
                self.START_TIME = time.time()
                self.update_time()
            
            self.generate_mines2(clicked_button)
            self.count_mines_around2()
            self.IS_FIRST_CLICK2 = False
        
        if clicked_button.is_mine:
            player_idx = 1  # Игрок 2
            if self.sapper_suit_active[player_idx]:
                clicked_button.is_mine = False
                clicked_button.is_open = True
                clicked_button.config(relief=tk.SUNKEN, state=tk.DISABLED, text="🛡", bg="lightgreen")
                self.sapper_suit_active[player_idx] = False
                self.update_player_display()
                messagebox.showinfo("Костюм сапера сработал!", "Костюм сапера защитил от мины!")
                
                self.count_mines_around2()
                self.open_cells(clicked_button.x, clicked_button.y, self.buttons2)
                
                self.player2_score += 1
                self.update_player_display()
                
                # Проверяем победу
                if self.check_win_multi(self.buttons2):
                    self.multiplayer_win(2)
                else:
                    self.switch_player()
            else:
                clicked_button.config(text="💣", bg="red", disabledforeground="black")
                self.multiplayer_game_over(2)
            return
        
        self.open_cells(clicked_button.x, clicked_button.y, self.buttons2)
        self.player2_score += 1
        self.update_player_display()
        
        # Обновляем активные эффекты
        self.update_active_effects_on_move(1)
        
        if self.check_win_multi(self.buttons2):
            self.multiplayer_win(2)
        else:
            self.switch_player()
    
    def update_active_effects_on_move(self, player_idx):
        """Обновляет активные эффекты после хода"""
        other_idx = 1 if player_idx == 0 else 0
        
        # Обновляем БПЛА противника
        if self.uav_active[other_idx]:
            self.uav_moves_left[other_idx] -= 1
            if self.uav_moves_left[other_idx] <= 0:
                self.uav_active[other_idx] = False
        
        # Обновляем ПВО противника
        if self.air_defense_active[other_idx]:
            self.air_defense_moves_left[other_idx] -= 1
            if self.air_defense_moves_left[other_idx] <= 0:
                self.air_defense_active[other_idx] = False
        
        self.update_player_display()
    
    def open_cells(self, x, y, field):
        """Открывает клетки используя алгоритм BFS"""
        queue = deque()
        queue.append((x, y))
        
        while queue:
            cx, cy = queue.popleft()
            button = field[cx][cy]
            
            if button.is_open or button.is_flag or button.is_mine:
                continue
            
            button.is_open = True
            button.config(relief=tk.SUNKEN, state=tk.DISABLED)
            
            if button.count_bomb:
                colors = {
                    1: "blue", 2: "green", 3: "red", 
                    4: "purple", 5: "maroon", 6: "turquoise",
                    7: "black", 8: "gray"
                }
                button.config(text=str(button.count_bomb), 
                              disabledforeground=colors.get(button.count_bomb, "black"))
            else:
                button.config(text="")
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < len(field) and 0 <= ny < len(field[0]):
                            if not field[nx][ny].is_open and not field[nx][ny].is_flag:
                                queue.append((nx, ny))
    
    def right_click(self, event):
        """Правый клик для поля 1"""
        if self.IS_GAME_OVER:
            return
            
        button = event.widget
        if button.is_open:
            return
            
        if not button.is_flag:
            if self.FLAGS < self.MINES:
                button.is_flag = True
                button.config(text="🚩", disabledforeground="red", state=tk.DISABLED)
                self.FLAGS += 1
        else:
            button.is_flag = False
            button.config(text="", state=tk.NORMAL)
            self.FLAGS -= 1
        
        self.update_labels()
    
    def right_click2(self, event):
        """Правый клик для поля 2"""
        if self.IS_GAME_OVER:
            return
            
        button = event.widget
        if button.is_open:
            return
            
        if not button.is_flag:
            if self.FLAGS < self.MINES:
                button.is_flag = True
                button.config(text="🚩", disabledforeground="red", state=tk.DISABLED)
                self.FLAGS += 1
        else:
            button.is_flag = False
            button.config(text="", state=tk.NORMAL)
            self.FLAGS -= 1
        
        self.update_labels()
    
    def generate_mines(self, first_click):
        """Генерация мин для поля 1"""
        mines_count = self.MINES
        mines_positions = []
        
        all_positions = [(i, j) for i in range(self.ROW) for j in range(self.COLUMNS)]
        all_positions.remove((first_click.x, first_click.y))
        
        # Создаем безопасную зону вокруг первой клетки
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = first_click.x + dx, first_click.y + dy
                if (nx, ny) in all_positions:
                    all_positions.remove((nx, ny))
        
        shuffle(all_positions)
        mines_positions = all_positions[:mines_count]
        
        for x, y in mines_positions:
            self.buttons[x][y].is_mine = True
    
    def generate_mines2(self, first_click):
        """Генерация мин для поля 2 - независимая от поля 1"""
        mines_count = self.MINES
        mines_positions = []
        
        all_positions = [(i, j) for i in range(self.ROW) for j in range(self.COLUMNS)]
        all_positions.remove((first_click.x, first_click.y))
        
        # Создаем безопасную зону вокруг первой клетки игрока 2
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = first_click.x + dx, first_click.y + dy
                if (nx, ny) in all_positions:
                    all_positions.remove((nx, ny))
        
        shuffle(all_positions)
        mines_positions = all_positions[:mines_count]
        
        for x, y in mines_positions:
            self.buttons2[x][y].is_mine = True
    
    def count_mines_around(self):
        """Подсчет мин вокруг для поля 1"""
        for i in range(self.ROW):
            for j in range(self.COLUMNS):
                button = self.buttons[i][j]
                if not button.is_mine:
                    count = 0
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = i + dx, j + dy
                            if 0 <= nx < self.ROW and 0 <= ny < self.COLUMNS:
                                if self.buttons[nx][ny].is_mine:
                                    count += 1
                    button.count_bomb = count
    
    def count_mines_around2(self):
        """Подсчет мин вокруг для поля 2"""
        for i in range(self.ROW):
            for j in range(self.COLUMNS):
                button = self.buttons2[i][j]
                if not button.is_mine:
                    count = 0
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = i + dx, j + dy
                            if 0 <= nx < self.ROW and 0 <= ny < self.COLUMNS:
                                if self.buttons2[nx][ny].is_mine:
                                    count += 1
                    button.count_bomb = count
    
    def update_time(self):
        if self.START_TIME and not self.IS_GAME_OVER:
            elapsed = int(time.time() - self.START_TIME)
            self.time_label.config(text=f"Время: {elapsed}")
            self.window.after(1000, self.update_time)
    
    def update_labels(self):
        if hasattr(self, 'mines_label'):
            self.mines_label.config(text=f"Мин: {self.MINES}")
            self.flags_label.config(text=f"Флагов: {self.FLAGS}/{self.MINES}")
    
    def game_over(self):
        self.IS_GAME_OVER = True
        for i in range(self.ROW):
            for j in range(self.COLUMNS):
                btn = self.buttons[i][j]
                if btn.is_mine:
                    if btn.is_flag:
                        btn.config(text="🚩", bg="green")
                    else:
                        btn.config(text="💣", bg="red")
                elif btn.is_flag and not btn.is_mine:
                    btn.config(text="❌", bg="pink")
        
        messagebox.showinfo("Игра окончена", "Вы взорвались!")
    
    def multiplayer_game_over(self, player_num):
        """Окончание игры для мультиплеера"""
        self.IS_GAME_OVER = True
        
        winner = 2 if player_num == 1 else 1
        
        messagebox.showinfo("Игра окончена!", 
                          f"Игрок {player_num} наступил на мину!\n"
                          f"Победитель: Игрок {winner}\n"
                          f"Счет: {self.player1_score}:{self.player2_score}\n"
                          f"Ходы: {self.player1_moves}:{self.player2_moves}")
    
    def game_win(self):
        self.IS_GAME_OVER = True
        elapsed = int(time.time() - self.START_TIME) if self.START_TIME else 0
        
        for i in range(self.ROW):
            for j in range(self.COLUMNS):
                btn = self.buttons[i][j]
                if btn.is_mine and not btn.is_flag:
                    btn.config(text="🚩", disabledforeground="green", state=tk.DISABLED)
                    btn.is_flag = True
        
        messagebox.showinfo("Победа!", f"Вы выиграли за {elapsed} секунд!")
    
    def multiplayer_win(self, player_num):
        """Победа в мультиплеере"""
        self.IS_GAME_OVER = True
        
        winner = player_num
        loser = 2 if player_num == 1 else 1
        
        messagebox.showinfo("Победа!", 
                          f"Игрок {winner} победил!\n"
                          f"Счет: {self.player1_score}:{self.player2_score}\n"
                          f"Ходы: {self.player1_moves}:{self.player2_moves}\n"
                          f"Все мины обезврежены!")
    
    def check_win(self):
        for i in range(self.ROW):
            for j in range(self.COLUMNS):
                btn = self.buttons[i][j]
                if not btn.is_mine and not btn.is_open:
                    return False
        return True
    
    def check_win_multi(self, field):
        """Проверка победы для мультиплеера"""
        for i in range(self.ROW):
            for j in range(self.COLUMNS):
                btn = field[i][j]
                if not btn.is_mine and not btn.is_open:
                    return False
        return True
    
    def set_difficulty(self, rows, columns, mines):
        if not self.IS_GAME_OVER:
            if messagebox.askyesno("Смена сложности", 
                                  f"Вы хотите сменить сложность на {rows}x{columns}, {mines} мин?\nТекущая игра будет перезапущена."):
                self.ROW = rows
                self.COLUMNS = columns
                self.MINES = mines
                self.new_game()
        else:
            self.ROW = rows
            self.COLUMNS = columns
            self.MINES = mines
            self.new_game()
    
    def new_game(self):
        self.create_widgets()
    
    def show_about(self):
        messagebox.showinfo("Об игре", 
                           "Сапер с предметами - Мультиплеер\n\n"
                           "Классическая игра Сапер с дополнительными предметами и поддержкой игры на двоих.\n\n"
                           "Режимы игры:\n"
                           "- Одиночная игра: игра против компьютера с предметами\n"
                           "- Игра на двоих: два игрока сражаются друг с другом\n\n"
                           "Каждый игрок имеет свои собственные предметы!\n\n"
                           "Изменение: Воздушное вторжение теперь дает 3 дополнительных хода игроку, использовавшему предмет!")
    
    def show_rules(self):
        messagebox.showinfo("Правила игры",
                           "1. Цель игры - открыть все клетки на своем поле, не содержащие мин\n"
                           "2. Левый клик - открыть клетку\n"
                           "3. Правый клик - поставить/убрать флаг\n"
                           "4. Число в клетке показывает сколько мин вокруг\n"
                           "5. Если открыть клетку с миной - игра проиграна\n\n"
                           "Режим на двоих:\n"
                           "- Игроки ходят по очереди\n"
                           "- Каждый игрок имеет 2 слота для предметов\n"
                           "- Предметы применяются на поле противника\n"
                           "- Кто первый обезвредит все мины - побеждает\n\n"
                           "Дополнительные предметы:\n"
                           "- Сапер: проверяет клетку на поле противника\n"
                           "- Костюм сапера: защищает от одной мины\n"
                           "- Воздушное вторжение: дает 3 дополнительных хода игроку, использовавшему предмет\n"
                           "- ПВО: защищает от воздушных атак и БПЛА\n"
                           "- БПЛА: отменяет костюм сапера противника\n"
                           "- Двойной ход: дает 2 дополнительных хода")
    
    def show_items_help(self):
        messagebox.showinfo("Управление предметами",
                           "1. Выберите предметы в меню 'Предметы Игрок 1' и 'Предметы Игрок 2'\n"
                           "2. Во время своего хода нажмите кнопку 'Исп.' под нужным предметом\n"
                           "3. Для большинства предметов: выберите клетку на поле противника\n"
                           "4. Для воздушного вторжения: предмет активируется сразу\n\n"
                           "Изменение воздушного вторжения:\n"
                           "- Теперь не блокирует противника, а дает 3 дополнительных хода игроку, использовавшему его\n"
                           "- ПВО может отразить воздушное вторжение\n\n"
                           "Особенности:\n"
                           "- Предметы можно использовать только во время своего хода\n"
                           "- Большинство предметов применяются на поле противника\n"
                           "- Костюм сапера и ПВО защищают ваше собственное поле\n"
                           "- БПЛА и Воздушное вторжение активно влияют на противника")
    
    def start(self):
        self.window.mainloop()

if __name__ == "__main__":
    game = Minesweeper()
    game.start()