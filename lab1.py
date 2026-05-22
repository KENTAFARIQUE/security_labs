# coding=utf-8
from random import randint
from math import sqrt
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


def vipe():  # обновление текста на экране
    test1['text'] = ''
    test2['text'] = ''
    test3['text'] = ''
    gen['text'] = ''
    load['text'] = ''


def generator():  # генерация последовательности заданной длины
    vipe()  # обновление текста на экране
    if not gen_entry.get().isdigit():  # проверка на корректность ввода пользователя
        gen['text'] = 'Ошибка генерации'
        gen['foreground'] = 'red'
        return
    len_e = int(gen_entry.get())
    e = [randint(0, 1) for _ in range(len_e)]  # генерация последовательности
    f = open(filename, 'w')
    for i in e:
        f.write(str(i) + ' ')  # запись в файл
    f.close()
    gen['text'] = 'Последовательность сгенерирована и сохранена'
    gen['foreground'] = 'green'


def take_sequence():  # получение последовательности из файла
    f = open(filename, 'r')
    e = list(map(int, f.readline().split()))
    f.close()
    return e


def print_sequence():  # печать последовательности
    window = tk.Toplevel()  # создание нового окна
    window.title("Последовательность")
    window.geometry("1120x600")

    f = open(filename, 'r')
    e = f.readline()
    f.close()

    text = ''
    param = 180
    for i in range(len(e) // (param * 2) + 1):  # разделение на строки для печати
        text += e[i * param * 2:(i + 1) * param * 2] + '\n'

    sequence = tk.Label(window, text=text, font=("Arial", 6),
                        background='white', pady=pad_10, width=1000, height=1000)
    sequence.pack()


def open_sequence():  # загрузка последовательности
    vipe()  # обновление текста на экране
    filepath = filedialog.askopenfilename()  # вызов окна для выбора файла
    if filepath == "":  # проверка файла
        load['text'] = 'Ошибка загрузки'
        load['foreground'] = 'red'
        return
    f = open(filepath, 'r')  # чтение файла
    text = f.readline()
    f.close()
    f = open(filename, 'w')
    f.write(text)
    f.close()
    load['text'] = 'Последовательность загружена'
    load['foreground'] = 'green'


def is_passing(test, result):  # проверка прохождения теста
    if result < 1.82138636:
        test['text'] = 'Тест успешно пройден'
        test['foreground'] = 'green'
        return True
    else:
        test['text'] = 'Тест не пройден'
        test['foreground'] = 'red'
        return False


def frequency_test():  # частотный тест
    log_message("=== Частотный тест ===")
    eps = take_sequence()  # входная последовательность
    n = len(eps)  # длина последовательности

    if n == 0:
        test1['text'] = 'Ошибка: последовательность пуста'
        test1['foreground'] = 'red'
        log_message("Ошибка: последовательность пуста")
        log_message("")
        return

    ones = sum(eps)
    zeros = n - ones
    log_message(f"Длина последовательности n = {n}")
    log_message(f"Количество единиц = {ones}, количество нулей = {zeros}")

    x = [0] * n  # последовательность -1 и 1
    sm = 0  # сумма
    for i in range(n):
        x[i] = 2 * eps[i] - 1  # подсчет последовательности по формуле
        sm += x[i]  # подсчет суммы
    s = abs(sm) / sqrt(n)  # подсчет статистики по формуле

    log_message(f"Сумма последовательности из -1 и 1: S = {sm}")
    log_message(f"Наблюдаемое значение статистики: S_n = {s:.6f}")
    log_message(f"Критическое значение: 1.82138636")

    passed = is_passing(test1, s)
    if passed:
        log_message("Результат: тест пройден")
    else:
        log_message("Результат: тест не пройден")
    log_message("")


def identical_sequence_test():  # тест на последовательность одинаковых бит
    log_message("=== Тест на последовательность одинаковых бит ===")
    eps = take_sequence()  # входная последовательность
    n = len(eps)  # длина последовательности

    if n == 0:
        test2['text'] = 'Ошибка: последовательность пуста'
        test2['foreground'] = 'red'
        log_message("Ошибка: последовательность пуста")
        log_message("")
        return

    pi = (1 / n) * sum(eps)  # частота, с которой в проверяемой последовательности встречаются единицы
    log_message(f"Длина последовательности n = {n}")
    log_message(f"Частота единиц pi = {pi:.6f}")

    r = 0
    for k in range(n - 1):
        if eps[k] != eps[k + 1]:
            r += 1
    v = 1 + r  # вычисляется значение Vn
    log_message(f"Количество смен бит r = {r}")
    log_message(f"Значение V_n = {v}")

    denominator = 2 * sqrt(2 * n) * pi * (1 - pi)
    if denominator == 0:
        test2['text'] = 'Тест не пройден: последовательность состоит из одинаковых бит'
        test2['foreground'] = 'red'
        log_message("Ошибка: последовательность состоит из одинаковых бит")
        log_message("")
        return

    s = abs(v - 2 * n * pi * (1 - pi)) / denominator  # подсчет статистики по формуле

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


def random_deviation_test():  # расширенный тест на произвольные отклонения
    log_message("=== Расширенный тест на произвольные отклонения ===")
    eps = take_sequence()  # входная последовательность
    n = len(eps)  # длина последовательности

    if n == 0:
        test3['text'] = 'Ошибка: последовательность пуста'
        test3['foreground'] = 'red'
        log_message("Ошибка: последовательность пуста")
        log_message("")
        return

    log_message(f"Длина последовательности n = {n}")

    x = [0] * n  # последовательность -1 и 1
    s = [0] * n  # последовательно удлиняющиеся подпоследовательности
    for i in range(n):
        x[i] = 2 * eps[i] - 1  # подсчет последовательности по формуле
        s[i] = s[i - 1] + x[i]  # подсчет подпоследовательности по формуле
    s_prime = [0] + s + [0]  # последовательность S'
    k = s_prime.count(0)  # количество нулей в полученной последовательности S'
    _l = k - 1  # вычисляется L

    log_message(f"Количество нулей в S': {s_prime.count(0)}")
    log_message(f"Значение L = {_l}")

    if _l == 0:
        test3['text'] = 'Тест не пройден: недостаточно нулей в последовательности'
        test3['foreground'] = 'red'
        log_message("Ошибка: недостаточно нулей в последовательности")
        log_message("")
        return

    e = [0] * 19  # сколько раз состояние встречалось в последовательности S'
    for i in range(19):
        if i == 9:
            continue
        e[i] = s_prime.count(i - 9)  # подсчет состояний по формуле

    log_message("Состояния и их наблюдаемые значения:")
    y = [0.0] * 19  # статистики для каждого состояния
    for i in range(19):
        if i == 9:
            continue
        y[i] = abs(e[i] - _l) / sqrt(2 * _l * (4 * abs(i - 9) - 2))  # подсчет статистики по формуле
        if e[i] > 0:
            log_message(f"  Состояние {i - 9:2d}: частота = {e[i]:3d}, статистика Y = {y[i]:.6f}")

    max_y = max(y)
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
    return re.match(r"^\d{0,5}$", value) is not None


# создание интерфейса
root = tk.Tk()
root.title("Лабораторная работа №1, Кузнецов С.А., группа ИВТАСбд-42")
root.geometry("900x720")
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

# интерфейс для генерации последовательности
tk.Label(left_panel, text='', font=("Arial", 1), background=white).pack()
tk.Label(left_panel, text='Введите желаемую длину последовательности для генерации (в битах)',
         font=font, background=white, pady=pad_10, width=width, anchor='w').pack()
check = (root.register(is_valid), "%P")
gen_entry = tk.Entry(left_panel, font=font, validate="key", validatecommand=check, width=15, justify='center')
gen_entry.pack()
tk.Label(left_panel, text='', font=font, background=white).pack()
tk.Button(left_panel, text="Сгенерировать последовательность",
          background=grey, foreground='white', pady=pad_5, padx=pad_10, font=font, command=generator).pack()
gen = tk.Label(left_panel, text='', font=font, background=white, pady=pad_10, width=width)
gen.pack()

# интерфейс для загрузки последовательности
tk.Label(left_panel, text='Или загрузите последовательность из текстового файла',
         font=font, background=white, pady=pad_10, width=width, anchor='w').pack()
tk.Button(left_panel, text="Загрузить последовательность",
          background=grey, foreground='white', pady=pad_5, padx=pad_10, font=font, command=open_sequence).pack()
load = tk.Label(left_panel, text='', font=font, background=white, pady=pad_10, width=width)
load.pack()

# разделительная линия
separator = tk.Label(left_panel, text='─────────────────────────────────────────────────────────────',
                     font=font, background=white, pady=pad_5)
separator.pack()

# интерфейс для частотного теста
tk.Label(left_panel, text='1. Частотный тест', font=font, background=white, pady=pad_10, width=width, anchor='w').pack()
tk.Button(left_panel, text="Выполнить",
          background=grey, foreground='white', pady=pad_5, padx=pad_10, font=font, command=frequency_test).pack()
test1 = tk.Label(left_panel, text='', font=font, background=white, pady=pad_10, width=width)
test1.pack()

# интерфейс для теста на последовательность одинаковых бит
tk.Label(left_panel, text='2. Тест на последовательность одинаковых бит',
         font=font, background=white, pady=pad_10, width=width, anchor='w').pack()
tk.Button(left_panel, text="Выполнить", background=grey,
          foreground='white', pady=pad_5, padx=pad_10, font=font, command=identical_sequence_test).pack()
test2 = tk.Label(left_panel, text='', font=font, background=white, pady=pad_10, width=width)
test2.pack()

# интерфейс для расширенного теста на произвольные отклонения
tk.Label(left_panel, text='3. Расширенный тест на произвольные отклонения',
         font=font, background=white, pady=pad_10, width=width, anchor='w').pack()
tk.Button(left_panel, text="Выполнить",
          background=grey, foreground='white', pady=pad_5, padx=pad_10, font=font, command=random_deviation_test).pack()
test3 = tk.Label(left_panel, text='', font=font, background=white, pady=pad_10, width=width)
test3.pack()

# кнопка для печати последовательности
tk.Label(left_panel, text='', font=('Arial', 5), background=white).pack()
tk.Button(left_panel, text="Печать последовательности",
          background=grey, foreground='white', pady=pad_5, padx=pad_10, font=font, command=print_sequence).pack()

# ==================== ПРАВАЯ ПАНЕЛЬ (ЛОГИ) ====================

log_frame = tk.Frame(right_panel, bg=white)
log_frame.pack(fill=tk.BOTH, expand=True)

log_text = tk.Text(log_frame, font=small_font, wrap=tk.WORD, height=35, width=35)
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