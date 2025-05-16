import os
import struct
from typing import List, Optional
from abc import abstractmethod
import chipwhisperer as cw
from ctypes import *

from .base import CSIDHBase

import time




NUM_PRIMES = 3
MAX_EXPONENT = 5
LIMBS = 1

class UIntC(Structure):
    _fields_ = [("c", c_longlong * LIMBS)]


class Fp(Structure):
    _fields_ = [("c", c_longlong * LIMBS)]


class Proj(Structure):
    _fields_ = [("x", Fp), ("z", Fp)]


class PublicKey(Structure):
    _fields_ = [("A", Fp)]


class PrivateKey(Structure):
    _fields_ = [("e", c_ubyte * NUM_PRIMES)]

class CSIDHDLL(CSIDHBase):
    """Wrapper for CSIDH running locally as a dynamically linked library."""

    DLL = "./libcsidh.so"
    


    def __init__(self, src_path="") -> None:
        self.SRC_PATH = src_path if src_path else self.SRC_PATH
        self.build_target()
        self.libcsidh = CDLL(self.DLL, mode=1)

        self._public = PublicKey()
        self._private = PrivateKey()

    def build_target(self):
        os.chdir(self.SRC_PATH)
        os.system("cmake -B build -S .")
        os.chdir("build")
        os.system("make")

    @property
    def public(self):
        return self._public.A.c[0]

    @public.setter
    def public(self, value: int):
        self._public.A.c[0] = value

    @property
    def private(self):
        return list(self._private.e)

    @private.setter
    def private(self, value: List[int]):
        for i in range(NUM_PRIMES):
            self._private.e[i] = -value[i]

    def action(self) -> int:
        """CSIDH Function

        :return bool: Success or error
        :param out: Public key
        :param in: Private key
        :param num_intervals: Always 1
        :param max_exponent: NUM_PRIMES * [MAX_EXPONENT]
        :param num_isogenies: NUM_PRIMES * MAX_EXPONENT
        :param my: Always 1
        """


        csidh = self.libcsidh.csidh
        csidh.argtypes = [
            POINTER(PublicKey),  # out
            POINTER(PublicKey),  # in
            POINTER(PrivateKey),  # priv
            c_ubyte,
            POINTER(NUM_PRIMES * c_byte),
            c_uint,
            c_ubyte,
        ]
        csidh.restype = c_bool

        result = PublicKey()

        max_exponent = (c_byte * NUM_PRIMES)()
        for i in range(NUM_PRIMES):
            max_exponent[i] = MAX_EXPONENT

        csidh(
            byref(result),
            byref(self._public),
            byref(self._private),
            1,
            byref(max_exponent),
            NUM_PRIMES * MAX_EXPONENT,
            1,
        )
        return result.A.c[0]

