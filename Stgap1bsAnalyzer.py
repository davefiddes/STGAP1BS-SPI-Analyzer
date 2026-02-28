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

from saleae.analyzers import AnalyzerFrame, HighLevelAnalyzer

from register_definitions import (COMMANDS, REGISTERS, STGAP1BS_CMD_READ_REG,
                                  STGAP1BS_CMD_REG_MASK,
                                  STGAP1BS_CMD_WRITE_REG, STGAP1BS_REG_MASK,
                                  decode_reg_byte)


def _generate_crc_table():
    """Generate CRC-8 lookup table for polynomial 0x07."""
    table = []
    for i in range(256):
        crc = i
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0x07) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
        table.append(crc)
    return table


CRC_TABLE = _generate_crc_table()


def crc8_ccitt(data: int, crc: int = 0xFF) -> int:
    """
    Calculate CRC-8-CCITT using lookup table (polynomial 0x07).

    This implements the CRC algorithm used by the STGAP1BS gate driver.
    It uses a precomputed lookup table for efficiency, and allows for chaining
    CRC calculations by accepting an initial CRC value.

    Args:
        data: The data byte to process
        crc: The current CRC value (default 0xFF for initial calculation)

    Returns:
        The updated CRC value
    """
    return CRC_TABLE[(crc ^ data) & 0xFF]


def invert_byte(value: int) -> int:
    """Invert all bits of a byte and mask to 8 bits."""
    return ~value & 0xFF


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
        # Track CRC from command byte for chained data CRC
        self.command_crc: List[int] = []
        self.chip_count = 0
        self.debug = False

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
            if len(self.command_crc) < self.chip_count:
                self.command_crc.append(0)
            if len(self.state) < self.chip_count:
                self.state.append(FrameState.COMMAND)

            # Process read register responses first before the register
            # is clobbered by a pipelined command starting
            response = ""
            if self.state[chip_index] == FrameState.REG_READ:
                # The next state will be set later
                register = self.register[chip_index]
                miso_data = frame.data['miso'][0]
                miso_crc = frame.data['miso'][1]

                # Check CRC for MISO data
                computed_crc = crc8_ccitt(miso_data)
                crc_status = self._check_crc(miso_crc, computed_crc)

                data = decode_reg_byte(register, miso_data)
                if register in REGISTERS:
                    response += (f" | {REGISTERS[register]['name']} " +
                                 f"read: {data}{crc_status}")
                else:
                    response += (f" | Unknown register {register:02X} " +
                                 f"read: {data}{crc_status}")

            message = ""
            crc_status = ""

            if (self.state[chip_index] == FrameState.COMMAND or
                    self.state[chip_index] == FrameState.REG_READ):
                cmd = frame.data['mosi'][0]
                mosi_crc = frame.data['mosi'][1]

                if cmd in COMMANDS:
                    self.next_state.append(FrameState.COMMAND)
                    message = COMMANDS[cmd]

                    # Check CRC for command MOSI
                    computed_crc = invert_byte(crc8_ccitt(cmd))
                    crc_status = self._check_crc(mosi_crc, computed_crc)

                    # Store command CRC for potential chaining to data CRC
                    self.command_crc[chip_index] = computed_crc

                elif cmd & STGAP1BS_CMD_REG_MASK == STGAP1BS_CMD_READ_REG:
                    register = cmd & STGAP1BS_REG_MASK
                    self.register[chip_index] = register
                    self.next_state.append(FrameState.REG_READ)
                    if register in REGISTERS:
                        message = f"Read {REGISTERS[register]['name']}"
                    else:
                        message = f"Read unknown register {register:02X}"

                    # Check CRC for read command MOSI
                    computed_crc = invert_byte(crc8_ccitt(cmd))
                    crc_status = self._check_crc(mosi_crc, computed_crc)

                elif cmd & STGAP1BS_CMD_REG_MASK == STGAP1BS_CMD_WRITE_REG:
                    register = cmd & STGAP1BS_REG_MASK
                    self.register[chip_index] = register
                    self.next_state.append(FrameState.REG_WRITE)
                    if register in REGISTERS:
                        message = f"Write {REGISTERS[register]['name']}"
                    else:
                        message = f"Write unknown register {register:02X}"

                    # Check CRC for write command MOSI
                    raw_cmd_crc = crc8_ccitt(cmd)
                    computed_crc = invert_byte(raw_cmd_crc)
                    crc_status = self._check_crc(mosi_crc, computed_crc)

                    # Store command CRC for chaining to write data CRC
                    self.command_crc[chip_index] = raw_cmd_crc

                else:
                    message = f"Error: Unknown command {cmd:02X}"

            if self.state[chip_index] == FrameState.REG_WRITE:
                self.next_state.append(FrameState.COMMAND)
                register = self.register[chip_index]
                mosi_data = frame.data['mosi'][0]
                mosi_crc = frame.data['mosi'][1]

                data = decode_reg_byte(register, mosi_data)
                if register in REGISTERS:
                    message = f"{REGISTERS[register]['name']} write: {data}"
                else:
                    message = f"Unknown register {register:02X} write: {data}"

                # Check CRC for write data MOSI
                # For write data, CRC is chained from the command byte CRC
                # dataCrc = crc8(data, cmdCrc) where cmdCrc is from the command
                cmd_crc = self.command_crc[chip_index]
                computed_crc = invert_byte(crc8_ccitt(mosi_data, cmd_crc))
                crc_status = self._check_crc(mosi_crc, computed_crc)

            message += crc_status

            if response:
                message += response

            return AnalyzerFrame('result', frame.start_time, frame.end_time,
                                 {'data': message})

        return None

    def _check_crc(self, received_crc: int, computed_crc: int) -> str:
        """Check the received and computed CRC values and return a status
        message."""
        if computed_crc != received_crc:
            return (f" [CRC ERROR: got {received_crc:02X}, " +
                    f"expected {computed_crc:02X}]")

        if self.debug:
            return f" [CRC OK: {received_crc:02X}]"

        return ""
