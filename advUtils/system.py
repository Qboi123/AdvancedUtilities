# from __future__ import print_function

from ctypes import windll, sizeof, c_uint
from threading import Thread, Event
# from playsound import playsound()

import win32api
from overload import overload
from past.builtins import unicode
from psutil import Process, ZombieProcess, NoSuchProcess
from pyGoogleSearch import Google as GoogleSearch
from pywin.scintilla.keycodes import MAPVK_VK_TO_CHAR
from win32api import MapVirtualKey, PostMessage, VkKeyScan
from win32con import WM_KEYDOWN, WM_KEYUP, VK_RIGHT


class Console(object):
    def __init__(self):
        """
        Minimal Windows console (command prompt)

        """
        import os
        import subprocess
        self._os = os
        self._subps = subprocess

    @staticmethod
    def _parse_command(file, *args):
        """
        Parses file and arguments into a string command.

        :param file:
        :param args:
        :return:
        """

        command = [file]

        for arg in args:
            if " " in arg:
                arg = '"' + arg + '"'
            command.append(arg)

        command_str = " ".join(command)
        return command_str

    def execute(self, file, *args):
        """
        Execute a file with arguments

        :param file:
        :param args:
        :return:
        """

        command = self._parse_command(file, *args)
        self._os.system(command)

    def subprocess(self, file, *args):
        """
        Create a subprocess of a file with arguments

        :param file:
        :param args:
        :return:
        """

        self._subps.run([file, *args])


class Std(object):
    def __init__(self):
        """
        STD I/O Base class
        """

        import sys
        self._sys = sys

    def out(self, string):
        """
        STD Output

        :param string:
        :return:
        """
        self._sys.stdout.write(string)

    def err(self, string):
        """
        STD Error

        :param string:
        :return:
        """
        self._sys.stderr.write(string)

    def in_(self, n):
        """
        STD Input

        :param n:
        :return:
        """

        self._sys.stdin.read(n)


class PythonPath(object):
    def __init__(self):
        """
        Python path class
        """

        import sys
        import os
        self._sys = sys
        self._os = os

    def _fix_path(self, path):
        """
        Fixes path for python path

        :param path:
        :return:
        """

        return self._os.path.abspath(path)

    def add(self, path):
        """
        Adds a path to the python path

        :param path:
        :return:
        """

        self._sys.path.append(self._fix_path(path))

    def remove(self, path):
        """
        Removes a path from the python path

        :param path:
        :return:
        """

        self._sys.path.remove(self._fix_path(path))

    def inpath(self, path):
        """
        Checks if a path is already in the python path

        :param path:
        :return:
        """

        return self._fix_path(path) in self._sys.path


class StoppableThread(Thread):
    def __init__(self, group=None, target=lambda: None, name="", args=None, kwargs=None, daemon=None):
        """
        Thread class with a stop() method. The thread itself has to check
        regularly for the stopped() condition.

        Code:
        ----------------
        >>> import time
        >>> def funct():
        ...     while not testthread.stopped():
        ...         time.sleep(1)
        ...         print("Hello")
        ...
        >>> testthread = StoppableThread()
        >>> testthread.start()
        >>> time.sleep(5)
        >>> testthread.stop()

        :param group:
        :param target:
        :param name:
        :param args:
        :param kwargs:
        :param daemon:
        """
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        super(StoppableThread, self).__init__(group, target, name, args, kwargs, daemon=daemon)

        self._stopEvent = Event()

    def stop(self):
        self._stopEvent.set()

    def stopped(self):
        self._stopEvent.is_set()


class Notification(object):
    iconNames = ["info", "error", "warn"]

    def __init__(self, title, message, icon):
        import wx.adv
        self._wx_adv = wx.adv
        self.app = wx.App()

        if icon not in self.iconNames:
            raise ValueError(f"Icon is not any of '{self.iconNames}'")
        if icon == "info":
            flags = wx.ICON_INFORMATION
        elif icon == "error":
            flags = wx.ICON_ERROR
        elif icon == "warn":
            flags = wx.ICON_WARNING
        else:
            raise ValueError(f"Icon is not any of '{self.iconNames}'")

        self._notify: wx.adv.NotificationMessage
        self._notify = wx.adv.NotificationMessage(title=title, message=message, flags=flags)

        self._title: str = title
        self._message: str = message

    def show(self):
        self._notify.Show(-1)
        self.app.Destroy()

    def close(self):
        self._notify.Close()

    def set_title(self, title):
        self._notify.SetTitle(title)
        self._title = title

    def get_title(self):
        return self._title

    def set_message(self, message):
        self._notify.SetTitle(message)
        self._message = message

    def get_message(self):
        return self._message

    settitle = set_title
    gettitle = get_title
    setmessage = set_message
    getmessage = get_message
    setmsg = set_message
    getmsg = get_message
    SetTitle = set_title
    GetTitle = get_title
    SetMessage = set_message
    GetMessage = get_message
    SetMsg = set_message
    GetMsg = get_message
    Close = close
    setTitle = set_title
    getTitle = get_title
    setMessage = set_message
    getMessage = get_message
    setMsg = set_message
    getMsg = get_message


class ScreenInfo(object):
    def __init__(self):
        import screeninfo
        self._screeninfo = screeninfo

    def get_monitors(self):
        monitors = self._screeninfo.get_monitors()
        return monitors

    getmonitors = get_monitors
    GetMonitors = get_monitors
    getMonitors = get_monitors


class Window(object):
    def __init__(self, hwnd):
        import platform
        if platform.system() != "Windows":
            raise OSError("Needed Windows for using the Window class")

        import win32gui
        import win32con
        self._wg = win32gui
        self._wc = win32con
        self.win32con = win32con
        self._hwnd = hwnd

    def move_window(self, dx, dy):
        x, y, x2, y2 = self._wg.GetWindowRect(self._hwnd)

        self._wg.MoveWindow(self._hwnd, x+dx, y+dy, x2+dx, y2+dy, True)

    def close_window(self):
        self._wg.CloseWindow(self._hwnd)

    @classmethod
    def get_parent(cls, hwnd):
        import win32gui as wg
        return wg.GetParent(hwnd)

    @classmethod
    def get_foreground_window(cls):
        import win32gui as wg
        return wg.GetForegroundWindow()

    @overload
    def send_keypress(self, key: int):
        virtual_key = MapVirtualKey(key, 0)
        PostMessage(self._hwnd, WM_KEYDOWN, key, 0x0001 | virtual_key >> 16)

    @send_keypress.add
    def send_keypress(self, key: str):
        result = windll.User32.VkKeyScanW(ord(unicode(key)))
        vk_key = virtual_key = result & 0xFF
        PostMessage(self._hwnd, WM_KEYDOWN, vk_key, 0x0001 | virtual_key >> 16)
        PostMessage(self._hwnd, WM_KEYUP, vk_key, 0x0001 | virtual_key >> 16 | 0xC0 >> 24)

    @overload
    def send_keyrelease(self, key: int):
        virtual_key = MapVirtualKey(key, 0)
        PostMessage(self._hwnd, WM_KEYUP, key, 0x0001 | virtual_key >> 16 | 0xC0 >> 24)

    @send_keyrelease.add
    def send_keyrelease(self, key: str):
        result = windll.User32.VkKeyScanW(ord(unicode(key)))
        vk_key = virtual_key = result & 0xFF
        PostMessage(self._hwnd, WM_KEYUP, vk_key, 0x0001 | virtual_key >> 16 | 0xC0 >> 24)


class TTS(object):
    def __init__(self, language, slow=False):
        """
        Text to Speech API, using the Google TTS API

        Example
        --------
        >>> tts = TTS("en")
        >>> tts.speak("This is a test message")
        >>> tts.pspeak("This is a printed test message")
        This is a printed test message

        :param language: The language code for the speech
        :param slow: Enable or disable slow speech output
        """

        self._lang = language
        self.slow = slow

    def speak(self, text, *, debug=False):
        from gtts import gTTS
        from playsound import playsound
        import os
        from advUtils.advRandom import Random

        import tempfile

        filename = f'temp_{Random().randomhex(range(0x10000000000, 0xFFFFFFFFFFF))[2:]}.mp3'
        filename = os.path.join(tempfile.gettempdir(), filename)

        if debug:
            print(f"Created temporary file: {filename}")

        tts = gTTS(text, lang=self._lang, slow=self.slow, lang_check=True)
        tts.save(filename)
        playsound(filename)
        os.remove(filename)

    def pspeak(self, text):
        print(text)
        self.speak(text)


class Translate(object):
    def __init__(self, from_, to_):
        self.langFrom = from_
        self.langTo = to_

    def translate(self, text):
        pass


class Beep(object):
    def __init__(self, freq, dur):
        import win32api as wa
        wa.Beep(freq, dur)


if __name__ == '__main__':
    tts = TTS("en")

    def test_tts():
        tts.speak("Test text, with single quotes")
        tts.speak("""Test text, with triple quotes""")

    def test_window_class():
        from tkinter import Tk
        import time

        root = Tk()
        root.update()
        window = Window(root.winfo_id())
        root.bind("<KeyPress>", lambda evt: print(f"KeyPress-{evt.keysym if evt.keysym != '??' else evt.char}"))
        root.bind("<KeyRelease>", lambda evt: print(f"KeyRelease-{evt.keysym if evt.keysym != '??' else evt.char}"))

        window.send_keypress(VK_RIGHT)
        window.send_keypress("H")
        # import ctypes.windll
        # import ctypes.wintypes

        import pyWinhook as pyHook

        def OnMouseEvent(event: pyHook.MouseEvent):
            print('MessageName: %s' % event.MessageName)
            print('Message: %s' % event.Message)
            print('Time: %s' % event.Time)
            print('Window: %s' % event.Window)
            print('WindowName: %s' % event.WindowName)
            print('Position: (%d, %d)' % event.Position)
            print('Wheel: %s' % event.Wheel)
            print('Injected: %s' % event.Injected)
            # print('Hallo'+chr(event.Ascii))
            print('---')

            # return True to pass the event to other handlers
            # return False to stop the event from propagating
            return True

        def OnKeyboardEvent(event):
            print('MessageName: %s' % event.MessageName)
            print('Message: %s' % event.Message)
            print('Time: %s' % event.Time)
            print('Window: %s' % event.Window)
            print('WindowName: %s' % event.WindowName)
            print('Ascii: %s' % event.Ascii, "A"+chr(event.Ascii))
            print('Key: %s' % event.Key)
            print('KeyID: %s' % event.KeyID)
            print('ScanCode: %s' % event.ScanCode)
            print('Extended: %s' % event.Extended)
            print('Injected: %s' % event.Injected)
            print('Alt %s' % event.Alt)
            print('Transition %s' % event.Transition)
            print('---')

            # return True to pass the event to other handlers
            # return False to stop the event from propagating
            return True

        # create the hook mananger
        hm = pyHook.HookManager()
        # register two callbacks
        hm.MouseAllButtonsDown = OnMouseEvent
        hm.KeyDown = OnKeyboardEvent

        # hook into the mouse and keyboard events
        hm.HookMouse()
        hm.HookKeyboard()

        if __name__ == '__main__':
            import pythoncom
            pythoncom.PumpMessages()
        root.mainloop()

        # print(type(window.win32con.VK_RIGHT))

    # for i in range(80, 800, 20):
    #     Beep(i, 1500)
    # while True:
    #     Beep(2400, 1200)

    # test_window_class()
