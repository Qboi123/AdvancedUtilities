import typing as _t

from overload import overload


def diff(first: list, second: list) -> list:
    """
    Returns the items of first that are not in second

    :param first:
    :param second:
    :return:
    """

    second = set(second)
    return [item for item in first if item not in second]


def remove_duplicates(list_: list) -> list:
    """
    Remove duplicates from a list

    Example
    --------
    >>> list_ = [0, 1, 2, 3, 3, 2, 4, 1]
    >>> remove_duplicates(list_)
    [0, 1, 2, 3, 4]

    :param list_:
    :return:
    """

    index = 0
    already_defined = []
    while index < len(list_):
        if already_defined:
            if list_[index] in already_defined:
                del list_[index]
                continue
        already_defined.append(list_[index])
        index += 1
    return list_


class Color(object):
    @overload
    def __init__(self, hex_: str):
        print(hex_)
        if hex_.startswith("#"):
            rh = hex_[1:3]
            gh = hex_[3:5]
            bh = hex_[5:7]
            ah = "ff"
            if len(hex_) == 9:
                ah = hex_[7:9]
        elif hex_.startswith("0x"):
            rh = hex_[2:4]
            gh = hex_[4:6]
            bh = hex_[6:8]
            ah = "ff"
            if len(hex_) == 10:
                ah = hex_[8:10]
        else:
            raise ValueError("Invalid hex value, must start with '0x' or '#'")
        self.r = eval(f"0x{rh}")
        self.g = eval(f"0x{gh}")
        self.b = eval(f"0x{bh}")
        self.a = eval(f"0x{ah}")

    @__init__.add
    def __init__(self, integer: int):
        h = hex(integer)
        if len(h) < 8:
            h = "0x" + ("0" * (8 - len(h))) + h[2:]
        self.__init__(h)

    @__init__.add
    def __init__(self, r: int, g: int, b: int, a: _t.Optional[int] = None):
        self.r = r
        self.g = g
        self.b = b
        self.a = 255
        if a is not None:
            self.a = a

    @__init__.add
    def __init__(self, r: float, g: float, b: float, a: _t.Optional[float] = None):
        self.r = int(r * 255.0)
        self.g = int(g * 255.0)
        self.b = int(b * 255.0)
        self.a = 255
        if a is not None:
            self.a = int(a * 255.0)

    @__init__.add
    def __init__(self, rgb: _t.Union[_t.Tuple[int, int, int], _t.Tuple[int, int, int, int]]):
        self.r = rgb[0]
        self.g = rgb[1]
        self.b = rgb[2]
        self.a = 255
        if len(rgb) == 4:
            self.a = rgb[3]

    @__init__.add
    def __init__(self, rgb: _t.Union[_t.Tuple[float, float, float], _t.Tuple[float, float, float, float]]):
        self.r = int(rgb[0] * 255)
        self.g = int(rgb[1] * 255)
        self.b = int(rgb[2] * 255)
        self.a = 255
        if len(rgb) == 4:
            self.a = int(rgb[3] * 255)

    def to_colorhex(self, include_alpha: bool = True):
        rh = hex(self.r)[2:]
        gh = hex(self.g)[2:]
        bh = hex(self.b)[2:]
        if len(rh) == 1:
            rh = "0"+rh
        if len(gh) == 1:
            gh = "0"+gh
        if len(bh) == 1:
            bh = "0"+bh

        if include_alpha:
            ah = hex(self.a)[2:]
            if len(ah) == 1:
                ah = "0"+ah
            return f"#{rh}{gh}{bh}{ah}"
        return f"#{rh}{gh}{bh}"

    def to_hex(self, include_alpha: bool = False):
        rh = hex(self.r)[2:]
        gh = hex(self.g)[2:]
        bh = hex(self.b)[2:]
        if len(rh) == 1:
            rh = "0" + rh
        if len(gh) == 1:
            gh = "0" + gh
        if len(bh) == 1:
            bh = "0" + bh

        if include_alpha:
            ah = hex(self.a)[2:]
            if len(ah) == 1:
                ah = "0"+ah
            return f"0x{rh}{gh}{bh}{ah}"
        return f"0x{rh}{gh}{bh}"

    def to_int(self, include_alpha: bool = False) -> int:
        return eval(self.to_hex(include_alpha))

    def to_tuple(self, type_: _t.Union[_t.Type[int], _t.Type[float]] = int):
        if type_ == int:
            return self.r, self.g, self.b, self.a
        elif type_ == float:
            return self.r / 255, self.g / 255, self.b / 255, self.a / 255

    def __repr__(self):
        return f"Color(<{self.to_colorhex()}>)"

    def __str__(self):
        return f"{self.to_colorhex()}"

    def to_hsv(self, type_: _t.Union[_t.Type[int], _t.Type[float]] = int):
        import colorsys
        f_hsv = colorsys.rgb_to_hsv(*self.to_tuple(float)[:3])
        if type_ == int:
            f = f_hsv
            return f[0] * 360, f[1] * 100, f[2] * 100
        return colorsys.rgb_to_hsv(*self.to_tuple(float)[:3])

    @classmethod
    def from_hsv(cls, h, s, v):
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h / 360, s / 100, v / 100)
        return Color(r, g, b)


class Pixel(object):
    def __init__(self, x, y, color: Color):
        self.x = x
        self.y = y
        self.color = color

    def __str__(self):
        return f"{self.x},{self.y},{self.color}"

    def __repr__(self):
        return "<Pixel(%s, %s, color=<%s>)" % (self.x, self.y, self.color)
