class QArchitecture(object):
    def __init__(self, arch, bits):
        self.arch = arch
        self.bits = bits

    def __str__(self):
        if self.arch.lower() == "intel":
            if self.bits == 64:
                return "x64"
            elif self.bits == 32:
                return "x86"
            else:
                return f"x{self.bits}"
        elif self.arch.lower() == "amd":
            if self.bits == 64:
                return "amd64"
            else:
                return f"amd{self.bits}"
        elif self.arch.lower() == "i":
            if self.bits == 32:
                return "i386"
            else:
                raise NotImplementedError("Unknown architecture bits")
        elif self.arch.lower() == "arm":
            if self.bits == 64:
                return "arm64"
            elif self.bits == 32:
                return "arm32"
            elif self.bits == 16:
                return "arm16"
            else:
                return f"arm{self.bits}"
        elif self.arch.lower() == "ppc":
            return f"ppc{self.bits}"
        else:
            ValueError(f"Unknown architecture: {self.arch}")


class QPythonVersion(object):
    def __init__(self, major, minor, patch):
        self.major = major
        self.minor = minor
        self.patch = patch
        
    def __eq__(self, other: 'QPythonVersion') -> bool:
        return (self.major == other.major) and (self.minor == other.minor) and (self.patch == other.patch)

    def __ne__(self, other: 'QPythonVersion') -> bool:
        return (self.major != other.major) and (self.minor != other.minor) and (self.patch != other.patch)

    def __gt__(self, other: 'QPythonVersion') -> bool:
        return (self.major > other.major) or (self.minor > other.minor) or (self.patch > other.patch)
    
    def __lt__(self, other: 'QPythonVersion') -> bool:
        return (self.major < other.major) or (self.minor < other.minor) or (self.patch < other.patch)

    def __ge__(self, other: 'QPythonVersion') -> bool:
        return (self.major >= other.major) or (self.minor >= other.minor) or (self.patch >= other.patch)
    
    def __le__(self, other: 'QPythonVersion') -> bool:
        return (self.major <= other.major) or (self.minor <= other.minor) or (self.patch <= other.patch)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch} {self.get_architecture()}"

    def __int__(self) -> int:
        return int(f"{self.major}{self.minor}{self.patch}")

    @classmethod
    def get_internal(cls):
        import sys
        version_tuple = sys.version.split(' ')[0].split('.')
        vt = version_tuple
        return QPythonVersion(vt[0], vt[1], vt[2])

    @classmethod
    def get_architecture(cls):
        import platform
        import sys
        return platform.architecture(sys.executable)


class QPlatform(object):
    def __init__(self, platform, version):
        self.platform = platform
        self.version = version

    # @classmethod
    # def get_systemplatform(cls):
    #     import platform
    #     p_ = platform.system()
    #     v_ = platform.version


if __name__ == '__main__':
    print(QPythonVersion.get_internal())
