from abc import abstractmethod

from advUtils.core.decorators import log
from advUtils.miscellaneous import Utils


class QEvent(object):
    def __init__(self, func):
        self._func = func

    @classmethod
    @abstractmethod
    def mainloop(cls):
        pass

    @classmethod
    def start_thread(cls):
        import threading
        _t = threading.Thread(target=cls.mainloop)
        _t.start()
        return _t

    @classmethod
    @abstractmethod
    def bind(cls, *args, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def unbind(cls, *args, **kwargs):
        pass


class QFolderEvent(QEvent):
    funcs = {}
    cache = {}

    import os

    def __init__(self, func, folder, new, old):
        self.folder = folder
        self.newItems = new
        self.oldItems = old
        # print(self)
        super(QFolderEvent, self).__init__(func)

    @classmethod
    def mainloop(cls, delay: float = 0.5):
        import time
        while True:
            a = QFolderEvent.cache.copy()
            for folder, c_listdir in a.items():
                # print(folder)
                listdir = QFolderEvent.os.listdir(folder)
                b = QFolderEvent.funcs.keys()
                if listdir != c_listdir and folder in b:
                    newlist = listdir
                    oldlist = c_listdir
                    newitems = Utils.diff(newlist, oldlist)
                    olditems = Utils.diff(oldlist, newlist)
                    func = QFolderEvent.funcs[folder]
                    # print(func)
                    c = QFolderEvent(func, folder, newitems, olditems)
                    # print(c)
                    QFolderEvent.funcs[folder](c)
                    del newlist, oldlist, newitems, olditems, func, c

                cls.cache[folder] = listdir
                del b, listdir
            del a, folder, c_listdir
            time.sleep(delay)

    @classmethod
    def start_thread(cls, delay: float = 0.01):
        import threading
        _t = threading.Thread(target=cls.mainloop, args=(delay,))
        _t.start()
        return _t

    @classmethod
    def bind(cls, folder):
        def decorator(func):
            cls.funcs[folder] = func
            cls.cache[folder] = cls.os.listdir(folder)
        return decorator

    @classmethod
    def unbind(cls, folder):
        del cls.funcs[folder]
        del cls.cache[folder]


if __name__ == '__main__':
    @log("Testing folder event.")
    def test_folderevent():
        import os
        import time
        from time import sleep

        @QFolderEvent.bind(rf"C:\Users\{os.getlogin()}")
        def event_handler(evt: QFolderEvent):
            time2 = time.strftime('%d/%m/%Y %H:%M:%S', time.gmtime(time.time()))
            print(f"{time2} | New Items: {evt.newItems}") if evt.newItems else None
            print(f"{time2} | Old Items: {evt.oldItems}") if evt.oldItems else None

        # FolderEvent.bind(event_handler, )
        # FolderEvent.bind(event_handler, f"C:\\Users\\{os.getlogin()}\\Documents")
        t = QFolderEvent.start_thread()

        while t.is_alive():
            sleep(1)

    test_folderevent()
