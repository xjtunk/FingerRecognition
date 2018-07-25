#!/usr/bin/python3
from read_bfee import CSI

import socket
import numpy as np
sk = socket.socket()

sk.bind(('192.168.10.1', 8090))

sk.listen(1)
print('Connecting...')
while True:
    conn, addr = sk.accept()
    print('Connect Success!')
    while True:
        field_len = conn.recv(2)
        field_len = int.from_bytes(field_len, byteorder='big')

        code = conn.recv(1)
        code = int.from_bytes(code, byteorder='big')
        raw_bytes = conn.recv(field_len - 1)
        tmp_csi = CSI(raw_bytes)
        print(tmp_csi.csi.shape)
        print(tmp_csi.csi)
        print(np.conj(tmp_csi.csi))
