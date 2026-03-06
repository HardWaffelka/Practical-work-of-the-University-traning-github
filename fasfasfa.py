import re

def simple_clean_text(text):
    text = re.sub(r'\s+', ' ', text)  #пробелы
    text = re.sub(r'\.{3,}', '…', text)  #Многоточие
    text = re.sub(r'([.,])\1+', r'\1', text)  #точки запятые
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)  #Пробелы перед знаками
    text = re.sub(r'([.,!?;:])(?=\w)', r'\1 ', text)  #Пробелы после знаков
    return text.strip()

if __name__ == "__main__":
    input_file = "text.txt"
    output_file = "Текст.txt"
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            original_text = f.read()
        
        cleaned_text = simple_clean_text(original_text)
        

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        
        print("Файл успешно обработан!")
        print(f"Создан очищенный файл: {output_file}")
        
    except FileNotFoundError:
        print(f"Файл '{input_file}' не найден!")
        print("Создайте файл 'text.txt' с текстом для очистки")
    except Exception as e:
        print(f"Ошибка: {e}")