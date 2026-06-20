import datetime
from _typeshed import Incomplete

class CabFile:
    buf: Incomplete
    date: datetime.date | None
    time: datetime.time | None
    is_readonly: bool
    is_hidden: bool
    is_system: bool
    is_arch: bool
    is_exec: bool
    def __init__(self, buf: bytes | None = None, filename: str | None = None, mtime: datetime.datetime | None = None) -> None: ...
    def __len__(self) -> int: ...
    @property
    def filename(self) -> str | None: ...
    is_name_utf8: Incomplete
    @filename.setter
    def filename(self, filename: str) -> None: ...
