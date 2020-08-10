import unittest

from advUtils.miscellaneous import QColor as _Color


class QWindows10Options(object):
    def __init__(self):
        import winreg as registry
        self.reg = registry

    def get_accentcolor(self) -> _Color:
        """
        Return the Windows 10 accent color used by the user in a HEX format

        :return:
        """

        # Open the registry
        registry = self.reg.ConnectRegistry(None, self.reg.HKEY_CURRENT_USER)

        # Navigate to the key that contains the accent color info
        from winreg import OpenKey
        key = OpenKey(registry, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Accent')

        # Read the value in a REG_DWORD format
        key_value = self.reg.QueryValueEx(key, 'AccentColorMenu')

        # Convert the interger to Hex and remove its offset
        accent_int = key_value[0]
        accent_hex = hex(accent_int + 4278190080)  # Remove FF offset and convert to HEX again
        accent_hex = str(accent_hex)[4:-1]  # Remove prefix and suffix

        # The HEX value was originally in a BGR order, instead of RGB,
        # so we reverse it...
        accent = accent_hex[4:6] + accent_hex[2:4] + accent_hex[0:2]
        return _Color("#" + accent)


class __Test(unittest.TestCase):
    @staticmethod
    def test_win10options():
        _win10options = QWindows10Options()
        accent_color = _win10options.get_accentcolor()
        h, s, v = accent_color.to_hsv()
        # h = h / 209 * 203
        h = h - 5.775
        # v = v / 92 * 84
        v = v - 8  # - 5
        accent_color = _Color.from_hsv(h, s, v)
        # accent_color.g += 2
        print(accent_color.to_hsv())
        # accent_color_int = accent_color.to_int(False)
        # accent_color_int -= 0x000909
        # accent_color = _Color(accent_color_int)
        print()

        import tkinter as tk
        root = tk.Tk()
        root.wm_geometry("400x300+20+20")
        frame = tk.Frame(root, bg=accent_color.to_colorhex(False))
        frame.pack(fill="both", expand=True)
        root.update()
        root.update_idletasks()
        # root.mainloop()
