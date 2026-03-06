import ast

transitions = {
    'q0': {'if': 'q1'},
    'q1': {'(': 'q2'},
    'q2': {},
    'q3': {')': 'q4'},
    'q4': {':': 'q5'},
    'q5': {},
    'q6': {'elif': 'q1', 'else': 'q7'}, 
    'q7': {':': 'q8'},
    'q8': {},
    'q9': {} 
}

accepting_state = 'q9'

def check_conditional(input_string):
    current_state = 'q0'
    tokens = input_string.split()
    forbidden_tokens = {'if', 'elif', 'else', ':', '(', ')'}
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        
        if current_state == 'q1':

            if token == '(':
                current_state = 'q2'
                print(f"Токен '{token}' -> состояние {current_state}")
            elif token not in forbidden_tokens:
                current_state = 'q4' 
                print(f"Токен '{token}' состояние {current_state}")
            else:
                print(f"Ошибка на токене '{token}' (позиция {i+1})")
                return False
        
        elif current_state == 'q2':

            if token not in forbidden_tokens:
                current_state = 'q3'
                print(f"Токен '{token}' состояние {current_state}")
            else:
                print(f"Ошибка на токене '{token}' (позиция {i+1})")
                return False
        
        elif current_state == 'q5':
            if token not in forbidden_tokens:
                current_state = 'q6'
                print(f"Токен '{token}' состояние {current_state}")
            else:
                print(f"Ошибка на токене '{token}' (позиция {i+1})")
                return False
        
        elif current_state == 'q8':
            if token not in forbidden_tokens:
                current_state = 'q9'
                print(f"Токен '{token}' состояние {current_state}")
            else:
                print(f"Ошибка на токене '{token}' (позиция {i+1})")
                return False
        
        else:
            if token not in transitions.get(current_state, {}):
                print(f"Ошибка на токене '{token}' (позиция {i+1}): нет перехода из состояния {current_state}")
                return False
            current_state = transitions[current_state][token]
            print(f"Токен '{token}' -> состояние {current_state}")
        
        i += 1
    
    if current_state != accepting_state:
        print(f"Ошибка: строка неполная, остановка в состоянии {current_state} (ожидается {accepting_state})")
        return False
    
    return True

try:
    with open('2.txt', 'r') as file:
        code = file.read()
        if check_conditional(code):
            print("Правильно")
        else:
            print("Неправильно")
except FileNotFoundError:
    print("Файл 2.txt не найден")