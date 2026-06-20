from cabarchive.archive import CabArchive as CabArchive
from cabarchive.errors import CorruptionError as CorruptionError, NotSupportedError as NotSupportedError
from cabarchive.file import CabFile as CabFile
from cabarchive.utils import FMT_CFDATA as FMT_CFDATA, FMT_CFFILE as FMT_CFFILE, FMT_CFFOLDER as FMT_CFFOLDER, FMT_CFHEADER as FMT_CFHEADER, FMT_CFHEADER_RESERVE as FMT_CFHEADER_RESERVE

COMPRESSION_MASK_TYPE: int
COMPRESSION_TYPE_NONE: int
COMPRESSION_TYPE_MSZIP: int
COMPRESSION_TYPE_QUANTUM: int
COMPRESSION_TYPE_LZX: int

class CabArchiveParser:
    cfarchive: CabArchive
    flattern: bool
    def __init__(self, cfarchive: CabArchive, flattern: bool = False) -> None: ...
    def parse_cffile(self, offset: int) -> int: ...
    def parse_cffolder(self, offset: int) -> None: ...
    def parse_cfdata(self, offset: int, compression: int) -> tuple[int, bytes]: ...
    def parse(self, buf: bytes) -> None: ...
