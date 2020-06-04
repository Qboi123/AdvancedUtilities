import io
import struct
import typing

import dill
from overload import overload

NoneType = type(None)


class QPyDataFile(object):
    def __init__(self):
        pass

    @staticmethod
    def _reduce_intdata(value: int):
        byte_data = value.to_bytes(int(value.bit_length() / 8) + 1, "big", signed=True)
        return b"\x00\x00", len(byte_data), byte_data

    @staticmethod
    def _revert_intdata(data: bytes):
        value = int.from_bytes(data, "big", signed=True)
        return value

    @staticmethod
    def _reduce_strdata(value: str):
        byte_data = value.encode("utf-8")
        return b"\x00\x01", len(byte_data), byte_data

    @staticmethod
    def _revert_strdata(data: bytes):
        value = data.decode("utf-8")
        return value

    @staticmethod
    def _reduce_booldata(value: bool):
        byte_data = value.to_bytes(1, "big")
        return b"\x00\x02", len(byte_data), byte_data

    def _reduce_listdata(self, value: list):
        list_io = io.BytesIO()
        list_io.seek(0)
        list_io.write(len(value).to_bytes(16, "little"))

        datas = []

        for i in value:
            datas.append(self._reduce_data(i))
            # datas.append((typeid, length, data))

        # print(datas)

        offset = 16
        for typeid, length, data in datas:
            list_io.seek(offset)
            length: int
            list_io.write(length.to_bytes(16, "little"))
            offset += 16

        for typeid, length, data in datas:
            # item_io = io.BytesIO()
            # QPyDataFile().write(item_io, value)

            list_io.seek(offset)
            list_io.write(typeid)
            list_io.seek(offset + 2)
            list_io.write(data)

            offset += len(data) + 2
            offset += 16 - (offset % 16)

        byte_data = list_io.getvalue()

        # print(byte_data)
        return b"\x00\x03", len(byte_data), byte_data

    def _revert_listdata(self, data: bytes):
        # Create a bytes-io for the data.
        list_io = io.BytesIO(data)
        list_io.seek(0)

        # Get list length.
        list_len = int.from_bytes(list_io.read(16), "little")

        # Generate list data.
        listtable_offset = 16  # List-table offset.
        itemoffset = 16 * list_len + 16  # Item offset
        value = []  # Return value.
        for i in range(list_len):
            # Item Size
            list_io.seek(listtable_offset)
            item_size = int.from_bytes(list_io.read(16), "little")

            # Item Type-ID
            list_io.seek(itemoffset)
            typeid = list_io.read(2)

            # Item Data
            list_io.seek(itemoffset + 2)
            data = list_io.read(item_size)

            # Revert Item Data
            value.append(self._revert_data(typeid, data))
            # print(value)

            # Advance to next item in list.
            itemoffset += item_size + 2
            itemoffset += 16 - (itemoffset % 16)
            listtable_offset += 16
        return value

    @overload
    def calculate_trailinglength(self, data: bytes, bytelength=16) -> int:
        overflow = len(data) % bytelength
        length = (bytelength - overflow)
        # print(len(data), length, overflow)
        return length

    @calculate_trailinglength.add
    def calculate_trailinglength(self, datalength: int, bytelength=16) -> int:
        overflow = datalength % bytelength
        length = (bytelength - overflow)
        # print(datalength, length, overflow)
        return length

    # noinspection PyUnusedLocal
    @staticmethod
    def create_trailingdata(data, bytelength=16):
        # length = self.calculate_trailinglength(data, bytelength)
        trailingdata = b"\xff" * (16 - len(data) % 16)
        return trailingdata

    def _reduce_dictdata(self, value: dict):
        # Create a bytes-io for the data.
        dict_io = io.BytesIO()

        # Generate dictionary data.
        offset = 0
        for key, value in value.items():
            # Get the type-id, length and reduced data from key and value.
            keytypeid, keylength, keydata = self._reduce_data(key)
            valuetypeid, valuelength, valuedata = self._reduce_data(value)

            # Get reduced key and value
            reducedkey = keytypeid + keylength.to_bytes(16, "little", signed=False) + keydata
            reducedkey += self.create_trailingdata(reducedkey)
            reducedvalue = valuetypeid + self._reduce_length(valuelength) + valuedata
            reducedvalue += self.create_trailingdata(reducedvalue)

            # Paste reduced value after reduced key.
            reduceditem = reducedkey + reducedvalue

            # print(reduceditem)

            # Write data at offset
            dict_io.seek(offset)
            dict_io.write(reduceditem)

            # Advance offset to next item.
            offset += len(reduceditem)

        byte_data = dict_io.getvalue()
        # print(byte_data)
        return b"\x00\x04", len(byte_data), byte_data

    def _revert_dictdata(self, data):
        items = {}

        dict_io = io.BytesIO(data)

        eof = False
        offset = 0
        while not eof:
            # Key
            dict_io.seek(offset)
            keytypeid = dict_io.read(2)
            if not keytypeid:
                break

            offset += 2

            dict_io.seek(offset)
            keylength = int.from_bytes(dict_io.read(16), "little", signed=False)

            offset += 16

            dict_io.seek(offset)
            keydata = dict_io.read(keylength)

            offset += len(keydata)

            key = self._revert_data(keytypeid, keydata)

            # print(offset)

            # Value
            offset += (16 - offset % 16)
            # print(offset)
            dict_io.seek(offset)
            valuetypeid = dict_io.read(2)

            # print(valuetypeid)

            offset += 2

            dict_io.seek(offset)
            zfg = dict_io.read(16)
            # print(zfg)
            valuelength = int.from_bytes(zfg, "little", signed=False)

            offset += 16

            dict_io.seek(offset)
            valuedata = dict_io.read(valuelength)

            value = self._revert_data(valuetypeid, valuedata)

            offset += len(valuedata)

            items[key] = value

            # print()
            # print(offset)
            offset += (16 - offset % 16)
            # print(offset)

        return items

    @staticmethod
    def _reduce_nonetypedata():
        return b"\x00\x05", 0, b""

    @staticmethod
    def _revert_nonetypedata(data):
        if len(data) == 0:
            return None
        else:
            raise ValueError("Invalid data, must be a empty bytes object.")

    def _reduce_tupledata(self, value: tuple):
        tuple_io = io.BytesIO()
        tuple_io.seek(0)
        tuple_io.write(len(value).to_bytes(16, "little"))

        datas = []

        for i in value:
            datas.append(self._reduce_data(i))
            # datas.append((typeid, length, data))

        # print(datas)

        offset = 16
        for typeid, length, data in datas:
            tuple_io.seek(offset)
            length: int
            tuple_io.write(length.to_bytes(16, "little"))
            offset += 16

        for typeid, length, data in datas:
            # item_io = io.BytesIO()
            # QPyDataFile().write(item_io, value)

            tuple_io.seek(offset)
            tuple_io.write(typeid)
            tuple_io.seek(offset + 2)
            tuple_io.write(data)
            offset += len(data) + 2

        byte_data = tuple_io.getvalue()

        # print(byte_data)
        return b"\x00\x06", len(byte_data), byte_data

    def _revert_tupledata(self, data: bytes):
        # Create a bytes-io for the data.
        tuple_io = io.BytesIO(data)
        tuple_io.seek(0)

        # Get list length.
        tuple_len = int.from_bytes(tuple_io.read(16), "little")

        # Generate list data.
        listtable_offset = 16  # List-table offset.
        itemoffset = 16 * tuple_len + 16  # Item offset
        value = []  # Return value.
        for i in range(tuple_len):
            # Item Size
            tuple_io.seek(listtable_offset)
            item_size = int.from_bytes(tuple_io.read(16), "little")

            # Item Type-ID
            tuple_io.seek(itemoffset)
            typeid = tuple_io.read(2)

            # Item Data
            tuple_io.seek(itemoffset + 2)
            data = tuple_io.read(item_size)

            # Revert Item Data
            value.append(self._revert_data(typeid, data))
            # print(value)

            # Advance to next item in list.
            itemoffset += item_size + 2
            listtable_offset += 16
        return tuple(value)

    @staticmethod
    def _reduce_setdata(value: set):
        byte_data = value.__reduce__()
        return b"\x00\x07", len(byte_data), byte_data

    # def _reduce_exception(self, value: Exception):
    #

    @staticmethod
    def _reduce_bytes(value: bytes):
        byte_data = value.__reduce__()
        return b"\x00\x08", len(byte_data), byte_data

    @staticmethod
    def _reduce_bytearray(value: bytearray):
        byte_data = value.__reduce__()
        return b"\x00\x09", len(byte_data), byte_data

    @staticmethod
    def _reduce_ascii(value: ascii):
        byte_data = value.__reduce__()
        return b"\x00\x0A", len(byte_data), byte_data

    def _reduce_complex(self, value: complex):
        _, length, byte_data = self._reduce_tupledata((value.real, value.imag))
        return b"\x00\x0B", length, byte_data

    def _revert_complex(self, data: bytes):
        return complex(*self._revert_tupledata(data))

    # def _reduce_ellipsis(self, value: ellipsis):
    #     byte_data = value.__reduce__()
    #     return b"\x00\x0C", len(byte_data), byte_data

    @staticmethod
    def _reduce_floatdata(value: float):
        byte_data = struct.pack("d", value)
        # print(value)
        # print(byte_data)
        return b"\x00\x0D", len(byte_data), byte_data

    @staticmethod
    def _revert_floatdata(data: bytes):
        value = struct.unpack("d", data)[0]
        # print(value)
        # print(data)
        return value

    def _reduce_rangedata(self, value: range):
        _, length, byte_data = self._reduce_tupledata((value.start, value.stop, value.step))
        return b"\x00\x0E", length, byte_data

    def _revert_rangedata(self, data: bytes):
        return range(*self._revert_tupledata(data))

    # def _reduce_property(self, value: property):
    #     byte_data = value.__reduce__()
    #     return b"\x00\x0F", len(byte_data), byte_data

    @staticmethod
    def _reduce_memoryview(value: memoryview):
        byte_data = value.tobytes()
        return b"\x00\x10", len(byte_data), byte_data

    @staticmethod
    def _revert_memoryview(data: bytes):
        value = memoryview(data)
        return value

    # def _reduce_frozenset(self, value: frozenset):
    #     byte_data = value.__reduce__()
    #     return b"\x00\x11", len(byte_data), byte_data
    #
    # def _reduce_enumerate(self, value: enumerate):
    #     byte_data = value.__reduce__()
    #     return b"\x00\x12", len(byte_data), byte_data

    @staticmethod
    def _reduce_objectdata(value: object):
        byte_data = dill.dumps(value)
        return b"\xff\xff", len(byte_data), byte_data

    @staticmethod
    def _revert_objectdata(data: bytes):
        value = dill.loads(data)
        return value

    @staticmethod
    def _reduce_length(length: int):
        return length.to_bytes(16, "little")

    def dump(self, stream: typing.Union[io.BytesIO, typing.BinaryIO], value: typing.Any):
        # if type(value) is str:
        #     typeid, length, value = self._reduce_strdata(value)
        # elif type(value) is int:
        #     typeid, length, value = self._reduce_intdata(value)
        # elif type(value) is list:
        #     typeid, length, value = self._reduce_listdata(value)
        # else:
        #     raise TypeError(f"Can't reduce {value.__class__.__name__}")

        typeid, length, data = self._reduce_data(value)

        stream.seek(0)
        stream.write(b"\xffQPyData\xff")
        stream.seek(14)
        aa = self._reduce_length(length)
        # print(aa)
        # print(value)
        stream.write(typeid + aa + data)

    def _reduce_data(self, value):
        if type(value) is int:
            return self._reduce_intdata(value)
        elif type(value) is str:
            return self._reduce_strdata(value)
        elif type(value) is list:
            return self._reduce_listdata(value)
        elif type(value) is dict:
            return self._reduce_dictdata(value)
        elif type(value) is NoneType:
            return self._reduce_nonetypedata()
        elif type(value) is tuple:
            return self._reduce_tupledata(value)
        elif type(value) is float:
            return self._reduce_floatdata(value)
        elif type(value) is range:
            return self._reduce_rangedata(value)
        else:
            return self._reduce_objectdata(value)

    def _revert_data(self, typeid: bytes, data: bytes):
        # print(typeid, data)
        if typeid == b'\x00\x00':
            return self._revert_intdata(data)
        elif typeid == b'\x00\x01':
            return self._revert_strdata(data)
        elif typeid == b'\x00\x03':
            return self._revert_listdata(data)
        elif typeid == b'\x00\x04':
            a = self._revert_dictdata(data)
            return a
        elif typeid == b'\x00\x05':
            # noinspection PyNoneFunctionAssignment
            a = self._revert_nonetypedata(data)
            return a
        elif typeid == b'\x00\x06':
            a = self._revert_tupledata(data)
            return a
        elif typeid == b'\x00\x0D':
            a = self._revert_floatdata(data)
            return a
        elif typeid == b'\x00\x0E':
            a = self._revert_rangedata(data)
            return a
        elif typeid == b"\xff\xff":
            a = self._revert_objectdata(data)
            return a
        else:
            raise ValueError(f"Invalid type-id: {str(typeid)[2:-1]}")

    def load(self, stream: typing.Union[io.BytesIO, typing.BinaryIO]):
        stream.seek(0)
        startbytes = stream.read(16)
        if not startbytes.startswith(b"\xffQPyData\xff"):
            raise IOError(f"Invalid QPyData header: {startbytes}")

        stream.seek(14)
        typeid = stream.read(2)
        stream.seek(16)
        length = stream.read(16)
        stream.seek(32)
        data = stream.read(int.from_bytes(length, "little", signed=False))

        value = self._revert_data(typeid, data)
        # if typeid == b'\x00\x00':
        #     stream.seek(16)
        #     length = stream.read(16)
        #     stream.seek(32)
        #     value = stream.read(int.from_bytes(length, "little", signed=False))
        #     value = self._revert_intdata(value)
        # elif typeid == b'\x00\x01':
        #     stream.seek(16)
        #     length = stream.read(16)
        #     stream.seek(32)
        #     value = stream.read(int.from_bytes(length, "little", signed=False))
        #     value = self._revert_strdata(value)
        # elif typeid == b'\x00\x03':
        #     stream.seek(16)
        #     length = stream.read(16)
        #     stream.seek(32)
        #     value = stream.read(int.from_bytes(length, "little", signed=False))
        #     value = self._revert_listdata(value)
        # else:
        #     raise ValueError(f"Invalid type-id: {str(typeid)[2:-1]}")
        return value

    def loads(self, data: bytes) -> typing.Any:
        """
        Loads QPy Data into a Python object/type.

        :param data: The data to be loaded.
        :return:
        """

        # Create a stream.
        stream = io.BytesIO(data)

        # Load the stream.
        obj = self.load(stream)

        # Close the stream.
        stream.close()

        # Return the object.
        return obj

    def dumps(self, obj: typing.Any) -> bytes:
        """
        Dumps (almost) any type or object into a QPyData bytes object.

        :param obj: The object to be dumped.
        :return:
        """

        # Create a stream, and dump the object into it.
        stream = io.BytesIO()
        self.dump(stream, obj)

        # Get the full data.
        stream.seek(0)
        data = stream.read()

        # Close the stream
        stream.close()

        # Return the data.
        return data
