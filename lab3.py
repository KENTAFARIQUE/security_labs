# coding=utf-8

from random import randint, choice
from math import gcd
import tkinter as tk
from tkinter import filedialog, ttk
import os
import math

b32 = 0xffffffff
b64 = 0xffffffffffffffff
b80 = 0x80000000

# ==================== ТАБЛИЦА ПОДСТАНОВКИ ДЛЯ MaHash3 ====================

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


def log_message(message):
    """Добавление сообщения в лог"""
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)


def left_rotate(x, n, bits=32):
    """Циклический сдвиг влево"""
    mask = (1 << bits) - 1
    return ((x << n) & mask) | (x >> (bits - n))


def right_rotate(x, n, bits=32):
    """Циклический сдвиг вправо"""
    mask = (1 << bits) - 1
    return (x >> n) | ((x & ((1 << n) - 1)) << (bits - n)) & mask


def string_to_int(s):
    """Преобразование строки в целое число (битовое представление)"""
    result = 0
    for ch in s:
        result = (result << 8) | ord(ch)
    return result


# ==================== ГЕНЕРАТОРЫ ИЗ ВТОРОЙ РАБОТЫ ====================

def linear_congruential_generator(n):
    """
    Линейный конгруэнтный генератор (ЛКГ)
    Формула: X_{i+1} = (a * X_i + c) mod m
    """
    if n <= 0:
        return 0

    a = 1103515245
    c = 12345
    m = 2 ** 31

    x = randint(1, m - 1)
    result = 0
    bits_generated = 0

    while bits_generated < n:
        x = (a * x + c) % m
        temp = x

        while temp > 1 and bits_generated < n:
            result = (result << 1) | (temp & 1)
            bits_generated += 1
            temp >>= 1

        if bits_generated < n:
            result = (result << 1) | (temp & 1)
            bits_generated += 1

    return result


def additive_generator(n):
    """
    Аддитивный генератор (запаздывающий генератор Фибоначчи)
    Формула: X_i = (X_{i-55} + X_{i-24}) mod 2^32
    """
    if n <= 0:
        return 0

    m = 2 ** 32
    j = 55
    k = 24

    state = [randint(0, m - 1) for _ in range(j)]
    result = 0
    idx = 0
    bits_generated = 0

    while bits_generated < n:
        new_value = (state[idx] + state[(idx + j - k) % j]) % m
        state[idx] = new_value
        idx = (idx + 1) % j

        temp = new_value
        while temp > 1 and bits_generated < n:
            result = (result << 1) | (temp & 1)
            bits_generated += 1
            temp >>= 1

        if bits_generated < n:
            result = (result << 1) | (temp & 1)
            bits_generated += 1

    return result


def rsa_generator(n):
    """
    RSA генератор псевдослучайных чисел (алгоритм BBS - Blum Blum Shub)
    X_{i+1} = X_i^2 mod N, где N = p * q, p и q - простые числа вида 4k+3
    """
    if n <= 0:
        return 0

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
    result = 0

    for _ in range(n):
        x = (x * x) % N
        result = (result << 1) | (x & 1)

    return result


# ==================== MD4 ХЕШ-ФУНКЦИЯ ====================

def md4_f(x, y, z):
    return (x & y) | (~x & z)


def md4_g(x, y, z):
    return (x & y) | (x & z) | (y & z)


def md4_h(x, y, z):
    return x ^ y ^ z


def md4_operation(a, b, c, d, func, xk, s, const):
    """Операция для MD4"""
    result = (a + func(b, c, d) + xk + const) & b32
    result = left_rotate(result, s, 32)
    return result


def md4(message):
    """
    MD4 хеш-функция
    Вход: целое число (битовое представление сообщения)
    Выход: 128-битный хеш
    """
    log_message("=== MD4 хеширование ===")

    # Добавляем бит равный 1 к сообщению
    m = message
    m = (m << 1) | 1
    n = len(bin(m)) - 2

    # Расширяем сообщение до длины 448 mod 512
    while n % 512 < 448:
        m = m << 1
        n += 1

    # Добавляем 64-битное представление длины
    m = (m << 32) | (n & b32)
    m = (m << 32) | ((n >> 32) & b32)
    n += 64
    n = n // 32

    # Инициализация буфера
    a = 0x67452301
    b = 0xefcdab89
    c = 0x98badcfe
    d = 0x10325476

    log_message(f"Начальные значения: a={hex(a)}, b={hex(b)}, c={hex(c)}, d={hex(d)}")

    # Константы
    gc = 0x5a827999
    hc = 0x6ed9eba1

    x = [0] * 16

    for i in range(0, n // 16):
        for j in range(0, 16):
            x[j] = m & b32
            m = m >> 32

        aa, bb, cc, dd = a, b, c, d

        # Раунд 1
        a = md4_operation(a, b, c, d, md4_f, x[0], 3, 0)
        d = md4_operation(d, a, b, c, md4_f, x[1], 7, 0)
        c = md4_operation(c, d, a, b, md4_f, x[2], 11, 0)
        b = md4_operation(b, c, d, a, md4_f, x[3], 19, 0)
        a = md4_operation(a, b, c, d, md4_f, x[4], 3, 0)
        d = md4_operation(d, a, b, c, md4_f, x[5], 7, 0)
        c = md4_operation(c, d, a, b, md4_f, x[6], 11, 0)
        b = md4_operation(b, c, d, a, md4_f, x[7], 19, 0)
        a = md4_operation(a, b, c, d, md4_f, x[8], 3, 0)
        d = md4_operation(d, a, b, c, md4_f, x[9], 7, 0)
        c = md4_operation(c, d, a, b, md4_f, x[10], 11, 0)
        b = md4_operation(b, c, d, a, md4_f, x[11], 19, 0)
        a = md4_operation(a, b, c, d, md4_f, x[12], 3, 0)
        d = md4_operation(d, a, b, c, md4_f, x[13], 7, 0)
        c = md4_operation(c, d, a, b, md4_f, x[14], 11, 0)
        b = md4_operation(b, c, d, a, md4_f, x[15], 19, 0)

        # Раунд 2
        a = md4_operation(a, b, c, d, md4_g, x[0], 3, gc)
        d = md4_operation(d, a, b, c, md4_g, x[4], 5, gc)
        c = md4_operation(c, d, a, b, md4_g, x[8], 9, gc)
        b = md4_operation(b, c, d, a, md4_g, x[12], 13, gc)
        a = md4_operation(a, b, c, d, md4_g, x[1], 3, gc)
        d = md4_operation(d, a, b, c, md4_g, x[5], 5, gc)
        c = md4_operation(c, d, a, b, md4_g, x[9], 9, gc)
        b = md4_operation(b, c, d, a, md4_g, x[13], 13, gc)
        a = md4_operation(a, b, c, d, md4_g, x[2], 3, gc)
        d = md4_operation(d, a, b, c, md4_g, x[6], 5, gc)
        c = md4_operation(c, d, a, b, md4_g, x[10], 9, gc)
        b = md4_operation(b, c, d, a, md4_g, x[14], 13, gc)
        a = md4_operation(a, b, c, d, md4_g, x[3], 3, gc)
        d = md4_operation(d, a, b, c, md4_g, x[7], 5, gc)
        c = md4_operation(c, d, a, b, md4_g, x[11], 9, gc)
        b = md4_operation(b, c, d, a, md4_g, x[15], 13, gc)

        # Раунд 3
        a = md4_operation(a, b, c, d, md4_h, x[0], 3, hc)
        d = md4_operation(d, a, b, c, md4_h, x[8], 9, hc)
        c = md4_operation(c, d, a, b, md4_h, x[4], 11, hc)
        b = md4_operation(b, c, d, a, md4_h, x[12], 15, hc)
        a = md4_operation(a, b, c, d, md4_h, x[2], 3, hc)
        d = md4_operation(d, a, b, c, md4_h, x[10], 9, hc)
        c = md4_operation(c, d, a, b, md4_h, x[6], 11, hc)
        b = md4_operation(b, c, d, a, md4_h, x[14], 15, hc)
        a = md4_operation(a, b, c, d, md4_h, x[1], 3, hc)
        d = md4_operation(d, a, b, c, md4_h, x[9], 9, hc)
        c = md4_operation(c, d, a, b, md4_h, x[5], 11, hc)
        b = md4_operation(b, c, d, a, md4_h, x[13], 15, hc)
        a = md4_operation(a, b, c, d, md4_h, x[3], 3, hc)
        d = md4_operation(d, a, b, c, md4_h, x[11], 9, hc)
        c = md4_operation(c, d, a, b, md4_h, x[7], 11, hc)
        b = md4_operation(b, c, d, a, md4_h, x[15], 15, hc)

        # Сложение
        a = (a + aa) & b32
        b = (b + bb) & b32
        c = (c + cc) & b32
        d = (d + dd) & b32

        log_message(f"Блок {i + 1}: a={hex(a)}, b={hex(b)}, c={hex(c)}, d={hex(d)}")

    # Конкатенация
    result = (d << 96) | (c << 64) | (b << 32) | a
    log_message(f"MD4 хеш: {hex(result)}")
    log_message("")
    return result


# ==================== MaHash3 ХЕШ-ФУНКЦИЯ ====================

def mahash3(message):
    """
    MaHash3 хеш-функция
    Вход: целое число (битовое представление сообщения)
    Выход: 32-битный хеш
    """
    log_message("=== MaHash3 хеширование ===")

    # Преобразуем число в байтовую строку
    hex_str = hex(message)[2:]
    if len(hex_str) % 2:
        hex_str = '0' + hex_str
    data = bytes.fromhex(hex_str)

    length = len(data)
    log_message(f"Длина сообщения в байтах: {length}")

    # Макросы для MaHash3
    def LROT(x):
        return left_rotate(x, 11, 32)

    def RROT(x):
        return right_rotate(x, 11, 32)

    # Инициализация
    hash1 = length
    hash2 = length
    log_message(f"Начальные значения: hash1={hash1}, hash2={hash2}")

    for i in range(length):
        idx = (data[i] + i) & 255
        val = sTable[idx]

        hash1 += val
        hash1 = LROT(hash1 + ((hash1 << 6) ^ (hash1 >> 8)))

        hash2 += sTable[(val + 1) & 255]
        hash2 = RROT(hash2 + ((hash2 << 6) ^ (hash2 >> 8)))

        # Обмен
        t = hash1
        hash1 = hash2
        hash2 = t

        # Дополнительные преобразования
        hash1 = LROT(hash1 + ((hash1 << 6) ^ (hash1 >> 8)))
        hash1 += sTable[length & 255]

        hash2 = RROT(hash2 + ((hash2 << 6) ^ (hash2 >> 8)))
        hash2 += sTable[length & 255]

    result = hash1 ^ hash2
    log_message(f"MaHash3 хеш: {hex(result)}")
    log_message("")
    return result


# ==================== MD5 ХЕШ-ФУНКЦИЯ ====================

MD5_S = [
    7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
    5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
    4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
    6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21
]

MD5_K = [int(math.floor(abs(math.sin(i + 1)) * (2 ** 32))) & 0xffffffff for i in range(64)]


def md5_f(x, y, z):
    return (x & y) | (~x & z)


def md5_g(x, y, z):
    return (x & z) | (y & ~z)


def md5_h(x, y, z):
    return x ^ y ^ z


def md5_i(x, y, z):
    return y ^ (x | ~z)


def md5_operation(a, b, c, d, k, s, i, func):
    """Операция для MD5"""
    result = (a + func(b, c, d) + MD5_K[i] + k) & b32
    result = left_rotate(result, s, 32)
    result = (b + result) & b32
    return result


def md5(message):
    """
    MD5 хеш-функция
    Вход: целое число (битовое представление сообщения)
    Выход: 128-битный хеш
    """
    log_message("=== MD5 хеширование ===")

    # Добавляем бит равный 1 к сообщению
    m = message
    m = (m << 1) | 1
    n = len(bin(m)) - 2

    # Расширяем сообщение до длины 448 mod 512
    while n % 512 < 448:
        m = m << 1
        n += 1

    # Добавляем 64-битное представление длины
    m = (m << 32) | (n & b32)
    m = (m << 32) | ((n >> 32) & b32)
    n += 64
    n = n // 32

    # Инициализация буфера
    a = 0x67452301
    b = 0xefcdab89
    c = 0x98badcfe
    d = 0x10325476

    log_message(f"Начальные значения: a={hex(a)}, b={hex(b)}, c={hex(c)}, d={hex(d)}")

    x = [0] * 16

    for i in range(0, n // 16):
        for j in range(0, 16):
            x[j] = m & b32
            m = m >> 32

        aa, bb, cc, dd = a, b, c, d

        # Раунд 1
        a = md5_operation(a, b, c, d, x[0], MD5_S[0], 0, md5_f)
        d = md5_operation(d, a, b, c, x[1], MD5_S[1], 1, md5_f)
        c = md5_operation(c, d, a, b, x[2], MD5_S[2], 2, md5_f)
        b = md5_operation(b, c, d, a, x[3], MD5_S[3], 3, md5_f)
        a = md5_operation(a, b, c, d, x[4], MD5_S[4], 4, md5_f)
        d = md5_operation(d, a, b, c, x[5], MD5_S[5], 5, md5_f)
        c = md5_operation(c, d, a, b, x[6], MD5_S[6], 6, md5_f)
        b = md5_operation(b, c, d, a, x[7], MD5_S[7], 7, md5_f)
        a = md5_operation(a, b, c, d, x[8], MD5_S[8], 8, md5_f)
        d = md5_operation(d, a, b, c, x[9], MD5_S[9], 9, md5_f)
        c = md5_operation(c, d, a, b, x[10], MD5_S[10], 10, md5_f)
        b = md5_operation(b, c, d, a, x[11], MD5_S[11], 11, md5_f)
        a = md5_operation(a, b, c, d, x[12], MD5_S[12], 12, md5_f)
        d = md5_operation(d, a, b, c, x[13], MD5_S[13], 13, md5_f)
        c = md5_operation(c, d, a, b, x[14], MD5_S[14], 14, md5_f)
        b = md5_operation(b, c, d, a, x[15], MD5_S[15], 15, md5_f)

        # Раунд 2
        a = md5_operation(a, b, c, d, x[1], MD5_S[16], 16, md5_g)
        d = md5_operation(d, a, b, c, x[6], MD5_S[17], 17, md5_g)
        c = md5_operation(c, d, a, b, x[11], MD5_S[18], 18, md5_g)
        b = md5_operation(b, c, d, a, x[0], MD5_S[19], 19, md5_g)
        a = md5_operation(a, b, c, d, x[5], MD5_S[20], 20, md5_g)
        d = md5_operation(d, a, b, c, x[10], MD5_S[21], 21, md5_g)
        c = md5_operation(c, d, a, b, x[15], MD5_S[22], 22, md5_g)
        b = md5_operation(b, c, d, a, x[4], MD5_S[23], 23, md5_g)
        a = md5_operation(a, b, c, d, x[9], MD5_S[24], 24, md5_g)
        d = md5_operation(d, a, b, c, x[14], MD5_S[25], 25, md5_g)
        c = md5_operation(c, d, a, b, x[3], MD5_S[26], 26, md5_g)
        b = md5_operation(b, c, d, a, x[8], MD5_S[27], 27, md5_g)
        a = md5_operation(a, b, c, d, x[13], MD5_S[28], 28, md5_g)
        d = md5_operation(d, a, b, c, x[2], MD5_S[29], 29, md5_g)
        c = md5_operation(c, d, a, b, x[7], MD5_S[30], 30, md5_g)
        b = md5_operation(b, c, d, a, x[12], MD5_S[31], 31, md5_g)

        # Раунд 3
        a = md5_operation(a, b, c, d, x[5], MD5_S[32], 32, md5_h)
        d = md5_operation(d, a, b, c, x[8], MD5_S[33], 33, md5_h)
        c = md5_operation(c, d, a, b, x[11], MD5_S[34], 34, md5_h)
        b = md5_operation(b, c, d, a, x[14], MD5_S[35], 35, md5_h)
        a = md5_operation(a, b, c, d, x[1], MD5_S[36], 36, md5_h)
        d = md5_operation(d, a, b, c, x[4], MD5_S[37], 37, md5_h)
        c = md5_operation(c, d, a, b, x[7], MD5_S[38], 38, md5_h)
        b = md5_operation(b, c, d, a, x[10], MD5_S[39], 39, md5_h)
        a = md5_operation(a, b, c, d, x[13], MD5_S[40], 40, md5_h)
        d = md5_operation(d, a, b, c, x[0], MD5_S[41], 41, md5_h)
        c = md5_operation(c, d, a, b, x[3], MD5_S[42], 42, md5_h)
        b = md5_operation(b, c, d, a, x[6], MD5_S[43], 43, md5_h)
        a = md5_operation(a, b, c, d, x[9], MD5_S[44], 44, md5_h)
        d = md5_operation(d, a, b, c, x[12], MD5_S[45], 45, md5_h)
        c = md5_operation(c, d, a, b, x[15], MD5_S[46], 46, md5_h)
        b = md5_operation(b, c, d, a, x[2], MD5_S[47], 47, md5_h)

        # Раунд 4
        a = md5_operation(a, b, c, d, x[0], MD5_S[48], 48, md5_i)
        d = md5_operation(d, a, b, c, x[7], MD5_S[49], 49, md5_i)
        c = md5_operation(c, d, a, b, x[14], MD5_S[50], 50, md5_i)
        b = md5_operation(b, c, d, a, x[5], MD5_S[51], 51, md5_i)
        a = md5_operation(a, b, c, d, x[12], MD5_S[52], 52, md5_i)
        d = md5_operation(d, a, b, c, x[3], MD5_S[53], 53, md5_i)
        c = md5_operation(c, d, a, b, x[10], MD5_S[54], 54, md5_i)
        b = md5_operation(b, c, d, a, x[1], MD5_S[55], 55, md5_i)
        a = md5_operation(a, b, c, d, x[8], MD5_S[56], 56, md5_i)
        d = md5_operation(d, a, b, c, x[15], MD5_S[57], 57, md5_i)
        c = md5_operation(c, d, a, b, x[6], MD5_S[58], 58, md5_i)
        b = md5_operation(b, c, d, a, x[13], MD5_S[59], 59, md5_i)
        a = md5_operation(a, b, c, d, x[4], MD5_S[60], 60, md5_i)
        d = md5_operation(d, a, b, c, x[11], MD5_S[61], 61, md5_i)
        c = md5_operation(c, d, a, b, x[2], MD5_S[62], 62, md5_i)
        b = md5_operation(b, c, d, a, x[9], MD5_S[63], 63, md5_i)

        # Сложение
        a = (a + aa) & b32
        b = (b + bb) & b32
        c = (c + cc) & b32
        d = (d + dd) & b32

        log_message(f"Блок {i + 1}: a={hex(a)}, b={hex(b)}, c={hex(c)}, d={hex(d)}")

    # Конкатенация
    result = (a << 96) | (b << 64) | (c << 32) | d
    log_message(f"MD5 хеш: {hex(result)}")
    log_message("")
    return result


class GUI:
    def __init__(self):
        self.filename_data = 'support/bin_data.txt'
        self.filename_cipher = 'support/cipher.txt'
        self.filename_decipher = 'support/decipher.txt'

        self.width = 60
        self.font = ("Arial", 11)
        self.small_font = ("Arial", 9)
        self.white = '#eee'
        self.grey = '#444'
        self.dark_grey = '#333'
        self.pad_10 = 10
        self.pad_5 = 5

        # Генераторы из второй работы (вариант 9)
        self.generators = ('Линейный конгруэнтный генератор', 'Аддитивный генератор', 'RSA генератор (BBS)')

        # Хеш-функции для варианта 9
        self.hash_functions = ('MD4', 'MaHash3', 'MD5')

        self.combo_gen = None
        self.combo_hash = None
        self.gen_label = None
        self.load_label = None
        self.cipher_label = None
        self.decipher_label = None
        self.hash_label = None
        self.password_entry = None
        self.password_mode = None

        self.password = None
        self.password_len = 430
        self.gamma = None

    def start(self):
        root = tk.Tk()
        root.title("Лабораторная работа №3 (Вариант 9) - Валиуллов Р.Р., ИВТИИбд-31")
        root.geometry("900x1000")
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

        # ==================== ВВОД ТЕКСТОВОГО ПАРОЛЯ ====================

        tk.Label(left_panel, text='Введите текстовый пароль (будет хеширован):',
                 font=self.font, background=self.white, pady=self.pad_10, width=self.width, anchor='w').pack()

        self.password_entry = tk.Entry(left_panel, font=self.font, width=40, justify='center')
        self.password_entry.pack()
        self.password_entry.insert(0, "123123qwe")

        # Выбор хеш-функции для пароля
        tk.Label(left_panel, text='Выберите хеш-функцию для пароля:',
                 font=self.font, background=self.white, pady=self.pad_10, width=self.width, anchor='w').pack()

        self.combo_hash = ttk.Combobox(left_panel, values=self.hash_functions, width=35, font=self.font)
        self.combo_hash.current(0)
        self.combo_hash.pack()

        tk.Label(left_panel, text='', font=self.font, background=self.white).pack()
        tk.Button(left_panel, text="Хешировать пароль и установить как ключ", background=self.grey,
                  foreground='white', pady=self.pad_5, padx=self.pad_10, font=self.font,
                  command=self.hash_password).pack()

        self.hash_label = tk.Label(left_panel, text='', font=self.font, background=self.white,
                                   pady=self.pad_10, width=self.width)
        self.hash_label.pack()

        # Разделитель
        separator2 = tk.Label(left_panel, text='─────────────────────────────────────────────────────────────',
                              font=self.font, background=self.white, pady=self.pad_5)
        separator2.pack()

        # ==================== ГЕНЕРАЦИЯ ПАРОЛЯ ЧЕРЕЗ ГЕНЕРАТОР ====================

        tk.Label(left_panel, text='ИЛИ сгенерируйте пароль через генератор:',
                 font=self.font, background=self.white, pady=self.pad_10, width=self.width, anchor='w').pack()

        # Выбор генератора для пароля
        tk.Label(left_panel, text='Выберите генератор:',
                 font=self.font, background=self.white, pady=self.pad_5, width=self.width, anchor='w').pack()

        self.combo_gen = ttk.Combobox(left_panel, values=self.generators, width=35, font=self.font)
        self.combo_gen.current(0)
        self.combo_gen.pack()

        # Выбор хеш-функции для генератора
        tk.Label(left_panel, text='Выберите хеш-функцию для генератора:',
                 font=self.font, background=self.white, pady=self.pad_10, width=self.width, anchor='w').pack()

        self.combo_hash_gen = ttk.Combobox(left_panel, values=self.hash_functions, width=35, font=self.font)
        self.combo_hash_gen.current(0)
        self.combo_hash_gen.pack()

        tk.Label(left_panel, text='', font=self.font, background=self.white).pack()
        tk.Button(left_panel, text="Сгенерировать и хешировать пароль", background=self.grey,
                  foreground='white', pady=self.pad_5, padx=self.pad_10, font=self.font,
                  command=self.create_password).pack()
        self.gen_label = tk.Label(left_panel, text='', font=self.font, background=self.white,
                                  pady=self.pad_10, width=self.width)
        self.gen_label.pack()

        # Разделитель
        separator3 = tk.Label(left_panel, text='─────────────────────────────────────────────────────────────',
                              font=self.font, background=self.white, pady=self.pad_5)
        separator3.pack()

        # ==================== ШИФРОВАНИЕ/ДЕШИФРОВАНИЕ ====================

        # Шифрование
        tk.Label(left_panel, text='Шифрование',
                 font=self.font, background=self.white, pady=self.pad_10, width=self.width, anchor='w').pack()
        tk.Button(left_panel, text="Выполнить шифрование", background=self.grey, foreground='white',
                  pady=self.pad_5, padx=self.pad_10, font=self.font, command=self.cipher).pack()
        self.cipher_label = tk.Label(left_panel, text='', font=self.font, background=self.white,
                                     pady=self.pad_10, width=self.width)
        self.cipher_label.pack()

        # Дешифрование
        tk.Label(left_panel, text='Дешифрование',
                 font=self.font, background=self.white, pady=self.pad_10, width=self.width, anchor='w').pack()
        tk.Button(left_panel, text="Выполнить дешифрование", background=self.grey, foreground='white',
                  pady=self.pad_5, padx=self.pad_10, font=self.font, command=self.decipher).pack()
        self.decipher_label = tk.Label(left_panel, text='', font=self.font, background=self.white,
                                       pady=self.pad_10, width=self.width)
        self.decipher_label.pack()

        # Просмотр хеша
        tk.Label(left_panel, text='', font=('Arial', 5), background=self.white).pack()
        tk.Button(left_panel, text="Просмотр текущего хеш-значения ключа", background=self.grey,
                  foreground='white', pady=self.pad_5, padx=self.pad_10, font=self.font,
                  command=self.print_password).pack()
        self.password_display = tk.Label(left_panel, text='', font=self.font, background=self.white,
                                         pady=self.pad_10, width=self.width)
        self.password_display.pack()

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
        log_message("Вариант 9: Линейный конгруэнтный, Аддитивный, RSA генераторы")
        log_message("Хеш-функции: MD4, MaHash3, MD5")
        log_message("Доступно: хеширование текстового пароля ИЛИ генерация через генератор")

        root.mainloop()

    def hash_password(self):
        """Хеширование текстового пароля, введённого пользователем"""
        log_message("=== ХЕШИРОВАНИЕ ТЕКСТОВОГО ПАРОЛЯ ===")

        password_text = self.password_entry.get()
        hash_type = self.combo_hash.get()

        if not password_text:
            self.hash_label['text'] = 'Ошибка: введите пароль'
            self.hash_label['foreground'] = 'red'
            log_message("Ошибка: пароль не введён")
            return

        log_message(f"Введён пароль: {password_text}")
        log_message(f"Выбрана хеш-функция: {hash_type}")

        # Преобразуем строку в число
        password_int = string_to_int(password_text)
        log_message(f"Пароль в числовом виде: {hex(password_int)}")

        # Хеширование пароля
        if hash_type == self.hash_functions[0]:
            password_hash = md4(password_int)
        elif hash_type == self.hash_functions[1]:
            password_hash = mahash3(password_int)
        elif hash_type == self.hash_functions[2]:
            password_hash = md5(password_int)
        else:
            self.hash_label['text'] = 'Ошибка: неизвестная хеш-функция'
            self.hash_label['foreground'] = 'red'
            log_message("Ошибка: неизвестная хеш-функция")
            return

        self.password = PasswordGenerator(password_hash)

        self.hash_label['text'] = f'Пароль захеширован через {hash_type}'
        self.hash_label['foreground'] = 'green'
        self.password_display['text'] = f'Хеш ключа: {hex(password_hash)}'
        log_message("Пароль успешно захеширован и установлен как ключ шифрования")

    def create_password(self):
        """Создание и хеширование пароля через генератор"""
        log_message("=== ГЕНЕРАЦИЯ ПАРОЛЯ ЧЕРЕЗ ГЕНЕРАТОР ===")

        gen_type = self.combo_gen.get()
        hash_type = self.combo_hash_gen.get()

        log_message(f"Выбран генератор: {gen_type}")
        log_message(f"Выбрана хеш-функция: {hash_type}")

        # Генерация псевдослучайной последовательности
        if gen_type == self.generators[0]:
            password_bits = linear_congruential_generator(self.password_len)
            log_message(f"Линейный конгруэнтный генератор: сгенерировано {self.password_len} бит")
        elif gen_type == self.generators[1]:
            password_bits = additive_generator(self.password_len)
            log_message(f"Аддитивный генератор: сгенерировано {self.password_len} бит")
        elif gen_type == self.generators[2]:
            password_bits = rsa_generator(self.password_len)
            log_message(f"RSA генератор (BBS): сгенерировано {self.password_len} бит")
        else:
            self.gen_label['text'] = 'Ошибка генерации'
            self.gen_label['foreground'] = 'red'
            log_message("Ошибка: неизвестный генератор")
            return

        # Хеширование пароля
        if hash_type == self.hash_functions[0]:
            password_hash = md4(password_bits)
        elif hash_type == self.hash_functions[1]:
            password_hash = mahash3(password_bits)
        elif hash_type == self.hash_functions[2]:
            password_hash = md5(password_bits)
        else:
            self.gen_label['text'] = 'Ошибка: неизвестная хеш-функция'
            self.gen_label['foreground'] = 'red'
            log_message("Ошибка: неизвестная хеш-функция")
            return

        self.password = PasswordGenerator(password_hash)

        self.gen_label['text'] = 'Пароль сгенерирован, хеширован и сохранен'
        self.gen_label['foreground'] = 'green'
        self.password_display['text'] = f'Хеш ключа: {hex(password_hash)}'
        log_message("Пароль успешно сгенерирован и сохранен")

    def print_password(self):
        """Печать хеш-значения текущего ключа"""
        if self.password is None:
            self.password_display['text'] = 'Сначала сгенерируйте или захешируйте пароль'
            log_message("Ошибка: ключ не установлен")
            return

        hash_value = hex(self.password.print())
        self.password_display['text'] = f'Хеш ключа: {hash_value}'
        log_message(f"Текущий хеш ключа: {hash_value}")

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

            # Преобразование в двоичный вид
            binary_str = ''
            for byte in data:
                binary_str += format(byte, '08b')

            with open(self.filename_data, 'w') as f:
                f.write(binary_str)

            with open(self.filename_cipher, 'w') as f:
                f.write(binary_str)

            file_size = os.path.getsize(filepath)
            log_message(f"Загружен файл: {filepath}")
            log_message(f"Размер файла: {file_size} байт ({len(binary_str)} бит)")

            self.load_label['text'] = f'Файл загружен ({file_size} байт)'
            self.load_label['foreground'] = 'green'
        except Exception as e:
            self.load_label['text'] = f'Ошибка загрузки: {str(e)}'
            self.load_label['foreground'] = 'red'
            log_message(f"Ошибка загрузки: {str(e)}")

    def cipher(self):
        """Шифрование"""
        log_message("=== ШИФРОВАНИЕ ===")

        if self.password is None:
            self.cipher_label['text'] = 'Сначала установите ключ (через хеширование пароля или генерацию)'
            self.cipher_label['foreground'] = 'red'
            log_message("Ошибка: ключ не установлен")
            return

        try:
            with open(self.filename_data, 'r') as f:
                data_bits = f.readline().strip()

            if not data_bits:
                log_message("Ошибка: файл с данными пуст")
                return

            n = len(data_bits)
            log_message(f"Данные для шифрования: {n} бит")

            # Преобразование в целое число
            data_int = int(data_bits, 2) if data_bits else 0

            # XOR шифрование
            cipher_bits = ''
            self.password.counter = -1
            bytes_processed = 0

            for i in range(0, n, 128):
                gamma = self.password.gamma()
                block_size = min(128, n - i)

                for j in range(block_size):
                    data_bit = (data_int >> (n - i - j - 1)) & 1
                    gamma_bit = (gamma >> (block_size - j - 1)) & 1
                    cipher_bits += str(data_bit ^ gamma_bit)

                bytes_processed += block_size // 8
                if bytes_processed % 1024 == 0 and bytes_processed > 0:
                    log_message(f"Зашифровано {bytes_processed} байт")

            with open(self.filename_cipher, 'w') as f:
                f.write(cipher_bits)

            log_message(f"Шифрование завершено. Результат: {len(cipher_bits)} бит")

            self.cipher_label['text'] = 'Шифрование выполнено, результат в cipher.txt'
            self.cipher_label['foreground'] = 'green'
        except Exception as e:
            self.cipher_label['text'] = f'Ошибка шифрования: {str(e)}'
            self.cipher_label['foreground'] = 'red'
            log_message(f"Ошибка шифрования: {str(e)}")

    def decipher(self):
        """Дешифрование"""
        log_message("=== ДЕШИФРОВАНИЕ ===")

        if self.password is None:
            self.decipher_label['text'] = 'Сначала установите ключ (через хеширование пароля или генерацию)'
            self.decipher_label['foreground'] = 'red'
            log_message("Ошибка: ключ не установлен")
            return

        try:
            with open(self.filename_cipher, 'r') as f:
                cipher_bits = f.readline().strip()

            if not cipher_bits:
                log_message("Ошибка: файл с шифротекстом пуст")
                return

            n = len(cipher_bits)
            log_message(f"Данные для дешифрования: {n} бит")

            cipher_int = int(cipher_bits, 2) if cipher_bits else 0

            # XOR дешифрование (то же самое, что и шифрование)
            plain_bits = ''
            self.password.counter = -1
            bytes_processed = 0

            for i in range(0, n, 128):
                gamma = self.password.gamma()
                block_size = min(128, n - i)

                for j in range(block_size):
                    cipher_bit = (cipher_int >> (n - i - j - 1)) & 1
                    gamma_bit = (gamma >> (block_size - j - 1)) & 1
                    plain_bits += str(cipher_bit ^ gamma_bit)

                bytes_processed += block_size // 8
                if bytes_processed % 1024 == 0 and bytes_processed > 0:
                    log_message(f"Расшифровано {bytes_processed} байт")

            # Преобразование из битов в байты
            plain_bytes = bytearray()
            for i in range(0, len(plain_bits), 8):
                if i + 8 <= len(plain_bits):
                    byte_val = int(plain_bits[i:i + 8], 2)
                    plain_bytes.append(byte_val)

            with open(self.filename_decipher, 'wb') as f:
                f.write(plain_bytes)

            log_message(f"Дешифрование завершено. Размер результата: {len(plain_bytes)} байт")

            self.decipher_label['text'] = 'Дешифрование выполнено, результат в decipher.txt'
            self.decipher_label['foreground'] = 'green'
        except Exception as e:
            self.decipher_label['text'] = f'Ошибка дешифрования: {str(e)}'
            self.decipher_label['foreground'] = 'red'
            log_message(f"Ошибка дешифрования: {str(e)}")


class PasswordGenerator:
    """Генератор пароля с хешированием"""

    def __init__(self, hash_value):
        self.counter = -1
        self.hash_value = hash_value

    def gamma(self):
        """Подсчет гаммы для потокового шифрования"""
        self.counter += 1
        # Используем MD4 для генерации гаммы (потоковый режим)
        data = (self.hash_value << 32) | (self.counter & 0xffffffff)
        return md4(data)

    def print(self):
        return self.hash_value


if __name__ == "__main__":
    # Создаём директорию support если её нет
    if not os.path.exists('support'):
        os.makedirs('support')

    gui = GUI()
    gui.start()