# coding=utf-8
"""
Лабораторная работа №2
Вариант 9: Линейный конгруэнтный генератор, Аддитивный генератор, RSA
Выполнил: Валиуллов Р.Р., группа ИВТИИбд-31
"""

from random import randint, choice
from math import sqrt
from math import gcd
import tkinter as tk
from tkinter import filedialog, ttk
import re

filename = 'support/sequence.txt'

# константы для GUI
width = 60
font = ("Arial", 11)
small_font = ("Arial", 9)
white = '#eee'
grey = '#444'
dark_grey = '#333'
pad_10 = 10
pad_5 = 5


def log_message(message):
    """Добавление сообщения в лог"""
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)
    root.update()


def vipe():
    """Очистка сообщений о результатах на экране"""
    test1['text'] = ''
    test2['text'] = ''
    test3['text'] = ''
    gen['text'] = ''
    load['text'] = ''


def generator():
    """Генерация последовательности заданной длины выбранным генератором"""
    vipe()

    if not gen_entry.get().isdigit():
        gen['text'] = 'Ошибка генерации: длина должна быть целым числом'
        gen['foreground'] = 'red'
        return

    len_e = int(gen_entry.get())

    if len_e == 0:
        gen['text'] = 'Ошибка генерации: длина должна быть больше 0'
        gen['foreground'] = 'red'
        return

    gen_type = combo.get()

    # Выбор генератора согласно варианту 9
    if gen_type == gens[0]:  # Линейный конгруэнтный генератор
        sequence = linear_congruential_generator(len_e)
    elif gen_type == gens[1]:  # Аддитивный генератор
        sequence = additive_generator(len_e)
    elif gen_type == gens[2]:  # RSA генератор
        sequence = rsa_generator(len_e)
    else:
        gen['text'] = 'Ошибка генерации: неизвестный тип генератора'
        gen['foreground'] = 'red'
        return

    # Сохранение последовательности в файл
    with open(filename, 'w') as f:
        for bit in sequence:
            f.write(str(bit) + ' ')

    gen['text'] = f'Последовательность длиной {len_e} бит сгенерирована и сохранена'
    gen['foreground'] = 'green'


def take_sequence():
    """Чтение последовательности из файла"""
    try:
        with open(filename, 'r') as f:
            content = f.readline()
            if not content.strip():
                return []
            sequence = list(map(int, content.split()))
        return sequence
    except (FileNotFoundError, ValueError):
        return []


def print_sequence():
    """Вывод последовательности в отдельном окне"""
    window = tk.Toplevel()
    window.title("Последовательность")
    window.geometry("1120x600")

    try:
        with open(filename, 'r') as f:
            content = f.readline()
    except FileNotFoundError:
        content = ""

    if not content:
        content = "Последовательность не сгенерирована"

    text = ''
    param = 180
    for i in range(len(content) // (param * 2) + 1):
        text += content[i * param * 2:(i + 1) * param * 2] + '\n'

    sequence_label = tk.Label(window, text=text, font=("Arial", 6),
                              background='white', pady=pad_10, width=1000, height=1000)
    sequence_label.pack()


def open_sequence():
    """Загрузка последовательности из выбранного пользователем файла"""
    vipe()
    filepath = filedialog.askopenfilename()

    if filepath == "":
        load['text'] = 'Ошибка загрузки: файл не выбран'
        load['foreground'] = 'red'
        return

    try:
        with open(filepath, 'r') as f:
            text = f.readline()

        numbers = text.split()
        if not numbers:
            load['text'] = 'Ошибка загрузки: файл пуст'
            load['foreground'] = 'red'
            return

        with open(filename, 'w') as f:
            f.write(text)

        load['text'] = 'Последовательность успешно загружена'
        load['foreground'] = 'green'
    except Exception as e:
        load['text'] = f'Ошибка загрузки: {str(e)}'
        load['foreground'] = 'red'


def is_passing(test, result):
    """Проверка прохождения теста (критическое значение 1.82138636 для уровня значимости 0.05)"""
    if result < 1.82138636:
        test['text'] = 'Тест успешно пройден'
        test['foreground'] = 'green'
        return True
    else:
        test['text'] = 'Тест не пройден'
        test['foreground'] = 'red'
        return False


def frequency_test():
    """Частотный тест (Frequency test)"""
    log_message("=== Частотный тест ===")
    eps = take_sequence()
    n = len(eps)

    if n == 0:
        test1['text'] = 'Ошибка: последовательность пуста'
        test1['foreground'] = 'red'
        log_message("Ошибка: последовательность пуста")
        return

    ones = sum(eps)
    zeros = n - ones
    log_message(f"Длина последовательности n = {n}")
    log_message(f"Количество единиц = {ones}, количество нулей = {zeros}")

    # Преобразование 0/1 в -1/1
    x = [2 * bit - 1 for bit in eps]
    sm = sum(x)
    s = abs(sm) / sqrt(n)

    log_message(f"Сумма последовательности из -1 и 1: S = {sm}")
    log_message(f"Наблюдаемое значение статистики: S_n = {s:.6f}")
    log_message(f"Критическое значение: 1.82138636")

    passed = is_passing(test1, s)
    if passed:
        log_message("Результат: тест пройден")
    else:
        log_message("Результат: тест не пройден")
    log_message("")


def identical_sequence_test():
    """Тест на последовательность одинаковых бит (Test for identical bits)"""
    log_message("=== Тест на последовательность одинаковых бит ===")
    eps = take_sequence()
    n = len(eps)

    if n == 0:
        test2['text'] = 'Ошибка: последовательность пуста'
        test2['foreground'] = 'red'
        log_message("Ошибка: последовательность пуста")
        return

    pi = sum(eps) / n
    log_message(f"Длина последовательности n = {n}")
    log_message(f"Частота единиц pi = {pi:.6f}")

    # Подсчет количества смен бит
    r = 0
    for k in range(n - 1):
        if eps[k] != eps[k + 1]:
            r += 1

    v = 1 + r
    log_message(f"Количество смен бит r = {r}")
    log_message(f"Значение V_n = {v}")

    denominator = 2 * sqrt(2 * n) * pi * (1 - pi)

    if denominator == 0:
        test2['text'] = 'Тест не пройден: последовательность состоит из одинаковых бит'
        test2['foreground'] = 'red'
        log_message("Ошибка: последовательность состоит из одинаковых бит")
        log_message("")
        return

    s = abs(v - 2 * n * pi * (1 - pi)) / denominator
    log_message(f"Числитель: |V_n - 2*n*pi*(1-pi)| = {abs(v - 2 * n * pi * (1 - pi)):.6f}")
    log_message(f"Знаменатель: 2*sqrt(2*n)*pi*(1-pi) = {denominator:.6f}")
    log_message(f"Наблюдаемое значение статистики: S_n = {s:.6f}")
    log_message(f"Критическое значение: 1.82138636")

    passed = is_passing(test2, s)
    if passed:
        log_message("Результат: тест пройден")
    else:
        log_message("Результат: тест не пройден")
    log_message("")


def random_deviation_test():
    """Расширенный тест на произвольные отклонения (Random deviation test)"""
    log_message("=== Расширенный тест на произвольные отклонения ===")
    eps = take_sequence()
    n = len(eps)

    if n == 0:
        test3['text'] = 'Ошибка: последовательность пуста'
        test3['foreground'] = 'red'
        log_message("Ошибка: последовательность пуста")
        return

    log_message(f"Длина последовательности n = {n}")

    # Преобразование в последовательность -1 и 1
    x = [2 * bit - 1 for bit in eps]

    # Частичные суммы
    s = [0] * n
    for i in range(n):
        s[i] = s[i - 1] + x[i]

    s_prime = [0] + s + [0]
    L = s_prime.count(0) - 1

    log_message(f"Количество нулей в S': {s_prime.count(0)}")
    log_message(f"Значение L = {L}")

    if L == 0:
        test3['text'] = 'Тест не пройден: недостаточно нулей в последовательности'
        test3['foreground'] = 'red'
        log_message("Ошибка: недостаточно нулей в последовательности")
        log_message("")
        return

    # Подсчет вхождений для каждого состояния от -9 до 9 (кроме 0)
    log_message("Состояния и их наблюдаемые значения:")
    y_values = []
    for state in range(-9, 10):
        if state == 0:
            continue
        count = s_prime.count(state)
        if count == 0:
            y = 0
        else:
            y = abs(count - L) / sqrt(2 * L * (4 * abs(state) - 2))
        y_values.append(y)
        if count > 0:
            log_message(f"  Состояние {state:2d}: частота = {count:3d}, статистика Y = {y:.6f}")

    max_y = max(y_values) if y_values else 0
    log_message(f"Максимальное значение статистики: max(Y) = {max_y:.6f}")
    log_message(f"Критическое значение: 1.82138636")

    passed = is_passing(test3, max_y)
    if passed:
        log_message("Результат: тест пройден")
    else:
        log_message("Результат: тест не пройден")
    log_message("")


def clear_log():
    """Очистка панели логов"""
    log_text.delete(1.0, tk.END)


def is_valid(value):
    """Валидация ввода: только цифры, максимум 5 символов"""
    return re.match(r"^\d{0,5}$", value) is not None


# ==================== ГЕНЕРАТОРЫ ПСЕВДОСЛУЧАЙНЫХ ЧИСЕЛ ====================

def linear_congruential_generator(n):
    """
    Линейный конгруэнтный генератор (ЛКГ)
    Формула: X_{i+1} = (a * X_i + c) mod m
    """
    if n <= 0:
        return []

    a = 1103515245
    c = 12345
    m = 2 ** 31

    x = randint(1, m - 1)

    sequence = []
    bits_generated = 0

    while bits_generated < n:
        x = (a * x + c) % m
        temp = x

        while temp > 1 and bits_generated < n:
            sequence.append(temp & 1)
            bits_generated += 1
            temp >>= 1

        if bits_generated < n:
            sequence.append(temp & 1)
            bits_generated += 1

    return sequence[:n]


def additive_generator(n):
    """
    Аддитивный генератор (запаздывающий генератор Фибоначчи)
    Формула: X_i = (X_{i-55} + X_{i-24}) mod 2^32
    """
    if n <= 0:
        return []

    m = 2 ** 32
    j = 55
    k = 24

    state = [randint(0, m - 1) for _ in range(j)]

    sequence = []
    idx = 0
    bits_generated = 0

    while bits_generated < n:
        new_value = (state[idx] + state[(idx + j - k) % j]) % m
        state[idx] = new_value
        idx = (idx + 1) % j

        temp = new_value
        while temp > 1 and bits_generated < n:
            sequence.append(temp & 1)
            bits_generated += 1
            temp >>= 1

        if bits_generated < n:
            sequence.append(temp & 1)
            bits_generated += 1

    return sequence[:n]


def rsa_generator(n):
    """
    RSA генератор псевдослучайных чисел (алгоритм BBS - Blum Blum Shub)
    X_{i+1} = X_i^2 mod N, где N = p * q, p и q - простые числа вида 4k+3
    """
    if n <= 0:
        return []

    blum_primes = [
        11, 19, 23, 31, 43, 47, 59, 67, 71, 79, 83, 103, 107, 127, 131, 139,
        151, 163, 167, 179, 191, 199, 211, 223, 227, 239, 251, 263, 271, 283,
        307, 311, 331, 347, 359, 367, 379, 383, 419, 431, 439, 443, 463, 467,
        479, 487, 491, 499, 503, 523, 547, 563, 571, 587, 599, 607, 619, 631,
        643, 647, 659, 683, 691, 719, 727, 739, 743, 751, 787, 811, 823, 827,
        839, 859, 863, 883, 887, 907, 911, 919, 947, 967, 971, 983, 991, 1019
    ]

    p = choice(blum_primes)
    q = choice(blum_primes)
    while p == q:
        q = choice(blum_primes)

    N = p * q

    s = randint(2, N - 2)
    while gcd(s, N) != 1:
        s = randint(2, N - 2)

    x = (s * s) % N

    sequence = []

    for _ in range(n):
        x = (x * x) % N
        sequence.append(x & 1)

    return sequence


# ==================== СОЗДАНИЕ ГРАФИЧЕСКОГО ИНТЕРФЕЙСА ====================

root = tk.Tk()
root.title("Лабораторная работа №2 (Вариант 9) - Валиуллов Р.Р., ИВТИИбд-31")
root.geometry("900x850")
root.resizable(False, False)
root.configure(bg=white)

# Создание основной панели с двумя колонками
main_frame = tk.Frame(root, bg=white)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Левая панель (управление)
left_panel = tk.Frame(main_frame, bg=white, width=600)
left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Правая панель (логи)
right_panel = tk.Frame(main_frame, bg=white, width=280)
right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# ==================== ЛЕВАЯ ПАНЕЛЬ (УПРАВЛЕНИЕ) ====================

# Интерфейс для генерации последовательности
tk.Label(left_panel, text='', font=("Arial", 1), background=white).pack()
tk.Label(left_panel, text='Введите желаемую длину последовательности (в битах):',
         font=font, background=white, pady=pad_10, width=width, anchor='w').pack()

check = (root.register(is_valid), "%P")
gen_entry = tk.Entry(left_panel, font=font, validate="key", validatecommand=check, width=15, justify='center')
gen_entry.pack()
gen_entry.insert(0, "100")

tk.Label(left_panel, text='Выберите генератор последовательности:',
         font=font, background=white, pady=pad_10, width=width, anchor='w').pack()

gens = ('Линейный конгруэнтный генератор', 'Аддитивный генератор', 'RSA генератор (BBS)')
combo = ttk.Combobox(left_panel, values=gens, width=35, font=font)
combo.current(0)
combo.pack()

tk.Label(left_panel, text='', font=font, background=white).pack()
tk.Button(left_panel, text="Сгенерировать последовательность",
          background=grey, foreground='white', pady=pad_5, padx=pad_10, font=font, command=generator).pack()

gen = tk.Label(left_panel, text='', font=font, background=white, pady=pad_10, width=width)
gen.pack()

# Интерфейс для загрузки последовательности
tk.Label(left_panel, text='Или загрузите последовательность из текстового файла',
         font=font, background=white, pady=pad_10, width=width, anchor='w').pack()
tk.Button(left_panel, text="Загрузить последовательность",
          background=grey, foreground='white', pady=pad_5, padx=pad_10, font=font, command=open_sequence).pack()

load = tk.Label(left_panel, text='', font=font, background=white, pady=pad_10, width=width)
load.pack()

# Разделительная линия
separator = tk.Label(left_panel, text='─────────────────────────────────────────────────────────────',
                     font=font, background=white, pady=pad_5)
separator.pack()

# Интерфейс для частотного теста
tk.Label(left_panel, text='1. Частотный тест (Frequency Test)',
         font=font, background=white, pady=pad_10, width=width, anchor='w').pack()
tk.Button(left_panel, text="Выполнить тест",
          background=grey, foreground='white', pady=pad_5, padx=pad_10, font=font, command=frequency_test).pack()

test1 = tk.Label(left_panel, text='', font=font, background=white, pady=pad_10, width=width)
test1.pack()

# Интерфейс для теста на последовательность одинаковых бит
tk.Label(left_panel, text='2. Тест на последовательность одинаковых бит (Identical Bits Test)',
         font=font, background=white, pady=pad_10, width=width, anchor='w').pack()
tk.Button(left_panel, text="Выполнить тест",
          background=grey, foreground='white', pady=pad_5, padx=pad_10, font=font,
          command=identical_sequence_test).pack()

test2 = tk.Label(left_panel, text='', font=font, background=white, pady=pad_10, width=width)
test2.pack()

# Интерфейс для расширенного теста на произвольные отклонения
tk.Label(left_panel, text='3. Расширенный тест на произвольные отклонения (Random Deviation Test)',
         font=font, background=white, pady=pad_10, width=width, anchor='w').pack()
tk.Button(left_panel, text="Выполнить тест",
          background=grey, foreground='white', pady=pad_5, padx=pad_10, font=font, command=random_deviation_test).pack()

test3 = tk.Label(left_panel, text='', font=font, background=white, pady=pad_10, width=width)
test3.pack()

# Кнопка для печати последовательности
tk.Label(left_panel, text='', font=('Arial', 5), background=white).pack()
tk.Button(left_panel, text="Показать последовательность",
          background=grey, foreground='white', pady=pad_5, padx=pad_10, font=font, command=print_sequence).pack()

# ==================== ПРАВАЯ ПАНЕЛЬ (ЛОГИ) ====================

log_frame = tk.Frame(right_panel, bg=white)
log_frame.pack(fill=tk.BOTH, expand=True)

log_text = tk.Text(log_frame, font=small_font, wrap=tk.WORD, height=40, width=35)
log_scrollbar = tk.Scrollbar(log_frame, command=log_text.yview)
log_text.configure(yscrollcommand=log_scrollbar.set)

log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

clear_log_button = tk.Button(right_panel, text="Очистить лог",
                             background=grey, foreground='white',
                             pady=pad_5, padx=pad_10, font=small_font,
                             command=clear_log)
clear_log_button.pack(pady=(5, 0))

root.mainloop()