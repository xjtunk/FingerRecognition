#!/usr/bin/python3
from read_bfee import CSI

import socket
import numpy as np
import threading
import time
import sys
import signal


class DataCollector(threading.Thread):
    """docstring for DataCollector"""
    def __init__(self, host, port):
        super(DataCollector, self).__init__()
        self.host = host
        self.port = port
        self.status = 'closed'
        self.csi = []

    def connect(self):
        self.sk = socket.socket()
        self.sk.bind((self.host, self.port))

        print("DataCollector running in (%s, %s)" % (self.host, self.port))
        
        self.sk.listen(1)
        self.conn, _ = self.sk.accept()
        
        print("Connect success!")


    def run(self):
        self.connect()
        while True:
            field_len = self.conn.recv(2)
            field_len = int.from_bytes(field_len, byteorder='big')

            code = self.conn.recv(1)
            code = int.from_bytes(code, byteorder='big')
            raw_bytes = self.conn.recv(field_len - 1)
            tmp_csi = CSI(raw_bytes).get_scaled_csi()
            # print(tmp_csi.shape)
            # print(tmp_csi)
            self.csi.append(tmp_csi)


def quit(signum, frame):
    print("\nExit\n")
    sys.exit()


if __name__ == '__main__':
    try:
        signal.signal(signal.SIGINT, quit)
        signal.signal(signal.SIGTERM, quit)
        collector = DataCollector('192.168.10.1', 8090)
        # collector.collect()
        collector.setDaemon(True)
        collector.start()

        while True:
            time.sleep(1)
            print(len(collector.csi))
    except Exception as e:
        # print(e)
        sys.exit()


        