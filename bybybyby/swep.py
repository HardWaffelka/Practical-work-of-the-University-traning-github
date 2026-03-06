import tkinter as tk
from random import shuffle

class mybutton(tk.Button):

    def __init__(self, master, x, y, number, *args, **kwargs):
        super(mybutton, self).__init__(master, width=5, font= 'calibri 15 bold', *args, **kwargs)
        self.x = x
        self.y = y
        self.number = number
        self.mine = False

    def __repr__(self):
        return f'mybutton {self.x} {self.y} {self.number}'

class minesweeper:

    windows = tk.Tk()
    row = 9
    column = 9
    mines = 10

    def __init__(self):
        self.buttons = []
        count = 1
        for i in range(minesweeper.row):

            temp = []

            for j in range(minesweeper.column):
                btn = mybutton(minesweeper.windows, x=i, y=j, number=count)
                btn.config(command=lambda button=btn: self.click(button))
                temp.append(btn)
                count += 1
            self.buttons.append(temp)

        self.insert_mines()

    def click(self, clickedBUT:mybutton):
        print(clickedBUT)
        if clickedBUT.mine:
            clickedBUT.config(text="*", bg='red')
            print("explosion")
        else:
            clickedBUT.config(text=clickedBUT.number)

    def create_widgets(self):
        for i in range(minesweeper.row):
            for j in range(minesweeper.column):
                btn = self.buttons[i][j]
                btn.grid(row=i, column=j)

    def start(self):
        self.create_widgets()
        print(self.place_mine())
        minesweeper.windows.mainloop()

    @staticmethod
    def place_mine():
        indexses = list(range(1, minesweeper.column * minesweeper.row + 1))
        shuffle(indexses)
        return indexses[:minesweeper.mines]
    
    def insert_mines(self):
        index_mines = self.place_mine()
        for row_btn in self.buttons:
            for btn in row_btn:
                if btn.number in index_mines:
                    btn.mine = True


game = minesweeper()
game.start()




