import sqlite3
import pandas as pd
from sympy import sympify
import re

import ast

conn = sqlite3.connect('092024.db')

df = pd.read_sql_query("SELECT * FROM Smeta_15_98_007", conn)

cyrllic_letters = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т',
                   'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ы', 'Э', 'Ю', 'Я']

if len(cyrllic_letters) >= len(df.columns):
    df.columns = cyrllic_letters[:len(df.columns)]
else:
    print("Недостаточно букв кириллицы для всех столбцов!")


def process_formulas(df):
    cells = []
    for row_index, row in df.iterrows():
        for col_index, cell in row.items():
            if isinstance(cell, str) and cell.startswith('='):
                cell = cell[1:]
                cells.append(cell)
    return cells


def check_for_letter_and_digit(expression):
    pattern = r'\b[А-Яа-я]\d+\b'
    matches = re.findall(pattern, expression)
    return matches


def check_for_double_letter_and_digit(expression):
    pattern = r'\b[А-Яа-я]\d+\b:\b[А-Яа-я]\d+\b'
    matches = re.findall(pattern, expression)

    result = []
    for match in matches:
        start, end = match.split(':')
        letter_start = start[0]
        number_start = int(start[1:])
        number_end = int(end[1:])

        # Генерируем все значения от number_start до number_end
        for num in range(number_start, number_end + 1):
            result.append(f'{letter_start}{num}')
    return result

def for_replace_function(expression):
    pattern = r'\b([А-Яа-я])(\d+):\1(\d+)\b'
    matches = re.findall(pattern, expression)

    for match in matches:
        letter = match[0]
        start = int(match[1])
        end = int(match[2])

        # Генерируем список ячеек
        range_cells = [f'{letter}{i}' for i in range(start, end + 1)]

        range_str = ','.join(range_cells)
        expression = expression.replace(f'{letter}{start}:{letter}{end}', range_str)

    return expression



def replace_functions(expression):
    # Замена функций Excel на эквиваленты Python
    expression = re.sub(r'МИН\((.*?)\)', r'min(\1)', expression)
    expression = re.sub(r'МАКС\((.*?)\)', r'max(\1)', expression)
    expression = re.sub(r'СУММ\((.*?)\)', r'sum([\1])', expression)
    expression = re.sub(r'СРЗНАЧ\((.*?)\)', r'(sum([\1]) / len([\1]))', expression)
    modified_expression = for_replace_function(expression)

    # Замена символа степени
    # modified_expression = modified_expression.replace('^', '**')
    return modified_expression



def evaluate_formula(expression, df):
    expression = replace_functions(expression)

    matches1 = check_for_letter_and_digit(expression)
    matches2 = check_for_double_letter_and_digit(expression)
    matches = list(set(matches1 + matches2))

    for match in matches:
        column = match[0]
        row = int(match[1:]) - 1
        value = df[column][row]
        if isinstance(value, str) and value.startswith('='):
            value = evaluate_formula(value[1:], df)
        expression = expression.replace(match, str(value))

    try:
        result = sympify(expression).evalf()
    except Exception as e:
        raise ValueError(f"Ошибка в формуле: {expression}. Причина: {e}")

    return result



print(df.head(10))

for expression in process_formulas(df):
    result = evaluate_formula(expression, df)
    print(expression, '\n', result)
