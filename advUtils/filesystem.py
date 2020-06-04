# Internal python modules.
import platform
import tkinter as _tk
import typing as _t
from enum import Enum as _Enum

# 3rd party modules.
# noinspection PyPackageRequirements
from Crypto.Cipher import ARC4 as _ARC4
from PIL.Image import Image as _Image

# Project modules
from advUtils.code import HtmlCode as _HtmlCode
from advUtils.system import PythonPath as _PythonPath

if platform.system().lower() == "windows":
    from win32comext.shell import shell as _shell, shellcon as _shellcon

    _PLATFORM = "Platform::Windows"
else:
    _PLATFORM = "Platform::Other"
    _shell = None
    _shellcon = None

_PLATFORM_WINDOWS = "Platform::Windows"
_PLATFORM_OTHER = "Platform::Other"

WINDOW_MINIMIZED = 7
WINDOW_MAXIMIZED = 3
WINDOW_NORMAL = 1


class Directory(object):
    def __init__(self, path):
        """
        Base directory class

        :param path: The path to the directory
        """

        import os
        self.path = path
        self.os = os

        self.absPath: str = os.path.abspath(path)
        try:
            self.relPath: str = os.path.relpath(path)
        except ValueError:
            self.relPath: _t.Optional[str] = None

    # noinspection PyUnusedLocal
    def listdir(self, recursive=False, depth=5) -> _t.List[_t.Union['File', 'Directory']]:
        """
        Indexes the directory

        :type depth: int
        :type recursive: bool
        :param depth: The depth to recursively search for files and directories.
        :param recursive: Whether to recursively search for files and directories.
        :returns: A list of File(...) and Directory(...) instances
        """

        list_ = []
        try:
            for item in self.os.listdir(self.path):
                if self.os.path.isdir(self.os.path.join(self.path, item)):
                    list_.append(Directory(self.os.path.join(self.path, item)))
                if self.os.path.isfile(self.os.path.join(self.path, item)):
                    list_.append(File(self.os.path.join(self.path, item)))
        except PermissionError:
            pass
        return list_

    def index(self, recursive=False, depth=5) -> _t.List[_t.Union['File', 'Directory']]:
        """
        Indexes the directory

        :type depth: int
        :type recursive: bool
        :param depth: The depth to recursively search for files and directories.
        :param recursive: Whether to recursively search for files and directories.
        :returns: A list of File(...) and Directory(...) objects
        """

        list_ = []
        items = self.listdirs()
        dirs = items.copy()
        if recursive and depth > 0:
            for dir_ in dirs:
                items.extend(dir_.index(recursive, depth - 1))
        list_.extend(items)
        list_.extend(self.listfiles())
        return list_

    def listdirs(self) -> _t.List['Directory']:
        """
        Lists directories in the directory

        :returns: A list of Directory(...) objects
        """

        list_ = []
        try:
            for item in self.os.listdir(self.path):
                if self.os.path.isdir(self.os.path.join(self.path, item)):
                    list_.append(Directory(self.os.path.join(self.path, item)))
        except PermissionError:
            pass
        return list_

    def listfiles(self) -> _t.List['File']:
        """
        Lists files in the directory.

        :returns: A list of File(...) objects.
        """

        list_ = []
        try:
            for item in self.os.listdir(self.path):
                if self.os.path.isfile(self.os.path.join(self.path, item)):
                    list_.append(File(self.os.path.join(self.path, item)))
        except PermissionError:
            pass
        return list_

    @staticmethod
    def _split_path(path: str) -> _t.Tuple:
        """
        Splits the path into a list, and then returns it.

        :param path: The path to split into a list.
        :returns: The splitted path.
        """

        return tuple(path.replace("\\", "/").split("/"))

    def upper(self) -> 'Directory':
        """
        Get directory above the directory.

        :returns: The directory above.
        """

        s_path = self._split_path(self.path)
        print(s_path)
        if len(s_path) >= 2:
            up = self.os.path.split(self.path)[0]
            print(up)
            return Directory(up)
        return Directory(self.path)

    def __repr__(self):
        return f"{self.__class__.__name__}(<{self.path}>)"

    def __str__(self):
        return self.path


class File(object):
    def __init__(self, path):
        """
        File base class

        :param path: The path to the file
        """

        import os
        import mimetypes

        self.directory = Directory(os.path.abspath(os.path.join(*os.path.split(path)[:-1])))
        self.path: str = path
        self.absPath: str = os.path.abspath(path)
        self.fileName: str = os.path.split(self.absPath)[-1]
        self.fileExt: str = os.path.splitext(self.fileName)[-1]

        try:
            self.relPath: str = os.path.relpath(path)
        except ValueError:
            self.relPath: _t.Optional[str] = None
        self._os = os

        self._fd: _t.Optional[_t.Union[_t.TextIO, _t.BinaryIO]] = None
        self._fileOpen = False

        try:
            self.mimeType = mimetypes.read_mime_types(self.path)
        except UnicodeDecodeError:
            pass

    def start_file(self) -> None:
        """
        Starts the file

        :returns: Nothing
        """

        self._os.startfile(self.path)

    def open(self, mode="w") -> _t.Union[_t.TextIO, _t.BinaryIO]:
        """
        Opens the file

        :param mode: The file mode to open.
        :returns: The open(...) return value, type: typing.TextIO.
        """

        if not self._fileOpen:
            self._fileOpen = True
            return open(self.path, mode)  # type: _t.Union[_t.TextIO, _t.BinaryIO]
        else:
            raise OSError(f"File {self.path} already opened")

    def close(self):
        """
        Closes the file

        :returns: Nothing
        """

        self._fd.close()
        self._fileOpen = False

    def exists(self) -> bool:
        """
        Returns True if the file exists, returns False otherwise

        :returns: True if the file exists else otherwise.
        """

        return self._os.path.exists(self.path)

    # noinspection PyTypeChecker
    def read(self, size=None) -> bytes:
        """
        Reads the file and returns a bytes-object

        :param size:
        :returns: The bytes-object read from the file
        """

        file_was_open = self._fileOpen
        if not self._fileOpen:
            self.open(mode="rb")

        data: bytes = self._fd.read(size)

        if not file_was_open:
            self.close()

        return data

    def readstring(self, size=None) -> str:
        """
        Reads the file and returns a string

        :param size:
        :returns: The string read from the file
        """

        file_was_open = self._fileOpen
        if not self._fileOpen:
            self.open(mode="r")

        data = self._fd.read(size)

        if not file_was_open:
            self.close()

        return data

    def write(self, data) -> None:
        """
        Writes a string, based on what the value was, uses repr() for non-string or non-bytes objects

        :param data: The value to write to the file
        :returns: Nothing, yes, nothing.
        """

        if type(data) == str:
            data: str
            self._fd.write(data.encode())
        elif type(data) in [bytes, bytearray]:
            self._fd.write(data)
        elif type(data) in [int, float, bool]:
            self._fd.write(str(data).encode())
        elif type(data) in [dict, list]:
            import json
            self._fd.write((json.JSONEncoder().encode(data)).encode())
        elif type(data) in [tuple]:
            import json
            self._fd.write((json.JSONEncoder().encode(list(data))).encode())
        else:
            self._fd.write(repr(data))

    def write_lines(self, data: _t.Union[_t.List, _t.Tuple]) -> None:
        """
        Writes a list or tuple of lines to the file

        :param data: The value to write
        :returns: Nothing
        """

        for obj in data:
            self.write(obj)

    def write_yaml(self, data) -> None:
        """
        Writes a yaml structured file

        :param data: The value to write
        :returns: Nothing
        """

        import yaml

        file_was_open = self._fileOpen
        if not self._fileOpen:
            self.open(mode="r")

        yaml.dump(data, self._fd)

        if file_was_open:
            self.close()

    def write_at(self, offset: int, data) -> None:
        """
        Writes value on the given offset, non-string or non-bytes value will use repr()

        :param offset: The offset to write the value
        :param data: The value to write
        :return:
        """

        fd = self.open(mode="r+b")
        fd.seek(offset)

        if type(data) == str:
            data: str
            fd.write(data.encode())
        elif type(data) in [bytes, bytearray]:
            fd.write(data)
        fd.close()
        self._fileOpen = False

    def read_at(self, offset: int, size: int = 1) -> bytes:
        """
        Reads value with the given offset and the given size from the file. Returns bytes

        :param offset: The offset where the value should be read
        :param size: The size to read from the file
        :returns bytes:
        """

        self.open(mode="r+b")
        self._fd.seek(offset)

        # noinspection PyTypeChecker,PyTypeChecker
        return self._fd.read(size)

    def create(self, size=0):
        """
        Creates a file with the given size, creating a file with an size is superfast!
        Trick: Seek with the offset 'size - 1' write the symbol chr(0) and close the file!

        :param size: The size to read from the file
        :return:
        """

        if self.exists():
            raise IOError("File already exists! Creating a file is only possible when the file doesn't exists")

        if self._fileOpen:
            raise IOError("File was already opened! Currently you can only create a file if the file wasn't open")

        fd = self.open("w+")
        fd.seek(size - 1)
        fd.write(chr(0))
        fd.close()

    def remove(self) -> None:
        """
        Removes the file.

        :returns: Nothing
        """

        self._os.remove(self.path)

    def delete(self):
        """
        Removes the file

        :returns: Nothing
        """

        self.remove()

    def rename(self, name, change_path=True):
        """
        Renames the file, when change_path is True, the path of the File(...) instance will be changed too.

        :param name: The new name for the file.
        :param change_path: Whether to change the File(...) instance path.
        :return:
        """

        if not self._os.path.isabs(name):
            name = self._os.path.abspath(name)
        else:
            if not self._os.path.abspath(self._os.path.join(*self._os.path.split(name)[:-1])) == self.directory.path:
                raise IOError("Can't rename file to another directory")
        self._os.rename(self._os.path.abspath(self.path), name)

        if change_path:
            if self._os.path.isabs(self.path):
                self.path = self._os.path.abspath(name)
            else:
                self.path = self._os.path.relpath(name)

    def get_size(self) -> int:
        """
        Get the file size in bytes of the file.

        :returns: The file size in bytes.
        """

        return self._os.path.getsize(self.path)

    def __repr__(self):
        return f"{self.__class__.__name__}(<{repr(self.path)}>)"

    def __str__(self):
        return self.path

    readat = read_at
    writeat = write_at


class ExecutableFile(File):
    def __init__(self, path):
        """
        Executable file, *.exe for windows, known support: Windows 10

        :param path:
        """

        super(ExecutableFile, self).__init__(path)

        import subprocess
        self._subps = subprocess

    @staticmethod
    def _parse_command(file, *args: str):
        command = [file]

        for arg in args:
            if " " in arg:
                arg = '"' + arg + '"'
            command.append(arg)

        command_str = " ".join(command)
        return command_str

    def execute(self, *args: str) -> int:
        """
        Executes the executable file

        :param args: The arguments to execute the program with.
        :returns: The exit code of the process
        """

        command = self._parse_command(self.absPath, *args)
        return self._os.system(command)

    def subprocess(self, *args: str):
        """
        Creates a subprocess for the executable file

        :param args:
        :return:
        """

        self._subps.run([self.absPath, *args])

    def start(self, *args: str):
        """
        **NOTE:** This method is only available for Windows

        Starts the executable with the given arguments

        :param args: The arguments to start the program with.
        :returns: Nothing
        """

        self._subps.Popen(["cmd", "/k", "start", "", self.absPath, *args])


class PythonFile(File):
    def __init__(self, path):
        """
        File class for executable python files

        :param path:
        """

        super(PythonFile, self).__init__(path)

        import sys
        import subprocess
        self._sys = sys
        self._subps = subprocess

        self._pythonPath: _t.Optional[_PythonPath] = None

    def import_(self):
        """
        Imports the python file
        Returns a module

        :return:
        """

        self._pythonPath = _PythonPath()
        self._pythonPath.add(self.directory.absPath)
        import_ = __import__(self._os.path.splitext(self.fileName)[0])
        self._pythonPath.remove(self.directory.absPath)
        return import_

    def execute(self, glob=None, loc=None):
        """
        Executes the python file, possible with globals and locals

        :param glob:
        :param loc:
        :return:
        """

        if loc is None:
            loc = {}
        if glob is None:
            glob = {"__name__": "__main__"}
        code = self.readstring()
        exec(compile(code + "\n", self.absPath, 'exec'), glob, loc)

    def subprocess(self, *args):
        self._subps.run([self._sys.executable, self.absPath, *args])

    def pycompile(self, to: str):
        """
        Compiles using the py_compile module.

        :param to:
        :return:
        """

        if not to.endswith(".pyc"):
            raise ValueError("invalid argument 'to', file must have the .pyc extension")

        from py_compile import compile
        return compile(self.path, cfile=to)

    def compile(self, mode, optimize=2):
        """
        Compiles using the built-in compiler function.

        :param mode: The compiling mode.
        :param optimize: Compilation optimization level, 0 means no optimization, 1 means low level optimization,
                         2 means high level optimization.
        :return:
        """
        return compile(self.read(), self.fileName, mode, optimize=optimize)


class JsonFile(File):
    def __init__(self, path):
        """
        JsonFile base class

        :param path:
        """

        super(JsonFile, self).__init__(path)

        import json
        self._json = json

    def read(self, **kwargs):
        """
        Reads a *.json file

        :param kwargs:
        :return:
        """

        if len(kwargs.keys()) != 0:
            raise ValueError("Method 'read()' doesn't take keyword arguments")
        data = self.readstring()
        self._json.JSONDecoder().decode(data)

    def write(self, o):
        """
        Writes a *.json file

        :param o:
        :return:
        """

        json = self._json.JSONEncoder().encode(o)
        self.write(json)


class PickleFile(File):
    def __init__(self, path):
        """
        Pickle is a file format for python variables

        :param path:
        """

        super(PickleFile, self).__init__(path)

        import pickle
        self._pickle = pickle

    # noinspection PyMethodOverriding
    def read(self):
        """
        Reads a pickle file

        :return:
        """

        # if len(kwargs.keys()) != 0:
        #     raise ValueError("Method 'read()' doesn't take keyword arguments")
        data = super().read()
        self._pickle.loads(data)

    def write(self, o):
        """
        Writes a pickle file

        :param o:
        :return:
        """

        data = self._pickle.dumps(o)
        super().write(data)


class DillFile(File):
    def __init__(self, path):
        """
        Pickle is a file format for python variables

        :param path:
        """

        super(DillFile, self).__init__(path)

        import dill
        self._dill = dill

    # noinspection PyMethodOverriding
    def read(self):
        """
        Reads a pickle file

        :return:
        """

        # if len(kwargs.keys()) != 0:
        #     raise ValueError("Method 'read()' doesn't take keyword arguments")
        data = super().read()
        self._dill.loads(data)

    def write(self, o):
        """
        Writes a pickle file

        :param o:
        :return:
        """

        data = self._dill.dumps(o)
        super().write(data)


class YamlFile(File):
    def __init__(self, path):
        """
        Yaml file (*.yaml) (*.yml)

        :param path:
        """

        super(YamlFile, self).__init__(path)

        import yaml
        import io
        self._yaml = yaml
        self._io = io

    def read(self, **kwargs):
        """
        Reads the Yaml file

        :param kwargs:
        :return:
        """

        if len(kwargs.keys()) != 0:
            raise ValueError("Method 'read()' doesn't take keyword arguments")
        data = super().readstring()
        stream = self._io.StringIO(data)
        self._yaml.full_load(stream)
        stream.close()

    def write(self, o):
        """
        Writes the Yaml file

        :param o:
        :return:
        """

        stream = self._io.StringIO()
        self._yaml.dump(o, stream)
        super().write(stream.read())
        stream.close()


class _ZipFile(File):
    def __init__(self, path, password=None, mode="w"):
        # print(mode)
        super().__init__(path)

        import zipfile
        self._zipfile = zipfile

        self._currentDir = ""
        self.zipfile = zipfile.ZipFile(path, mode)
        self.password = password

    def chdir(self, path):
        path = self.get_fp(path)
        self._currentDir = path

    def getcwd(self):
        return self._currentDir

    @staticmethod
    def split_path(path: str):
        return tuple(path.replace("\\", "/").split("/"))

    def get_fp(self, fp=None):
        if not fp:
            fp = self._currentDir
        else:
            if not self._os.path.isabs(fp):
                fp = self._os.path.join(self._currentDir, fp).replace("\\", "/")

        fp = "/" + fp

        fp = fp.replace("\\", "/")

        if fp[-1] == "/" and fp != "/":
            fp = fp[:-1]

        return fp[1:]

    def listdir(self, fp=None):
        fp = self.get_fp(fp)
        list_ = []
        # print(self.zipfile.infolist())
        for item in self.zipfile.infolist():
            if len(self.split_path(item.filename)) >= 2:
                # print(item.filename)
                # print(self.split_path(item.filename))
                # print(self.os.path.split(item.filename))
                s_path2 = self.split_path(item.filename)[:-1]
                s_path3 = self._os.path.join(
                    s_path2[0] if len(s_path2) >= 2 else "", *[s_path2[1]] if len(s_path2) >= 3 else []). \
                    replace("\\", "/")

                # print("SPath:", s_path2)
                # print("SPath 3:", s_path3)
                if s_path2:
                    if s_path3 == fp:
                        list_.append(self.split_path(item.filename)[-2])
            if self._os.path.join(*self._os.path.split(item.filename)[:-1]) == fp:
                list_.append(self._os.path.split(item.filename)[-1])
        return list_

    def listfiles(self, fp=None):
        fp = self.get_fp(fp)

        list_ = []
        # print(self.zipfile.infolist())
        # for item in self.zipfile.infolist():
        #     print("File [x] == [ ]:", self.os.path.join(*self.os.path.split(item.filename)[:-1]))
        #     print("File [ ] == [x]:", fp)
        #     if self.os.path.join(*self.os.path.split(item.filename)[:-1]) == fp:
        #         if not item.is_dir():
        #             list_.append(self.os.path.split(item.filename)[-1])

        for item in self.zipfile.infolist():
            # if len(self.split_path(item.filename)) >= 2:
            #     print(item.filename)
            #     print(self.split_path(item.filename))
            #     print(self.os.path.split(item.filename))
            #     s_path2 = self.split_path(item.filename)[:-1]
            #     s_path3 = self.os.path.join(
            #         s_path2[0] if len(s_path2) >= 2 else "", *[s_path2[1]] if len(s_path2) >= 3 else []). \
            #         replace("\\", "/")
            #
            #     print("SPath:", s_path2)
            #     print("SPath 3:", s_path3)
            #     if s_path2:
            #         if s_path3 == fp:
            #             list_.append(self.split_path(item.filename)[-2])
            file1 = self._os.path.join(*self._os.path.split(item.filename)[:-1])
            # if item.filename[-1] != "/":
            #     if item.filename.count("/") > 0:
            #         file2 = item.filename.split("/")[:-1]
            #     else:
            #         file2 = ""
            # else:
            #     file2 = item.filename.split("/")[:-2]

            file2 = fp
            # print("FILE [x] == [ ]:", file1)
            # print("FILE [ ] == [x]:", file2)
            # print("ITEM IS NOT DIR:", not item.is_dir())
            # print()
            if file1 == file2:
                if not item.is_dir():
                    list_.append(self._os.path.split(item.filename)[-1])
        return list_

    def listdirs(self, fp=None):
        fp = self.get_fp(fp)

        list_ = []
        # print(self.zipfile.infolist())
        for item in self.zipfile.infolist():
            # print("ITEM.FILENAME", item.filename)
            # print("SPLIT PATH", self.split_path(item.filename))
            # print("OS SPLIT", self.os.path.split(item.filename))
            if item.filename.count("/") > 0:
                s_path2 = self.split_path(item.filename)[:-1]
                s_path3 = "/".join(s_path2[:-1])

                # print("S_PATH:", s_path2)
                # print("S_PATH3:", s_path3)
                if s_path2:
                    if s_path3 == fp:
                        if item.filename[-1] == "/":
                            append_value1 = self.split_path(item.filename[:-1])[-1]
                        else:
                            append_value1 = self.split_path(item.filename)[-2]
                        if append_value1 not in list_ + [""]:
                            list_.append(append_value1)
            else:  # if self.os.path.join(*self.os.path.split(item.filename)[:-1]) == fp:
                if item.is_dir():
                    append_value2 = self._os.path.split(item.filename)[-1]
                    if append_value2 not in list_ + [""]:
                        list_.append(append_value2)
        return list_

    def close(self):
        self.zipfile.close()


# noinspection PyProtectedMember
class ZippedFile(object):
    def __init__(self, zip_file: _ZipFile, path: str, pwd=None):
        self.zipFormatFile = zip_file
        self.path = path
        self.password = pwd

        import zipfile
        import os
        self._zipfile = zipfile
        self._os = os

        self.fileName = self._os.path.split(path)[-1]

        self._fd: _t.Optional[zipfile.ZipExtFile] = None
        self._fileOpen = False

    # noinspection PyUnusedLocal
    def read(self, size=None):
        with self.zipFormatFile.zipfile.open(self.zipFormatFile.get_fp(self.path)[:], "r") as file:
            data = file.read()
        return data

    def readline(self, size=None):
        with self.zipFormatFile.zipfile.open(self.zipFormatFile.get_fp(self.path)[:], "r") as file:
            data = file.readline(limit=size)
        return data

    def write(self, data: _t.Union[bytes, bytearray]):
        with self.zipFormatFile.zipfile.open(self.path, "w", self.password) as file:
            file.write(data)

    def __repr__(self):
        return f"<ZippedFile '{self.path}'>"

    #
    # def __gt__(self, other):
    #     if type(other) == ZippedDirectory:
    #         other: ZippedDirectory
    #         return self.fileName > other.dirName
    #     elif type(other) == ZippedFile:
    #         other: ZippedFile
    #         return self.fileName > other.fileName
    #
    # def __ge__(self, other):
    #     if type(other) == ZippedDirectory:
    #         other: ZippedDirectory
    #         return self.fileName >= other.dirName
    #     elif type(other) == ZippedFile:
    #         other: ZippedFile
    #         return self.fileName >= other.fileName

    def __lt__(self, other):
        if type(other) == ZippedDirectory:
            other: ZippedDirectory
            return int(self._os.path.splitext(self.fileName)[0]) < int(self._os.path.splitext(other.dirName)[0])
        elif type(other) == ZippedFile:
            other: ZippedFile
            return int(self._os.path.splitext(self.fileName)[0]) < int(self._os.path.splitext(other.fileName)[0])
    #
    # def __le__(self, other):
    #     if type(other) == ZippedDirectory:
    #         other: ZippedDirectory
    #         return self.fileName <= other.dirName
    #     elif type(other) == ZippedFile:
    #         other: ZippedFile
    #         return self.fileName <= other.fileName
    #
    # def __eq__(self, other):
    #     if type(other) == ZippedDirectory:
    #         other: ZippedDirectory
    #         return False
    #     elif type(other) == ZippedFile:
    #         other: ZippedFile
    #         return self.fileName == other.fileName
    #
    # def __ne__(self, other):
    #     if type(other) == ZippedDirectory:
    #         other: ZippedDirectory
    #         return True
    #     elif type(other) == ZippedFile:
    #         other: ZippedFile
    #         return self.fileName != other.fileName


# noinspection PyProtectedMember
class ZippedDirectory(object):
    def __init__(self, zip_file: _ZipFile, path, pwd=None):
        import os
        self._os = os

        self.zipFormatFile = zip_file
        self.path = path
        self.password = pwd
        self.dirName = os.path.split(path)[-1]

    def create(self):
        pass

    def listdir(self):
        return self.index()

    def index(self):
        list_ = []
        # print(self.path)
        # print(self.zipFormatFile.listdir(self.path))
        # print(self.zipFormatFile.listdirs(self.path))
        for dir_ in self.zipFormatFile.listdirs(self.path):
            # print("LIST DIRS IN FOLDER", self.path, "ARE", self.zipFormatFile.listdirs(self.path))
            list_.append(
                ZippedDirectory(self.zipFormatFile, self.zipFormatFile.get_fp(self._os.path.join(self.path, dir_)),
                                self.password))

        for file in self.zipFormatFile.listfiles(self.path):
            # print("LIST FILES IN FOLDER", self.path, "ARE", self.zipFormatFile.listfiles(self.path))
            list_.append(
                ZippedFile(self.zipFormatFile, self.zipFormatFile.get_fp(self._os.path.join(self.path, file)),
                           self.password))
        return list_

    def listfiles(self):
        # print("LIST FILES IN FOLDER", self.path, "ARE", self.zipFormatFile.listfiles(self.path))
        return [
            ZippedFile(self.zipFormatFile, self._os.path.join(self.path, file).replace("\\", "/"), self.password)
            for file in self.zipFormatFile.listfiles(self.path)]

    def listdirs(self):
        return [
            ZippedDirectory(self.zipFormatFile, self._os.path.join(self.path, dir_).replace("\\", "/"), self.password)
            for dir_ in self.zipFormatFile.listdirs(self.path)]

    def __repr__(self):
        return f"<ZippedDirectory '{self.path}' at '{self.__hash__()}'>"

    def __lt__(self, other):
        if type(other) == ZippedDirectory:
            other: ZippedDirectory
            return int(self._os.path.splitext(self.dirName)[0]) < int(self._os.path.splitext(other.dirName)[0])
        elif type(other) == ZippedFile:
            other: ZippedFile
            return int(self._os.path.splitext(self.dirName)[0]) < int(self._os.path.splitext(other.fileName)[0])


class ZipArchive(ZippedDirectory):
    def __init__(self, path, mode="r", password=None):
        # print(mode)
        import os
        mode = mode.replace("b", "")
        mode = mode.replace("+", "")
        zip_file = _ZipFile(path, mode=mode, password=password)
        if password:
            zip_file.zipfile.setpassword(password)
        super().__init__(zip_file, "", pwd=password)

        self.absPath: str = os.path.abspath(path)
        try:
            self.relPath: str = os.path.relpath(path)
        except ValueError:
            self.relPath: _t.Optional[str] = None


class NZTFile(ZipArchive):
    def __init__(self, filename, mode="rb"):
        super().__init__(filename, mode)

        # Modules
        import zipfile
        import pickle
        self._zipfile = zipfile
        self._pickle = pickle

        # Dictionaries
        self._contents: dict = {}
        self.data: dict = {}

    def _save_value(self, fp, value):
        # with self.zipFormatFile.zipfile.open(fp, "w") as file:
        #     pickle.dump(value, file, protocol=2)
        #     file.close()
        a = self.zipFormatFile.zipfile.open(fp, "w")
        self._pickle.dump(value, a, 4)
        a.close()

    def _save(self, fp: str, data: _t.Union[dict, list, tuple]):
        # print("LISTDIR:", fp)
        if type(data) == dict:
            for key, value in data.items():
                if type(value) == int:
                    self._save_value(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{key}.int")), value)
                elif type(value) == float:
                    self._save_value(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{key}.float")), value)
                elif type(value) == str:
                    self._save_value(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{key}.str")), value)
                elif type(value) == bytes:
                    self._save_value(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{key}.bytes")), value)
                elif type(value) == bytearray:
                    self._save_value(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{key}.bytearray")), value)
                elif type(value) == bool:
                    self._save_value(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{key}.bool")), value)
                elif type(value) == list:
                    self.zipFormatFile.zipfile.writestr(
                        self._zipfile.ZipInfo(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{key}.list/")) + "/"),
                        '')
                    self._save(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{key}.list")), value)
                elif type(value) == tuple:
                    self.zipFormatFile.zipfile.writestr(
                        self._zipfile.ZipInfo(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{key}.list/")) + "/"),
                        '')
                    self._save(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{key}.list")), value)
                elif type(value) == dict:
                    self.zipFormatFile.zipfile.writestr(
                        self._zipfile.ZipInfo(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{key}.dict/")) + "/"),
                        '')
                    self._save(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{key}.dict")), value)
                elif value is None:
                    self._save_value(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{key}.none")), None)
                elif type(value) == type:
                    self._save_value(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{key}.type")), value)
                else:
                    self._save_value(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{key}.object")), value)
        elif type(data) in [list, tuple]:
            for index in range(len(data)):
                value = data[index]
                if type(value) == int:
                    self._save_value(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{index}.int")), value)
                elif type(value) == float:
                    self._save_value(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{index}.float")), value)
                elif type(value) == str:
                    self._save_value(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{index}.str")), value)
                elif type(value) == bytes:
                    self._save_value(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{index}.bytes")), value)
                elif type(value) == bytearray:
                    self._save_value(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{index}.bytearray")), value)
                elif type(value) == bool:
                    self._save_value(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{index}.bool")), value)
                elif type(value) == list:
                    self.zipFormatFile.zipfile.writestr(
                        self._zipfile.ZipInfo(
                            self.zipFormatFile.get_fp(self._os.path.join(fp, f"{index}.list/")) + "/"), '')
                    self._save(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{index}.list")), value)
                elif type(value) == tuple:
                    self.zipFormatFile.zipfile.writestr(
                        self._zipfile.ZipInfo(
                            self.zipFormatFile.get_fp(self._os.path.join(fp, f"{index}.tuple/")) + "/"), '')
                    self._save(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{index}.tuple")), value)
                elif type(value) == dict:
                    self.zipFormatFile.zipfile.writestr(
                        self._zipfile.ZipInfo(
                            self.zipFormatFile.get_fp(self._os.path.join(fp, f"{index}.dict/")) + "/"), '')
                    self._save(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{index}.dict")), value)
                elif value is None:
                    self._save_value(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{index}.none")), None)
                elif type(value) == type:
                    self._save_value(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{index}.type")), value)
                else:
                    self._save_value(self.zipFormatFile.get_fp(self._os.path.join(fp, f"{index}.object")), value)

    def save(self):
        # self.zipFormatFile.zipfile("w")
        for key, value in self.data.items():
            if type(value) == int:
                # print(f"{key}.int")
                self._save_value(f"{key}.int", value)
            elif type(value) == float:
                self._save_value(f"{key}.float", value)
            elif type(value) == str:
                self._save_value(f"{key}.str", value)
            elif type(value) == bytes:
                self._save_value(f"{key}.bytes", value)
            elif type(value) == bytearray:
                self._save_value(f"{key}.bytearray", value)
            elif type(value) == bool:
                self._save_value(f"{key}.bool", value)
            elif type(value) == list:
                self.zipFormatFile.zipfile.writestr(
                    self._zipfile.ZipInfo(f"{key}.list/"), '')
                self._save(self.zipFormatFile.get_fp(f"{key}.list"), value)
            elif type(value) == tuple:
                self.zipFormatFile.zipfile.writestr(
                    self._zipfile.ZipInfo(f"{key}.tuple/"), '')
                self._save(self.zipFormatFile.get_fp(f"{key}.tuple"), value)
            elif type(value) == dict:
                self.zipFormatFile.zipfile.writestr(
                    self._zipfile.ZipInfo(f"{key}.dict/"), '')
                self._save(self.zipFormatFile.get_fp(f"{key}.dict"), value)
            elif type(value) == type:
                self._save_value(f"{key}.type", value)
            elif value is None:
                self._save_value(f"{key}.none", None)
            else:
                self._save_value(f"{key}.object", value)
        self.zipFormatFile.zipfile.close()

    def _load_value(self, zipped_file: ZippedFile):
        return self._pickle.loads(zipped_file.read())

    def _load(self, zipped_dir: ZippedDirectory, data: _t.Union[dict, list, tuple]):
        # print("ZIPPED DIR PATH:", zipped_dir.path)
        # print("ZIPPED DIR INDEX:", zipped_dir.index())
        index = zipped_dir.index()
        if type(data) == dict:
            for item in index:
                if type(item) == ZippedDirectory:
                    if self._os.path.splitext(item.dirName)[-1] == ".dict":
                        data[self._os.path.splitext(item.dirName)[0]] = self._load(item, {})
                    elif self._os.path.splitext(item.dirName)[-1] == ".list":
                        data[self._os.path.splitext(item.dirName)[0]] = self._load(item, [])
                    elif self._os.path.splitext(item.dirName)[-1] == ".tuple":
                        data[self._os.path.splitext(item.dirName)[0]] = self._load(item, ())
                elif type(item) == ZippedFile:
                    if self._os.path.splitext(item.fileName)[-1] in [".float", ".int", ".bool", ".str",
                                                                     ".object", ".type", ".bytes", ".bytearray"]:
                        data[self._os.path.splitext(item.fileName)[0]] = self._load_value(item)
                    elif self._os.path.splitext(item.fileName)[-1] == ".none":
                        data[self._os.path.splitext(item.fileName)[0]] = None
            return data
        elif type(data) == list:
            index.sort()
            # print("LIST:", index)
            for item in index:
                if type(item) == ZippedDirectory:
                    if self._os.path.splitext(item.dirName)[-1] == ".dict":
                        data.append(self._load(item, {}))
                    elif self._os.path.splitext(item.dirName)[-1] == ".list":
                        data.append(self._load(item, []))
                    elif self._os.path.splitext(item.dirName)[-1] == ".tuple":
                        data.append(self._load(item, ()))
                elif type(item) == ZippedFile:
                    if self._os.path.splitext(item.fileName)[-1] in [".float", ".int", ".bool", ".str",
                                                                     ".object", ".type", ".bytes", ".bytearray"]:
                        data.append(self._load_value(item))
                    elif self._os.path.splitext(item.fileName)[-1] == ".none":
                        data.append(None)
            return data
        elif type(data) == tuple:
            index.sort()
            # print("TUPLE:", index)
            data = []
            for item in index:
                if type(item) == ZippedDirectory:
                    if self._os.path.splitext(item.dirName)[-1] == ".dict":
                        data.append(self._load(item, {}))
                    elif self._os.path.splitext(item.dirName)[-1] == ".list":
                        data.append(self._load(item, []))
                    elif self._os.path.splitext(item.dirName)[-1] == ".tuple":
                        data.append(self._load(item, ()))
                elif type(item) == ZippedFile:
                    if self._os.path.splitext(item.fileName)[-1] in [".float", ".int", ".bool", ".str",
                                                                     ".object", ".type", ".bytes", ".bytearray"]:
                        data.append(self._load_value(item))
                    elif self._os.path.splitext(item.fileName)[-1] == ".none":
                        data.append(None)
            return tuple(data)

    def load(self):
        data = {}
        index = self.index()
        # print("INDEX():", index)
        for item in index:
            if type(item) == ZippedDirectory:
                if self._os.path.splitext(item.dirName)[-1] == ".dict":
                    data[self._os.path.splitext(item.dirName)[0]] = self._load(item, {})
                elif self._os.path.splitext(item.dirName)[-1] == ".list":
                    data[self._os.path.splitext(item.dirName)[0]] = self._load(item, [])
                elif self._os.path.splitext(item.dirName)[-1] == ".tuple":
                    data[self._os.path.splitext(item.dirName)[0]] = self._load(item, ())
            elif type(item) == ZippedFile:
                if self._os.path.splitext(item.fileName)[-1] in [".float", ".int", ".bool", ".str",
                                                                 ".object", ".type", ".bytes", ".bytearray"]:
                    data[self._os.path.splitext(item.fileName)[0]] = self._load_value(item)
                elif self._os.path.splitext(item.fileName)[-1] == ".none":
                    data[self._os.path.splitext(item.fileName)[0]] = None
        self.data = data
        return data

    def close(self):
        self.zipFormatFile.close()


class EncryptedFile(File):
    def __init__(self, path, key):
        """
        Uses ARC4 to encrypt.

        :param path:
        """
        super(EncryptedFile, self).__init__(path)
        self.key = key

    # noinspection PyMethodOverriding
    def read(self, size=None):
        if size is not None:
            raise ValueError("The size argument must not be specified")

        fd = self.open("rb+")
        encrypted_data = fd.read()
        if isinstance(encrypted_data, bytes):
            data = _ARC4.ARC4Cipher(self.key).decrypt(encrypted_data)
        else:
            raise IOError(f"Invalid data, expected bytes not {type(encrypted_data).__name__}")
        return data

    def write(self, data: bytes):
        fd = self.open("wb+")
        encrypted_data = _ARC4.ARC4Cipher(self.key).encrypt(data)
        fd.write(encrypted_data)


class NZT2File(NZTFile):
    def __init__(self, path, mode="r"):
        super(NZT2File, self).__init__(path, mode)

        import dill
        self._pickle = dill


class TextFile(File):
    def __init__(self, path):
        super(TextFile, self).__init__(path)

    def read(self, size=None) -> str:
        with open(self.path, "r") as file:
            data = file.read(size)
            file.close()
        return data

    def readline(self, limit=None) -> str:
        with open(self.path, "r") as file:
            data = file.readline(limit)
            file.close()
        return data

    def readlines(self, hint=None) -> _t.List[str]:
        with open(self.path, "r") as file:
            data = file.readlines(hint)
            file.close()
        return data

    def read_at(self, offset: int, size: int = 1) -> str:
        """
        Reads value with the given offset and the given size from the file. Returns str

        :param offset:
        :param size:
        :returns bytes:
        """

        self.open(mode="r+b")
        self._fd.seek(offset)

        # noinspection PyUnresolvedReferences
        return self._fd.read(size).decode()

    def write(self, o: str = "") -> _t.NoReturn:
        with open(self.path, "w") as file:
            file.write(o)
            file.close()

    def writelines(self, lines: _t.Iterable[str]) -> _t.NoReturn:
        with open(self.path, "w") as file:
            file.writelines(lines)
            file.close()

    def write_at(self, offset: int, data: str) -> _t.NoReturn:
        """
        Writes value on the given offset, non-string or non-bytes value will use repr()

        :param offset:
        :param data:
        :return:
        """

        self.open(mode="w+b")
        self._fd.seek(offset)

        data: str
        self._fd.write(data.encode())

    readat = read_at
    writeat = write_at


class BinaryFile(File):
    def __init__(self, path):
        super(BinaryFile, self).__init__(path)

    def read(self, size=None) -> bytes:
        with open(self.path, "rb") as file:
            data = file.read(size)
            file.close()
        return data

    def readline(self, limit=None) -> bytes:
        with open(self.path, "rb") as file:
            data = file.readline(limit)
            file.close()
        return data

    def readlines(self, hint=None) -> _t.List[bytes]:
        with open(self.path, "rb") as file:
            data = file.readlines(hint)
            file.close()
        return data

    def read_at(self, offset: int, size: int = 1) -> bytes:
        """
        Reads value with the given offset and the given size from the file. Returns str

        :param offset:
        :param size:
        :returns bytes:
        """

        self.open(mode="r+b")
        self._fd.seek(offset)

        # noinspection PyTypeChecker
        return self._fd.read(size)

    def write(self, o: bytes = b"") -> _t.NoReturn:
        with open(self.path, "wb") as file:
            file.write(o)
            file.close()

    def writelines(self, lines: _t.Iterable[bytes]) -> _t.NoReturn:
        with open(self.path, "wb") as file:
            file.writelines(lines)
            file.close()

    def write_at(self, offset: int, data: bytes) -> _t.NoReturn:
        """
        Writes value on the given offset, non-string or non-bytes value will use repr()

        :param offset:
        :param data:
        :return:
        """

        self.open(mode="w+b")
        self._fd.seek(offset)

        if type(data) == str:
            data: str
            self._fd.write(data.encode())
        elif type(data) in [bytes, bytearray]:
            self._fd.write(data)
        elif type(data) in [int, float, bool]:
            self._fd.write(str(data).encode())

    readat = read_at
    writeat = write_at


class TomlFile(File):
    def __init__(self, path):
        super(TomlFile, self).__init__(path)

        import toml
        self._toml = toml

    def read(self, *args) -> dict:
        if args:
            raise ValueError("TomlFile(...).read(...) doen't take any arguments")

        with open(self.path, "r") as file:
            data = self._toml.loads(file.read())
        return data

    def write(self, o: dict) -> _t.NoReturn:
        with open(self.path, "w") as file:
            file.write(self._toml.dumps(o))


class HtmlFile(File):
    def __init__(self, path):
        super(HtmlFile, self).__init__(path)

    def get_code_class(self) -> _HtmlCode:
        fd = self.open("r")
        code = _HtmlCode(fd.read())
        fd.close()
        return code


class PngFile(File):
    def __init__(self, path):
        super(PngFile, self).__init__(path)

    def get_pillowimage(self, filemode="r") -> _Image:
        from PIL.Image import open
        return open(self.absPath, filemode)

    def get_tkimage(self) -> _tk.PhotoImage:
        from tkinter import PhotoImage
        return PhotoImage(file=self.absPath)


class WindowsShortcut(File):
    if _PLATFORM != _PLATFORM_WINDOWS:
        raise OSError("WindowsShortcut(...) is Windows-only")

    def __init__(self, path):
        super(WindowsShortcut, self).__init__(path)

        # Import modules
        import sys
        import pythoncom

        # Make attribytes for modules
        self._sys = sys
        self._pycom = pythoncom
        self._shell = _shell
        self._shellcon = _shellcon

    def _create_old(self, dest: str = "", description: str = "", icon: _t.Optional[_t.Tuple[str, int]] = None):
        import sys
        from comtypes import CLSCTX_INPROC_SERVER, CoCreateInstance
        from comtypes.persist import IPersistFile

        shortcut = CoCreateInstance(
            _shell.CLSID_ShellLink,
            None,
            CLSCTX_INPROC_SERVER,
            _shell.IID_IShellLink
        )

        shortcut.SetPath(dest)
        shortcut.SetDescription(description)
        if icon:
            shortcut.SetIconLocation(icon[0], icon[1])
        else:
            shortcut.SetIconLocation(sys.executable, 0)

        persist_file = shortcut.QueryInterface(IPersistFile)
        persist_file.Save(self.path, 0)

    def create(self, target: str = "", icon: _t.Tuple[str, int] = None, is_threaded=False, windows_state=WINDOW_NORMAL):
        import win32com.client
        import os
        from comtypes import CoInitialize

        if not os.path.isabs(target):
            raise OSError("The path of the shortcut target must be absolute")

        if is_threaded:
            CoInitialize()

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(self.absPath)
        shortcut.SetTargetPath(target)
        shortcut.SetIconLocation(icon[0], icon[1])
        shortcut.SetWindowStyle(7)  # 7 - Minimized, 3 - Maximized, 1 - Normal
        shortcut.save()


class WinSpecialFolders(_Enum):
    if _shell is not None:
        if _shellcon is not None:
            Fonts = _shell.SHGetFolderPath(0, _shellcon.CSIDL_FONTS, 0, 0)
            # Drives = shell.SHGetFolderPath(0, shellcon.CSIDL_DRIVES, 0, 0)  # Has problems
            Recent = _shell.SHGetFolderPath(0, _shellcon.CSIDL_RECENT, 0, 0)
            SendTo = _shell.SHGetFolderPath(0, _shellcon.CSIDL_SENDTO, 0, 0)
            System = _shell.SHGetFolderPath(0, _shellcon.CSIDL_SYSTEM, 0, 0)
            AppData = _shell.SHGetFolderPath(0, _shellcon.CSIDL_APPDATA, 0, 0)
            Cookies = _shell.SHGetFolderPath(0, _shellcon.CSIDL_COOKIES, 0, 0)
            Desktop = _shell.SHGetFolderPath(0, _shellcon.CSIDL_DESKTOP, 0, 0)
            History = _shell.SHGetFolderPath(0, _shellcon.CSIDL_HISTORY, 0, 0)
            MyMusic = _shell.SHGetFolderPath(0, _shellcon.CSIDL_MYMUSIC, 0, 0)
            MyVideo = _shell.SHGetFolderPath(0, _shellcon.CSIDL_MYVIDEO, 0, 0)
            NetHood = _shell.SHGetFolderPath(0, _shellcon.CSIDL_NETHOOD, 0, 0)
            # Network = shell.SHGetFolderPath(0, shellcon.CSIDL_NETWORK, 0, 0)  # Has problems
            Profile = _shell.SHGetFolderPath(0, _shellcon.CSIDL_PROFILE, 0, 0)
            Windows = _shell.SHGetFolderPath(0, _shellcon.CSIDL_WINDOWS, 0, 0)
            # Controls = shell.SHGetFolderPath(0, shellcon.CSIDL_CONTROLS, 0, 0)  # Has problems
            # Internet = shell.SHGetFolderPath(0, shellcon.CSIDL_INTERNET, 0, 0)  # Has problems
            Personal = _shell.SHGetFolderPath(0, _shellcon.CSIDL_PERSONAL, 0, 0)
            # Printers = shell.SHGetFolderPath(0, shellcon.CSIDL_PRINTERS, 0, 0)  # Has problems
            Programs = _shell.SHGetFolderPath(0, _shellcon.CSIDL_PROGRAMS, 0, 0)
            Favorites = _shell.SHGetFolderPath(0, _shellcon.CSIDL_FAVORITES, 0, 0)
            PrintHood = _shell.SHGetFolderPath(0, _shellcon.CSIDL_PRINTHOOD, 0, 0)
            Resources = _shell.SHGetFolderPath(0, _shellcon.CSIDL_RESOURCES, 0, 0)
            StartMenu = _shell.SHGetFolderPath(0, _shellcon.CSIDL_STARTMENU, 0, 0)
            SystemX86 = _shell.SHGetFolderPath(0, _shellcon.CSIDL_SYSTEMX86, 0, 0)
            Templates = _shell.SHGetFolderPath(0, _shellcon.CSIDL_TEMPLATES, 0, 0)
            AdminTools = _shell.SHGetFolderPath(0, _shellcon.CSIDL_ADMINTOOLS, 0, 0)
            MyPictures = _shell.SHGetFolderPath(0, _shellcon.CSIDL_MYPICTURES, 0, 0)
            CdBurnArea = _shell.SHGetFolderPath(0, _shellcon.CSIDL_CDBURN_AREA, 0, 0)
            # Connections = shell.SHGetFolderPath(0, shellcon.CSIDL_CONNECTIONS, 0, 0)  # Has problems
            # MyDocuments = shell.SHGetFolderPath(0, shellcon.CSIDL_MYDOCUMENTS, 0, 0)  # Has problems
            CommonMusic = _shell.SHGetFolderPath(0, _shellcon.CSIDL_COMMON_MUSIC, 0, 0)
            CommonVideo = _shell.SHGetFolderPath(0, _shellcon.CSIDL_COMMON_VIDEO, 0, 0)
            LocalAppData = _shell.SHGetFolderPath(0, _shellcon.CSIDL_LOCAL_APPDATA, 0, 0)
            CommonAppData = _shell.SHGetFolderPath(0, _shellcon.CSIDL_COMMON_APPDATA, 0, 0)
            CommonStartup = _shell.SHGetFolderPath(0, _shellcon.CSIDL_COMMON_STARTUP, 0, 0)
            InternetCache = _shell.SHGetFolderPath(0, _shellcon.CSIDL_INTERNET_CACHE, 0, 0)
            CommonPictures = _shell.SHGetFolderPath(0, _shellcon.CSIDL_COMMON_PICTURES, 0, 0)
            CommonPrograms = _shell.SHGetFolderPath(0, _shellcon.CSIDL_COMMON_PROGRAMS, 0, 0)
            # CommonOEMLinks = shell.SHGetFolderPath(0, shellcon.CSIDL_COMMON_OEM_LINKS, 0, 0)  # Has problems
            # ComputersNearMe = shell.SHGetFolderPath(0, shellcon.CSIDL_COMPUTERSNEARME, 0, 0)  # Has problems
            CommonDocuments = _shell.SHGetFolderPath(0, _shellcon.CSIDL_COMMON_DOCUMENTS, 0, 0)
            CommonFavorites = _shell.SHGetFolderPath(0, _shellcon.CSIDL_COMMON_FAVORITES, 0, 0)
            CommonStartMenu = _shell.SHGetFolderPath(0, _shellcon.CSIDL_COMMON_STARTMENU, 0, 0)
            CommonTemplates = _shell.SHGetFolderPath(0, _shellcon.CSIDL_COMMON_TEMPLATES, 0, 0)
            ProgramFilesX86 = _shell.SHGetFolderPath(0, _shellcon.CSIDL_PROGRAM_FILESX86, 0, 0)
            DesktopDirectory = _shell.SHGetFolderPath(0, _shellcon.CSIDL_DESKTOPDIRECTORY, 0, 0)
            CommonAdminTools = _shell.SHGetFolderPath(0, _shellcon.CSIDL_COMMON_ADMINTOOLS, 0, 0)
            CommonAltStartup = _shell.SHGetFolderPath(0, _shellcon.CSIDL_COMMON_ALTSTARTUP, 0, 0)
            # ResourcesLocalized = shell.SHGetFolderPath(0, shellcon.CSIDL_RESOURCES_LOCALIZED, 0, 0)  # Has problems
            ProgramFilesCommon = _shell.SHGetFolderPath(0, _shellcon.CSIDL_PROGRAM_FILES_COMMON, 0, 0)
            ProgramFilesCommonX86 = _shell.SHGetFolderPath(0, _shellcon.CSIDL_PROGRAM_FILES_COMMONX86, 0, 0)
            CommonDesktopDirectory = _shell.SHGetFolderPath(0, _shellcon.CSIDL_COMMON_DESKTOPDIRECTORY, 0, 0)


PickledFile = PickleFile

if __name__ == '__main__':
    def test_winspecialfolders():
        print(WinSpecialFolders.Profile)
        print(WinSpecialFolders.AppData)
        print(WinSpecialFolders.Desktop)
        print(WinSpecialFolders.Recent)
        print(WinSpecialFolders.CommonAppData)

        print(Directory("/").index(recursive=True, depth=2))

    def test_winexecutable():
        import os as _os
        ExecutableFile(
            "C:/Windows/notepad.exe"
        ).start(_os.path.join(str(WinSpecialFolders.Desktop), "TestDocument.txt"))

    test_winexecutable()
