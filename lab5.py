# coding=utf-8
"""
Лабораторная работа №5
Вариант 9: Алгоритм RSA, тест простоты Лемана (128 бит)
Выполнил: Валиуллов Р.Р., группа ИВТИИбд-31
"""

from random import randint
import tkinter as tk
from tkinter import filedialog
import os
import re

# Глобальная переменная для лога
log_text = None


def log_message(message):
    """Добавление сообщения в лог"""
    if log_text:
        log_text.insert(tk.END, message + "\n")
        log_text.see(tk.END)


# ==================== РАБОТА С БОЛЬШИМИ ЧИСЛАМИ ====================

def gf_factor(number, factor, modulus):
    """
    Быстрое возведение в степень по модулю (бинарный метод)
    Вычисляет (number^factor) mod modulus
    """
    result = 1
    base = number % modulus
    exp = factor

    while exp > 0:
        if exp & 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exp >>= 1

    return result


def lehmann_primality_test(n, tries=10):
    """
    Тест простоты Лемана
    Возвращает True, если число вероятно простое
    Вероятность ошибки: (1/2)^tries
    """
    if n == 2 or n == 3:
        return True
    if n % 2 == 0 or n == 1:
        return False

    for i in range(tries):
        a = randint(2, n - 2)
        exp = (n - 1) // 2
        result = gf_factor(a, exp, n)

        if result != 1 and result != n - 1:
            log_message(f"  Итерация {i + 1}: число не прошло тест с a={a}")
            return False
        else:
            log_message(f"  Итерация {i + 1}: число прошло тест с a={a}")

    return True


def prime_number_generator(bits):
    """
    Генерация простого числа заданной длины в битах
    Использует тест Лемана
    """
    log_message(f"Начало генерации {bits}-битного простого числа")

    # Малые простые числа для предварительной проверки
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101,
                    103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199,
                    211, 223, 227, 229, 233, 239, 241, 251]

    attempts = 0

    while True:
        attempts += 1
        # Генерируем случайное нечетное число заданной длины
        num = 1
        for _ in range(bits - 2):
            num = (num << 1) | randint(0, 1)
        num = (num << 1) | 1

        log_message(f"Попытка {attempts}: проверка числа")

        # Проверка на малые простые числа
        divisible = False
        for p in small_primes:
            if num % p == 0:
                divisible = True
                break

        if divisible:
            continue

        # Тест Лемана
        if lehmann_primality_test(num):
            log_message(f"Найдено простое число: {num}")
            log_message(f"Размер: {num.bit_length()} бит")
            return num


def gcd(a, b):
    """Алгоритм Евклида"""
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    """Расширенный алгоритм Евклида"""
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return g, x, y


def mod_inverse(e, phi):
    """Вычисление обратного элемента по модулю"""
    g, x, _ = extended_gcd(e, phi)
    if g != 1:
        raise Exception("Обратный элемент не существует")
    return x % phi


# ==================== АЛГОРИТМ RSA ====================

class RSA:
    """Реализация алгоритма RSA"""

    def __init__(self, bits=128):
        log_message("=== ГЕНЕРАЦИЯ КЛЮЧЕЙ RSA ===")
        log_message(f"Длина простых чисел: {bits} бит")

        # Генерируем два простых числа
        log_message("Генерация p...")
        self.p = prime_number_generator(bits)

        log_message("Генерация q...")
        self.q = prime_number_generator(bits)

        # Вычисляем n = p * q
        self.n = self.p * self.q
        log_message(f"n = p * q (размер: {self.n.bit_length()} бит)")

        # Функция Эйлера φ(n) = (p-1)*(q-1)
        self.phi = (self.p - 1) * (self.q - 1)

        # Открытая экспонента e
        self.e = 65537
        if gcd(self.e, self.phi) != 1:
            for e_candidate in range(65537, 100000, 2):
                if gcd(e_candidate, self.phi) == 1:
                    self.e = e_candidate
                    break

        log_message(f"Открытая экспонента e = {self.e}")

        # Закрытая экспонента d
        self.d = mod_inverse(self.e, self.phi)
        log_message("Ключи успешно сгенерированы")

    def get_public_key(self):
        return (self.e, self.n)

    def get_private_key(self):
        return (self.d, self.n)

    def encrypt_block(self, message, public_key):
        e, n = public_key
        return gf_factor(message, e, n)

    def decrypt_block(self, ciphertext, private_key):
        d, n = private_key
        return gf_factor(ciphertext, d, n)

    def encrypt_data(self, data, public_key):
        """Шифрование данных"""
        e, n = public_key
        block_size = n.bit_length() // 8 - 1

        if block_size < 1:
            block_size = 1

        result = []
        total = (len(data) + block_size - 1) // block_size

        for i in range(0, len(data), block_size):
            block = data[i:i + block_size]
            block_int = int.from_bytes(block, 'big')
            encrypted_int = self.encrypt_block(block_int, public_key)
            # Сохраняем как десятичное число (для читаемости в txt)
            result.append(str(encrypted_int))

            if (i // block_size + 1) % 5 == 0:
                log_message(f"  Зашифровано {i // block_size + 1}/{total} блоков")

        return ' '.join(result)  # Возвращаем строку с числами через пробел

    def decrypt_data(self, ciphertext_str, private_key):
        """Дешифрование данных из строки"""
        d, n = private_key

        # Разбиваем строку на отдельные числа
        blocks = ciphertext_str.strip().split()
        result = bytearray()
        total = len(blocks)

        for i, block_str in enumerate(blocks):
            block_int = int(block_str)
            decrypted_int = self.decrypt_block(block_int, private_key)

            byte_len = (decrypted_int.bit_length() + 7) // 8
            if byte_len == 0:
                byte_len = 1
            result.extend(decrypted_int.to_bytes(byte_len, 'big'))

            if (i + 1) % 5 == 0:
                log_message(f"  Расшифровано {i + 1}/{total} блоков")

        return bytes(result)


class GUI:
    def __init__(self):
        # Все файлы теперь в формате .txt
        self.filename_temp = 'support/original.txt'  # Исходный файл (текст/бинарник перекодирован)
        self.filename_cipher = 'support/encrypted.txt'  # Зашифрованный файл (числа через пробел)
        self.filename_decipher = 'support/decrypted.txt'  # Расшифрованный файл (восстановленные данные)

        self.width = 60
        self.font = ("Arial", 11)
        self.small_font = ("Arial", 9)
        self.white = '#eee'
        self.grey = '#444'
        self.dark_grey = '#333'
        self.pad_10 = 10
        self.pad_5 = 5

        self.load_label = None
        self.cipher_label = None
        self.decipher_label = None
        self.keys_label = None
        self.bits_var = None

        self.rsa = None
        self.bits = 128
        self.last_data = None

    def start(self):
        root = tk.Tk()
        root.title("Лабораторная работа №5 (Вариант 9) - RSA, тест Лемана, 128 бит")
        root.geometry("900x750")
        root.resizable(False, False)
        root.configure(bg=self.white)

        # Создание основной панели с двумя колонками
        main_frame = tk.Frame(root, bg=self.white)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая панель (управление)
        left_panel = tk.Frame(main_frame, bg=self.white, width=600)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Правая панель (логи)
        right_panel = tk.Frame(main_frame, bg=self.white, width=280)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # ==================== ЛЕВАЯ ПАНЕЛЬ ====================

        tk.Label(left_panel, text='АСИММЕТРИЧНАЯ КРИПТОГРАФИЯ (RSA)',
                 font=("Arial", 14, "bold"), background=self.white, pady=self.pad_10).pack()

        # Выбор длины
        tk.Label(left_panel, text='Выберите длину простых чисел (бит):',
                 font=self.font, background=self.white, pady=self.pad_10, width=self.width, anchor='w').pack()

        self.bits_var = tk.StringVar(value="128")
        bits_frame = tk.Frame(left_panel, bg=self.white)
        bits_frame.pack()

        for bits in ["128", "256", "512"]:
            tk.Radiobutton(bits_frame, text=f"{bits} бит", variable=self.bits_var, value=bits,
                           font=self.font, background=self.white, padx=10).pack(side=tk.LEFT)

        tk.Label(left_panel, text='', font=self.font, background=self.white).pack()

        # Генерация ключей
        tk.Button(left_panel, text="Сгенерировать RSA ключи", background=self.grey, foreground='white',
                  pady=self.pad_5, padx=self.pad_10, font=self.font, command=self.generate_keys).pack()

        self.keys_label = tk.Label(left_panel, text='', font=self.font, background=self.white,
                                   pady=self.pad_10, width=self.width)
        self.keys_label.pack()

        # Разделитель
        tk.Label(left_panel, text='─────────────────────────────────────────────────────────────',
                 font=self.font, background=self.white, pady=self.pad_5).pack()

        # Загрузка файла
        tk.Label(left_panel, text='Загрузите файл для шифрования',
                 font=self.font, background=self.white, pady=self.pad_10, width=self.width, anchor='w').pack()
        tk.Button(left_panel, text="Загрузить файл", background=self.grey, foreground='white',
                  pady=self.pad_5, padx=self.pad_10, font=self.font, command=self.load_file).pack()
        self.load_label = tk.Label(left_panel, text='', font=self.font, background=self.white,
                                   pady=self.pad_10, width=self.width)
        self.load_label.pack()

        # Разделитель
        tk.Label(left_panel, text='─────────────────────────────────────────────────────────────',
                 font=self.font, background=self.white, pady=self.pad_5).pack()

        # Шифрование
        tk.Label(left_panel, text='Шифрование (открытым ключом)',
                 font=self.font, background=self.white, pady=self.pad_10, width=self.width, anchor='w').pack()
        tk.Button(left_panel, text="Выполнить шифрование", background=self.grey, foreground='white',
                  pady=self.pad_5, padx=self.pad_10, font=self.font, command=self.cipher).pack()
        self.cipher_label = tk.Label(left_panel, text='', font=self.font, background=self.white,
                                     pady=self.pad_10, width=self.width)
        self.cipher_label.pack()

        # Дешифрование
        tk.Label(left_panel, text='Дешифрование (закрытым ключом)',
                 font=self.font, background=self.white, pady=self.pad_10, width=self.width, anchor='w').pack()
        tk.Button(left_panel, text="Выполнить дешифрование", background=self.grey, foreground='white',
                  pady=self.pad_5, padx=self.pad_10, font=self.font, command=self.decipher).pack()
        self.decipher_label = tk.Label(left_panel, text='', font=self.font, background=self.white,
                                       pady=self.pad_10, width=self.width)
        self.decipher_label.pack()

        # Разделитель
        tk.Label(left_panel, text='─────────────────────────────────────────────────────────────',
                 font=self.font, background=self.white, pady=self.pad_5).pack()

        # Просмотр ключей
        tk.Button(left_panel, text="Просмотр ключей", background=self.grey, foreground='white',
                  pady=self.pad_5, padx=self.pad_10, font=self.font, command=self.print_keys).pack()
        self.keys_display = tk.Label(left_panel, text='', font=self.font, background=self.white,
                                     pady=self.pad_10, width=self.width)
        self.keys_display.pack()

        # ==================== ПРАВАЯ ПАНЕЛЬ (ЛОГИ) ====================

        log_header = tk.Label(right_panel, text="ЛОГ РАБОТЫ",
                              font=("Arial", 12, "bold"),
                              background=self.dark_grey,
                              foreground='white',
                              pady=5)
        log_header.pack(fill=tk.X, pady=(0, 5))

        log_frame = tk.Frame(right_panel, bg=self.white)
        log_frame.pack(fill=tk.BOTH, expand=True)

        global log_text
        log_text = tk.Text(log_frame, font=self.small_font, wrap=tk.WORD, height=35, width=35)
        log_scrollbar = tk.Scrollbar(log_frame, command=log_text.yview)
        log_text.configure(yscrollcommand=log_scrollbar.set)

        log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def clear_log():
            log_text.delete(1.0, tk.END)
            log_message("Лог очищен")

        clear_button = tk.Button(right_panel, text="Очистить лог",
                                 background=self.grey, foreground='white',
                                 pady=self.pad_5, padx=self.pad_10, font=self.small_font,
                                 command=clear_log)
        clear_button.pack(pady=(5, 0))

        log_message("Программа запущена")
        log_message("Вариант 9: Алгоритм RSA, тест простоты Лемана")
        log_message("Длина простых чисел: 128 бит (можно изменить)")
        log_message("")
        log_message("Файлы сохраняются в папке support:")
        log_message("  - original.txt - исходный файл")
        log_message("  - encrypted.txt - зашифрованный файл (числа через пробел)")
        log_message("  - decrypted.txt - расшифрованный файл")

        root.mainloop()

    def generate_keys(self):
        """Генерация ключей RSA"""
        log_message("")
        log_message("========================================")
        log_message("ГЕНЕРАЦИЯ КЛЮЧЕЙ RSA")

        self.bits = int(self.bits_var.get())
        log_message(f"Выбрана длина: {self.bits} бит")

        try:
            self.rsa = RSA(bits=self.bits)
            self.keys_label['text'] = f'Ключи RSA ({self.bits} бит) сгенерированы'
            self.keys_label['foreground'] = 'green'
            self.keys_display['text'] = f'Ключи готовы. Нажмите "Просмотр ключей"'
        except Exception as e:
            self.keys_label['text'] = f'Ошибка: {str(e)}'
            self.keys_label['foreground'] = 'red'
            log_message(f"Ошибка: {str(e)}")

    def print_keys(self):
        """Вывод ключей в отдельном окне"""
        if self.rsa is None:
            self.keys_display['text'] = 'Сначала сгенерируйте ключи'
            log_message("Ошибка: ключи не сгенерированы")
            return

        window = tk.Toplevel()
        window.title("Ключи RSA")
        window.geometry("700x450")
        window.configure(bg=self.white)

        text_widget = tk.Text(window, font=self.small_font, wrap=tk.WORD, bg=self.white)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(text_widget)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text_widget.yview)

        e, n = self.rsa.get_public_key()
        d, n2 = self.rsa.get_private_key()

        key_info = f"""
ОТКРЫТЫЙ КЛЮЧ (публичный)

  e = {e}

  n = {n}


ЗАКРЫТЫЙ КЛЮЧ (приватный)

  d = {d}

  n = {n2}


ПРОСТЫЕ ЧИСЛА

  p = {self.rsa.p}

  q = {self.rsa.q}

  φ(n) = {self.rsa.phi}


ПАРАМЕТРЫ

  Длина простых чисел: {self.bits} бит
  Размер модуля n: {n.bit_length()} бит
"""
        text_widget.insert(tk.END, key_info)
        text_widget.config(state=tk.DISABLED)

        log_message("Ключи выведены в отдельном окне")

    def load_file(self):
        """Загрузка файла"""
        log_message("=== ЗАГРУЗКА ФАЙЛА ===")

        filepath = filedialog.askopenfilename()
        if filepath == "":
            self.load_label['text'] = 'Ошибка загрузки'
            self.load_label['foreground'] = 'red'
            log_message("Ошибка: файл не выбран")
            return

        try:
            with open(filepath, 'rb') as file:
                data = file.read()

            # Сохраняем в original.txt
            with open(self.filename_temp, 'wb') as f:
                f.write(data)

            file_size = os.path.getsize(filepath)
            log_message(f"Загружен файл: {os.path.basename(filepath)}")
            log_message(f"Размер файла: {file_size} байт")
            log_message(f"Сохранён в: {self.filename_temp}")

            self.load_label['text'] = f'Файл загружен ({file_size} байт)'
            self.load_label['foreground'] = 'green'
        except Exception as e:
            self.load_label['text'] = f'Ошибка: {str(e)}'
            self.load_label['foreground'] = 'red'
            log_message(f"Ошибка: {str(e)}")

    def cipher(self):
        """Шифрование RSA"""
        log_message("=== ШИФРОВАНИЕ RSA ===")

        if self.rsa is None:
            self.cipher_label['text'] = 'Сначала сгенерируйте ключи'
            self.cipher_label['foreground'] = 'red'
            log_message("Ошибка: ключи не сгенерированы")
            return

        try:
            with open(self.filename_temp, 'rb') as f:
                data = f.read()

            if not data:
                log_message("Ошибка: файл с данными пуст")
                return

            log_message(f"Исходные данные: {len(data)} байт")

            public_key = self.rsa.get_public_key()
            encrypted_str = self.rsa.encrypt_data(data, public_key)

            # Сохраняем в encrypted.txt
            with open(self.filename_cipher, 'w', encoding='utf-8') as f:
                f.write(encrypted_str)

            log_message(f"Шифрование завершено. Результат: {len(encrypted_str.split())} блоков")
            log_message(f"Сохранён в: {self.filename_cipher}")

            self.cipher_label['text'] = f'Шифрование выполнено'
            self.cipher_label['foreground'] = 'green'
        except Exception as e:
            self.cipher_label['text'] = f'Ошибка: {str(e)}'
            self.cipher_label['foreground'] = 'red'
            log_message(f"Ошибка: {str(e)}")

    def decipher(self):
        """Дешифрование RSA"""
        log_message("=== ДЕШИФРОВАНИЕ RSA ===")

        if self.rsa is None:
            self.decipher_label['text'] = 'Сначала сгенерируйте ключи'
            self.decipher_label['foreground'] = 'red'
            log_message("Ошибка: ключи не сгенерированы")
            return

        try:
            with open(self.filename_cipher, 'r', encoding='utf-8') as f:
                encrypted_str = f.read()

            if not encrypted_str:
                log_message("Ошибка: файл с шифротекстом пуст")
                return

            log_message(f"Зашифрованные данные: {len(encrypted_str.split())} блоков")

            private_key = self.rsa.get_private_key()
            decrypted_data = self.rsa.decrypt_data(encrypted_str, private_key)

            # Сохраняем в decrypted.txt
            with open(self.filename_decipher, 'wb') as f:
                f.write(decrypted_data)

            log_message(f"Дешифрование завершено. Результат: {len(decrypted_data)} байт")
            log_message(f"Сохранён в: {self.filename_decipher}")

            self.decipher_label['text'] = f'Дешифрование выполнено'
            self.decipher_label['foreground'] = 'green'
        except Exception as e:
            self.decipher_label['text'] = f'Ошибка: {str(e)}'
            self.decipher_label['foreground'] = 'red'
            log_message(f"Ошибка: {str(e)}")


if __name__ == "__main__":
    if not os.path.exists('support'):
        os.makedirs('support')

    gui = GUI()
    gui.start()