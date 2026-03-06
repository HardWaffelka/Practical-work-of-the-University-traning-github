import time

time_stop = 30 
while True:
    t = time.time()

    while True:
        Login = input("Введите логин на английском.\n")
        if time.time() - t > time_stop: 
            
            match Login:
                case 'Valera':
                        Try = 3
                        for i in range(Try):
                            Password = input(f"Введите пароль, для юзера Валеры\n(Попытка {i+1}) Всего 3 попытки")    
                            if Password == '123':
                                print("succes in")
                            else:
                                print("Nepravilno poprobuy isho raz")

                case 'Nikita':
                        Try = 3
                        for i in range(Try):
                            Password = input(f"Введите пароль, для юзера Валеры\n(Попытка {i+1}) Всего 3 попытки")               
                            if Password == 'QWERTY':
                                print("succes in")
                            else:
                                print("Nepravilno poprobuy isho raz")   


                case 'Eva':
                        Try = 3
                        for i in range(Try):
                            Password = input(f"Введите пароль, для юзера Валеры\n(Попытка {i+1}) Всего 3 попытки")   
                            if Password == 'password':
                                print("succes in")
                            else:
                                print("Nepravilno poprobuy isho raz")

                case 'exit':
                    break

                case _:
                    print("User not found")
        else:
             break

