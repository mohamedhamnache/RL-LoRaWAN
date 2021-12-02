from config import *


class Packet:
    def __init__(self, nodeid, sf, bw, freq, rssi, rectime):
        self.nodeid = nodeid
        self.pl = packetlen
        self.arriveTime = 0
        # Reception Parameters
        self.sf = sf
        self.bw = bw
        self.freq = freq
        self.rssi = rssi
        self.rectime = rectime
        self.collided = 0
        self.processed = 0
