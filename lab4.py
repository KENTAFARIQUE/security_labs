# coding=utf-8
"""
Лабораторная работа №4
Вариант 9: ГОСТ (гаммирование с обратной связью)
Выполнил: Валиуллов Р.Р., группа ИВТИИбд-31
"""

import tkinter as tk
from tkinter import filedialog
import os

# ==================== ТАБЛИЦА ПОДСТАНОВКИ ДЛЯ ГОСТ ====================

sTable = [
    0xa3, 0xd7, 0x09, 0x83, 0xf8, 0x48, 0xf6, 0xf4, 0xb3, 0x21, 0x15, 0x78, 0x99, 0xb1, 0xaf, 0xf9,
    0xe7, 0x2d, 0x4d, 0x8a, 0xce, 0x4c, 0xca, 0x2e, 0x52, 0x95, 0xd9, 0x1e, 0x4e, 0x38, 0x44, 0x28,
    0x0a, 0xdf, 0x02, 0xa0, 0x17, 0xf1, 0x60, 0x68, 0x12, 0xb7, 0x7a, 0xc3, 0xe9, 0xfa, 0x3d, 0x53,
    0x96, 0x84, 0x6b, 0xba, 0xf2, 0x63, 0x9a, 0x19, 0x7c, 0xae, 0xe5, 0xf5, 0xf7, 0x16, 0x6a, 0xa2,
    0x39, 0xb6, 0x7b, 0x0f, 0xc1, 0x93, 0x81, 0x1b, 0xee, 0xb4, 0x1a, 0xea, 0xd0, 0x91, 0x2f, 0xb8,
    0x55, 0xb9, 0xda, 0x85, 0x3f, 0x41, 0xbf, 0xe0, 0x5a, 0x58, 0x80, 0x5f, 0x66, 0x0b, 0xd8, 0x90,
    0x35, 0xd5, 0xc0, 0xa7, 0x33, 0x06, 0x65, 0x69, 0x45, 0x00, 0x94, 0x56, 0x6d, 0x98, 0x9b, 0x76,
    0x97, 0xfc, 0xb2, 0xc2, 0xb0, 0xfe, 0xdb, 0x20, 0x01, 0xeb, 0xd6, 0xe4, 0xdd, 0x47, 0x4a, 0x1d,
    0x42, 0xed, 0x9e, 0x6e, 0x49, 0x3c, 0xcd, 0x43, 0x27, 0xd2, 0x07, 0xd4, 0xde, 0xc7, 0x67, 0x18,
    0x89, 0xcb, 0x30, 0x1f, 0x8d, 0xc6, 0x8f, 0xaa, 0xc8, 0x74, 0xdc, 0xc9, 0x5d, 0x5c, 0x31, 0xa4,
    0x70, 0x88, 0x61, 0x2c, 0x9f, 0x0d, 0x2b, 0x87, 0x50, 0x82, 0x54, 0x64, 0x26, 0x7d, 0x03, 0x40,
    0x34, 0x4b, 0x1c, 0x73, 0xd1, 0xc4, 0xfd, 0x3b, 0xcc, 0xfb, 0x7f, 0xab, 0xe6, 0x3e, 0x5b, 0xa5,
    0xad, 0x04, 0x23, 0x9c, 0x14, 0x51, 0x22, 0x0f, 0x29, 0x79, 0x71, 0x7e, 0xff, 0x8c, 0x0e, 0xe2,
    0x0c, 0xef, 0xbc, 0x72, 0x75, 0x6f, 0x37, 0x01, 0xec, 0xd3, 0x8e, 0x62, 0x8b, 0x86, 0x10, 0xe8,
    0x08, 0x77, 0x11, 0xbe, 0x92, 0x4f, 0x24, 0xc5, 0x32, 0x36, 0x9d, 0xcf, 0xf3, 0xa6, 0xbb, 0xac,
    0x5e, 0x6c, 0xa9, 0x13, 0x57, 0x25, 0xb5, 0xe3, 0xbd, 0xa8, 0x3a, 0x01, 0x05, 0x59, 0x2a, 0x46
]

# Глобальная переменная для лога
log_text = None


def log_message(message):
    """Добавление сообщения в лог"""
    if log_text:
        log_text.insert(tk.END, message + "\n")
        log_text.see(tk.END)


def left_rotate(x, n, bits=32):
    """Циклический сдвиг влево"""
    mask = (1 << bits) - 1
    return ((x << n) & mask) | (x >> (bits - n))


def string_to_int(s):
    """Преобразование строки в целое число (битовое представление)"""
    result = 0
    for ch in s:
        result = (result << 8) | ord(ch)
    return result


# ==================== ХЕШ-ФУНКЦИЯ MD4 ====================

def md4(message):
    """MD4 хеш-функция для преобразования пароля в ключ"""
    m = message
    m = (m << 1) | 1
    n = len(bin(m)) - 2
    while n % 512 < 448:
        m = m << 1
        n += 1
    m = (m << 32) | (n & 0xffffffff)
    m = (m << 32) | ((n >> 32) & 0xffffffff)
    n += 64
    n = n // 32

    a = 0x67452301
    b = 0xefcdab89
    c = 0x98badcfe
    d = 0x10325476

    def f(x, y, z):
        return (x & y) | (~x & z)

    def g(x, y, z):
        return (x & y) | (x & z) | (y & z)

    def h(x, y, z):
        return x ^ y ^ z

    def op(a, b, c, d, func, xk, s, const):
        res = (a + func(b, c, d) + xk + const) & 0xffffffff
        return left_rotate(res, s, 32)

    gc = 0x5a827999
    hc = 0x6ed9eba1
    x = [0] * 16

    for i in range(0, n // 16):
        for j in range(0, 16):
            x[j] = m & 0xffffffff
            m = m >> 32
        aa, bb, cc, dd = a, b, c, d

        # Раунд 1
        a = op(a, b, c, d, f, x[0], 3, 0)
        d = op(d, a, b, c, f, x[1], 7, 0)
        c = op(c, d, a, b, f, x[2], 11, 0)
        b = op(b, c, d, a, f, x[3], 19, 0)
        a = op(a, b, c, d, f, x[4], 3, 0)
        d = op(d, a, b, c, f, x[5], 7, 0)
        c = op(c, d, a, b, f, x[6], 11, 0)
        b = op(b, c, d, a, f, x[7], 19, 0)
        a = op(a, b, c, d, f, x[8], 3, 0)
        d = op(d, a, b, c, f, x[9], 7, 0)
        c = op(c, d, a, b, f, x[10], 11, 0)
        b = op(b, c, d, a, f, x[11], 19, 0)
        a = op(a, b, c, d, f, x[12], 3, 0)
        d = op(d, a, b, c, f, x[13], 7, 0)
        c = op(c, d, a, b, f, x[14], 11, 0)
        b = op(b, c, d, a, f, x[15], 19, 0)

        # Раунд 2
        a = op(a, b, c, d, g, x[0], 3, gc)
        d = op(d, a, b, c, g, x[4], 5, gc)
        c = op(c, d, a, b, g, x[8], 9, gc)
        b = op(b, c, d, a, g, x[12], 13, gc)
        a = op(a, b, c, d, g, x[1], 3, gc)
        d = op(d, a, b, c, g, x[5], 5, gc)
        c = op(c, d, a, b, g, x[9], 9, gc)
        b = op(b, c, d, a, g, x[13], 13, gc)
        a = op(a, b, c, d, g, x[2], 3, gc)
        d = op(d, a, b, c, g, x[6], 5, gc)
        c = op(c, d, a, b, g, x[10], 9, gc)
        b = op(b, c, d, a, g, x[14], 13, gc)
        a = op(a, b, c, d, g, x[3], 3, gc)
        d = op(d, a, b, c, g, x[7], 5, gc)
        c = op(c, d, a, b, g, x[11], 9, gc)
        b = op(b, c, d, a, g, x[15], 13, gc)

        # Раунд 3
        a = op(a, b, c, d, h, x[0], 3, hc)
        d = op(d, a, b, c, h, x[8], 9, hc)
        c = op(c, d, a, b, h, x[4], 11, hc)
        b = op(b, c, d, a, h, x[12], 15, hc)
        a = op(a, b, c, d, h, x[2], 3, hc)
        d = op(d, a, b, c, h, x[10], 9, hc)
        c = op(c, d, a, b, h, x[6], 11, hc)
        b = op(b, c, d, a, h, x[14], 15, hc)
        a = op(a, b, c, d, h, x[1], 3, hc)
        d = op(d, a, b, c, h, x[9], 9, hc)
        c = op(c, d, a, b, h, x[5], 11, hc)
        b = op(b, c, d, a, h, x[13], 15, hc)
        a = op(a, b, c, d, h, x[3], 3, hc)
        d = op(d, a, b, c, h, x[11], 9, hc)
        c = op(c, d, a, b, h, x[7], 11, hc)
        b = op(b, c, d, a, h, x[15], 15, hc)

        a = (a + aa) & 0xffffffff
        b = (b + bb) & 0xffffffff
        c = (c + cc) & 0xffffffff
        d = (d + dd) & 0xffffffff

    return (d << 96) | (c << 64) | (b << 32) | a


# ==================== АЛГОРИТМ ГОСТ 28147-89 ====================

class GOSTCipher:
    """
    Реализация ГОСТ 28147-89
    Блок: 8 байт (64 бита)
    Ключ: 256 бит (32 байта)
    Режим: гаммирование с обратной связью
    """

    def __init__(self, key):
        self.block_size = 8  # 64 бита
        self.key = key  # 32 байта

    def _sbox_transform(self, value):
        """
        Преобразование через S-блоки (8 блоков по 4 бита)
        S-блоки взяты из таблицы подстановки
        """
        result = 0
        for i in range(8):
            nibble = (value >> (4 * i)) & 0xF
            replaced = sTable[(nibble + i * 16) & 0xFF]
            result |= (replaced & 0xF) << (4 * i)
        return result

    def _gost_round(self, left, right, key_part):
        """
        Один раунд сети Фейстеля для ГОСТ
        left, right - 32-битные половины блока
        key_part - 32-битная часть ключа
        """
        # Функция F: сложение с ключом, S-преобразование, циклический сдвиг
        f = (right + key_part) & 0xFFFFFFFF
        f = self._sbox_transform(f)
        f = left_rotate(f, 11, 32)
        new_left = left ^ f
        return right, new_left

    def _encrypt_64bit(self, block):
        """
        Шифрование одного 64-битного блока (8 байт) по ГОСТ
        """
        # Разбиваем блок на два 32-битных слова
        left = int.from_bytes(block[:4], 'little')
        right = int.from_bytes(block[4:], 'little')

        # Разбиваем ключ на 8 частей по 32 бита
        key_parts = []
        for i in range(0, 32, 4):
            key_parts.append(int.from_bytes(self.key[i:i + 4], 'little'))

        # 32 раунда ГОСТ
        # Первые 24 раунда: использование всех 8 ключей по 3 раза (прямой порядок)
        for r in range(24):
            key_idx = r % 8
            left, right = self._gost_round(left, right, key_parts[key_idx])

        # Последние 8 раундов: ключи в обратном порядке
        for r in range(8):
            key_idx = 7 - r
            left, right = self._gost_round(left, right, key_parts[key_idx])

        # Формируем результат (обратный порядок слов)
        result = left.to_bytes(4, 'little') + right.to_bytes(4, 'little')
        return result


class GOSTGammaMode:
    """
    Режим гаммирования с обратной связью для ГОСТ 28147-89
    """

    def __init__(self, cipher, sync_message):
        """
        cipher: объект шифра ГОСТ
        sync_message: синхропосылка (8 байт)
        """
        self.cipher = cipher
        self.sync_message = sync_message
        self.block_size = cipher.block_size

    def _xor_bytes(self, a, b):
        """Побайтовый XOR двух байтовых строк"""
        return bytes(x ^ y for x, y in zip(a, b))

    def encrypt(self, data, callback=None):
        """
        Шифрование данных в режиме гаммирования с обратной связью
        """
        result = bytearray()
        feedback = self.sync_message
        total = len(data)

        for i in range(0, len(data), self.block_size):
            block = data[i:i + self.block_size]

            # Гамма = шифрование обратной связи
            gamma = self.cipher._encrypt_64bit(feedback)

            # Обновляем обратную связь для следующего блока
            feedback = gamma

            # Шифруем блок: XOR с гаммой
            encrypted = self._xor_bytes(block, gamma[:len(block)])
            result.extend(encrypted)

            if callback:
                callback(i + len(block), total)

        return bytes(result)

    def decrypt(self, data, callback=None):
        """
        Дешифрование данных в режиме гаммирования с обратной связью
        (симметрично шифрованию)
        """
        return self.encrypt(data, callback)


class GUI:
    def __init__(self):
        # Все файлы теперь в формате .txt
        self.filename_temp = 'support/original.txt'      # Исходный файл
        self.filename_cipher = 'support/encrypted.txt'   # Зашифрованный файл (бинарные данные в hex)
        self.filename_decipher = 'support/decrypted.txt' # Расшифрованный файл (текст)

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
        self.password_display = None
        self.password_entry = None

        self.gost_mode = None
        self.password_hash = None

    def start(self):
        root = tk.Tk()
        root.title("Лабораторная работа №4 (Вариант 9) - ГОСТ с гаммированием")
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

        # Загрузка файла
        tk.Label(left_panel, text='', font=("Arial", 1), background=self.white).pack()
        tk.Label(left_panel, text='Загрузите файл для шифрования',
                 font=self.font, background=self.white, pady=self.pad_10, width=self.width, anchor='w').pack()
        tk.Button(left_panel, text="Загрузить файл", background=self.grey, foreground='white',
                  pady=self.pad_5, padx=self.pad_10, font=self.font, command=self.load_file).pack()
        self.load_label = tk.Label(left_panel, text='', font=self.font, background=self.white,
                                   pady=self.pad_10, width=self.width)
        self.load_label.pack()

        # Разделитель
        separator1 = tk.Label(left_panel, text='─────────────────────────────────────────────────────────────',
                              font=self.font, background=self.white, pady=self.pad_5)
        separator1.pack()

        # ==================== ВВОД ПАРОЛЯ ====================

        tk.Label(left_panel, text='Введите текстовый пароль (будет хеширован MD4):',
                 font=self.font, background=self.white, pady=self.pad_10, width=self.width, anchor='w').pack()

        self.password_entry = tk.Entry(left_panel, font=self.font, width=40, justify='center')
        self.password_entry.pack()
        self.password_entry.insert(0, "my_secret_password")

        tk.Label(left_panel, text='', font=self.font, background=self.white).pack()
        tk.Button(left_panel, text="Установить пароль", background=self.grey,
                  foreground='white', pady=self.pad_5, padx=self.pad_10, font=self.font,
                  command=self.set_password).pack()

        self.password_display = tk.Label(left_panel, text='', font=self.font, background=self.white,
                                         pady=self.pad_10, width=self.width)
        self.password_display.pack()

        # Разделитель
        separator2 = tk.Label(left_panel, text='─────────────────────────────────────────────────────────────',
                              font=self.font, background=self.white, pady=self.pad_5)
        separator2.pack()

        # ==================== ШИФРОВАНИЕ/ДЕШИФРОВАНИЕ ====================

        tk.Label(left_panel, text='Шифрование (ГОСТ с гаммированием)',
                 font=self.font, background=self.white, pady=self.pad_10, width=self.width, anchor='w').pack()
        tk.Button(left_panel, text="Выполнить шифрование", background=self.grey, foreground='white',
                  pady=self.pad_5, padx=self.pad_10, font=self.font, command=self.cipher).pack()
        self.cipher_label = tk.Label(left_panel, text='', font=self.font, background=self.white,
                                     pady=self.pad_10, width=self.width)
        self.cipher_label.pack()

        tk.Label(left_panel, text='Дешифрование',
                 font=self.font, background=self.white, pady=self.pad_10, width=self.width, anchor='w').pack()
        tk.Button(left_panel, text="Выполнить дешифрование", background=self.grey, foreground='white',
                  pady=self.pad_5, padx=self.pad_10, font=self.font, command=self.decipher).pack()
        self.decipher_label = tk.Label(left_panel, text='', font=self.font, background=self.white,
                                       pady=self.pad_10, width=self.width)
        self.decipher_label.pack()

        # Кнопка просмотра расшифрованного файла
        tk.Button(left_panel, text="Просмотреть расшифрованный текст", background=self.grey, foreground='white',
                  pady=self.pad_5, padx=self.pad_10, font=self.font, command=self.view_decrypted).pack()

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
        log_message("Вариант 9: ГОСТ 28147-89 в режиме гаммирования с обратной связью")
        log_message("  - Блок: 64 бита (8 байт)")
        log_message("  - Ключ: 256 бит (32 байта) получается из MD4(пароля)")
        log_message("  - Синхропосылка: первые 8 байт MD4(пароля)")
        log_message("")
        log_message("Файлы сохраняются в папке support:")
        log_message("  - original.txt - исходный файл")
        log_message("  - encrypted.txt - зашифрованный файл (в hex-формате)")
        log_message("  - decrypted.txt - расшифрованный файл (читаемый текст)")

        root.mainloop()

    def view_decrypted(self):
        """Просмотр расшифрованного текста"""
        try:
            if not os.path.exists(self.filename_decipher):
                log_message("Ошибка: файл decrypted.txt не найден. Сначала выполните дешифрование.")
                return

            with open(self.filename_decipher, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            window = tk.Toplevel()
            window.title("Расшифрованный текст")
            window.geometry("800x600")
            window.configure(bg=self.white)

            text_widget = tk.Text(window, font=self.small_font, wrap=tk.WORD, bg=self.white)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            scrollbar = tk.Scrollbar(text_widget)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=text_widget.yview)

            text_widget.insert(tk.END, content)
            text_widget.config(state=tk.DISABLED)

            log_message("Открыто окно с расшифрованным текстом")
        except Exception as e:
            log_message(f"Ошибка при открытии файла: {str(e)}")

    def _get_key_and_sync(self, password_hash):
        """Получение ключа и синхропосылки из хеша пароля"""
        hash_bytes = password_hash.to_bytes(16, 'little')
        # Ключ ГОСТ: 256 бит = 32 байта (удваиваем 16-байтный хеш)
        key = bytearray()
        for i in range(2):
            key.extend(hash_bytes)
        # Синхропосылка: 8 байт (первые 8 байт хеша)
        sync_message = hash_bytes[:8]
        return bytes(key), sync_message

    def _update_progress(self, processed, total):
        """Обновление прогресса в логе"""
        if total == 0:
            return
        percent = (processed / total) * 100
        if int(percent) % 10 == 0 and percent > 0 and processed < total:
            log_message(f"  Прогресс: {processed}/{total} байт ({percent:.0f}%)")

    def set_password(self):
        """Установка пароля и создание ключей"""
        log_message("=== УСТАНОВКА ПАРОЛЯ ===")

        password_text = self.password_entry.get()

        if not password_text:
            log_message("Ошибка: пароль не введён")
            return

        log_message(f"Введён пароль: {password_text}")

        # Хеширование пароля MD4
        password_int = string_to_int(password_text)
        self.password_hash = md4(password_int)
        log_message(f"MD4 хеш пароля: {hex(self.password_hash)}")

        # Создание ключа и синхропосылки
        key, sync_message = self._get_key_and_sync(self.password_hash)
        log_message(f"Ключ ГОСТ (256 бит): {key.hex()[:32]}...")
        log_message(f"Синхропосылка (8 байт): {sync_message.hex()}")

        # Создание объекта шифра ГОСТ
        gost_cipher = GOSTCipher(key)
        self.gost_mode = GOSTGammaMode(gost_cipher, sync_message)

        self.password_display['text'] = f'Пароль установлен, хеш: {hex(self.password_hash)[:20]}...'
        log_message("Пароль успешно установлен, объект шифрования создан")

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

            with open(self.filename_temp, 'wb') as f:
                f.write(data)

            file_size = os.path.getsize(filepath)
            log_message(f"Загружен файл: {os.path.basename(filepath)}")
            log_message(f"Размер файла: {file_size} байт")
            log_message(f"Сохранён в: {self.filename_temp}")

            self.load_label['text'] = f'Файл загружен ({file_size} байт)'
            self.load_label['foreground'] = 'green'
        except Exception as e:
            self.load_label['text'] = f'Ошибка загрузки: {str(e)}'
            self.load_label['foreground'] = 'red'
            log_message(f"Ошибка загрузки: {str(e)}")

    def cipher(self):
        """Шифрование ГОСТ в режиме гаммирования с обратной связью"""
        log_message("=== ШИФРОВАНИЕ (ГОСТ с гаммированием) ===")

        if self.gost_mode is None:
            self.cipher_label['text'] = 'Сначала установите пароль'
            self.cipher_label['foreground'] = 'red'
            log_message("Ошибка: пароль не установлен")
            return

        try:
            with open(self.filename_temp, 'rb') as f:
                data = f.read()

            if not data:
                log_message("Ошибка: файл с данными пуст")
                return

            log_message(f"Исходные данные: {len(data)} байт")
            log_message("Начало шифрования...")

            # Шифрование ГОСТ в режиме гаммирования с обратной связью
            encrypted = self.gost_mode.encrypt(data, self._update_progress)

            # Сохраняем зашифрованные данные в hex-формате (чтобы можно было открыть в txt)
            with open(self.filename_cipher, 'w', encoding='utf-8') as f:
                f.write(encrypted.hex())

            log_message(f"Шифрование завершено. Результат: {len(encrypted)} байт")
            log_message(f"Сохранён в: {self.filename_cipher}")

            self.cipher_label['text'] = f'Шифрование выполнено, результат в encrypted.txt'
            self.cipher_label['foreground'] = 'green'
        except Exception as e:
            self.cipher_label['text'] = f'Ошибка шифрования: {str(e)}'
            self.cipher_label['foreground'] = 'red'
            log_message(f"Ошибка шифрования: {str(e)}")

    def decipher(self):
        """Дешифрование ГОСТ в режиме гаммирования с обратной связью"""
        log_message("=== ДЕШИФРОВАНИЕ (ГОСТ с гаммированием) ===")

        if self.gost_mode is None:
            self.decipher_label['text'] = 'Сначала установите пароль'
            self.decipher_label['foreground'] = 'red'
            log_message("Ошибка: пароль не установлен")
            return

        try:
            # Читаем зашифрованные данные из hex-файла
            with open(self.filename_cipher, 'r', encoding='utf-8') as f:
                hex_data = f.read().strip()

            if not hex_data:
                log_message("Ошибка: файл с шифротекстом пуст")
                return

            encrypted = bytes.fromhex(hex_data)
            log_message(f"Зашифрованные данные: {len(encrypted)} байт")
            log_message("Начало дешифрования...")

            # Дешифрование (симметрично шифрованию)
            decrypted = self.gost_mode.decrypt(encrypted, self._update_progress)

            # Пытаемся сохранить как текст (декодируем в utf-8, если возможно)
            try:
                # Пробуем декодировать как текст
                decrypted_text = decrypted.decode('utf-8')
                with open(self.filename_decipher, 'w', encoding='utf-8') as f:
                    f.write(decrypted_text)
                log_message("Расшифрованные данные сохранены как текст")
            except UnicodeDecodeError:
                # Если не текст, сохраняем как есть
                with open(self.filename_decipher, 'wb') as f:
                    f.write(decrypted)
                log_message("Расшифрованные данные сохранены в бинарном формате")

            log_message(f"Дешифрование завершено. Размер результата: {len(decrypted)} байт")
            log_message(f"Сохранён в: {self.filename_decipher}")

            self.decipher_label['text'] = f'Дешифрование выполнено, результат в decrypted.txt'
            self.decipher_label['foreground'] = 'green'
        except Exception as e:
            self.decipher_label['text'] = f'Ошибка дешифрования: {str(e)}'
            self.decipher_label['foreground'] = 'red'
            log_message(f"Ошибка дешифрования: {str(e)}")


if __name__ == "__main__":
    if not os.path.exists('support'):
        os.makedirs('support')

    gui = GUI()
    gui.start()