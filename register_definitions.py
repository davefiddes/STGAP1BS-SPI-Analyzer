"""
STGAP1BS/STGAP1BS Gate Driver Register Definitions

Based on the STGAP1BS datasheet
(https://www.st.com/resource/en/datasheet/stgap1bs.pdf)
"""

STGAP1BS_CMD_REG_MASK = 0b11100000
STGAP1BS_CMD_WRITE_REG = 0b10000000
STGAP1BS_CMD_READ_REG = 0b10100000
STGAP1BS_REG_MASK = 0x1F

COMMANDS = {
    0b00101010: "START_CONFIG",
    0b00111010: "STOP_CONFIG",
    0b00000000: "NOP",
    0b11010000: "RESET_STATUS",
    0b11101010: "GLOBAL_RESET",
    0b11110101: "SLEEP"
}


REG_CFG1 = {
    0b1000_0000: "CRC_SPI",
    0b0100_0000: "UVLOD_EN",
    0b0010_0000: "SD_FLAG",
    0b0001_0000: "DIAG_EN",
    0b0000_1100: {  # Deadtime group
        0b0000_0000: "DT_DISABLED",
        0b0000_0100: "DT_250NS",
        0b0000_1000: "DT_800NS",
        0b0000_1100: "DT_1200NS"
    },
    0b0000_0011: {  # Input filter group
        0b0000_0000: "IN_FILTER_DISABLED",
        0b0000_0001: "IN_FILTER_160NS",
        0b0000_0010: "IN_FILTER_500NS",
        0b0000_0011: "IN_FILTER_70NS"
    }
}

REG_CFG2 = {
    0b1110_0000: {  # Sense threshold (bits 7:5)
        0b0000_0000: "SENSE_100MV",
        0b0010_0000: "SENSE_125MV",
        0b0100_0000: "SENSE_150MV",
        0b0110_0000: "SENSE_175MV",
        0b1000_0000: "SENSE_200MV",
        0b1010_0000: "SENSE_250MV",
        0b1100_0000: "SENSE_300MV",
        0b1110_0000: "SENSE_400MV"
    },
    0b00011000: {  # Desaturation current (bits 4:3)
        0b00000000: "DESAT_CUR_250UA",
        0b00001000: "DESAT_CUR_500UA",
        0b00010000: "DESAT_CUR_750UA",
        0b00011000: "DESAT_CUR_1000UA"
    },
    0b00000111: {  # Desaturation threshold (bits 2:0)
        0b00000000: "DESAT_TH_3V",
        0b00000001: "DESAT_TH_4V",
        0b00000010: "DESAT_TH_5V",
        0b00000011: "DESAT_TH_6V",
        0b00000100: "DESAT_TH_7V",
        0b00000101: "DESAT_TH_8V",
        0b00000110: "DESAT_TH_9V",
        0b00000111: "DESAT_TH_10V"
    }
}

REG_CFG3 = {
    0b11110000: {  # 2-level turn off threshold (bits 7:4)
        0b00000000: "2LTO_TH_7V",
        0b00010000: "2LTO_TH_7_5V",
        0b00100000: "2LTO_TH_8V",
        0b00110000: "2LTO_TH_8_5V",
        0b01000000: "2LTO_TH_9V",
        0b01010000: "2LTO_TH_9_5V",
        0b01100000: "2LTO_TH_10V",
        0b01110000: "2LTO_TH_10_5V",
        0b10000000: "2LTO_TH_11V",
        0b10010000: "2LTO_TH_11_5V",
        0b10100000: "2LTO_TH_12V",
        0b10110000: "2LTO_TH_12_5V",
        0b11000000: "2LTO_TH_13V",
        0b11010000: "2LTO_TH_13_5V",
        0b11100000: "2LTO_TH_14V",
        0b11110000: "2LTO_TH_14_5V"
    },
    0b00001111: {  # 2-level turn off time (bits 3:0)
        0b00000000: "2LTO_TIME_DISABLED",
        0b00000001: "2LTO_TIME_0_75US",
        0b00000010: "2LTO_TIME_1_00US",
        0b00000011: "2LTO_TIME_1_50US",
        0b00000100: "2LTO_TIME_2_00US",
        0b00000101: "2LTO_TIME_2_50US",
        0b00000110: "2LTO_TIME_3_00US",
        0b00000111: "2LTO_TIME_3_50US",
        0b00001000: "2LTO_TIME_3_75US",
        0b00001001: "2LTO_TIME_4_00US",
        0b00001010: "2LTO_TIME_4_25US",
        0b00001011: "2LTO_TIME_4_50US",
        0b00001100: "2LTO_TIME_4_75US",
        0b00001101: "2LTO_TIME_5_00US",
        0b00001110: "2LTO_TIME_5_25US",
        0b00001111: "2LTO_TIME_5_50US"
    }
}

REG_CFG4 = {
    0b00100000: "OVLO_EN",         # bit 5
    0b00010000: "UVLO_LATCHED",    # bit 4
    # VL negative supply voltage UVLO threshold (bits 3:2)
    0b00001100: {
        0b00000000: "VLON_TH_DISABLED",
        0b00000100: "VLON_TH_NEG_3V",
        0b00001000: "VLON_TH_NEG_5V",
        0b00001100: "VLON_TH_NEG_7V"
    },
    # VH positive supply voltage UVLO threshold (bits 1:0)
    0b00000011: {
        0b00000000: "VHON_TH_DISABLED",
        0b00000001: "VHON_TH_10V",
        0b00000010: "VHON_TH_12V",
        0b00000011: "VHON_TH_14V"
    }
}

REG_CFG5 = {
    0b00001000: "2LTO_EN",     # bit 3
    0b00000100: "CLAMP_EN",    # bit 2
    0b00000010: "DESAT_EN",    # bit 1
    0b00000001: "SENSE_EN"     # bit 0
}

REG_STATUS1 = {
    0b10000000: "OVLOH",   # bit 7
    0b01000000: "OVLOL",   # bit 6
    0b00100000: "DESAT",   # bit 5
    0b00010000: "SENSE",   # bit 4
    0b00001000: "UVLOH",   # bit 3
    0b00000100: "UVLOL",   # bit 2
    0b00000010: "TSD",     # bit 1
    0b00000001: "TWN"      # bit 0
}

REG_STATUS2 = {
    0b00000100: "REGERRR",  # bit 2
    0b00000010: "ASC",     # bit 1
    # bit 0 unused
}

REG_STATUS3 = {
    0b00010000: "DT_ERR",  # bit 4
    0b00001000: "SPI_ERR",  # bit 3
    0b00000100: "REGERRL",  # bit 2
    0b00000010: "OVLOD",   # bit 1
    0b00000001: "UVLOD"    # bit 0
}

REG_TEST1 = {
    0b00010000: "GOFFCHK",  # bit 4
    0b00001000: "GONCHK",  # bit 3
    0b00000100: "DESCHK",  # bit 2
    0b00000010: "SNSCHK",  # bit 1
    0b00000001: "RCHK"     # bit 0
}

REG_DIAG1CFG = {
    0b10000000: "SPI_REG_ERR",      # bit 7
    0b01000000: "UVLOD_OVLOD",      # bit 6
    0b00100000: "UVLOH_UVLOL",      # bit 5
    0b00010000: "OVLOH_OVLOL",      # bit 4
    0b00001000: "DESAT_SENSE",      # bit 3
    0b00000100: "ASC_DT_ERR",       # bit 2
    0b00000010: "TSD",              # bit 1
    0b00000001: "TWN"               # bit 0
}

REG_DIAG2CFG = {
    0b10000000: "SPI_REG_ERR",      # bit 7
    0b01000000: "UVLOD_OVLOD",      # bit 6
    0b00100000: "UVLOH_UVLOL",      # bit 5
    0b00010000: "OVLOH_OVLOL",      # bit 4
    0b00001000: "DESAT_SENSE",      # bit 3
    0b00000100: "ASC_DT_ERR",       # bit 2
    0b00000010: "TSD",              # bit 1
    0b00000001: "TWN"               # bit 0
}

REGISTERS = {
    0x0C: {"name": "CFG1", "bits": REG_CFG1},
    0x1D: {"name": "CFG2", "bits": REG_CFG2},
    0x1E: {"name": "CFG3", "bits": REG_CFG3},
    0x1F: {"name": "CFG4", "bits": REG_CFG4},
    0x19: {"name": "CFG5", "bits": REG_CFG5},
    0x02: {"name": "STATUS1", "bits": REG_STATUS1},
    0x01: {"name": "STATUS2", "bits": REG_STATUS2},
    0x0A: {"name": "STATUS3", "bits": REG_STATUS3},
    0x11: {"name": "TEST1", "bits": REG_TEST1},
    0x05: {"name": "DIAG1CFG", "bits": REG_DIAG1CFG},
    0x06: {"name": "DIAG2CFG", "bits": REG_DIAG2CFG}
}


def decode_reg_byte(register: int, byte: int) -> str:
    """
    Decodes a single byte representing the specifying the register state into
    a textual representation.
    """
    result = []

    if register not in REGISTERS:
        return "UNKNOWN_REGISTER"

    reg_bits = REGISTERS[register]["bits"]

    # Decode individual bits
    for mask, name in reg_bits.items():
        bits = byte & mask
        if isinstance(name, dict):
            if bits in name:
                result.append(name[bits])
            else:
                result.append(f"UNKNOWN_{bits:02X}")
        elif isinstance(name, str) and bits == mask:
            result.append(name)

    if len(result) > 0:
        return ", ".join(result)

    return "NONE"


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: %s <register hex> <value hex>" % sys.argv[0])
        sys.exit(1)

    reg = int(sys.argv[1], 16)
    val = int(sys.argv[2], 16)

    print("Register %02x value %02x: %s:%s" %
          (reg, val, REGISTERS[reg]["name"], decode_reg_byte(reg, val)))
