import os
import time
import unittest


class Test(unittest.TestCase):
    a = {"List": ["512", 512, True, None, {"512": 512}]}

    @staticmethod
    def testdill():
        import dill

        start = time.time()

        with open("filetest.dill", "wb+") as file:
            file.write(dill.dumps(a))

        with open("filetest.pik", "rb+") as file:
            b = dill.loads(file.read())

        end = time.time()

        assert a == b

        print(f"Dill File Size:   {os.path.getsize('filetest.dill')}")
        print(f"Dill File Speed:  {end - start}")

    @staticmethod
    def testpickle():
        import pickle

        start = time.time()

        with open("filetest.pik", "wb+") as file:
            file.write(pickle.dumps(a))

        with open("filetest.pik", "rb+") as file:
            b = pickle.loads(file.read())
            assert a == b

        end = time.time()

        print(f"Pickle File Size: {os.path.getsize('filetest.pik')}")
        print(f"Pickle File Speed:{end - start}")

    @staticmethod
    def testnzt():
        from advUtils.filesystem import NZT2File

        start = time.time()

        file = NZT2File("filetest.nzt", "w")
        file.data = a.copy()
        file.save()
        file.close()

        file = NZT2File("filetest.nzt")
        b = file.load()
        file.close()

        end = time.time()

        assert a == b

        print(f"NZT File Size:    {os.path.getsize('filetest.nzt')}")
        print(f"NZT File Speed:   {end - start}")

    @staticmethod
    def testqpydata():
        from experimental.qpydata import QPyDataFile

        start = time.time()

        with open("filetest.qdat", "wb+") as file:
            qfile = QPyDataFile()
            qfile.write(file, a)

        with open("filetest.qdat", "rb+") as file:
            qfile = QPyDataFile()
            b = qfile.read(file)

        end = time.time()

        assert a == b

        print(f"QPyDataFile Size: {os.path.getsize('filetest.qdat')}")
        print(f"QPyDataFile Speed:{end - start}")

    @staticmethod
    def testyml():
        import yaml

        start = time.time()

        with open("filetest.yml", "w") as file:
            yaml.safe_dump(a, file)

        with open("filetest.yml", "r") as file:
            b = yaml.safe_load(file)

        end = time.time()

        assert a == b

        print(f"Yaml File Size:   {os.path.getsize('filetest.yml')}")
        print(f"Yaml File Speed:  {end - start}")

    @staticmethod
    def testjson():
        import json

        start = time.time()

        with open("filetest.json", "w") as file:
            file.write(json.dumps(a, indent=4, sort_keys=True))

        with open("filetest.json", "r") as file:
            b = json.loads(file.read())

        end = time.time()

        assert a == b

        print(f"Json File Size:   {os.path.getsize('filetest.json')}")
        print(f"Json File Speed:  {end - start}")
