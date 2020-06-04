# Importing the required packages
import threading
import time

import click
import requests

completed_threads = 0
info_threads = []


# The below code is used for each chunk of file handled
# by each thread for downloading the content from specified
# location to storage
def handler(start, end, url, filename, thread_no, block_size):
    global info_threads

    # info_threads[thread_no]

    block_length = block_size
    content_length = end - start
    downloaded = 0
    # open the file and write the content of the html page
    # into file.
    for index in range(start, end, block_length):
        error = True
        while error:
            try:
                if index + block_length > end:
                    headers = {'Range': 'bytes=%d-%d' % (index, end)}
                    r = requests.get(url, headers=headers, stream=True)
                else:
                    # specify the starting and ending of the file
                    headers = {'Range': 'bytes=%d-%d' % (index, index + block_length)}
                    r = requests.get(url, headers=headers, stream=True)
                with open(filename, "r+b") as fp:
                    fp.seek(index)
                    fp.tell()
                    fp.write(r.content)
                    downloaded += block_length
                    info_threads[thread_no] = {"Downloaded": downloaded, "ContentLength": content_length}
                error = False
            except requests.ConnectionError:
                error = True
    global completed_threads
    completed_threads += 1


# noinspection PyUnusedLocal
@click.command(help="It downloads the specified file with specified name")
@click.option('--number_of_threads', default=4, help="No of Threads")
@click.option('--name', type=click.Path(), help="Name of the file with extension")
@click.option('--block-size', default=1024, help="Name of the file with extension")
@click.argument('url_of_file', type=click.Path())
@click.pass_context
def download_file(ctx, url_of_file, name, number_of_threads, block_size):
    import re
    r = requests.head(url_of_file)
    if name:
        file_name = name
    else:
        try:
            d = r.headers['content-disposition']
            file_name = re.findall("filename=(.+)", d)[0]
        except KeyError:
            file_name = url_of_file.split('/')[-1]

    try:
        file_size = int(r.headers['content-length']) + 1
    except ValueError:
        print("Invalid URL")
        return
    except TypeError:
        print("Invalid URL")
        return

    part = int(file_size / number_of_threads)
    fp = open(file_name, "wb+")
    fp.seek(file_size - 1)
    fp.write(b"\0")
    fp.close()

    global info_threads

    prog = {}

    for i in range(number_of_threads):
        start = part * i
        end = start + part

        info_threads.append({"Downloaded": 0, "ContentLength": end - start, "DownloadComplete": False})

        # create a Thread with start and end locations
        t = threading.Thread(target=handler,
                             kwargs={'start': start, 'end': end - 1, 'url': url_of_file, 'filename': file_name,
                                     'thread_no': i, 'block_size': block_size})
        # t.setDaemon(True)
        t.start()

    # prog = click.progressbar(length=file_size, label="Download Progress", show_eta=False, show_percent=True)

    global completed_threads

    downloading = True
    downloaded_bytes = 0
    while downloading:
        d24 = True
        downloaded_bytes = 0
        for k in range(len(info_threads)):
            downloaded_bytes += info_threads[k]["Downloaded"]
            # print("Thread %s: Downloaded: %s of %s" % (k, info_threads[k]["Downloaded"], info_threads[k][
            # "ContentLength"]))
        click.clear()
        click.echo("Downloading of %s\n%s%% complete - %s of %s bytes downloaded.\nCompleted Threads: %s of %s" %
                   (file_name, 100 * downloaded_bytes / file_size, downloaded_bytes, file_size, completed_threads,
                    number_of_threads))
        # click.termui.style(, reset=True)
        if completed_threads == number_of_threads:
            d24 = False
        downloading = d24
        time.sleep(1)

    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is main_thread:
            continue
        t.join()

    print('%s downloaded' % file_name)


if __name__ == '__main__':
    download_file(obj={})
