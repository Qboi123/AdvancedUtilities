from pyGoogleSearch import Google as GoogleSearch


class QGoogleImages(object):
    def __init__(self):
        """
        Google images scraper
        """

        from googleimagedownloader import googleimagedownloader as googleimg
        self._googleimg = googleimg

    def download(self, query, n):
        """
        Download images from google

        :param query:
        :param n:
        :return:
        """

        self._googleimg.GoogleImageDownloader(query, n)


class QGoogle(object):
    @staticmethod
    def google_search(query, num=10, start=0, recent=None, pages=1, sleep=False):
        """
        Google searcher

        :param query:
        :param num:
        :param start:
        :param recent:
        :param pages:
        :param sleep:
        :return:
        """
        return GoogleSearch(query, num, start, recent, '', pages, sleep)

    @staticmethod
    def google_images():
        """
        Google images scraper

        :return:
        """

        return QGoogleImages()
