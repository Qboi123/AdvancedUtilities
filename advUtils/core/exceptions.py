class PlatformNotSupportedError(Exception):
    __module__ = "builtins"  # Tweak to avoid the module name from being included.

    def __init__(self, *args: object):
        """
        Exception for unsupported platforms.

        :param args: The arguments for the message.
        """

        super(PlatformNotSupportedError, self).__init__(*args)

    def __str__(self):
        import platform

        if len(self.args) == 0:
            return f"Platform {platform.system()} is not supported"
        else:
            return f"Platform {platform.system()} is not supported ({' '.join(self.args)})"


if __name__ == '__main__':
    def platformerror():
        raise PlatformNotSupportedError()

    def platformerror_withmessage():
        try:
            raise PlatformNotSupportedError("This is a test message")
        except PlatformNotSupportedError:
            raise PlatformNotSupportedError("This is a test message") from None

    platformerror_withmessage()
