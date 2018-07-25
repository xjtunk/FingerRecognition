#!/usr/bin/python3
import struct
from read_bfee import CSI

def read_bf_file(filename):
    try:
        infile = open(filename, 'rb')
    except Exception as e:
        print(e)
        return

    tolen = infile.seek(0, 2)
    # print(tolen)
    infile.seek(0, 0)

    # Holds the return values
    ret = []

    # Current offset into file
    cur = 0

    # Number of records output
    count = 0

    # Flag marking whether we've encountered a broken CSI yet
    broken_perm = 0

    # What perm should sum to for 1,2,3 antennas
    triangle = [1, 3, 6]

    raw_csi = []
    while cur < tolen - 3:
        field_len = struct.unpack('!h', infile.read(2))[0]
        # print(type(field_len), field_len)
        code = struct.unpack('>B', infile.read(1))[0]
        # print(code, int(code))

        cur += 3

        # If unhandled code, skip (seek over) the record and continue
        if code == 187:
            raw_bytes = infile.read(field_len - 1)
            # print(type(raw_bytes))
            cur += (field_len - 1)
            # print(len(raw_bytes), field_len)
            if len(raw_bytes) != field_len - 1:
                infile.close()
                return
        else:
            infile.seek(field_len - 1, 1)
            cur += (field_len - 1)
            continue

        # hex2dec('bb')) Beamforming matrix -- output a record
        if code == 187:
            count += 1
            # read_bfee(raw_bytes)
            csi = CSI(raw_bytes)
            # print(csi.__dict__)
            raw_csi.append(csi)
            csi.get_scaled_csi()
            break


    print(len(raw_csi))
    infile.close()


if __name__ == '__main__':
    read_bf_file('test.dat')
