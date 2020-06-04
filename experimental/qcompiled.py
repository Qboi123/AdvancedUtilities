from io import BytesIO
from typing import BinaryIO, Union

from advUtils.core.decorators import experimental

OPCODE_NOP = 0x0000  # No Operation
OPCODE_ADD = 0x0001  # Calc: Add OP Code
OPCODE_MIN = 0x0002  # Calc: Substract OP Code
OPCODE_MUL = 0x0003  # Calc: Multiply OP Code
OPCODE_DIV = 0x0004  # Calc: Divide OP Code
OPCODE_OR = 0x0005   # Logical: OR, OP Code
OPCODE_AND = 0x0006  # Logical: AND, OP Code
OPCODE_NOT = 0x0007  # Logical: NOT, OP Code
OPCODE_JUMP = 0x0010    # Jump: Jump Instruction OP Code
OPCODE_JMSBRT = 0x0011  # Subroutine: Jump Subroutine OP Code
OPCODE_RTSBRT = 0x0012  # Subroutine: Return Subroutine OP Code
OPCODE_IOSEEK = 0x0030  # IO: Seek OP Code
OPCODE_IOWRIT = 0x0031  # IO: Write OP Code
OPCODE_IOREAD = 0x0032  # IO: Read OP Code
OPCODE_IOFLUS = 0x0033  # IO: Flush OP Code
OPCODE_IOOPEN = 0x0034  # IO: Open OP Code
OPCODE_STDOUT = 0x0040  # STD: Std Output OP Code
OPCODE_STDERR = 0x0041  # STD: Std Error OP Code
OPCODE_STDIN = 0x0042   # STD: Std Input OP Code
OPCODE_KEYBRD = 0x0050  # Buffer: Keyboard Buffer OP Code
OPCODE_CNTRLL = 0x0051  # Buffer: Controller Buffer OP Code
OPCODE_MOUSE = 0x0052   # Buffer: Mouse Buffer OP Code
OPCODE_GETX = 0x0060    # Variable: Get Variable OP Code
OPCODE_SETX = 0x0061    # Variable: Set Variable OP Code
OPCODE_DELX = 0x0062    # Variable: Delete Variable OP Code
OPCODE_ADDARR = 0x0063  # Array: Add Value OP Code
OPCODE_RMVARR = 0x0064  # Array: Remove Value OP Code
OPCODE_INSARR = 0x0065  # Array: Insert Value OP Code
OPCODE_NWLN = 0x0070    # Character: Newline Character OP Code
OPCODE_EQUAL = 0x0080   # Operator: Equal Operator OP Code
OPCODE_NOTEQ = 0x0081   # Operator: Not Equal Operator OP Code
OPCODE_DEFINE = 0x0090  # Declaration: Define Operator OP Code
OPCODE_CLASS = 0x0091   # Declaration: Class Operator OP Code
OPCODE_INTEG = 0x0092   # Type: Integer Type OP Code
OPCODE_STRIN = 0x0093   # Type: String Type OP Code
OPCODE_BOOLN = 0x0094   # Type: Boolean Type OP Code
OPCODE_ARRAY = 0x0095   # Type: Array Type OP Code
OPCODE_DICT = 0x0096    # Type: Dictionary Type OP Code
OPCODE_TUPLE = 0x0097   # Type: Tuple Type OP Code
OPCODE_LIST = 0x0098    # Type: List Type OP Code
OPCODE_FUNCT = 0x0099   # Type: Function Type OP Code
OPCODE_TYPE = 0x009A    # Type: Type OP Code
OPCODE_EXCEPT = 0x009B  # Type: Exception Type OP Code
OPCODE_RANDOM = 0x009C  # Type: Random Seed Type OP Code
OPCODE_FLOAT = 0x009D   # Type: Float Type OP Code
OPCODE_BYTES = 0x009E   # Type: Bytes Type OP Code
OPCODE_METHOD = 0x009F  # Type: Method Type OP Code
OPCODE_ELLPSS = 0x00A0  # Type: Ellipsis Type OP Code
OPCODE_TRACBK = 0x00A1  # Type: Traceback Type OP Code
OPCODE_SETPX = 0x00B0   # Screen: Set Pixel OP Code
OPCODE_GETPX = 0x00B1   # Screen: Get Pixel OP Code


@experimental
class QCompiled(object):
    def __init__(self, rom: Union[BytesIO, BinaryIO]):
        self.rom = rom
        self.index = 0

        self.vars = {}

    def read(self):
        self.rom.seek(self.index)
        return self.rom.read()

    def exec(self):
        self.rom.seek(0x0000)

        while True:
            opcode = self.advance()

            if opcode == bytes([OPCODE_NOP]):
                continue

            if opcode == bytes([OPCODE_SETX]):
                ram_addr = self.advance(4)
                # noinspection PyUnusedLocal
                alloc_size = self.advance(4)

                self.ram.writeat(ram_addr, )

    def advance(self, size=1):
        self.index += size
        return self.read()
