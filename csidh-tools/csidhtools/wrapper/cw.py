import os
import struct
from typing import List, Optional
from abc import abstractmethod
import chipwhisperer as cw
from .base import  CSIDHBase
from ctypes import *

import time




class CSIDHCW(CSIDHBase):
    """Wrapper for CSIDH running on ChipWhisperer."""

    def __init__(self, src_path="", attack_type="A1", PLATFORM="CW308_STM32F3") -> None:
        self.SCOPETYPE = "OPENADC"
        self.PLATFORM = PLATFORM
        self.SS_VER = "SS_VER_2_1"
        self.CRYPTO_TARGET = "NONE"
        self.BIN = "main-" + self.PLATFORM + ".hex"
        self.RNG = 'DETERMINISTIC'

        self.scope = None
        self.target = None
        self.programmer = None
        self.SRC_PATH = src_path if src_path else self.SRC_PATH
        self.firmware_path = self.SRC_PATH + self.BIN
        self.attack_type = attack_type
        self.name = None
        self.action_sleep = 0.5

    def __str__(self) -> str:
        return f"Public:  {self.public}\nPrivate: {self.private}"

    def setup(self) -> None:
        self.connect()
        self.choose_programmer()
        time.sleep(0.05)
        self.scope.default_setup()

    def connect(self) -> None:
        """Connect to the ChipWhisperer target and scope."""
        try:
            if not self.scope.connectStatus:
                self.scope.con()
        except AttributeError:
            if self.name:
                self.scope = cw.scope(name=self.name)
            else:
                self.scope = cw.scope()

        try:
            if self.SS_VER == "SS_VER_2_1":
                self.target_type = cw.targets.SimpleSerial2
            elif self.SS_VER == "SS_VER_2_0":
                raise OSError("SS_VER_2_0 is deprecated. Use SS_VER_2_1")
            else:
                self.target_type = cw.targets.SimpleSerial
        except:
            self.SS_VER = "SS_VER_1_1"
            self.target_type = cw.targets.SimpleSerial

        try:
            self.target = cw.target(self.scope, self.target_type)
        except:
            print(
                "INFO: Caught exception on reconnecting to target - attempting to reconnect to scope first."
            )
            print(
                "INFO: This is a work-around when USB has died without Python knowing. Ignore errors above this line."
            )
            self.scope = cw.scope()
            self.target = cw.target(self.scope, self.target_type)

        print("INFO: Found ChipWhisperer😍")

    def choose_programmer(self) -> None:
        """Choose the programmer based on the platform."""
        if (
            "STM" in self.PLATFORM
            or self.PLATFORM == "CWLITEARM"
            or self.PLATFORM == "CWNANO"
        ):
            self.programmer = cw.programmers.STM32FProgrammer
        elif self.PLATFORM == "CW303" or self.PLATFORM == "CWLITEXMEGA":
            self.programmer = cw.programmers.XMEGAProgrammer
        elif "neorv32" in self.PLATFORM.lower():
            self.programmer = cw.programmers.NEORV32Programmer
        elif self.PLATFORM == "CW308_SAM4S" or self.PLATFORM == "CWHUSKY":
            self.programmer = cw.programmers.SAM4SProgrammer
        else:
            self.programmer = None

    def voltage_glitching_setup(self) -> None:
        """Setup for voltage glitching."""
        if self.scope._is_husky:
            self.scope.glitch.enabled = True
            self.scope.glitch.clk_src = "pll"
            self.scope.io.glitch_hp = False
            self.scope.io.glitch_hp = True
            self.scope.io.glitch_lp = False
            self.scope.io.glitch_lp = False
        else:
            self.scope.glitch.clk_src = "clkgen"  # set glitch input clock
        self.scope.glitch.output = "glitch_only"  # glitch_out = clk ^ glitch
        self.scope.glitch.trigger_src = (
            "ext_single"  # glitch only after scope.arm() called
        )
        if self.PLATFORM == "CWLITEXMEGA":
            self.scope.io.glitch_lp = True
            self.scope.io.glitch_hp = True
        elif self.PLATFORM == "CWLITEARM":
            self.scope.io.glitch_lp = True
            self.scope.io.glitch_hp = True
        elif self.PLATFORM == "CW308_STM32F3":
            self.scope.io.glitch_hp = True
            self.scope.io.glitch_lp = True

    def build_target(self) -> None:
        """Build the target firmware."""
        os.chdir(self.SRC_PATH)
        os.system(
            f"make clean"
        )
        os.system(
            f"make PLATFORM={self.PLATFORM} CRYPTO_TARGET={self.CRYPTO_TARGET} SS_VER={self.SS_VER} ATTACK_TYPE={self.attack_type} RNG={self.RNG}"
        )

    def program_target(self) -> None:
        """Program the target with the firmware."""
        cw.program_target(self.scope, self.programmer, self.firmware_path)
        if self.SS_VER == "SS_VER_2_1":
            self.target.reset_comms()

    def reset_target(self) -> None:
        """Reset the target device."""
        if self.PLATFORM == "CW303" or self.PLATFORM == "CWLITEXMEGA":
            self.scope.io.pdic = "low"
            time.sleep(0.1)
            self.scope.io.pdic = "high_z"  # XMEGA doesn't like pdic driven high
            time.sleep(0.1)  # xmega needs more startup time
        elif "neorv32" in self.PLATFORM.lower():
            raise IOError(
                "Default iCE40 neorv32 build does not have external reset - reprogram device to reset"
            )
        elif self.PLATFORM == "CW308_SAM4S" or self.PLATFORM == "CWHUSKY":
            self.scope.io.nrst = "low"
            time.sleep(0.25)
            self.scope.io.nrst = "high_z"
            time.sleep(0.25)
        else:
            self.scope.io.nrst = "low"
            time.sleep(0.05)
            self.scope.io.nrst = "high_z"
            time.sleep(0.05)
        self.target.flush()

    def flash_target(self) -> None:
        """Build, program, and reset the target."""
        self.build_target()
        self.program_target()
        self.reset_target()

    @property
    def public_with_errors(self, timeout=100, glitch_timeout=1):
        """Read the public key without error checking."""
        self.target.flush()
        self.target.send_cmd("2", 0, bytearray([]))
        value = self.target.simpleserial_read_witherrors(
            timeout=timeout, glitch_timeout=glitch_timeout
        )
        if not value["valid"]:
            return value
        value = int.from_bytes(value["payload"], "little")
        self.target.flush()
        return self.from_projective(value)

    @property
    def public(self):
        self.target.flush()
        self.target.send_cmd("2", 0, bytearray([]))
        value = self.target.simpleserial_read('r', timeout=3000)
        value = int.from_bytes(value, "little")
        self.target.flush()
        return self.from_projective(value)

    @public.setter
    def public(self, value: int):
        self.target.flush()
        self.target.send_cmd("1", 0, value.to_bytes(8, "little"))
        self.target.flush()
        time.sleep(0.1)

    @property
    def private(self):
        self.target.flush()
        self.target.send_cmd("4", 0, bytearray([]))
        time.sleep(0.1)
        value = self.target.simpleserial_read('r', timeout=3000)
        self.target.flush()
        time.sleep(0.1)
        return list([-struct.unpack("b", bytearray([x]))[0] for x in value])

    @private.setter
    def private(self, value: List[int]):
        assert len(value) == 3
        self.target.flush()
        priv = b""
        for x in value:
            priv += struct.pack("b", -x)
        self.target.send_cmd("3", 0, priv)
        time.sleep(0.1)

    def action(self) -> int:
        self.target.send_cmd("5", 0, bytearray([]))
        time.sleep(self.action_sleep)

    def dis(self) -> None:
        self.target.dis()
        self.scope.dis()
