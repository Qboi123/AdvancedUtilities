import io
from typing import Optional, Tuple, List, Union

from advUtils.system import PythonPath


class Directory(object):
    def __init__(self, path):
        """
        Base directory class

        :param path:
        """

        import os
        self.path = path
        self.os = os

        self.absPath: str = os.path.abspath(path)
        try:
            self.relPath: str = os.path.relpath(path)
        except ValueError:
            self.relPath: Optional[str] = None

    def listdir(self):
        """
        Indexes the directory
        Returns a list of File(...) and Directory(...) objects

        :return:
        """

        return self.index()

    def index(self):
        """
        Indexes the directory
        Returns a list of File(...) and Directory(...) objects

        :return:
        """

        list_ = []
        list_.extend(self.listdirs())
        list_.extend(self.listfiles())
        return list_

    def listdirs(self):
        """
        lists directories in the directory
        Returns a list of Directory(...) objects

        :return:
        """

        list_ = []
        for item in self.os.listdir(self.path):
            if self.os.path.isdir(self.os.path.join(self.path, item)):
                list_.append(Directory(self.os.path.join(self.path, item)))
        return list_

    def listfiles(self):
        """
        Lists files in the directory
        Returns a list of File(...) objects

        :return:
        """

        list_ = []
        for item in self.os.listdir(self.path):
            if self.os.path.isfile(self.os.path.join(self.path, item)):
                list_.append(File(self.os.path.join(self.path, item)))
        return list_

    @staticmethod
    def _split_path(path: str):
        """
        Returns splitted path

        :param path:
        :return:
        """

        return tuple(path.replace("\\", "/").split("/"))

    def upper(self):
        """
        Get directory above the directory

        :return:
        """

        s_path = self._split_path(self.path)
        print(s_path)
        if len(s_path) >= 2:
            up = self.os.path.split(self.path)[0]
            print(up)
            return Directory(up)
        return Directory(self.path)


class File(object):
    def __init__(self, path):
        """
        File base class

        :param path:
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
            self.relPath: Optional[str] = None
        self._os = os

        self._fd: Optional[io.IOBase] = None
        self._fileOpen = False

        try:
            self.mimeType = mimetypes.read_mime_types(self.path)
        except UnicodeDecodeError:
            pass

    def start_file(self):
        """
        Starts the file

        :return:
        """

        self._os.startfile(self.path)

    def open(self, mode="w"):
        """
        Opens the file

        :param mode:
        :return:
        """

        if not self._fileOpen:
            self._fd = open(self.path, mode)
            self._fileOpen = True
        else:
            raise OSError(f"File {self.path} already opened")

    def close(self):
        """
        Closes the file

        :return:
        """

        self._fd.close()
        self._fileOpen = False

    def exists(self):
        """
        Returns True if the file exists, returns False otherwise

        :return:
        """

        return self._os.path.exists(self.path)

    def read(self, size=None):
        """
        Reads the file and returns a bytes-object

        :param size:
        :return:
        """

        file_was_open = self._fileOpen
        if not self._fileOpen:
            self.open(mode="rb")

        data = self._fd.read(size)

        if not file_was_open:
            self.close()

        return data

    def readstring(self, size=None):
        """
        Reads the file and returns a string

        :param size:
        :return:
        """

        file_was_open = self._fileOpen
        if not self._fileOpen:
            self.open(mode="r")

        data = self._fd.read(size)

        if not file_was_open:
            self.close()

        return data

    def write(self, data):
        """
        Writes a string, based on what the value was, uses repr() for non-string or non-bytes objects

        :param data:
        :return:
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

    def write_lines(self, data: Union[List, Tuple]):
        """
        Writes a list or tuple of lines to the file

        :param data:
        :return:
        """

        for obj in data:
            self.write(obj)

    def write_yaml(self, data):
        """
        Writes a yaml structured file

        :param data:
        :return:
        """

        import yaml

        file_was_open = self._fileOpen
        if not self._fileOpen:
            self.open(mode="r")

        yaml.dump(data, self._fd)

        if file_was_open:
            self.close()

    def write_at(self, offset: int, data):
        """
        Writes data on the given offset, non-string or non-bytes data will use repr()

        :param offset:
        :param data:
        :return:
        """

        self.open(mode="r+b")
        self._fd.seek(offset)

        if type(data) == str:
            data: str
            self._fd.write(data.encode())
        elif type(data) in [bytes, bytearray]:
            self._fd.write(data)
        elif type(data) in [int, float, bool]:
            self._fd.write(str(data).encode())

    def read_at(self, offset: int, size: int = 1) -> bytes:
        """
        Reads data with the given offset and the given size from the file. Returns bytes

        :param offset:
        :param size:
        :returns bytes:
        """

        self.open(mode="r+b")
        self._fd.seek(offset)

        return self._fd.read(size)

    def create(self, size=0):
        """
        Creates a file with the given size, creating a file with an size is superfast!
        Trick: Seek with the offset 'size - 1' write the symbol chr(0) and close the file!

        :param size:
        :return:
        """

        if self.exists():
            raise IOError("File already exists! Creating a file is only possible when the file don't exists")

        if self._fileOpen:
            raise IOError("File was already opened! Currently you can only a file if the file wasn't open")

        self.open("w+")

        self._fd.seek(size - 1)
        self._fd.write(chr(0))
        self.close()

    def remove(self):
        self._os.remove(self.path)

    def delete(self):
        self.remove()

    def rename(self, name, change_path=True):
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

    def get_size(self):
        return self._os.path.getsize(self.path)


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
    def _parse_command(file, *args):
        command = [file]

        for arg in args:
            if " " in arg:
                arg = '"' + arg + '"'
            command.append(arg)

        command_str = " ".join(command)
        return command_str

    def execute(self, *args):
        """
        Executes the executable file

        :param args:
        :return:
        """

        command = self._parse_command(self.absPath, *args)
        self._os.system(command)

    def subprocess(self, *args):
        """
        Creates a subprocess for the executable file

        :param args:
        :return:
        """

        self._subps.run([self.absPath, *args])


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

        self._pythonPath: Optional[PythonPath] = None

    def import_(self):
        """
        Imports the python file
        Returns a module

        :return:
        """

        self._pythonPath = PythonPath()
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

    def read(self, **kwargs):
        """
        Reads a pickle file

        :param kwargs:
        :return:
        """

        if len(kwargs.keys()) != 0:
            raise ValueError("Method 'read()' doesn't take keyword arguments")
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
        data = super().read()
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

        self._fd: Optional[zipfile.ZipExtFile] = None
        self._fileOpen = False

    def read(self, size=None):
        with self.zipFormatFile.zipfile.open(self.zipFormatFile.get_fp(self.path)[:], "r") as file:
            data = file.read(size)
        return data

    def readline(self, size=None):
        with self.zipFormatFile.zipfile.open(self.zipFormatFile.get_fp(self.path)[:], "r") as file:
            data = file.readline(limit=size)
        return data

    def write(self, data: Union[bytes, bytearray]):
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
            self.relPath: Optional[str] = None


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

    def _save(self, fp: str, data: Union[dict, list, tuple]):
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

    def _load(self, zipped_dir: ZippedDirectory, data: Union[dict, list, tuple]):
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
