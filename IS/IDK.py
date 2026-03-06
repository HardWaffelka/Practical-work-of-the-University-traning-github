Sur_name = str
Name = str
salary = int
PayCheck = int
WorkHours = int
WorkShifts = int
PayInfo = int
SurInfo = ["Илле"]
NameInfo = ["Полина"]
PayInfo = [110]
WorkShifts = [5]
WorkHours = [8]

while True:
    Menu = input("Сделайте выбор. \n1. Вывести списки \n2. Ввести фамилию \n3. Ввести имя \n4. Ввести зарплату \n5. Количество часов работы \n6. Количество рабочих дней в неделю \n7. Рассчитать ЗП \n8. Уйти с позором \n")
    match Menu:

        case '1':
            print("Вывод списка сотрудников и ЗП")
                        # Исправленный вывод - один цикл для всех данных
            for i in range(len(SurInfo)):
                print(f"{i+1}. Фамилия: {SurInfo[i]}, Имя: {NameInfo[i]}, "
                                f"ЗП в час: {PayInfo[i]}, Часов в день: {WorkHours[i]}, "
                                f"Дней в неделю: {WorkShifts[i]}")

        case '2':
            Sur_name = input("Введите Фамилию")
            SurInfo.append(Sur_name)
            print('Фамилия добавлена')

        case '3':
            Name = input("Имя")
            NameInfo.append(Name)
            print('Имя добавлена')

        case '4':
            Salary = int(input("Введите зарплату в час"))
            PayInfo.append(Salary)
            print('Зарплата добавлена')

        case '5':
            WorkHour = int(input("Сколько часов работает в день"))
            WorkHours.append(WorkHour)

        case '6':
            WorkShift = int(input("Сколько рабочих дней в неделю"))
            WorkShifts.append(WorkShift)

        case '7':
            if len(PayInfo) == len(WorkHours) == len(WorkShifts):
                print("Расчет зарплаты за месяц:")
                for i in range(len(PayInfo)):
                    PayCheck = WorkHours[i] * PayInfo[i] * WorkShifts[i] * 4 
                    print(PayCheck)

        case '8':
            break

        