"""
Saleae Logic 2 High Level Analyzer Extension for STGAP1BS Gate Driver
SPI Protocol

This analyzer is able to decode the SPI communication protocol used by the
STGAP1BS gate driver IC from STMicroelectronics. It also supports older
STGAP1AS devices.

It is capable of automatically determining the number of devices in a
daisy-chained configuration, and decoding pipelined register reads and writes.
"""

from enum import IntEnum
from typing import List

from register_definitions import (COMMANDS, REGISTERS, STGAP1BS_CMD_READ_REG,
                                  STGAP1BS_CMD_REG_MASK,
                                  STGAP1BS_CMD_WRITE_REG, STGAP1BS_REG_MASK,
                                  decode_reg_byte)
from saleae.analyzers import AnalyzerFrame, HighLevelAnalyzer, NumberSetting


class FrameState(IntEnum):
    """What the expected state of the gate driver is for this frame."""
    COMMAND = 0
    REG_READ = 1
    REG_WRITE = 2


class Stgap1bsAnalyzer(HighLevelAnalyzer):
    """High Level Analyzer for STGAP1BS Gate Driver SPI Protocol."""

    # We have just the single frame type
    result_types = {
        'result': {
            'format': '{{data.data}}'
        }
    }

    def __init__(self):
        """
        Create the state variables used to track the state of the analyzer.
        """

        self.state: List[FrameState] = []
        self.next_state: List[FrameState] = []
        self.register: List[int] = []
        self.chip_count = 0

    def decode(self, frame: AnalyzerFrame):
        """
        Process each frame from the SPI input analyzer. The analyzer resets its
        state on each 'enable' frame, and then tracks the state of each chip in
        the daisy chain as it processes 'result' frames.
        """

        if frame.type == 'enable':
            self.state = self.next_state
            self.next_state = []
            self.chip_count = 0
            return None

        if frame.type == 'result':
            self.chip_count += 1
            chip_index = self.chip_count - 1

            # learn how many chips are in the chain - should only happen on the
            # first iteration
            if len(self.register) < self.chip_count:
                self.register.append(0)
            if len(self.state) < self.chip_count:
                self.state.append(FrameState.COMMAND)

            # Process read register responses first before the register
            # is clobbered by a pipelined command starting
            response = ""
            if self.state[chip_index] == FrameState.REG_READ:
                # The next state will be set later
                register = self.register[chip_index]
                data = decode_reg_byte(register, frame.data['miso'][0])
                response += (f" | {REGISTERS[register]['name']} " +
                             f"read: {data}")

            message = ""
            if (self.state[chip_index] == FrameState.COMMAND or
                    self.state[chip_index] == FrameState.REG_READ):
                cmd = frame.data['mosi'][0]

                if cmd in COMMANDS:
                    self.next_state.append(FrameState.COMMAND)
                    message = COMMANDS[cmd]

                elif cmd & STGAP1BS_CMD_REG_MASK == STGAP1BS_CMD_READ_REG:
                    register = cmd & STGAP1BS_REG_MASK
                    self.register[chip_index] = register
                    self.next_state.append(FrameState.REG_READ)
                    message = f"Read {REGISTERS[register]['name']}"

                elif cmd & STGAP1BS_CMD_REG_MASK == STGAP1BS_CMD_WRITE_REG:
                    register = cmd & STGAP1BS_REG_MASK
                    self.register[chip_index] = register
                    self.next_state.append(FrameState.REG_WRITE)
                    message = f"Write {REGISTERS[register]['name']}"

                else:
                    message = f"Error: Unknown command {cmd:02X}"

            if self.state[chip_index] == FrameState.REG_WRITE:
                self.next_state.append(FrameState.COMMAND)
                register = self.register[chip_index]
                data = decode_reg_byte(register, frame.data['mosi'][0])
                message = f"{REGISTERS[register]['name']} write: {data}"

            if response:
                message += response

            return AnalyzerFrame('result', frame.start_time, frame.end_time,
                                 {'data': message})

        return None
