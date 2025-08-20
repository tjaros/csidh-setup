import os
import struct
from typing import List, Optional
from abc import abstractmethod
import chipwhisperer as cw
from ctypes import *

import time


class CSIDHBase:
    """Base class for CSIDH wrappers."""

    SRC_PATH = "../../../csidh-target/src/"

    # CSIDH parameters
    p = 419
    m = 5
    Fp_1 = 409

    @property
    @abstractmethod
    def public(self):
        """Public key."""
        pass

    @public.setter
    @abstractmethod
    def public(self, value: int):
        """Public key setter."""
        pass

    @property
    @abstractmethod
    def private(self):
        """Private key."""
        pass

    @private.setter
    @abstractmethod
    def private(self, value: List[int]):
        """Private key setter."""
        pass

    @abstractmethod
    def build_target(self):
        """Method for building the target on commandline."""
        pass

    def from_projective(self, value: int) -> int:
        """Convert projective coordinates to affine coordinates."""
        return (value * pow(self.Fp_1, -1, self.p)) % self.p

    def to_projective(self, value: int) -> int:
        """Convert affine coordinates to projective coordinates."""
        return (value * self.Fp_1) % self.p