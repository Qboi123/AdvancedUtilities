import os as _os
import sys as _sys


class QApplication(object):
    def __init__(self, argv=None):
        self.argv = argv if argv is not None else _sys.argv
        self.file = self.argv[0]
        self.args = self.argv[1:] if len(self.argv) > 1 else []
        self.commandline = " ".join(['"'+i+'"' if " " in i else i for i in _sys.argv])
        self.pid = _os.getpid()

    def kill(self, signal):
        _os.kill(self.pid, signal)


class QApp(QApplication):
    def __init__(self, argv=None):
        super(QApp, self).__init__(argv)
