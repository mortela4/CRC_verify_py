# -*- coding: utf8 -*-

#
# CRC CCITT
#
# comes in 3 flavors
# (XModem)  starting value: 0x0000
#           starting value: 0xffff
#           starting value: 0x1d0f
#


from ctypes import c_ushort


class CRCCCITT(object):
    crc_ccitt_table = []

    # The CRC's are computed using polynomials.
    # Here is the most used coefficient for CRC CCITT
    crc_ccitt_constant = 0x1021

    def __init__(self, version='XModem'):
        try:
            dict_versions = {'XModem': 0x0000, 'FFFF': 0xffff, '1D0F': 0x1d0f}
            if version not in dict_versions.keys():
                raise Exception("Your version parameter should be one of \
                    the {} options".format("|".join(dict_versions.keys())))

            self.starting_value = dict_versions[version]

            # initialize the precalculated tables
            if len(self.crc_ccitt_table) == 0:
                self.init_crc_table()
        except Exception as e:
            print("EXCEPTION(__init__): {}".format(e))

    def calculate(self, input_data=None, debug=False):
        try:
            is_string = isinstance(input_data, str)
            is_bytes = isinstance(input_data, (bytes, bytearray))

            if not is_string and not is_bytes:
                raise Exception("Please provide a string or a byte sequence \
                    as argument for calculation.")

            crc_value = self.starting_value

            for j, c in enumerate(input_data):
                d = ord(c) if is_string else c
                tmp = ((crc_value >> 8) & 0xff) ^ d
                crc_value = ((crc_value << 8) & 0xff00) ^ self.crc_ccitt_table[tmp]
                if debug:
                    print("Byte %s: %s" % (j, hex(d)))

            return crc_value
        except Exception as e:
            print("EXCEPTION(calculate): {}".format(e))

    def calculate_endian(self, input_data=None, endian_ness='little', prev_value=None, debug=False):
        """ 
        Simple extension of 'calculate' for 
        accumulation and endianness-handling.
        TODO: combine these 3 methods into 1 - simplify & make pythonic!
        """
        if len(input_data) % 4 != 0:
            print("Cannot process input data - NOT a multiple of 4!")
            return None
        try:
            is_string = isinstance(input_data, str)
            is_bytes = isinstance(input_data, (bytes, bytearray))

            if not is_string and not is_bytes:
                raise Exception("Please provide a string or a byte sequence \
                    as argument for calculation.")

            if prev_value is None:
                crc_value = self.starting_value
            else:
                crc_value = prev_value

            if debug:
                print("CRC start-value = %d" % crc_value)

            # TODO: clean up - simplify this!
            # TODO: handle string-data also!
            num_bytes = 0
            for i in range(len(input_data)+1):
                if i % 4 == 0 and i > 0:
                    sub_arr = input_data[num_bytes:i]
                    uint32_val = int.from_bytes(sub_arr, byteorder=endian_ness, signed=False)
                    if debug:
                        print("Converting bytearr from idx=%s to idx=%s: %s --> intval=%s (%s)" %
                              (num_bytes, i, sub_arr, uint32_val, hex(uint32_val)))
                    for k in range(4):
                        byte_val = uint32_val & 0x000000FF
                        if debug:
                            print("byte_val: %s" % hex(byte_val))
                        tmp = ((crc_value >> 8) & 0xff) ^ byte_val
                        crc_value = ((crc_value << 8) & 0xff00) ^ self.crc_ccitt_table[tmp]
                        uint32_val >>= 8
                    num_bytes += 4
                    #
            #
            print("CRC: processed %s bytes (bytearr=%s)..." % (num_bytes, len(input_data)))
            return crc_value
        except Exception as e:
            print("EXCEPTION(calculate): {}".format(e))

    def init_crc_table(self):
        """The algorithm uses tables with precalculated values"""
        for i in range(0, 256):
            crc = 0
            c = i << 8

            for j in range(0, 8):
                if (crc ^ c) & 0x8000:
                    crc = c_ushort(crc << 1).value ^ self.crc_ccitt_constant
                else:
                    crc = c_ushort(crc << 1).value

                c = c_ushort(c << 1).value  # equivalent of c = c << 1

            self.crc_ccitt_table.append(crc)
