# -*- coding: utf8 -*-

import CRCCCITT


# NOTE: the bytestring should be modulo 4!
test_data_A = "abcdefghij0123456789klmnopqrstuvwxyz"


def calculate_CRC(hex_data):
    """ 
    Takes HEX-string directly, then decodes it to bytes
    TODO: exception-handling (and/or input evaluation - string length must be multiple of 2 etc.) 
    """
    raw_bytes = bytes(bytearray.fromhex(hex_data))
    chk_sum = CRCCCITT().calculate(raw_bytes)
    return chk_sum


def asciihex_to_binary(char_arr):
    if len(char_arr) % 2 != 0:
        print("Cannot convert! Must be multiple of 2 ...")
        return None
    byteArr = bytearray()
    i = 0
    subStr = ""
    for char_val in char_arr:
        subStr += char_val
        i += 1
        if i > 0 and i % 2 == 0:
            bin_val = int(subStr, 16)
            byteArr.append(bin_val)
            subStr = ""
    return byteArr


def calculate_file_crc(fp):
    lines = fp.readlines()
    #
    allBytes = bytearray()
    for line in lines:
        raw_data = line.strip()
        if raw_data.startswith('S2'):
            charData = raw_data[10:-2]
            binData = asciihex_to_binary(charData)
            for binVal in binData:
                allBytes.append(binVal)
    #
    crc = CRCCCITT.CRCCCITT().calculate(allBytes)
    return crc, allBytes


def calculate_file_crc2(fp):
    lines = fp.readlines()
    #
    crc = 0x0000
    allBytes = bytearray()
    i = 0
    for line in lines:
        raw_data = line.strip()
        if raw_data.startswith('S2'):
            charData = raw_data[10:-2]
            binData = bytearray.fromhex(charData)
            if i == 0:
                print("Raw data: ", charData)
                print("DATA line0: %s" % binData)
            allBytes += binData
            #
        i += 1
    #
    crc = CRCCCITT.CRCCCITT().calculate(allBytes)
    return crc, allBytes


def calculate_file_crc3(fp):
    lines = fp.readlines()
    #
    allBytes = bytearray()
    for line in lines:
        raw_data = line.strip()
        if raw_data.startswith('S2'):
            charData = raw_data[10:-2]
            binData = asciihex_to_binary(charData)
            for binVal in binData:
                allBytes.append(binVal)
    #
    crc = CRCCCITT.CRCCCITT().calculate_endian(allBytes)
    return crc, allBytes


# **************************************************
if __name__=="__main__":
    #
    byteArr = bytearray()

    for num, charVal in enumerate(test_data_A):
        val = ord(charVal)
        # print("Value no.%s: %s" % (num, val))
        byteArr.append(val)

    crc1 = CRCCCITT.CRCCCITT().calculate(test_data_A)
    crc2 = CRCCCITT.CRCCCITT().calculate(byteArr, debug=True)

    crc3 = bytearray()
    crc3val = 0
    for data in test_data_A:
        crc3.append(ord(data))
        val = CRCCCITT.CRCCCITT().calculate(crc3)
        crc3.clear()
        crc3val = val

    crc4 = CRCCCITT.CRCCCITT().calculate_endian(byteArr, debug=True)

    print("CRC1 computed: %s (as hex: %s)" % (crc1, hex(crc1)))
    print("CRC2 computed: %s (as hex: %s)" % (crc2, hex(crc2)))
    print("CRC3 computed: %s (as hex: %s)" % (crc3val, hex(crc3val)))
    print("CRC4 computed: %s (as hex: %s)" % (crc4, hex(crc4)))

    # Full test with SREC FW-file:
    rfp = open("IrrigationSensorAppl_FW1.srec", 'r')
    crc5, allData1 = calculate_file_crc(rfp)
    rfp.seek(0)
    crc6, allData2 = calculate_file_crc2(rfp)
    rfp.seek(0)
    crc7, allData3 = calculate_file_crc3(rfp)

    rfp.close()

    if allData1 != allData2 or allData1 != allData3:
        print("WARN: binary data differs!")
    else:
        print("INFO: binary data equal ...")
    #
    wfp = open("IrrigationSensorAppl_FW1.bin", 'wb')
    wfp.write(allData1)
    wfp.close()

    print("CRC5 computed from file: %s (as hex: %s)" % (crc5, hex(crc5)))
    print("CRC6 computed from file: %s (as hex: %s)" % (crc6, hex(crc6)))
    print("CRC7 computed from file: %s (as hex: %s)" % (crc7, hex(crc7)))

    print("Test FINISH!")



