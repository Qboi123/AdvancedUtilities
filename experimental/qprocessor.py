import sys
from io import BytesIO
from tkinter import Tk, Canvas, TclError

from advUtils.core.decorators import experimental

RAM_SIZE = 0xffff
print(RAM_SIZE)
RAM = bytearray([0xff] * (RAM_SIZE + 1))

ROM_SIZE = 0xffff
ROM = bytearray([0xff] * (ROM_SIZE + 1))

DATAROM_SIZE = 0xffff
DATAROM = bytearray([0xff] * (DATAROM_SIZE + 1))

SCREENWIDTH = 32
SCREENHEIGHT = 8

STACK_OFFSET = 0x0100
STACK_SIZE = 0x00ff

OP_JMP = 0x80
OP_LDA = 0xa9
OP_STA = 0x8d
OP_JSR = 0x20
OP_RTS = 0x60
OP_PHS = None
OP_PLS = None
OP_STP = 0xff


@experimental
class QPowerIO(object):
    def __init__(self):
        pass

    # noinspection PyUnusedLocal
    def write(self, byte: bytes):
        binary_byte = bin(int.from_bytes(byte, "big", signed=False))
        for i in range(8, len(binary_byte), -1):
            binary_byte = "0" + binary_byte
        switches = [bool(int(bit)) for bit in list(binary_byte)]
        if binary_byte == "00000001":
            self.shutdown()
        elif binary_byte == "00000010":
            self.reboot()

    def shutdown(self):
        pass

    def reboot(self):
        pass


@experimental
class QProcessor(object):
    def __init__(self, rom: bytearray, dram: BytesIO):
        """
        Processor

        :param rom: ROM
        :param dram: Data RAM, must be a BytesIO.
        """

        self.index = (SCREENWIDTH * SCREENHEIGHT) - 1
        self.dram: BytesIO = dram
        # self.ram: BytesIO = BytesIO(RAM)
        self.rom: BytesIO = BytesIO(rom)
        # self.rom.writable = lambda: False
        # self.rom.write = None
        # self.rom.writelines = None
        self.powerIO = QPowerIO()
        self.screen = Screen(self.rom)
        self.lda: int = -1

    def read_data(self, adress, size):
        pass

    def write_data(self, adress, data):
        pass

    def read_rom(self, adress):
        self.rom.seek(adress)
        data = self.rom.read(1)
        print("r", data.hex(), adress.to_bytes(2, "big", signed=False).hex())
        return data

    def write_rom(self, adress: int, byte: bytes):
        self.rom.seek(adress)
        self.rom.write(byte)
        print("W", byte.hex(), adress.to_bytes(2, "big", signed=False).hex())
        if 0x0000 <= adress < 0x0100:
            self.screen.write(byte)
        elif adress == 0x6000:
            self.powerIO.write(byte)

    def reset(self):
        self.index = len(self.rom.getvalue()) - 4
        # self.advance()
        exec_addr = int.from_bytes(self.advance()+self.advance(), "little", signed=False)
        # print(hex(exec_addr))
        self.index = exec_addr - 1
        # self.advance()
        # self.exec_opcode(self.rom)

    # noinspection PyUnusedLocal
    @staticmethod
    def exec_opcode(io, *, repeat=1):
        while True:
            pass

    def exec(self):
        self.rom.seek((SCREENWIDTH * SCREENHEIGHT))

        repeat = 0
        while True:
            opcode = self.advance()
            # print(opcode.hex(), repeat.to_bytes(1, "big", signed=False).hex(), hex(io.tell()))
            # print(opcode, bytes([OP_LDA]))
            if opcode == b"\xea":  # No OP (No Operation)
                repeat += 1
                if repeat == 7:
                    self.reset()
                    continue
                continue  # Advance to next byte
            repeat = 0
            if opcode == bytes([OP_LDA]):
                adress = int.from_bytes(self.advance()+self.advance(), "little", signed=False)
                # print(f"READ_ROM: {adress:08x}")
                # print(f"READ:     000000{data.hex()}")
                self.lda = adress

                opcode = self.advance()
                # print(opcode)
                if opcode == bytes([OP_STA]):
                    self.write_rom(self.lda, self.advance())
            elif opcode == bytes([OP_JMP]):
                self.index = int.from_bytes(self.advance()+self.advance(), "little", signed=False)
                continue
            # elif opcode == bytes([OP_STA]):
            #     print(f"Invalid opcode: {opcode.hex()}")
            # else:
            #     print(f"Invalid opcode: {opcode.hex()}")

    def advance(self):
        self.screen.update()

        self.index += 1
        if self.index > len(self.rom.getvalue()):
            self.index = 0
        return self.read_rom(self.index)


def opcode_lda(adress):
    return b"\xa9" + adress.to_bytes(2, "little", signed=False)


def opcode_sta(byte: int):
    return b"\x8d" + byte.to_bytes(1, "little", signed=False)


def opcode_jmp(adress):
    return b"\x80" + adress.to_bytes(2, "little", signed=False)


def initialize_rom():
    rom = BytesIO(ROM.copy())

    # Screen
    rom.seek(0)
    rom.write(b"\x00" * (SCREENWIDTH * SCREENHEIGHT))

    # Reset
    rom.write(b"\xea" * 7)

    # Execution adress
    rom.seek(len(ROM) - 3)
    rom.write(b"\x00\x80")

    # Main program
    rom.seek(0x8000)

    text = "Hello World!"
    for i in range(len(text)):
        rom.write(opcode_lda(i))
        rom.write(opcode_sta(ord(text[i])))

    line2 = "This is a test..."
    for i in range(0, len(line2)):
        rom.write(opcode_lda(i+32))
        rom.write(opcode_sta(ord(line2[i])))

    rom.write(opcode_jmp(0x8000))

    # Go back to adress 0x00000000
    rom.seek(0)

    with open("rom.bin", "wb+") as file:
        file.write(rom.getvalue())
        file.close()

    rom.seek(0)
    return rom.getvalue()


class Screen(object):
    def __init__(self, rom, size=None):
        if size is None:
            pass

        self._root = Tk()
        self._canvas = Canvas(self._root, width=SCREENWIDTH*16, height=SCREENHEIGHT*16)
        self._canvas.pack()
        self._root.update()
        print(f"+{SCREENWIDTH * 32}+{SCREENHEIGHT * 32}")
        # exit(-1)
        # self._root.wm_geometry(f"+{SCREENWIDTH * 32}+{SCREENHEIGHT * 32}")

        self._chars = {}

        for x in range(SCREENWIDTH):
            for y in range(SCREENHEIGHT):
                self._chars[x, y] = self._canvas.create_text(
                    x*16, y*16, text="\x00", anchor="nw", font=("Consolas", 11))

        # b"\x00" * size

        super().__init__()
        self.rom = rom

    def update(self):
        try:
            self._root.update()
        except TclError:
            sys.exit(0)

    def updatechar(self, x, y, char):
        self._canvas.itemconfig(self._chars[x, y], text=char)

    def write(self, byte: bytes):
        char = byte.decode("ascii")
        index = self.rom.tell()
        x = index % SCREENWIDTH
        y = index // SCREENWIDTH
        self.updatechar(x, y, char)


if __name__ == '__main__':
    _rom = initialize_rom()
    _ram = RAM
    proc = QProcessor(bytearray(_rom), BytesIO(_ram))
    proc.exec()

    while True:
        continue
