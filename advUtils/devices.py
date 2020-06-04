import platform
import typing as _t

from Geometry import Point
from overload import overload

from advUtils.miscellaneous import QPixel, QColor


class Screen(object):
    # noinspection PyUnboundLocalVariable
    def __init__(self, getpixel_method="Pillow", create_wxapp: bool = True):
        """
        Class for Screen Information and value.

        Pixel Methods:
        --------------
        - Pillow: ``PIL.ImageGrab.grab(...)``.        \n
          **NOTE:** Windows and Mac only          \n
        - PyWin32: Uses the PyWin32 DC with ID 0. \n
          **NOTE:** Windows only                  \n

        Example:
        --------
        >>> screen = Screen()         # Does create wx.App(...)
        >>> screen.get_pixel(24, 24)  # Gets the pixel at 24, 24. Returns a Pixel(...) instance.

        >>> color = QColor(255, 0, 0)             # Color red
        >>> screen = Screen(create_wxapp=False)  # Does not create wx.App(...)
        >>> screen.set_pixel(24, 24, color)      # Sets the pixel at 24, 24 to variable 'color' (red)

        :param getpixel_method: The method to get the pixel from the screen.
        :param create_wxapp: If True, it creates the wxPython App() instance and set it to Screen(...).wxapp.
        """

        self.getPixelMethod = getpixel_method

        try:
            # noinspection PyPackageRequirements
            import win32gui
            self._use_pywin32 = True
        except ImportError:
            self._use_pywin32 = False
            win32gui = None
        try:
            # noinspection PyPackageRequirements
            import wx
            self._use_wx = True
        except ImportError:
            self._use_wx = False
            wx = None

        if create_wxapp:
            if wx is None:
                raise ImportError("You must install wxPython to use this feature.")
            self.wxapp = wx.App()
        else:
            self.wxapp = None
        if self._use_pywin32:
            self.dc = win32gui.GetDC(0)
        if self._use_wx:
            self.wdc = wx.ScreenDC()

    def get_size(self, using="pywin32") -> _t.Tuple[int, int]:
        """
        Get screen size of the first monitor

        Methods of getting the screen size
        -----------------------------------
        - ``using="pywin32"`` -- Uses PyWin32 (Windows only)
        - ``using="ctypes"`` -- Uses Ctypes (Windows only)
        - ``using="tkinter"`` -- Uses Tkinter (Windows, Linux, Mac)
        - ``using="wxpython"`` -- Uses wxPython (Windows, other unknown)

        Example
        --------
        >>> screen = Screen()
        >>> screen.get_size(using="pywin32")  # Will be different depending on the screen resolution
        1920x1080

        :param using: See method __doc__ for details
        :returns: The screen width and height.
        """

        if using == "pywin32":
            if not self._use_pywin32:
                raise ImportError("You must need PyWin32 to use this (NOTE: Windows only)")
            from win32api import GetSystemMetrics
            w = GetSystemMetrics(0)
            h = GetSystemMetrics(1)
        elif using == "ctypes":
            if platform.system() != "Windows":
                raise ImportError(f"ctypes is not supported on {platform.system()}, it's Windows only")
            import ctypes
            user32 = ctypes.windll.user32
            w = user32.GetSystemMetrics(0)
            h = user32.GetSystemMetrics(1)
        elif using == "tkinter":
            from tkinter import Tk
            tk = Tk()
            w = tk.winfo_screenwidth()
            h = tk.winfo_screenheight()
        elif using == "wxpython":
            if not self._use_wx:
                raise ImportError("You must need wxPython to use this")
            w, h = self.wdc.GetSize()
        else:
            raise ValueError("Invalid 'using' parameter, check 'get_screensize.__doc__' for more information")
        return w, h

    def get_width(self, using="pywin32"):
        return self.get_size(using)[0]

    def get_height(self, using="pywin32"):
        return self.get_size(using)[1]

    # noinspection PyArgumentList
    @overload
    def get_pixel(self, x: int, y: int) -> QPixel:
        """
        Gets the pixel at x,y

        Example:
        --------
        >>> screen = Screen()         # Does create wx.App(...)
        >>> screen.get_pixel(24, 24)  # Gets the pixel at 24, 24. Returns a Pixel(...) instance.

        :param x: The Y coordinate of the pixel
        :param y: The X coordinate of the pixel
        :returns: A Pixel(...) instance of the given x and y coordinates
        """

        if self.getPixelMethod == "Pillow":
            from PIL import ImageGrab, Image
            pil_color: _t.Tuple[int, int, int] = ImageGrab.grab((x, y, x + 1, y + 1)).getpixel((0, 0))
            # noinspection PyTypeChecker
            return QPixel(x, y, QColor(pil_color))
        elif self.getPixelMethod == "PyWin32":
            # noinspection PyPackageRequirements
            import win32gui
            win32gui.GetPixel(self.dc, x, y)
        else:
            raise ValueError(f"Invalid pixel method: {self.getPixelMethod}, "
                             f"look at the Screen Class doc for more information")

    @get_pixel.add
    def get_pixel(self, xy: _t.Tuple[int, int]) -> QPixel:
        """
        Gets the pixel at xy

        Example:
        --------
        >>> screen = Screen()         # Does create wx.App(...)
        >>> screen.get_pixel((24, 24))  # Gets the pixel at 24, 24. Returns a Pixel(...) instance.

        :param xy: The X and Y coordinate of the pixel
        :returns: A Pixel(...) instance of the given x and y coordinates
        """

        return self.get_pixel(xy[0], xy[1])

    @get_pixel.add
    def get_pixel(self, coords: Point) -> QPixel:
        """
        Gets the pixel at the given coordinates

        Example:
        --------
        >>> screen = Screen()         # Does create wx.App(...)
        >>> screen.get_pixel(Point(24, 24))  # Gets the pixel at 24, 24. Returns a Pixel(...) instance.

        :param coords:
        :returns: A Pixel(...) instance of the given x and y coordinates
        """

        return self.get_pixel(int(coords.x), int(coords.y))

    @overload
    def set_pixel(self, x: int, y: int, color: QColor) -> None:
        """
        Sets the pixel at x,y to color

        Example
        --------
        >>> color = QColor(255, 0, 0)                # Color red
        >>> screen = Screen(create_wxapp=False)     # Does not create wx.App(...)
        >>> screen.set_pixel(24, 24, color)         # Sets the pixel at 24, 24 to variable 'color' (red)
        >>> screen.set_pixel((24, 24), color)       # Sets the pixel at 24, 24 to variable 'color' (red)
        >>> screen.set_pixel(Point(24, 24), color)  # Sets the pixel at 24, 24 to variable 'color' (red)

        >>> color = QColor(255, 0, 0)             # Color red
        >>> pixel = QPixel(24, 24, color)         # Create a pixel instance with red color for position 24, 24
        >>> screen = Screen(create_wxapp=False)  # Does not create wx.App(...)
        >>> screen.set_pixel(pixel)              # Sets the pixel to variable 'pixel'


        :param x: The X coordinate of the pixel to set, must be an integer
        :param y: The Y coordinate of the pixel to set, must be an integer
        :param color: The pixel color to set, must be a Color instance
        :return: Nothing
        """

        if not self._use_pywin32:
            raise ValueError("Can't set pixel without having PyWin32 installed")

        # noinspection PyPackageRequirements
        import win32gui
        import win32api
        red = win32api.RGB(color.r, color.g, color.b)
        win32gui.SetPixel(self.dc, x, y, red)  # draw red at 0,0

    @set_pixel.add
    def set_pixel(self, xy: _t.Tuple[int, int], color: QColor) -> None:
        """
        Sets the pixel at xy to color

        Example
        --------
        >>> color = QColor(255, 0, 0)             # Color red
        >>> screen = Screen(create_wxapp=False)  # Does not create wx.App(...)
        >>> screen.set_pixel((24, 24), color)    # Sets the pixel at 24, 24 to variable 'color' (red)


        :param xy:
        :param color:
        :return:
        """

        self.set_pixel(xy[0], xy[1], color)

    @set_pixel.add
    def set_pixel(self, coords: Point, color: QColor) -> None:
        """
        Sets the pixel at the given coordinates to color

        Example
        --------
        >>> color = QColor(255, 0, 0)                # Color red
        >>> screen = Screen(create_wxapp=False)     # Does not create wx.App(...)
        >>> screen.set_pixel(Point(24, 24), color)  # Sets the pixel at 24, 24 to variable 'color' (red)


        :param coords:
        :param color:
        :return:
        """

        self.set_pixel(int(coords.x), int(coords.y), color)

    @set_pixel.add
    def set_pixel(self, pixel: QPixel) -> None:
        """
        Sets the pixel at the pixel x,y to the pixel color

        Example
        --------
        >>> color = QColor(255, 0, 0)             # Color red
        >>> pixel = QPixel(24, 24, color)         # Create a pixel instance with red color for position 24, 24
        >>> screen = Screen(create_wxapp=False)  # Does not create wx.App(...)
        >>> screen.set_pixel(pixel)              # Sets the pixel to variable 'pixel'


        :param pixel:
        :return:
        """

        self.set_pixel(pixel.x, pixel.y, pixel.color)

    @overload
    def draw_line(self, x1, y1, x2, y2, color: QColor) -> None:
        """
        Draws a line from x1,y1 to x2,y2 with the specified color

        Example
        --------
        >>> screen = Screen()                                    # Creates the screen instance
        >>> color = QColor(0, 255, 127)                          # Turquoise color
        >>> screen.draw_line(0, 0, 100, 100, color)              # Draws a line from 0,0 to 100,100 in the color 'color'
        >>> screen.draw_line((0, 0), (100, 50), color)           # Draws a line from 0,0 to 100,50 in the color 'color'
        >>> screen.draw_line(Point(0, 0), Point(50, 100), color)  # Draws a line from 0,0 to 50,100 in the color 'color'

        :param x1: The X coordinate of the first point
        :param y1: The Y coordinate of the first point
        :param x2: The X coordinate of the second point
        :param y2: The Y coordinate of the second point
        :param color: The color of the line
        :returns: Nothing
        """

        if not self._use_wx:
            raise ValueError("Can't draw line without having wxPython installed")
        import wx
        self.wdc.StartDrawingOnTop(None)
        self.wdc.SetPen(wx.Pen(color.to_colorhex(False)))
        self.wdc.DrawLine(x1, y1, x2, y2)

    @draw_line.add
    def draw_line(self, xy1: _t.Tuple[int, int], xy2: _t.Tuple[int, int], color: QColor):
        self.draw_line(xy1[0], xy1[1], xy2[0], xy2[1], color)

    @draw_line.add
    def draw_line(self, pos1: Point, pos2: Point, color: QColor):
        self.draw_line(int(pos1.x), int(pos1.y), int(pos2.x), int(pos2.y), color)

    def paint_desktop(self):
        if not self._use_pywin32:
            raise ValueError("Can't paint desktop without having PyWin32 installed")

        # noinspection PyPackageRequirements
        import win32gui
        win32gui.PaintDesktop(self.dc)

    # noinspection PyUnresolvedReferences
    @staticmethod
    def get_displaymodes():
        """
        Get the primary windows display width and height

        Example
        --------
        >>> screen = Screen()                                  # Create a new screen instance
        >>> highest_size = screen.get_displaymodes()[-1]       # Gets the highest available display mode
        >>> screen.set_size(highest_size[0], highest_size[1])  # Sets the display mode to the highest available

        :returns: A list of tuples containing the width and height
        """

        import win32api
        from pywintypes import error
        modes = []
        i = 0
        try:
            while True:
                mode = win32api.EnumDisplaySettings(None, i)
                modes.append((
                    int(mode.PelsWidth),
                    int(mode.PelsHeight),
                    int(mode.BitsPerPel),
                ))
                i += 1
        except error:
            pass

        return modes

    @staticmethod
    def get_size2():
        """
        Get the primary Windows display width and height

        Example
        --------
        >>> screen = Screen()   # Create a new screen instance
        >>> screen.get_size2()  # Output can be different depending on the current screen resolution
        (1920, 1080)

        :return:
        """

        import ctypes
        user32 = ctypes.windll.user32
        screensize = (
            user32.GetSystemMetrics(0),
            user32.GetSystemMetrics(1),
        )
        return screensize

    @staticmethod
    def set_size(width=None, height=None, depth=32):
        """
        **Note: only works when the display mode is available**

        Set the primary Windows display to the specified mode

        Example
        --------
        >>> screen = Screen()                                  # Create a new screen instance
        >>> highest_size = screen.get_displaymodes()[-1]       # Gets the highest available display mode
        >>> screen.set_size(highest_size[0], highest_size[1])  # Sets the display mode to the highest available

        :param width: The screen width to set the display mode to
        :param height: The screen height to set the display mode to
        :param depth: The screen depth to set the display mode to
        :returns: Nothing
        """

        # Gave up on ctypes, the struct is really complicated
        # user32.ChangeDisplaySettingsW(None, 0)
        import win32api
        if width and height:

            if not depth:
                depth = 32

            mode = win32api.EnumDisplaySettings()
            mode.PelsWidth = width
            mode.PelsHeight = height
            mode.BitsPerPel = depth

            win32api.ChangeDisplaySettings(mode, 0)
        else:
            win32api.ChangeDisplaySettings(None, 0)

    @staticmethod
    def set_defaultsize():
        """
        Reset the primary windows display to the default mode

        Example
        --------
        >>> screen = Screen()         # Create a new screen instance
        >>> screen.set_defaultsize()  # Sets the display mode to the highest available

        :returns: Nothing, what do you expect?
        """

        # Interesting since it doesn't depend on pywin32
        import ctypes
        user32 = ctypes.windll.user32
        # set screen size
        user32.ChangeDisplaySettingsW(None, 0)


if __name__ == '__main__':
    screen = Screen(create_wxapp=True)
    import random as rand
    import ctypes
    import win32api
    import win32security

    print(repr(screen.get_pixel(0, 1079)))


    def glitch2():
        w, h = screen.get_size()
        while True:
            for y in range(0, h):
                for x in range(0, w):
                    color = QColor(*[rand.randint(0, 255) for _ in range(3)])
                    # color = Color(*([rand.randint(0, 255)] * 3))
                    screen.set_pixel(x, y, color)
                    del color


    def glitch4():
        while True:
            x = rand.randint(0, 1919)
            y = rand.randint(0, 1079)
            color = QColor(*[rand.randint(0, 255) for _ in range(3)])
            screen.set_pixel((x, y), color)


    def glitch3():
        while True:
            screen.paint_desktop()


    def glitch1():
        import wx
        import time

        wx.App()
        dc = wx.ScreenDC()
        screen_width, screen_height = wx.DisplaySize()
        dc.StartDrawingOnTop(None)
        dc.SetPen(wx.Pen(QColor(*[rand.randint(0, 255) for _ in range(3)]).to_colorhex(False), 100000))
        dc.SetBrush(wx.CYAN_BRUSH)
        dc.SetLogicalFunction(wx.AND_REVERSE)
        a = [wx.AND, wx.OR, wx.NOR, wx.NAND, wx.XOR, wx.AND_INVERT, wx.AND_REVERSE, wx.OR_INVERT, wx.OR_REVERSE]
        while True:
            dc.SetPen(wx.Pen(QColor(*[rand.randint(0, 255) for _ in range(3)]).to_colorhex(False), 100000))
            dc.SetBrush(wx.WHITE_BRUSH)
            dc.SetLogicalFunction(rand.choice(a))
            b = (rand.randint(0, screen_width), rand.randint(0, screen_height), rand.randint(1, screen_width),
                 rand.randint(1, screen_height))
            print(b)
            dc.DrawRectangle(b)
            time.sleep(1)


    def test_line():
        screen_ = Screen(create_wxapp=False)

        while True:
            w, h = screen_.get_size()
            # noinspection PyArgumentList
            screen_.draw_line(rand.randint(0, w), rand.randint(0, h), rand.randint(0, w), rand.randint(0, h),
                              QColor(255, 0, 0))


    def test_random_mouse(dx, dy, speed):
        import sys
        import time
        import win32api

        # if (len(sys.argv) < 4):
        #     print("Usage: python mousemove.py dx dy speed")
        #     sys.exit()

        current = win32api.GetCursorPos()
        cx = sx = current[0]
        cy = sy = current[1]

        mx = dx  # int(sys.argv[1])
        my = dy  # int(sys.argv[2])
        vx = vy = speed  # int(sys.argv[3])

        print("Moving", mx, my, "with", vx, "pixels per second")
        print("Press 'q' to quit")

        last = time.time()

        while True:
            if win32api.GetAsyncKeyState(ord('Q')):
                sys.exit()

            current = time.time()
            tick = current - last
            last = current

            if mx > 0:
                cx += vx * tick
                if cx > mx + sx or cx < sx:
                    vx = -vx
                    cx = max(sx, min(mx + sx, cx))
            if my > 0:
                cy += vy * tick
                if cy > my + sy or cy < sy:
                    vy = -vy
                    cy = max(sy, min(my + sy, cy))

            win32api.SetCursorPos((int(cx), int(cy)))
            time.sleep(0.001)

    # noinspection PyBroadException
    def suspend(hibernate=False):
        """
        Puts Windows to Suspend/Sleep/Standby or Hibernate.

        Parameters
        ----------
        hibernate: bool, default False
            If False (default), system will enter Suspend/Sleep/Standby state.
            If True, system will Hibernate, but only if Hibernate is enabled in the
            system settings. If it's not, system will Sleep.

        Example
        --------
        >>> suspend()
        """

        # Enable the SeShutdown privilege (which must be present in your
        # token in the first place)
        priv_flags = (win32security.TOKEN_ADJUST_PRIVILEGES |
                      win32security.TOKEN_QUERY)
        h_token = win32security.OpenProcessToken(
            win32api.GetCurrentProcess(),
            priv_flags
        )
        priv_id = win32security.LookupPrivilegeValue(
            None,
            win32security.SE_SHUTDOWN_NAME
        )
        old_privs = win32security.AdjustTokenPrivileges(
            h_token,
            0,
            [(priv_id, win32security.SE_PRIVILEGE_ENABLED)]
        )

        if (win32api.GetPwrCapabilities()['HiberFilePresent'] is False and
                hibernate is True):
            import warnings
            warnings.warn("Hibernate isn't available. Suspending.")
        try:
            ctypes.windll.powrprof.SetSuspendState(not hibernate, True, False)
        except:
            # True=> Standby; False=> Hibernate
            # https://msdn.microsoft.com/pt-br/library/windows/desktop/aa373206(v=vs.85).aspx
            # says the second parameter has no effect.
            #        ctypes.windll.kernel32.SetSystemPowerState(not hibernate, True)
            win32api.SetSystemPowerState(not hibernate, True)

        # Restore previous privileges
        win32security.AdjustTokenPrivileges(
            h_token,
            0,
            old_privs
        )


    # glitch2()

    # print(screen.get_displaymodes())
    screen.set_size(1920, 1080, 32)
