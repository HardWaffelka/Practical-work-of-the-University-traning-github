# -*- coding: utf-8 -*-

class Role:
    """Класс для роли пользователя (Админ/Обычный пользователь)"""
    def __init__(self):
        self.isAdmin = False

    def becomeAdmin(self):
        self.isAdmin = True

    def becomeUser(self):
        self.isAdmin = False


class BookInfo:
    """Класс, хранящий информацию о книге (по аналогии с C#)"""
    def __init__(self, title, author, genre, year, pages):
        self.title = title
        self.author = author
        self.genre = genre
        self.year = year
        self.pages = pages

    def __str__(self):
        """Для удобного вывода информации о книге"""
        return f"{self.author}, {self.genre}, {self.year}, {self.pages} стр."


class LocalLibrary:
    """Класс, представляющий библиотеку"""
    def __init__(self):
        # В Python в качестве ключа словаря может быть строка, поэтому используем его
        self.booksInLibrary = {}  # Словарь: ключ - название (str), значение - объект BookInfo

    def GetAllBooks(self):
        """Возвращает весь словарь книг"""
        return self.booksInLibrary

    def DisplayAllBooks(self):
        """Отображает все книги в библиотеке"""
        if not self.booksInLibrary:
            print("Библиотека пуста.")
            return

        print("Список книг в библиотеке:")
        for title, info in self.booksInLibrary.items():
            print(
                f"Название: {info.title}, "
                f"Автор: {info.author}, "
                f"Жанр: {info.genre}, "
                f"Год: {info.year}, "
                f"Страниц: {info.pages}"
            )

    def AddBook(self):
        """Добавляет новую книгу в библиотеку"""
        print("Введите название книги:")
        title = input().strip()

        # Проверка на пустой ввод (можно добавить по желанию)
        if not title:
            print("Название не может быть пустым.")
            return

        # Проверяем, есть ли уже такая книга
        if title in self.booksInLibrary:
            print("Такая книга уже есть в библиотеке.")
            return

        print("Введите автора книги:")
        author = input().strip()

        print("Введите жанр книги:")
        genre = input().strip()

        try:
            print("Введите год книги:")
            year = int(input().strip())

            print("Введите количество страниц:")
            pages = int(input().strip())
        except ValueError:
            print("Ошибка: Год и количество страниц должны быть числами.")
            return

        # Создаем объект книги и добавляем в словарь
        new_book = BookInfo(title, author, genre, year, pages)
        self.booksInLibrary[title] = new_book
        print(f"Книга \"{title}\" добавлена в библиотеку.")

    def DeleteBook(self):
        """Удаляет книгу из библиотеки по названию"""
        print("Введите название книги для удаления:")
        bookToDelete = input().strip()

        if bookToDelete in self.booksInLibrary:
            del self.booksInLibrary[bookToDelete]
            print(f"Книга \"{bookToDelete}\" удалена из библиотеки.")
        else:
            print(f"Книга \"{bookToDelete}\" не найдена.")

    def SearchBook(self):
        """Ищет книги по части названия"""
        print("Введите название или часть названия для поиска:")
        query = input().strip().lower()  # Приводим к нижнему регистру для поиска без учета регистра
        found = False

        for title, info in self.booksInLibrary.items():
            if query in title.lower():  # Сравниваем в нижнем регистре
                print(f"Найдена книга: \"{info.title}\" Автор: {info.author}, {info.genre}, {info.year}")
                found = True

        if not found:
            print("Книги по вашему запросу не найдены.")


# --- Основная программа ---
if __name__ == "__main__":
    # Настройка вывода для русского языка в консоль (обычно в Python 3 это работает по умолчанию)
    print("Добро пожаловать в библиотеку!")

    library = LocalLibrary()
    # Для примера добавим пару книг, чтобы было с чем работать
    library.booksInLibrary["Война и мир"] = BookInfo("Война и мир", "Лев Толстой", "Роман", 1869, 1300)
    library.booksInLibrary["Преступление и наказание"] = BookInfo("Преступление и наказание", "Фёдор Достоевский", "Роман", 1866, 400)


    admin = Role()
    admin.isAdmin = False  # По умолчанию пользователь

    while True:
        print("\nВведите, что вам нужно.")
        print("\n[show] - просмотреть список книг")
        print("[role] - выбрать роль")
        print("[add] - добавить книгу")
        print("[delete] - удалить книгу")
        print("[search] - поиск книги")
        print("[exit] - выход\n")

        user_input = input().strip().lower()

        if user_input == "exit":
            print("Выход из программы.")
            break

        elif user_input == "role":
            print("\nНажмите 1 - админ, 2 - пользователь, back - назад\n")
            while True:
                role_choice = input().strip().lower()
                if role_choice == "1":
                    admin.isAdmin = True
                    print("Вы теперь админ!")
                    break
                elif role_choice == "2":
                    admin.isAdmin = False
                    print("Вы теперь пользователь!")
                    break
                elif role_choice == "back":
                    print("Назад.")
                    break
                else:
                    print("Неверный ввод. Попробуйте снова (1, 2, back).")

        elif user_input == "show":
            library.DisplayAllBooks()

        elif user_input == "add":
            if admin.isAdmin:
                library.AddBook()
            else:
                print("Нужно быть админом!!!")

        elif user_input == "delete":
            if admin.isAdmin:
                library.DeleteBook()
            else:
                print("Нужно быть админом!!!")

        elif user_input == "search":
            library.SearchBook()

        else:
            print("Неизвестная команда. Пожалуйста, введите одну из предложенных.")