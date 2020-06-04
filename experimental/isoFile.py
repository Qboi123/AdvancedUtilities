import os
from io import BytesIO

import pycdlib

from advUtils.core.decorators import experimental


@experimental
def test1():
    a = pycdlib.PyCdlib(True)
    a.new()
    a.write("test.iso")
    # a.write_fp()


@experimental
def test2():
    import pycdlib

    iso = pycdlib.PyCdlib()
    iso.new()
    foostr = b'foo\n'
    iso.add_fp(BytesIO(foostr), len(foostr), '/FOO.;1')
    outiso = BytesIO()
    iso.write_fp(outiso)
    iso.close()

    iso.open_fp(outiso)

    bazstr = b'bazzzzzz\n'
    iso.modify_file_in_place(BytesIO(bazstr), len(bazstr), '/FOO.;1')

    iso.write("test2.iso")
    iso.close()

    # with open("test2.iso", "wb") as file:
    #     file.write(modifiediso.read())


@experimental
class IsoFile(object):
    def __init__(self, path, new=True, udf=True):
        self._iso = pycdlib.PyCdlib()

        if not os.path.exists(path):
            self._iso.new(4, udf="2.60" if udf else None)
        elif new:
            self._iso.new(4, udf="2.60" if udf else None)
        else:
            self._iso.open(path)

        self._path = path

    def write_file(self, fp, data):
        fp.replace("\\", "/")
        foostr = f"{fp}\n".encode()
        self._iso.add_fp(BytesIO(foostr), len(foostr), f'/{fp.upper()}.;1', udf_path="/"+fp)
        outiso = BytesIO()
        self._iso.write_fp(outiso)
        # self._iso.close()

        # self._iso.open_fp(outiso)

        bazstr = data.encode("utf-8")
        self._iso.modify_file_in_place(BytesIO(bazstr), len(bazstr), f'/{fp.upper()}.;1', udf_path="/"+fp)

        # modifiediso = BytesIO()
        # self._iso.write("test2.iso")
        # self._iso.close()

    writefile = write_file

    def modify_file(self, fp, data):
        fp = self._fix_path(fp)

        foostr = f"{fp[1:]}\n".encode()
        self._iso.add_fp(BytesIO(foostr), len(foostr), f'{fp.upper()}.;1', udf_path=fp)
        outiso = BytesIO()

        self._iso.open_fp(outiso)

        bazstr = data.encode("utf-8")
        self._iso.modify_file_in_place(BytesIO(bazstr), len(bazstr), f'/{fp.upper()}.;1', udf_path="/"+fp)

    def mk_directory(self, path):
        path = self._fix_path(path)

        self._iso.add_directory(path.upper(), udf_path=path)

    mkdir = mk_directory

    def mk_directories(self, path):
        path = self._fix_path(path)

        paths = [path]
        for i in range(path.count("/")-1):
            paths.append(paths[-1].rsplit("/", 1)[0])
        paths.reverse()
        print(paths)
        # exit()

        for path2 in paths:
            self.mk_directory(path2)

    def walk(self, path):
        return self._iso.walk(udf_path=path)

    @staticmethod
    def _fix_path(path):
        path.replace("\\", "/")

        while path[-1] == '/':
            path = path[:-1]

        if len(path) == 0:
            path = "/"

        if path[0] != '/':
            path = "/" + path

        return path

    def exists_directory(self, path):
        path = self._fix_path(path)

        for path_tuple in self.walk(path):
            if path_tuple[0] == path:
                return True
        return False

    def exists_file(self, path):
        pass

    def close(self):
        self._iso.close()

    def write(self):
        self._iso.write(self._path)


if __name__ == '__main__':
    def test3():
        file_ = IsoFile("test3.iso")
        file_.write_file("hallo.txt", "Hallo dit is een test.")
        # file_.mkdir("SomeDirectory")
        # file_.mkdir("SomeDirectory/SomeDirectoryInADirectory")
        file_.mk_directories("SomeDirectory/SomeDirectoryInADirectory/YetAnotherDirectoryInADirectory")
        print(list(file_.walk("/")))
        file_.write()

    test3()
