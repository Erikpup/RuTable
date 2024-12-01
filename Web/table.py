import pandas as pd
import re
from sympy import sympify
from sympy.logic.boolalg import BooleanFalse,BooleanTrue

# Извлекает формулы из DataFrame, начиная с '='.
def process_formulas(df):
    formulas = []
    for row_index, row in df.iterrows():
        for col_index, cell in row.items():
            if isinstance(cell, str) and cell.startswith('='):
                formulas.append((row_index, col_index, cell[1:]))  # Убираем '='
    return formulas

# Проверка одиночных ячеек
def check_formula(formula, data):
    df = create_df(data)
    #print(df.head())
    formula = formula[1:]
    return evaluate_formula(formula, df)

# Посмотреть содержимое ячейки
def look_in_cell(cell, data):
    df = create_df(data)
    col = cell[0]
    row = int(cell[1:]) - 1
    return df[col][row]

# Находит ссылки на ячейки формата БукваЦифра (например, А1).
def check_for_letter_and_digit(expression):
    pattern = r'\b[А-Яа-я]\d+\b'
    return re.findall(pattern, expression)

# Находит диапазоны вида БукваЦифра:БукваЦифра (например, В3:В5) и заменяет их на список ячеек (например, В3,В4,В5).
def for_replace_function(expression):
    pattern = r'\b([А-Яа-я])(\d+):([А-Яа-я])(\d+)\b'
    matches = re.findall(pattern, expression)
    for match in matches:
        letter1 = match[0]
        letter2 = match[2]
        start = int(match[1])
        end = int(match[3])

        # Генерация всех букв от letter1 до letter2
        letter_range = [chr(i) for i in range(ord(letter1), ord(letter2) + 1)]

        # Генерация списка ячеек для каждой буквы
        range_cells = []
        for letter in letter_range:
            range_cells.extend([f'{letter}{i}' for i in range(start, end + 1)])

        # Заменяем диапазон на список
        range_str = ','.join(range_cells)
        expression = expression.replace(f'{letter1}{start}:{letter2}{end}', range_str)

    return expression

# Создание датафрейма из списка
def create_df(data):
    # Делаем датафрейм из списка
    processed_data = [(row)[1:] for row in data]
    df = pd.DataFrame(processed_data)

    # Список букв кириллицы
    cyrllic_letters = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С',
                       'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ы', 'Э', 'Ю', 'Я']

    # Замена названий столбцов на буквы
    if len(cyrllic_letters) >= len(df.columns):
        df.columns = cyrllic_letters[:len(df.columns)]
    else:
        print("Недостаточно букв кириллицы для всех столбцов!")

    return df

# Вывод результата, в соответствии с типом данных
def output_solution(expression):
    # Определяем тип данных и если он логический, то возвращаем результат
    try:
        if isinstance(sympify(expression), BooleanFalse) or isinstance(sympify(expression), bool) or isinstance(sympify(expression), BooleanTrue):
            if sympify(expression) == True:
                return 'ПРАВДА'
            else:
                return 'ЛОЖЬ'
        # Вычисляем итоговое значение
        result = float(sympify(expression).evalf())
        if result.is_integer():
            result = int(result)
    except Exception:
        return ("Ошибка в формуле")
    return result

# Заменяет функции Excel на эквиваленты Python.
def replace_functions(expression):
    expression = re.sub(r'МИН\((.*?)\)', r'min(\1)', expression)
    expression = re.sub(r'МАКС\((.*?)\)', r'max(\1)', expression)
    expression = re.sub(r'СУММ\((.*?)\)', r'sum([\1])', expression)
    expression = re.sub(r'СРЗНАЧ\((.*?)\)', r'(sum([\1]) / len([\1]))', expression)
    return for_replace_function(expression)


# Вычисление условия ЕСЛИ
def condition_if(cond, df):
    cond = ((re.sub(r'ЕСЛИ\((.*?)\)', r'\1', cond)).split(';'))
    result = evaluate_formula(cond[0], df)
    if result == 'ПРАВДА':
        return cond[1]
    elif result == 'ЛОЖЬ':
        return cond[2]
    else:
        return ("Ошибка в формуле")


# Вычисляет значение формулы, подставляя данные из DataFrame.
def evaluate_formula(expression, df):
    expression = replace_functions(expression)

    if expression.startswith('ЕСЛИ'):
        return condition_if(expression, df)
    # Находим ссылки на ячейки и заменяем их значениями
    matches = check_for_letter_and_digit(expression)

    for match in matches:
        column = match[0]
        row = int(match[1:]) - 1  # Преобразуем индекс в нулевую базу
        try:
            value = df[column][row]


        # Рекурсивно обрабатываем вложенные формулы
            if isinstance(value, str) and value.startswith('='):
                value = evaluate_formula(value[1:], df)
            else:
                value = value.replace(" ", '')

            expression = expression.replace(match, str(value))
        except Exception:
            return ("Ошибка в формуле")

    result = str(output_solution(expression))
    return result


# Основная функция обработки DataFrame.
# Вычисляет значения всех формул в таблице и заменяет формулы на их результат.
# Внутри изменяет названия столбцов на буквы, но возвращает DataFrame с исходными названиями столбцов.
def get_table(data: list) -> list:
    df = create_df(data)
    # Получаем все формулы
    formulas = process_formulas(df)

    # Вычисляем каждую формулу
    for row_index, col_index, expression in formulas:
        result = evaluate_formula(expression, df)
        df.at[row_index, col_index] = result # Заменяем формулу на результат
    result = df.values.tolist()

    return result
