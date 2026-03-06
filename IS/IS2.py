print("Привет введите цифру необходимой функции")
result = str
result = " "
flag = int
flag = 1
library = ["Остров Сокровищ", "Метро", "Питон чайникам"]
while (flag == 1):
    print (" 1.Библиотека", "\n 2.Добавить в библиотеку", "\n 3.Удалить из библиотеке" "\n 4.Поиск", "\n 5.Выход")
    Menu = input("Сделайте выбор")
    match Menu:
        case '1':
            print("Выбрана библиотека")
            for i, book in enumerate(library, 1):
                print(f"{i}. {book}")                
        case '2':
            print("Выбрано добавить книгу")
            new_book = input("Введите название новой книги: ")
            library.append(new_book)
            print(f"Книга'{new_book}' добавлена")
        case '3':
            print("Выбранно удалить книгу")
            delete_book = str(input("Напишите название книги: "))
            for i in library:
                if (delete_book == i):
                    library.remove(delete_book)
                    print("Книга удалена")
                else:
                    print("книга не найдена")
        case '4':
            search_book = str(input("Напишите название книги: "))
            for i in library:
                result = search_book in library 
                print(f"123123 '{result}'") 
                if (result != " "):              
                    print(f"найдена книга '{result}'")
                else:
                    print("книга не найдена")
        case '5':
            flag = 0
            

    
