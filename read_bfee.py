import struct
import numpy as np
from ctypes import c_byte
import math


def dbinv(x):
    return np.power(10, x / 10)

def db(x):
    return 10 * math.log10(x)

'''
struct iwl5000_bfee_notif {
    uint8_t reserved;
    int8_t noiseA, noiseB, noiseC;
    uint16_t bfee_count;
    uint16_t reserved1;
    uint8_t Nrx, Ntx;
    uint8_t rssiA, rssiB, rssiC;
    int8_t noise;
    uint8_t agc, antenna_sel;
    uint16_t len;
    uint16_t fake_rate_n_flags;
    uint8_t payload[0];
} __attribute__ ((packed));
'''


class CSI:
    def __init__(self, raw_bytes=None):
        self.timestamp_low = None
        self.bfee_count = None
        self.Nrx = None
        self.Ntx = None
        self.rssi_a = None
        self.rssi_b = None
        self.rssi_c = None
        self.noise = None
        self.agc = None
        self.antenna_sel = None
        self.len = None
        self.fake_rate_n_flags = None
        self.calc_len = None
        self.payload = None
        if raw_bytes:
            self.read_bfee(raw_bytes)

    def read_bfee(self, raw_bytes):
        # print(len(raw_bytes))
        self.timestamp_low = raw_bytes[0] + (raw_bytes[1] << 8)\
            + (raw_bytes[2] << 16) + (raw_bytes[3] << 24)
        self.bfee_count = raw_bytes[4] + (raw_bytes[5] << 8)
        self.Nrx = raw_bytes[8]
        self.Ntx = raw_bytes[9]
        self.rssi_a = raw_bytes[10]
        self.rssi_b = raw_bytes[11]
        self.rssi_c = raw_bytes[12]
        self.noise = c_byte(raw_bytes[13]).value
        self.agc = raw_bytes[14]
        self.antenna_sel = raw_bytes[15]
        self.len = raw_bytes[16] + (raw_bytes[17] << 8)
        self.fake_rate_n_flags = raw_bytes[18] + (raw_bytes[19] << 8)
        self.calc_len = (30 * (self.Nrx * self.Ntx * 8 * 2 + 3) + 7) // 8

        payload = raw_bytes[20:]


        # Check that length matches what it should
        assert self.len == self.calc_len

        # Compute CSI from all this crap :)
        index = 0
        remainder = 0
        self.csi = []
        for i in range(30):
            index += 3
            remainder = index % 8
            for j in range(self.Ntx * self.Nrx):
                tmp_real = (payload[index // 8] >> remainder) |\
                (payload[index // 8 + 1] << (8 - remainder))
                # print(c_int8(tmp_real).value == c_byte(tmp_real).value)
                tmp_real = c_byte(tmp_real).value
                # print("%x %x %d"%(payload[index // 8], payload[index // 8 + 1], tmp_real))

                tmp_imag = (payload[index // 8 + 1] >> remainder) |\
                (payload[index // 8 + 2] << (8 - remainder))
                tmp_imag = c_byte(tmp_imag).value
                self.csi.append(complex(tmp_real, tmp_imag))
                index += 16
        self.perm = []
        # print(bin(self.antenna_sel))
        self.perm.append((self.antenna_sel & 0x3) + 1)
        self.perm.append((self.antenna_sel >> 2 & 0x3) + 1)
        self.perm.append((self.antenna_sel >> 4 & 0x3) + 1)
        self.csi = np.array(self.csi).\
            reshape((30, self.Nrx, self.Ntx)).transpose()
        # print(self.csi)
        self.csi[:, :] = self.csi[:, [idx - 1 for idx in self.perm]]
        # print(self.csi)

    def get_scaled_csi(self):
        csi = self.csi
        csi_sq = csi * np.conj(csi)
        csi_pwr = np.sum(csi_sq).real
        rssi_pwr = dbinv(self.get_total_rss())
        scale = rssi_pwr / (csi_pwr / 30)
        # print(scale)
        # print(self.noise)
        if self.noise == -127:
            noise_db = -92
        else:
            noise_db = self.noise
        thermal_noise_pwr = dbinv(noise_db)
        # print(thermal_noise_pwr)
        quant_error_pwr = scale * (self.Nrx * self.Ntx)
        # print(quant_error_pwr)

        total_noise_pwr = thermal_noise_pwr + quant_error_pwr

        ret = self.csi * math.sqrt(scale / total_noise_pwr)
        if self.Ntx == 2:
            ret *= math.sqrt(2)
        elif self.Ntx == 3:
            ret *= math.sqrt(dbinv(4.5))
        # print(ret)
        return ret

    def get_total_rss(self):
        rssi_mag = 0
        if self.rssi_a != 0:
            rssi_mag += dbinv(self.rssi_a)
        if self.rssi_b != 0:
            rssi_mag += dbinv(self.rssi_b)
        if self.rssi_c != 0:
            rssi_mag += dbinv(self.rssi_c)
        # print(rssi_mag)
        ret = db(rssi_mag) - 44 - self.agc
        # print(ret)
        return ret