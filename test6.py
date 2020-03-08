import threading

import requests

# The below code is used for each chunk of file handled
# by each thread for downloading the content from specified
# location to storage
from advUtils.filesystem import File
from advUtils.network import Downloader
from advUtils.system import StoppableThread


def handler(start, end, url, filename):
    # specify the starting and ending of the file
    headers = {'Range': 'bytes=%d-%d' % (start, end)}

    # request the specified part and get into variable
    r = requests.get(url, headers=headers, stream=True)

    # open the file and write the content of the html page
    # into file.
    with open(filename, "r+b") as fp:
        fp.seek(start)
        var = fp.tell()
        fp.write(r.content)


def download_file(url_of_file, name, number_of_threads):
    r = requests.head(url_of_file)
    if name:
        file_name = name
    else:
        file_name = url_of_file.split('/')[-1]
    try:
        file_size = int(r.headers['content-length'])
    except:
        print("Invalid URL")
        return

    part = int(file_size) / number_of_threads
    fp = open(file_name, "w+b")
    fp.write(('\0' * file_size).encode())
    fp.close()

    for i in range(number_of_threads):
        start = part * i
        end = start + part

        # create a Thread with start and end locations
        t = threading.Thread(target=handler,
                             kwargs={'start': start, 'end': end, 'url': url_of_file, 'filename': file_name})
        t.setDaemon(True)
        t.start()
        main_thread = threading.current_thread()
        for t in threading.enumerate():
            if t is main_thread:
                continue
            t.join()
        print('%s downloaded' % file_name)
        
        
class ThreadedDownloader(Downloader):
    def __init__(self, url, file, block_size: int = 1024):
        super().__init__(url, file)

        self.blockSize = block_size
        self._handlers = []
        
    def handler(self, start, end, thread_number):
        file = File(self._file)

        self._handlers[thread_number]["size"] = end-start
        self._handlers[thread_number]["downloaded"] = 0

        print(start, end)

        for offset in range(start, end, self.blockSize):
            _block_start = offset
            _block_end = offset + self.blockSize
            if _block_end > end:
                _block_end = end

            # specify the starting and ending of the file
            headers = {"Range": "bytes=%d-%d" % (_block_start, _block_end)}

            # request the specified part and get into variable
            r = requests.get(self._url, headers=headers, stream=True)

            # open the file and write the content of the block into file.
            file.write_at(offset, r.content)

            self._handlers[thread_number]["downloaded"] = start-_block_end
            self.totalDownloaded += self.blockSize
            r.close()

    def speed(self):
        """
        Speed information update thread

        :return:
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

    def download(self, threads: int = 10):
        r = requests.head(self._url)
        _tempmemfile = File(self._file)

        try:
            file_size = int(r.headers["content-length"])
        except KeyError:
            raise IOError(f"Url {self._url} has no filesize, can't download with threads")

        part = int(file_size) / threads

        file = File(self._file)
        file.create(file_size)
        self.fileTotalbytes = file_size

        for i in range(threads):
            start = int(part * i)
            end = int(start + part)

            self._handlers.append({})

            print("Handlers append")

            # create a Thread with start and end locations, and the thread index
            t = StoppableThread(target=lambda s_=start, e_=end, i_=i: self.handler(s_, e_, i_))
            print("Thread created")
            self._handlers[i]["thread"] = t
            t.setDaemon(True)
            t.start()
            print("Thread started")

        threads_done = []
        while len(threads_done) < threads:
            for handler in self._handlers:
                if not handler["thread"].is_alive():
                    if handler["thread"] not in threads_done:
                        threads_done.append(handler["thread"])

            _temp0002 = self._url.split('/')[-1]
            try:
                _temp0003 = str(int(self.totalDownloaded / self.fileTotalbytes * 100))
            except ZeroDivisionError:
                _temp0003 = 0

            self.title = f"Downloading..."
            self.message1 = f"Downloading of \"{_temp0002} is {_temp0003}% complete."
            self.message2 = f""
            self.message3 = f"{str(self.totalDownloaded)} of {str(self.fileTotalbytes)}"
            # self.message4 = f"With {str(self.spd)} bytes/sec | {h}:{m}:{s} remaining."
            self.status_list = [self.title, self.message1, self.message2, self.message3, self.message4]
            self.status = str.join("\n", self.status_list)

        print("%s downloaded" % self._file)


if __name__ == "__main__":
    file_ = File("ubuntu-19.10-desktop-amd64.iso")
    if file_.exists():
        file_.remove()

    down = ThreadedDownloader("http://releases.ubuntu.com/19.10/ubuntu-19.10-desktop-amd64.iso", "ubuntu-19.10-desktop-amd64.iso", 1024)
    t_ = StoppableThread(target=lambda: down.download(1))
    t_.start()

    from time import sleep

    while t_.is_alive():
        print(down.message3)
        sleep(2)
