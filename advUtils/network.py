import socketserver
from typing import Union, Callable, Any
import win32net

import wx
import wx.adv

# Message types
from advUtils.filesystem import File

INFO = "info"
WARN = "warn"
WARNING = "warn"
ERROR = "error"

# Connection lost types
CONN_LOST = "conn_lost"
CONN_TIMEOUT = "conn_timeout"
CONN_SUCCESS = "conn_success"

# States
STATE_LAUNCH = "state_launch"

# Connection types
CLIENT = "client"
SERVER = "server"


class _Utils:
    @staticmethod
    def remove_duplicates(list_: list) -> list:
        index = 0
        already_defined = []
        while index < len(list_):
            if already_defined:
                if list_[index] in already_defined:
                    del list_[index]
                    continue
            already_defined.append(list_[index])
            index += 1
        return list_


class Downloader(object):
    def __init__(self, url, file):
        # noinspection PyProtectedMember
        """
                Download a file from the specified URL and save it to the specified filepath (file)

                Example
                --------
                >>> import time
                >>> download = Downloader("https://www.google.com/", "./googlesite.html")
                >>> download.download()
                >>> while download.is_downloading():
                ...     print(f"Status: downloaded {download.totalDownloaded} of {download.fileTotalbytes}")
                ...     time.sleep(1)   # wait a second before printing the status again
                >>> print(f"Download of {download._url} is completed!")

                :param url: The URL to download
                :param file: The filepath to write it to.
                """

        # InfoNone
        self._url = url
        self._file = file

        # Booleans
        self.downloadActive = True

        # Integers
        self.totalDownloaded = 0
        self.fileTotalbytes = 0
        self.timeRemaining = -1

        # Strings
        self.info = ""

        # Modules
        import os
        import time
        import advUtils.system
        import threading
        self._os = os
        self._time = time
        self._system = advUtils.system
        self._threading = threading
        self.spd = 0

        # Status
        self.title = f"Initializing..."
        self.message1 = f""
        self.message2 = f""
        self.message3 = f""
        self.message4 = f""
        self.status_list = [self.title, self.message1, self.message2, self.message3, self.message4]
        self.status = str.join("\n", self.status_list)

    def speed(self):
        """
        Speed information update thread

        :returns: Nothing
        """
        # Load.SetValue(int(self.totalDownloaded / self.fileTotalbytes), )
        self.info = f"Downloading...\nDownloading of \"{self._url.split('/')[-1]}\""
        while self.downloadActive:
            total1 = self.totalDownloaded
            self._time.sleep(0.45)
            total2 = self.totalDownloaded
            self.spd = (total2 - total1) * 2
            try:
                a = self.fileTotalbytes / self.spd
                b = self._time.gmtime(a)
            except ZeroDivisionError:
                a = -1
                b = self._time.gmtime(a)
            self.timeRemaining = b

    def _download(self):
        """
        Core download method, use only when you have a customized Thread object you want to use.

        :returns: Nothing
        """

        import urllib.request
        h = "23"
        m = "59"
        s = "59"
        self.spd: Union[int, float] = 0
        self.totalDownloaded: int = 0

        # Get the total number of bytes of the file to download before downloading
        url_request = urllib.request.urlopen(str(self._url))
        meta: dict = url_request.info()
        if "Content-Length" in meta.keys():
            self.fileTotalbytes = int(meta["Content-Length"])
        else:
            raise KeyError(f"The url '{self._url}' has no meta named 'Content-Length'")
        if self.fileTotalbytes < 0:
            raise ValueError(f"The file at '{self._url}' has an invalid file size: {self.fileTotalbytes}")
        elif self.fileTotalbytes == 0:
            raise ValueError(f"The file at '{self._url}' is empty")

        data_blocks: list = []
        total: int = 0

        file = File(self._file)

        self._system.StoppableThread(target=lambda: self.speed(), name="SpeedThread").start()

        while True:
            block = url_request.read()
            data_blocks.append(block)
            total += len(block)
            _hash = ((60 * self.totalDownloaded) // self.fileTotalbytes)
            # Frame.Update()
            # Panel.Update()
            # Down.Update()
            _temp0002 = self._url.split('/')[-1]
            _temp0003 = str(int(self.totalDownloaded / self.fileTotalbytes * 100))

            self.title = f"Downloading..."
            self.message1 = f"Downloading of \"{_temp0002} is {_temp0003}% complete."
            self.message2 = f""
            self.message3 = f"{str(total)} of {str(self.fileTotalbytes)}"
            self.message4 = f"With {str(self.spd)} bytes/sec | {h}:{m}:{s} remaining."
            self.status_list = [self.title, self.message1, self.message2, self.message3, self.message4]
            self.status = str.join("\n", self.status_list)

            if not len(block):
                self.downloadActive = False
                break

            fd = file.open("ab")
            fd.write(block)
            fd.close()

        # value = b''.join(data_blocks)  # had to add b because I was joining bytes not strings
        url_request.close()

        # with open("C:\\Users\\" + self._os.getlogin() + "\\Downloads\\" + self._url.split("/")[-1], "wb") as f:
        #     f.write(value)

        # Frame.SetWindowStyle(wx.DEFAULT_FRAME_STYLE)
        # load.Destroy()
        # Frame.Show(True)
        notify = wx.adv.NotificationMessage(
            title="Download successful",
            message="Your download is complete!\n\nCheck out in your downloads folder.",
            parent=None, flags=wx.ICON_INFORMATION)
        notify.Show(timeout=0)  # 1 for short timeout, 100 for long timeout

    def download(self, *, threadname=None):
        """
        Spawns a thread for downloading the file / webpage

        :param threadname: The name of the thread, leave it to None to use default name
        :returns: The Thread(...) instance of the downloader
        """

        t_ = self._threading.Thread(target=self._download, name=threadname)
        t_.start()
        return t_

    def is_downloading(self):
        return self.downloadActive


class Server(object):
    "A class for a Server instance."""

    def __init__(self, port_):
        # noinspection PyUnresolvedReferences
        """
        Server constructor, used for communicate between client and server.

        You can use it for host a multiplayer game, and this should be used for hosting the server.

        Example
        --------
        >>> def s_runner(conn, secret):
        >>>     import random
        >>>     pak = PacketSystem(conn)
        >>>     for i in range(1):
        >>>         b = []
        >>>         for _ in range(16):
        >>>             b.append(chr(random.randint(64, 96)))
        >>>         a = f"{''.join(b)}"
        >>>         b = random.randint(-5000, +5000)
        >>>         pak.send(a)
        >>>         pak.send(b)
        >>>         pak.send(list(a))
        >>>     exit(0)
        >>>
        >>> server_ = Server(36673)
        >>> server_.runner = s_runner
        >>> server_.start()

        :param port_: The port number to use for the server, used for clients to connect to
        """

        self.port = port_

        self.preInitHook: Callable = lambda server, sock1, sock2: None
        self.postInitHook: Callable = lambda server, conn, addr, secret: None

        self.conn_array = []
        self.secret_array = {}

        import math
        import random
        import socket
        import threading
        self._math = math
        self._random = random
        self._socket = socket
        self._threading = threading

        self.event: Callable = lambda evt_type, server: None

    def is_prime(self, number):
        """
        Checks to see if a number is prime.

        :param number:
        :return:
        """
        x = 1
        if number == 2 or number == 3:
            return True
        while x < self._math.sqrt(number):
            x += 1
            if number % x == 0:
                return False
        return True

    def runner(self, conn, secret):
        """
        Used for the handling the connection, like sending packages, or recieving packages.
        Must be overridden in subclass to take effect.

        :param conn:
        :param secret:
        :return:
        """

        pass

    def run(self):
        """
        Stars the server in non-thread-mode.

        :return: Nothing
        """

        while True:
            s = self._socket.socket(self._socket.AF_INET, self._socket.SOCK_STREAM)
            try:
                s.bind(('', self.port))
            except OSError:
                return

            if len(self.conn_array) == 0:
                self.event(CONN_SUCCESS, "server")
            s.listen(1)

            conn_init, addr_init = s.accept()
            pak_init = PacketSystem(conn_init)
            serv = self._socket.socket(self._socket.AF_INET, self._socket.SOCK_STREAM)
            serv.bind(('', 0))  # get a random empty port_

            self.preInitHook(self, s, serv)

            serv.listen(1)

            port_val = serv.getsockname()[1]
            pak_init.send(port_val)

            del pak_init
            conn_init.close()
            conn, addr = serv.accept()

            pak = PacketSystem(conn)

            self.conn_array.append(conn)  # add an array entry for this connection
            self.event(CONN_SUCCESS, self)

            # create the numbers for my encryption
            prime = self._random.randint(1000, 9000)
            while not self.is_prime(prime):
                prime = self._random.randint(1000, 9000)
            base = self._random.randint(20, 100)
            a = self._random.randint(20, 100)

            # send the numbers (base, prime, A)
            # conn.send(self.network.format_number(len(str(base))).encode())
            # conn.send(str(base).encode())
            #
            # conn.send(self.network.format_number(len(str(prime))).encode())
            # conn.send(str(prime).encode())
            #
            # conn.send(self.network.format_number(len(str(pow(base, a) % prime))).encode())
            # conn.send(str(pow(base, a) % prime).encode())
            #
            # # get B
            # value = conn.recv(4)
            # value = conn.recv(int(value.decode()))
            # b = int(value.decode())

            pak.send(base)
            pak.send(prime)
            pak.send(pow(base, a))

            b = PacketReciever(conn).recv()

            # calculate the encryption key
            secret = pow(b, a) % prime
            # store the encryption key by the connection
            self.secret_array[conn] = secret

            self.postInitHook(self, conn, addr, secret)

            self._threading.Thread(target=self.runner, args=(conn, secret)).start()
            del pak
            # # Server(self.port_).start()
        # self.start()

    def start(self):
        """
        Starts ther server in thread-mode.

        :return:
        """

        self._threading.Thread(target=self.run).start()


# Client chat
class Client(object):
    """
    A class for a Client instance.
    """

    def __init__(self, host, port_):
        # noinspection PyUnresolvedReferences
        """
                Client constructor, used for communicate between client and server.

                You can use it for multiplayer in a game, and this should be used for the user side.

                Example
                --------
                >>> def c_runner(conn, secret):
                ...     pak = PacketSystem(conn)
                ...     for i in range(3):
                ...         recieved = pak.recv()
                ...         print(f"Recieved Type: {type(recieved)}")
                ...         print(f"Recieved Data: {recieved}")
                ...     exit(0)
                ...
                >>> client_ = Client("127.0.0.1", 36673)
                >>> client_.runner = c_runner
                >>> client_.start()

                :param host: The IP adress for the client
                :param port_: The port number for the client
                """
        # super(Client, self).__init__(chat_text)
        self.port = port_
        self.host = host
        # self.network = network

        self.preInitHook: Callable = lambda client, conn_init2: None
        self.postInitHook: Callable = lambda client, conn, secret: None

        import socket
        import random
        import threading
        self._socket = socket
        self._random = random
        self._threading = threading

        self.secret_array = {}
        self.conn_array = []

        self.event: Callable = lambda evt_type, client: None

    def runner(self, conn, secret):
        """
        Used for the handling the connection, like sending packages, or recieving packages.
        Must be overridden in subclass to take effect.

        :param conn:
        :param secret:
        :return:
        """

        pass

    def run(self):
        """
        Starts the client in non-thread-mode

        :returns: Nothing
        """

        conn_init2 = self._socket.socket(self._socket.AF_INET, self._socket.SOCK_STREAM)
        conn_init2.settimeout(5.0)
        pak_init = PacketSystem(conn_init2)
        try:
            conn_init2.connect((self.host, self.port))
        except self._socket.timeout:
            raise SystemExit(0)
        except self._socket.error:
            raise SystemExit(0)

        self.preInitHook(self, conn_init2)

        # Recieve port
        porte = pak_init.recv()

        del pak_init
        conn_init2.close()

        # New connection
        conn = self._socket.socket(self._socket.AF_INET, self._socket.SOCK_STREAM)
        conn.connect((self.host, porte))
        pak = PacketSystem(conn)

        self.event(CONN_SUCCESS, self)

        self.conn_array.append(conn)

        # Get my base, prime, and A values
        base = pak.recv()
        prime = pak.recv()
        a = pak.recv()
        b = self._random.randint(20, 100)
        # Send the 'b' value
        pak.send(pow(base, b) % prime)
        secret = pow(a, b) % prime

        self.secret_array[conn] = secret
        self.postInitHook(self, conn, secret)

        self._threading.Thread(target=self.runner, args=(conn, secret)).start()
        del pak
        # Server(self.port_).start()                             # Errored command! #
        # THIS IS GOOD, BUT I CAN'T TEST ON ONE MACHINE

    def start(self):
        """
        Starts the client in thread-mode

        :returns: The Thread(...) instance of the client thread
        """

        t_ = self._threading.Thread(target=self.run)
        t_.start()
        return t_


class PacketEncoder(object):
    def __init__(self, data):
        self.data = data

        import dill as dill
        self._dill = dill

    def get_encoded(self):
        data = self._dill.dumps(self.data)
        length = len(data)

        return length, data

    @classmethod
    def dump(cls, data, stream) -> None:
        import dill

        stream.seek(0)
        dill.dump(data, stream)

    @classmethod
    def dumps(cls, data) -> bytes:
        import dill

        return dill.dumps(data)


class PacketDecoder(object):
    def __init__(self, data: bytes):
        self.data = data

        import dill as dill
        self._dill = dill

    def get_decoded(self):
        data = self._dill.loads(self.data)

        return data

    @classmethod
    def load(cls, stream) -> Any:
        """
        Loads dilled data from the stream, and returns the normalized data.

        :param stream:
        :return:
        """

        import dill

        stream.seek(0)
        return dill.load(stream)

    @classmethod
    def loads(cls, data) -> Any:
        """
        Loads dilled data and returns the normalized data.

        :param data:
        :return:
        """

        import dill

        return dill.loads(data)


class PacketSender(object):
    def __init__(self, conn, data, len_bytesize=8):
        self.lengthByteSize = len_bytesize
        self._length, self._data = PacketEncoder(data).get_encoded()

        import socket
        import socketserver

        self.conn: Union[socket.socket, socketserver.BaseRequestHandler] = conn

    def send(self):
        self.conn.send(self._length.to_bytes(self.lengthByteSize, "big", signed=False))
        self.conn.send(self._data)

    def sendall(self):
        if not issubclass(type(self.conn), socketserver.BaseRequestHandler):
            raise Exception(f"the conn argument and attribute of {self.__class__.__name__}() "
                            f"must be a subclass of socketserver.BaseRequestHandler")

        self.conn.sendall(self._length.to_bytes(self.lengthByteSize, "big", signed=False))
        self.conn.sendall(self._data)

    def __repr__(self):
        if self.lengthByteSize == 8:
            return f"<{self.__class__.__name__} data={repr(self._data)}>"
        else:
            return f"<{self.__class__.__name__} data={repr(self._data)} len_bytesize={repr(self.lengthByteSize)}>"


class PacketReciever(object):
    def __init__(self, conn):
        """
        Packet receiver.

        :param conn: The socket connection.
        """

        import socket

        self.conn: socket.socket = conn

    def recv(self):
        length = self.conn.recv(8)
        data = self.conn.recv(int.from_bytes(length, "big", signed=False))

        return PacketDecoder(data).get_decoded()

    def __repr__(self):
        return f"<PacketReciever conn=<{self.conn.__class__.__name__} peername={repr(self.conn.getpeername())}>>"


class PacketSystem(object):
    def __init__(self, conn):
        """
        Packet System for communicate with servers / clients
        Maximum size of a packet is 4294967296 Bytes, 4 Gigabytes. Calculated from the lengthByteSize attribute.
        
        **Note:** Don't change the lengthByteSize attribute, if you will change it frequently, That will cause problems
        with different clients, with different lengthByteSize attributes.

        :param conn: The socket connection.
        """

        import socket

        self.conn: socket.socket = conn
        self.lengthByteSize = 8

    def send(self, o):
        """
        Send a packet to the connection.

        :param o: The data to send.
        :return:
        """

        length, data = PacketEncoder(o).get_encoded()

        self.conn.send(length.to_bytes(self.lengthByteSize, "big", signed=False))
        self.conn.send(data)

    def sendall(self, o):
        """
        Send a packet to all connected clients.

        :param o:
        :return:
        """

        if not issubclass(type(self.conn), socketserver.BaseRequestHandler):
            raise Exception(f"the conn argument and attribute of {self.__class__.__name__}() "
                            f"must be a subclass of socketserver.BaseRequestHandler")

        length, data = PacketEncoder(o).get_encoded()

        self.conn.sendall(length.to_bytes(self.lengthByteSize, "big", signed=False))
        self.conn.sendall(data)

    def recv(self):
        """
        Recieve a packet from the socket.

        :return:
        """

        length = self.conn.recv(self.lengthByteSize)
        data = self.conn.recv(int.from_bytes(length, "big", signed=False))

        return PacketDecoder(data).get_decoded()


class CryptedPacketSystem(PacketSystem):
    def __init__(self, conn):
        """
        Crypted Packet System for communicate with servers / clients using the ARC4 encryption algorithm.
        Maximum size of a packet is 4294967296 Bytes, 4 Gigabytes. Calculated from the lengthByteSize attribute.

        **Note:** Don't change the lengthByteSize attribute, if you will change it frequently, That will cause problems
        with different clients, with different lengthByteSize attributes.

        :param conn: The socket connection.
        """

        super(CryptedPacketSystem, self).__init__(conn)

    @staticmethod
    def _encrypt(b, key):
        """
        Encryption for packets

        :param b:
        :param key:
        :return:
        """

        # noinspection PyPackageRequirements
        from Crypto.Cipher import ARC4

        obj = ARC4.new(key.encode())
        return obj.encrypt(b)

    @staticmethod
    def _decrypt(b, key):

        # noinspection PyPackageRequirements
        from Crypto.Cipher import ARC4

        obj2 = ARC4.new(key.encode())
        return obj2.decrypt(b)

    def send_c(self, o, key):
        _, data = PacketEncoder(o).get_encoded()
        # print(value, key)
        data = self._encrypt(data, key)
        length = len(data)

        self.conn.send(length.to_bytes(self.lengthByteSize, "big", signed=False))
        self.conn.send(data)

    def recv_c(self, key):
        try:
            length = self.conn.recv(self.lengthByteSize)
            data = self.conn.recv(int.from_bytes(length, "big", signed=False))
        except ValueError:
            return None
        return PacketDecoder(self._decrypt(data, key)).get_decoded()


class NetworkInfo(object):
    """
    Used for getting information about the network, and the connection

    Example
    --------
    >>> print(f"NetworkInfo Test | Data value                                            ")
    >>> print(f"_________________|_______________________________________________________")
    >>> print(f"Get internal IPv6| {NetworkInfo.convert2ipv6(NetworkInfo.get_internal_ip())}")
    >>> print(f"Get external IP  | {NetworkInfo.get_external_ip()}                       ")
    >>> print(f"Get internal IP  | {NetworkInfo.get_internal_ip()}                       ")
    >>> print(f"List WiFi SSIDs  | {NetworkInfo.list_wifi_ssids()}                       ")
    >>> print(f"Network shares   | {win32net.NetShareEnum(NetworkInfo.get_internal_ip())}")
    >>> print(f"_________________|_______________________________________________________")

    """

    localIPv4 = "127.0.0.1"
    localIPv6 = "::1"

    @staticmethod
    def get_external_ip(ext_ip_url='https://ident.me'):
        """
        Used for getting the external IP address.

        Example
        --------
        >>> print(f"External IP: {NetworkInfo.get_external_ip()}")

        :param ext_ip_url:
        :returns: The external IP address
        """

        import urllib.request
        external_ip = urllib.request.urlopen(ext_ip_url).read().decode('utf8')
        return external_ip

    @staticmethod
    def get_internal_ip():
        """
        Used for getting the external IP address.

        Example
        --------
        >>> print(f"Internal IP: {NetworkInfo.get_internal_ip()}")

        :returns: The internal / local IP address
        """
        import socket
        ip = [l_ for l_ in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
                             if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)),
                                                                   s.getsockname()[0], s.close()) for s in
                                                                  [socket.socket(socket.AF_INET,
                                                                                 socket.SOCK_DGRAM)]][0][1]]) if l_][
            -1][0]
        return ip

    @staticmethod
    def convert2ipv6(ip4str):
        """
        Is not working properly

        :param ip4str:
        :return:
        """

        import ipaddress
        return str(ipaddress.IPv6Address(int(ipaddress.IPv4Address(ip4str))))

    @staticmethod
    def connect_wifi(ssid, password):
        """
        Not implemented yet

        :param ssid:
        :param password:
        :return:
        """

        raise NotImplementedError("NetworkInfo(...).connect_wifi(...) is not yet created")

    @staticmethod
    def list_wifi_ssids():
        """
        Returns a list of WiFi SSIDs

        :returns: A list of WiFi SSIDs
        """

        import pywifi

        wifi = pywifi.PyWiFi()
        interfaces = wifi.interfaces()
        # print(interfaces)
        interfaces[-1].scan()
        from time import sleep
        sleep(2)
        # interfaces[0].connect()
        results = interfaces[0].scan_results()
        # print(results)
        # print(results[0].ssid)
        ssids = [result.ssid for result in results]
        print(ssids)
        ssids = _Utils.remove_duplicates(ssids)
        # print(ssids)
        return ssids

    @staticmethod
    def get_personal_shares():
        """
        Returns the Windows shares of the current computer

        :returns: The Windows shares of the current computer
        """

        WindowsShares(NetworkInfo.get_internal_ip())

    @staticmethod
    def add_personal_share():
        """
        Not implemented yet

        :return:
        """

        raise NotImplementedError()
        # win32net.NetShareAdd()

    @staticmethod
    def get_network_interfaces():
        """
        Returns a list of WiFi interfaces

        :returns: A list of WiFi interfaces
        """

        import pywifi

        wifi = pywifi.PyWiFi()
        interfaces = wifi.interfaces()
        return interfaces


class WindowsShares(object):
    def __init__(self, ip):
        """
        WindowsShares constructor

        :param ip:
        """

        self._ip = ip

    def get_shares(self):
        """
        Get the Windows shares.

        :return:
        """

        win32net.NetShareEnum(self._ip)


if __name__ == '__main__':
    # a_ = PacketSender(None, {"Hallo"})
    # a_.send()

    # noinspection PyUnusedLocal
    def c_runner(conn, secret):
        import os
        pak = PacketSystem(conn)
        for i in range(5):
            recieved = pak.recv()
            print(f"Recieved Type: {type(recieved)}")
            print(f"Recieved Data: {recieved}")
        os.kill(os.getpid(), 0)

    # noinspection PyUnusedLocal
    def s_runner(conn, secret):
        import random
        import os

        pak = PacketSystem(conn)
        for i in range(1):
            b = []
            for _ in range(16):
                b.append(chr(random.randint(64, 96)))
            a = f"{''.join(b)}"

            b = random.randint(-5000, +5000)
            pak.send(a)
            pak.send(b)
            pak.send(list(a))
            pak.send(lambda: print("Hello World"))
            pak.send(__import__)
        # os.kill(os.getpid(), 0)


    print(f"NetworkInfo Test | Data value                                            ")
    print(f"_________________|_______________________________________________________")
    print(f"Get internal IPv6| {NetworkInfo.convert2ipv6(NetworkInfo.get_internal_ip())}")
    print(f"Get external IP  | {NetworkInfo.get_external_ip()}                       ")
    print(f"Get internal IP  | {NetworkInfo.get_internal_ip()}                       ")
    print(f"List WiFi SSIDs  | {NetworkInfo.list_wifi_ssids()}                       ")
    print(f"Network shares   | {win32net.NetShareEnum(NetworkInfo.get_internal_ip())}")
    print(f"_________________|_______________________________________________________")

    print("\nClient and Server Test")

    server_ = Server(36673)
    server_.runner = s_runner
    server_.start()
    client_ = Client("127.0.0.1", 36673)
    client_.runner = c_runner
    client_.start()
