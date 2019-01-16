# coding: UTF-8

import os
import sys
from ctypes import Structure, c_int16, c_int64, c_uint, c_uint16, c_uint32, c_uint64, c_ulong, sizeof
from enum import IntEnum

PADDED = {
    (4, 'little'): lambda w, x, y: [(x, w), (y, c_uint)],
    (8, 'little'): lambda w, x, y: [(x, w), (y, w)],
    (8, 'big'): lambda w, x, y: [(y, c_uint), (x, w)],
    (4, 'big'): lambda w, x, y: [(y, c_uint), (x, w)],
}[(sizeof(c_ulong), sys.byteorder)]


class IOCB(Structure):
    _fields_ = (
        # internal fields used by the kernel
        ('aio_data', c_uint64),
        *PADDED(c_uint32, 'aio_key', 'aio_rw_flags'),

        # common fields
        ('aio_lio_opcode', c_uint16),
        ('aio_reqprio', c_int16),
        ('aio_fildes', c_uint32),

        ('aio_buf', c_uint64),
        ('aio_nbytes', c_uint64),
        ('aio_offset', c_int64),

        # extra parameters
        ('aio_reserved2', c_uint64),

        # flags for IOCB
        ('aio_flags', c_uint32),

        # if the IOCB_FLAG_RESFD flag of "aio_flags" is set, this is an eventfd to signal AIO readiness to
        ('aio_resfd', c_uint32),
    )


# Define the types we need.
class _CtypesEnum(IntEnum):
    """A ctypes-compatible IntEnum superclass."""

    @classmethod
    def from_param(cls, obj) -> int:
        return int(obj)


class IOCBCMD(_CtypesEnum):
    PREAD = 0
    PWRITE = 1
    FSYNC = 2
    FDSYNC = 3
    # These two are experimental.
    # PREADX = 4
    POLL = 5
    NOOP = 6
    PREADV = 7
    PWRITEV = 8


class IOCBFlag(_CtypesEnum):
    """ flags for :attr:`IOCB.aio_flags` """
    RESFD = 1 << 0
    IOPRIO = 1 << 1


# TODO: detail description (e.g. minimum required linux version)
class IOCBRWFlag(_CtypesEnum):
    """ flags for :attr:`IOCB.aio_rw_flags`. from linux code (/include/uapi/linux/fs.h) """
    HIPRI = 1 << 0 if sys.version_info < (3, 7) else os.RWF_HIPRI
    DSYNC = 1 << 1 if sys.version_info < (3, 7) else os.RWF_DSYNC
    SYNC = 1 << 2 if sys.version_info < (3, 7) else os.RWF_SYNC
    NOWAIT = 1 << 3 if sys.version_info < (3, 7) else os.RWF_NOWAIT
    APPEND = 1 << 4


# TODO: detail description (e.g. minimum required linux version, how priority value works)
class IOCBPriorityClass(_CtypesEnum):
    """ priority class. from linux code (/include/linux/ioprio.h) """
    NONE = 0
    RT = 1
    BE = 2
    IDLE = 3


IOPRIO_CLASS_SHIFT = 13


def gen_io_priority(priority_class: IOCBPriorityClass, priority: int) -> int:
    return (priority_class << IOPRIO_CLASS_SHIFT) | priority