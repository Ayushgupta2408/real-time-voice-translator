from cabarchive.archive import CabArchive as CabArchive
from cabarchive.file import CabFile as CabFile
from cabarchive.utils import FMT_CFDATA as FMT_CFDATA, FMT_CFFILE as FMT_CFFILE, FMT_CFFOLDER as FMT_CFFOLDER, FMT_CFHEADER as FMT_CFHEADER

class CabArchiveWriter:
    cfarchive: CabArchive
    compress: bool
    sort: bool
    def __init__(self, cfarchive: CabArchive, compress: bool = False, sort: bool = True) -> None: ...
    def write(self) -> bytes: ...
