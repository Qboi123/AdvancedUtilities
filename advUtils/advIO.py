import pickle
import struct
import urllib.request
from http.client import HTTPResponse
# noinspection PyProtectedMember
from io import RawIOBase, BytesIO, _bytearray_like
from typing import Optional as _Optional, Any as _Any, List as _List

import dill


class IntegerIO(BytesIO):
    def __init__(self, initial_value=0):
        super(IntegerIO, self).__init__()
        self.write(initial_value)

    # noinspection PyTypeChecker
    def read(self, size: int = None, index: int = 0) -> int:
        if size is not None:
            raise ValueError("argument 'size' must be a NoneType object")
        if index < 0:
            raise ValueError("argument 'index' must be a non-negative integer")
        if not isinstance(index, int):
            raise TypeError("argument 'index' must be an integer")

        super(IntegerIO, self).seek(index * 1024)
        int.from_bytes(super(IntegerIO, self).read(1024), "little")

    def write(self, value: int, index=0) -> None:
        if index < 0:
            raise ValueError("argument 'index' must be a non-negative integer")
        if not isinstance(index, int):
            raise TypeError("argument 'index' must be an integer")

        super(IntegerIO, self).seek(index * 1024)
        super(IntegerIO, self).write(int.to_bytes(value, 1024, "little"))


class FloatIO(BytesIO):
    def __init__(self, initial_value=0):
        super(FloatIO, self).__init__()
        self.write(initial_value)

    # noinspection PyTypeChecker
    def read(self, size=None, index=0) -> int:
        if size is not None:
            raise ValueError("argument 'size' must be a NoneType object")
        if index < 0:
            raise ValueError("argument 'index' must be a non-negative integer")
        if not isinstance(index, int):
            raise TypeError("argument 'index' must be an integer")

        super(FloatIO, self).seek(index * 1024)
        size = int.from_bytes(super(FloatIO, self).read(4), "little")
        struct.unpack("f", super(FloatIO, self).read(size))

    def write(self, value: float, index=0) -> None:
        """
        Writes a float in the io stream at the given index.
        The offset is based on the index specified, calculated by ``{index} * 1024``.

        :param float value: The value to write to the stream.
        :param int index: The index to write the value to.
        :raises ValueError: If the index is a non-negative integer.
        :raises TypeError: If the index is not an integer.
        :raises OverflowError: If the float value is too large to fit in 1020 bytes.
        :return:
        """

        if index < 0:
            raise ValueError("argument 'index' must be a non-negative integer")
        if not isinstance(index, int):
            raise TypeError("argument 'index' must be an integer")

        data = struct.pack("f", value)
        if len(data) >= 1020:
            raise OverflowError("Float value too large to fit in 1020 bytes: {}".format(value))
        size = len(data)
        super(FloatIO, self).seek(index * 1024)
        super(FloatIO, self).write(int.to_bytes(size, 4, "little"))
        super(FloatIO, self).seek((index * 1024) + 4)
        super(FloatIO, self).write(data)


class BooleanIO(BytesIO):
    def __init__(self, initial_value=False):
        super(BooleanIO, self).__init__()
        self.write(initial_value)

    def read(self, size=None, id_=0) -> _Optional[bool]:
        if size is not None:
            raise ValueError("argument 'size' must be a NoneType object")
        super(BooleanIO, self).seek(id_)
        byte = super(BooleanIO, self).read()
        if byte == b"\1":
            return True
        elif byte == b"\0":
            return False
        else:
            return None

    def write(self, value: bool, id_=0) -> None:
        super(BooleanIO, self).seek(id_)
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
