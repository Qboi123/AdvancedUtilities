import random
import string


class Random(random.Random):
    # noinspection PyAttributeOutsideInit
    def seed(self, a=None, version=2):
        from os import urandom as _urandom
        from hashlib import sha512 as _sha512
        if a is None:
            try:
                # Seed with enough bytes to span the 19937 bit
                # state space for the Mersenne Twister
                a = int.from_bytes(_urandom(2500), 'big')
            except NotImplementedError:
                import time
                a = int(time.time() * 256)  # use fractional seconds

        if version == 2:
            if isinstance(a, (str, bytes, bytearray)):
                if isinstance(a, str):
                    a = a.encode()
                a += _sha512(a).digest()
                a = int.from_bytes(a, 'big')

        self._current_seed = a
        super().seed(a)

    def getseed(self):
        return self._current_seed

    def randomstring(self, length, symbols=string.ascii_letters):
        s = ""
        symbols_list = list(symbols)
        for _ in range(length):
            s += self.choice(symbols_list)
        return s

    def randombytes(self, length, range_: range):
        b = b''

        if range_.start < 0:
            raise ValueError("Range start must be between 0 and 255")
        elif range_.start > 255:
            raise ValueError("Range start must be between 0 and 255")
        if range_.stop < 0:
            raise ValueError("Range stop must be between 0 and 255")
        elif range_.stop > 255:
            raise ValueError("Range stop must be between 0 and 255")
        for _ in range(length):
            rand = self.randrange(range_.start, range_.stop, range_.step)
            integer = int(rand)
            b += integer.to_bytes(1, "little")
        return b

    def randomhex(self, range_: range):
        rand = self.randrange(range_.start, range_.stop, range_.step)
        hexadecimal = hex(int(rand))
        return hexadecimal

    def randomfloat(self, min_, max_):
        rand: float = self.random()
        out = (rand * (max_ - min_)) + min_
        return out


# fast math algorithms
class FastRandom(object):
    def __init__(self, seed):
        self.seed = seed

    def randint(self):
        self.seed = (214013 * self.seed + 2531011)
        return (self.seed >> 16) & 0x7FFF


if __name__ == '__main__':
    a = Random(65535)
    print(f"Random bytes : {a.randombytes(1, range(15, 255, 16))}")
    print(f"Random hex   : {a.randomhex(range(0x0f, 0xff, 0x0010))}")
    print(f"Random string: {a.randomstring(10, string.ascii_letters)}")
    print(f"Random float : {a.randomfloat(0, 10)}")

    print(f"\nRandom Values are now the same value")
    print(f"Random bytes : {Random(1024).randombytes(1, range(15, 255, 16))}")
    print(f"Random hex   : {Random(1024).randomhex(range(0x0f, 0xff, 0x0010))}")
    print(f"Random string: {Random(1024).randomstring(10, string.ascii_letters)}")
    print(f"Random float : {Random(1024).randomfloat(0, 10)}")

    print("\nTesting Random floats")

    import tkinter as tk
    import tkinter.ttk as ttk

    root = tk.Tk()
    root.geometry("400x191")

    max_seed_number = 16  # Standard: 1024
    max_tries = 65536  # 65536  # Standard: 16

    highest = -1.0

    highest_lbl = tk.Label(root, text=f"{highest}", anchor="w", font="consolas")
    randfloat_lbl = tk.Label(root, text=f"", anchor="w", font="consolas")
    curr_seed_lbl = tk.Label(root, text=f"", anchor="w", font="consolas")
    curr_try_lbl = tk.Label(root, text=f"", anchor="w", font="consolas")
    progress = ttk.Progressbar(root, maximum=(max_seed_number * max_tries), value=0)
    empty = tk.Label(root, text=f"")
    seed_progress = ttk.Progressbar(root, maximum=max_seed_number, value=0)
    try_progress = ttk.Progressbar(root, maximum=max_tries, value=0)
    highest_lbl.pack(fill="x")  # , expand=True)
    randfloat_lbl.pack(fill="x")  # , expand=True)
    curr_seed_lbl.pack(fill="x")  # , expand=True)
    curr_try_lbl.pack(fill="x")  # , expand=True)
    progress.pack(fill="x")
    empty.pack(fill="x", pady=1)
    seed_progress.pack(fill="x", pady=1)
    try_progress.pack(fill="x")

    i = 0
    for seed in range(0, max_seed_number+1):
        a = Random(seed)
        curr_seed_lbl.config(text=f"seed={seed}")
        seed_progress.config(value=seed)
        for tries in range(0, max_tries+1):
            _randfloat = a.randomfloat(0, 10)
            curr_try_lbl.config(text=f"try={tries}")
            randfloat_lbl.config(text=f"_randfloat={_randfloat}")
            # print(f"Seed {seed} | Try {tries} | {_randfloat}")
            if _randfloat > highest:
                highest = _randfloat
                highest_lbl.config(text=f"{highest}")
            i += 1
            try_progress.config(value=tries)
            progress.config(value=i)
            root.update()

    root.mainloop()

    print(f"Highest float value: {highest}")
