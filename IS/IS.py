print("Привет введите цифру необходимой функции \n 1.Библиотека \n 2.Добавить в библиотеку \n 3.Удалить из библиотеке \n 4.Поиск \n 5.Выход")
Menu = input("Сделайте выбор")

library = ["Остров Сокровищ", "Метро", "Питон чайникам"]
while True:
    match Menu:
        case '1':
            print("Выбрана библиотека")
            for i, book in enumerate(library, 1):
                print(f"{i}. {book}")
                break
        case '2':
            print("Выбрано добавить книгу")
            new_book = input("Введите название новой книги: ")
            library.append(new_book)
            print(f"Книга'{new_book}' добавлена")
            break
        case '3':
            print("Выбранно удалить книгу")
            delete_book = str(input("Напишите название книги: "))
            for i in library:
                if (delete_book == i):
                    library.remove(delete_book)
                    print("Книга удалена")
                    break
                else:
                    print("книга не найдена")
                    break
            break
        case '4':
            print("Выбрано поиск книги")

            input
        case '5':
            break

    




