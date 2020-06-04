from io import BytesIO

from advUtils.core.decorators import experimental


@experimental
class QPartitionedFile(object):
    def __init__(self, file: BytesIO):
        if not file.seekable():
            raise IOError("File is not seekable")
        if not file.readable():
            raise IOError("File is not readable")
        self.io = file

    def _create_scheme(self):
        if not self.io.writable():
            raise IOError("File is not writable")

        a = self.io
        a.seek(0)
        a.write(b"\x00")
        # a.seek(8192)
        # a.write(b"\xff")

    def create(self, size=9216):
        if not self.io.writable():
            raise IOError("File is not writable")

        if size < 9216:
            raise ValueError("Size must be at least 9216 bytes. (9 KB)")

        if size > 256**8-1:
            raise OverflowError(f"Size must be less than {256**8} bytes.")

        # super(PartitionedFile, self).create(size)

        self.io.seek(size - 4)
        self.io.write(b"\xff\xff\xff\xff")

        self._create_scheme()

    def get_partitionsize(self, index: int):
        """
        Gets the partition size for the given index.

        :param index: The index of the partition, must be between 0 and 255. And must be existing partition.
        :return:
        :raises OverflowError: If the partition index exceeds 255.
        :raises IndexError: If the partition is not found.
        """

        if index > 255:
            raise OverflowError("Partition index is out of range.")

        paritiondata_offset = (32 * index)

        def readat(offset, size):
            a.seek(paritiondata_offset + offset)
            return a.read(size)

        a = self.io

        # print(readat(0, 1).hex())
        # print(readat(1, 1).hex())
        # print(readat(2, 8).hex())
        # print(readat(10, 1).hex())
        # print(readat(17, 1).hex())
        # print(readat(18, 8).hex())
        # print(readat(26, 1).hex())
        # print(readat(31, 1).hex())
        # print()

        # exit()

        if readat(0, 32) == (0).to_bytes(32, "little"):
            raise IndexError("Partition not found.")

        if readat(0, 1) == b"\x01":
            if readat(17, 1) == b"\x03":
                if readat(26, 1) == b"\x03":
                    return int.from_bytes(readat(18, 8), "little")

    def get_partitionoffset(self, index: int):
        """
        Gets the partition offset for a given partition.

        :param index: The index of the partition, must be between 0 and 255. And must be existing partition.
        :return:
        :raises OverflowError: If the partition index exceeds 255.
        """

        if index > 255:
            raise OverflowError("Partition index is out of range.")

        paritiondata_offset = (32 * index)

        def readat(offset, size):
            a.seek(paritiondata_offset + offset)
            return a.read(size)

        a = self.io

        # print(readat(0, 1).hex())
        # print(readat(1, 1).hex())
        # print(readat(2, 8).hex())
        # print(readat(10, 1).hex())
        # print(readat(11, 1).hex())
        # print(readat(12, 8).hex())
        # print(readat(20, 1).hex())
        # print(readat(21, 1).hex())
        # print()

        # exit()

        if readat(0, 32) == (0).to_bytes(32, "little"):
            raise IndexError("Partition not found.")

        if readat(0, 1) == b"\x01":
            if readat(1, 1) == b"\x02":
                if readat(10, 1) == b"\x02":
                    return int.from_bytes(readat(2, 8), "little")

    # noinspection PyUnusedLocal
    def new_partition(self, index, name, offset: int, size):
        if not self.io.writable():
            raise IOError("File is not writable")

        a = self.io

        paritiondata_offset = (32 * index)

        if offset + size > len(self.io.getbuffer()) - 4 - 8192:
            raise EOFError("Partition stop position exceeds the end of file.")

        a.seek(paritiondata_offset)
        a.write(b"\x01")
        a.write(b"\x02")
        a.write(offset.to_bytes(8, "little"))
        a.write(b"\x02")

        a.seek(paritiondata_offset+17)
        a.write(b"\x03")
        a.write(size.to_bytes(8, "little"))
        a.write(b"\x03")
        a.write(b"\x01")
        # print(a.tell())

    def writedata(self, partition, data: bytes):
        offset = self.get_partitionoffset(partition)
        size = self.get_partitionsize(partition)

        if len(data) > size:
            raise OverflowError("Data is larger than the partition size")

        a = self.io
        a.seek(8192+offset)
        a.write(data)

    def list_partitions(self):
        _partitions = []
        for i in range(256):
            if self.partition_exists(i):
                _partitions.append(i)
        return _partitions

    def data_available(self, offset, size):
        def isoverlapped(a, b):
            a = list(a)
            b = list(b)
            a.sort()
            b.sort()
            return ((a[0] < a[1]) and (b[0] > b[1])) or ((a[1] > b[0]) and b[1] > a[0])

        for partition in self.list_partitions():
            size2 = self.get_partitionsize(partition)
            offset2 = self.get_partitionoffset(partition)

            if isoverlapped((offset, offset+size), (offset2, offset2+size2)):
                return False
        return True

    def readdata(self, partition, size=None):
        offset = self.get_partitionoffset(partition)
        _size = self.get_partitionsize(partition)
        if size is None:
            size = _size
        elif size > _size:
            raise OverflowError("Can't read more than the partition size")

        a = self.io
        a.seek(8192+offset)
        return a.read(size)

    def partition_exists(self, index):
        if index > 255:
            raise OverflowError("Partition index is out of range.")

        paritiondata_offset = (32 * index)

        def readat(offset, size):
            a.seek(paritiondata_offset + offset)
            return a.read(size)

        a = self.io

        if readat(0, 32) == (0).to_bytes(32, "little"):
            return False
        return True


if __name__ == '__main__':
    def test1():
        print((256**8-1).to_bytes(8, "little"))
        print((1024**6-1).to_bytes(8, "little"))

    def test2():
        file_ = BytesIO()
        pfile = QPartitionedFile(file_)
        pfile.create(1024*9)
        pfile.new_partition(255, "", offset=0, size=16)
        print(f"Partition Size:   {pfile.get_partitionsize(255)}")
        print(f"Partition Offset: {pfile.get_partitionoffset(255)}")
        pfile.io.seek(0)
        pfile.writedata(255, "Hello World!".encode("utf-8"))
        print(f"Partition Data:   {pfile.readdata(255).decode('utf-8')}")
        print(f"Buffer:           {pfile.io.getbuffer().hex()}")
        print(f"Partitions:       {pfile.list_partitions()}")

        print(f"DataAvailable:    {pfile.data_available(0, 16)}")
        print(f"DataAvailable:    {pfile.data_available(768, 16)}")

        file_.seek(0)

        with open("test.partition", "wb") as file2_:
            file2_.write(file_.read())

        def test(a, b):
            a = list(a)
            b = list(b)
            a.sort()
            b.sort()
            print(((a[0] < a[1]) and (b[0] > b[1])) or ((a[1] > b[0]) and b[1] > a[0]))

        test((20, 30), (30, 40))
        test((20, 25), (30, 40))
        test((20, 35), (30, 40))
        test((30, 40), (20, 35))
        test((35, 20), (30, 40))
        test((0, 16), (0, 64))
        test((64, 72), (0, 64))

        # print((20 < 30) and (30 > 40))
        # print((20 < 25) and (30 > 40))

        # print(pfile._io.read())

    def test3():
        file_ = BytesIO()
        pfile_ = QPartitionedFile(file_)
        pfile_.create(8192*2+16)
        for i in range(255, 0, -1):
            pfile_.new_partition(i, "", (32*(255-i)), 32)
            pfile_.writedata(i, f"Partition {i}".encode("utf-8"))
            print(f"Writing partition {i}")

        file_.seek(0)

        with open("test.partition", "wb") as file2_:
            file2_.write(pfile_.io.read())

    test3()
