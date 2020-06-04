import pickle
import urllib.request
# noinspection PyProtectedMember
from io import TextIOBase, RawIOBase, BytesIO, _bytearray_like
from typing import Optional as _Optional, Any as _Any, List as _List
from http.client import HTTPResponse

import dill


class IntegerIO(TextIOBase):
    def __init__(self, initial_value=0):
        super(IntegerIO, self).__init__()
        self.write(initial_value)

    # noinspection PyTypeChecker
    def read(self, size=None) -> int:
        if size is not None:
            raise ValueError("argument 'size' must be a NoneType object")
        int(super(IntegerIO, self).read())

    def write(self, value: int) -> None:
        super(IntegerIO, self).write(str(value))


class BooleanIO(RawIOBase):
    def __init__(self, initial_value=False):
        super(BooleanIO, self).__init__()
        self.write(initial_value)

    # noinspection PyTypeChecker
    def read(self, size=None) -> _Optional[bool]:
        if size is not None:
            raise ValueError("argument 'size' must be a NoneType object")
        byte = super(BooleanIO, self).read()
        if byte == b"\1":
            return True
        elif byte == b"\0":
            return False
        else:
            return None

    def write(self, value: bool) -> None:
        super(BooleanIO, self).write(b"\0" if value is False else b"\1" if value is True else b"\f")


class NullIO(RawIOBase):
    def __init__(self):
        """
        Sends the data to a null stream. Literly writing nothing, and reading nothing.
        """

        super(NullIO, self).__init__()

    def read(self, size=None):
        return b""

    def write(self, data):
        return


class WebIO(BytesIO):
    def __init__(self, url, data=None, timeout=None, *, cafile=None, capath=None):
        super(WebIO, self).__init__()
        self.url = url
        self._fd: HTTPResponse = urllib.request.urlopen(url, data, timeout, cafile=cafile, capath=capath)

    def read(self, __size: _Optional[int] = ...) -> bytes:
        return self._fd.read(__size)

    def read1(self, __size: _Optional[int] = ...) -> bytes:
        return self._fd.read1(__size)

    def readable(self) -> bool:
        return self._fd.readable()

    def write(self, data):
        self._fd.write(data)

    def writable(self) -> bool:
        return self._fd.writable()

    def writelines(self, __lines: _Any) -> None:
        self._fd.writelines(__lines)

    def flush(self) -> None:
        self._fd.flush()

    def fileno(self) -> int:
        return self._fd.fileno()

    def readinto(self, __buffer: _bytearray_like) -> int:
        return self._fd.readinto(__buffer)

    def readinto1(self, __buffer: _bytearray_like) -> int:
        return self._fd.readinto1(__buffer)

    def readline(self, __size: _Optional[int] = ...) -> bytes:
        return self._fd.readline(__size)

    def readlines(self, __size: int = ...) -> _List[bytes]:
        return self._fd.readlines(__size)

    def seek(self, __pos: int, __whence: int = ...) -> int:
        return self._fd.seek(__pos, __whence)

    def tell(self) -> int:
        return self._fd.tell()

    def truncate(self, __size: _Optional[int] = ...) -> int:
        return self._fd.truncate(__size)

    def seekable(self) -> bool:
        return self._fd.seekable()


class DillIO(RawIOBase):
    def __init__(self):
        super(DillIO, self).__init__()

    def read(self, size=None):
        if size is not None:
            raise ValueError("argument 'size' must be a NoneType object")
        dill.loads(super(DillIO, self).read())

    def write(self, data):
        super(DillIO, self).write(dill.dumps(data))


class PickleIO(RawIOBase):
    def __init__(self):
        super(PickleIO, self).__init__()

    def read(self, size=None):
        if size is not None:
            raise ValueError("argument 'size' must be a NoneType object")
        pickle.loads(super(PickleIO, self).read())

    def write(self, data):
        super(PickleIO, self).write(pickle.dumps(data))


class DeviceIO(object):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("This will be may be implemented in the future.")
