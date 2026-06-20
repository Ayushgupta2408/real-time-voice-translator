#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2020 Richard Hughes <richard@hughsie.com>
#
# SPDX-License-Identifier: LGPL-2.1+
#
# pylint: disable=protected-access,too-few-public-methods

from typing import List, TYPE_CHECKING, Union
import struct
import zlib

from cabarchive.file import CabFile
from cabarchive.utils import (
    FMT_CFHEADER,
    FMT_CFFOLDER,
    FMT_CFFILE,
    FMT_CFDATA,
    _chunkify,
    _checksum_compute,
)

if TYPE_CHECKING:
    from cabarchive.archive import CabArchive


class CabArchiveWriter:
    def __init__(
        self, cfarchive: "CabArchive", compress: bool = False, sort: bool = True
    ) -> None:
        self.cfarchive: "CabArchive" = cfarchive
        self.compress: bool = compress
        self.sort: bool = sort

    def write(self) -> bytes:
        # sort files before export
        cffiles: List[CabFile] = (
            [self.cfarchive[k] for k in sorted(self.cfarchive.keys())]
            if self.sort
            else list(self.cfarchive.values())
        )

        # create linear CFDATA block (join once instead of repeated +=)
        if len(cffiles) > 1:
            parts = [f.buf for f in cffiles if f.buf]
            cfdata_linear = b"".join(parts) if parts else bytes()
        else:
            cfdata_linear = cffiles[0].buf or bytes()

        # _chunkify and compress with a fixed size
        chunks = _chunkify(cfdata_linear, 0x8000)
        if self.compress:
            chunks_zlib = []
            for chunk in chunks:
                compressobj = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)
                chunk_zlib = b"CK"
                chunk_zlib += compressobj.compress(chunk)
                chunk_zlib += compressobj.flush()
                chunks_zlib.append(memoryview(chunk_zlib))
        else:
            chunks_zlib = chunks

        # files with names only, encode filename once per file
        cffiles_named = [
            (f, f._filename_win32.encode() + b"\0")
            for f in cffiles
            if f._filename_win32
        ]
        sz_header = struct.calcsize(FMT_CFHEADER)
        sz_folder = struct.calcsize(FMT_CFFOLDER)
        sz_file = struct.calcsize(FMT_CFFILE)
        sz_cfdata = struct.calcsize(FMT_CFDATA)
        archive_size = sz_header + sz_folder
        for _f, enc in cffiles_named:
            archive_size += sz_file + len(enc)
        for chunk in chunks_zlib:
            archive_size += sz_cfdata + len(chunk)
        offset_cffile = sz_header + sz_folder
        offset_cfdata = offset_cffile
        for _f, enc in cffiles_named:
            offset_cfdata += sz_file + len(enc)

        # build output in one join instead of repeated +=
        segments: List[Union[bytes, memoryview]] = []
        segments.append(
            struct.pack(
                FMT_CFHEADER,
                b"MSCF",  # signature
                archive_size,  # complete size
                offset_cffile,  # offset to CFFILE
                3,
                1,  # ver minor major
                1,  # no of CFFOLDERs
                len(self.cfarchive),  # no of CFFILEs
                0,  # flags
                self.cfarchive.set_id,  # setID
                0,
            )  # cnt of cabs in set
        )
        segments.append(
            struct.pack(
                FMT_CFFOLDER,
                offset_cfdata,  # offset to CFDATA
                min(len(chunks), 0xFFFF),  # number of CFDATA blocks
                self.compress,
            )  # compression type
        )
        index_into = 0
        for f, enc in cffiles_named:
            segments.append(
                struct.pack(
                    FMT_CFFILE,
                    len(f),  # uncompressed size
                    index_into,  # uncompressed offset
                    0,  # index into CFFOLDER
                    f._date_encode(),  # date
                    f._time_encode(),  # time
                    f._attr_encode(),
                )  # attribs
            )
            segments.append(enc)
            index_into += len(f)
        for i in range(len(chunks)):
            chunk = chunks[i]
            chunk_zlib = chunks_zlib[i]
            checksum = _checksum_compute(chunk_zlib)
            hdr = struct.pack("<HH", len(chunk_zlib), len(chunk))
            checksum = _checksum_compute(hdr, checksum)
            segments.append(
                struct.pack(
                    FMT_CFDATA,
                    checksum,
                    len(chunk_zlib),
                    len(chunk),
                )
            )
            segments.append(chunk_zlib)
        return b"".join(segments)
