from config import *
from packet import *
import random
import math

random.seed(SEED)


class Device:
    def __init__(self, id):
        self.id = id
        self.x = 0
        self.y = 0
        self.dist = 0
        found = False
        while not found:
            a = random.random()
            b = random.random()
            if b < a:
                a, b = b, a
            posx = b * RAY * math.cos(2 * math.pi * a / b) + BSX
            posy = b * RAY * math.sin(2 * math.pi * a / b) + BSY
            if len(NODES) > 0:
                for index, n in enumerate(NODES):
                    dist = np.sqrt(((abs(n.x - posx)) ** 2) + ((abs(n.y - posy)) ** 2))
                    if dist >= 20:
                        found = 1
                        self.x = posx
                        self.y = posy
                        break
            else:
                self.x = posx
                self.y = posy
                found = True

        dist_2d = np.sqrt(
            (self.x - BSX) * (self.x - BSX) + (self.y - BSY) * (self.y - BSY)
        )
        # self.dist = np.sqrt((dist_2d)**2+(HB-HM)**2)
        self.dist = dist_2d
        # Radio Parameters
        self.bw = BW
        self.sf = 7
        self.tx = PTX
        self.cr = 1
        self.freq = random.choice(ch)
        # self.freq = 868100000
        self.rssi = self.tx - self.estimatePathLoss(MODEL)
        self.snr = random.randrange(-10, 20)
        self.rectime = self.airtime(self.sf, self.cr, packetlen, BW)
        self.packet = Packet(
            self.id, self.sf, self.bw, self.freq, self.rssi, self.rectime
        )
        self.sent = 0
        self.received = 0

    def airtime(self, sf, cr, pl, bw):
        H = 0  # implicit header disabled (H=0) or not (H=1)
        DE = 0  # low data rate optimization enabled (=1) or not (=0)
        Npream = 8  # number of preamble symbol (12.25  from Utz paper)

        if bw == 125 and sf in [11, 12]:
            # low data rate optimization mandated for BW125 with SF11 and SF12
            DE = 1
        if sf == 6:
            # can only have implicit header with SF6
            H = 1
        Tsym = (2.0 ** sf) / bw  # msec
        Tpream = (Npream + 4.25) * Tsym
        # print "sf", sf, " cr", cr, "pl", pl, "bw", bw
        payloadSymbNB = 8 + max(
            math.ceil((8.0 * pl - 4.0 * sf + 28 + 16 - 20 * H) / (4.0 * (sf - 2 * DE)))
            * (cr + 4),
            0,
        )
        Tpayload = payloadSymbNB * Tsym
        return (Tpream + Tpayload) / 1000.0  # in seconds

    def log_distance_loss(self, dist):
        Lpl = LPLD0 + 10 * GAMMA * math.log10(dist / D0)
        rssi = PTX - Lpl
        return rssi

    def update_rectime(self, sf):
        self.rectime = self.airtime(sf, self.cr, packetlen, BW)
        self.packet.rectime = self.rectime

    def estimatePathLoss(self, model):
        # Log-Distance model
        if model == 0:
            Lpl = LPLD0 + 10 * GAMMA * math.log10(self.dist / D0)

        # Okumura-Hata model
        elif model >= 1 and model <= 4:
            # small and medium-size cities
            if model == 1:
                ahm = (
                    1.1 * (math.log10(self.freq) - math.log10(1000000)) - 0.7
                ) * HM - (1.56 * (math.log10(self.freq) - math.log10(1000000)) - 0.8)

                C = 0
            # metropolitan areas
            elif model == 2:
                if self.freq <= 200000000:
                    ahm = 8.29 * ((math.log10(1.54 * HM)) ** 2) - 1.1
                elif self.freq >= 400000000:
                    ahm = 3.2 * ((math.log10(11.75 * HM)) ** 2) - 4.97
                C = 0
            # suburban enviroments
            elif model == 3:
                ahm = (
                    1.1 * (math.log10(self.freq) - math.log10(1000000)) - 0.7
                ) * HM - (1.56 * (math.log10(self.freq) - math.log10(1000000)) - 0.8)

                C = -2 * ((math.log10(self.freq) - math.log10(28000000)) ** 2) - 5.4
            # rural area
            elif model == 4:
                ahm = (
                    1.1 * (math.log10(self.freq) - math.log10(1000000)) - 0.7
                ) * HM - (1.56 * (math.log10(self.freq) - math.log10(1000000)) - 0.8)

                C = (
                    -4.78 * ((math.log10(self.freq) - math.log10(1000000)) ** 2)
                    + 18.33 * (math.log10(self.freq) - math.log10(1000000))
                    - 40.98
                )

            A = (
                69.55
                + 26.16 * (math.log10(self.freq) - math.log10(1000000))
                - 13.82 * math.log(HB)
                - ahm
            )

            B = 44.9 - 6.55 * math.log10(HB)

            Lpl = A + B * (math.log10(self.dist) - math.log10(1000)) + C

        # 3GPP model
        elif model >= 5 and model < 7:
            # Suburban Macro
            if model == 5:
                C = 0  # dB
            # Urban Macro
            elif model == 6:
                C = 3  # dB

            Lpl = (
                (44.9 - 6.55 * math.log10(HB))
                * (math.log10(self.dist) - math.log10(1000))
                + 45.5
                + (35.46 - 1.1 * HM) * (math.log10(self.freq) - math.log10(1000000))
                - 13.82 * math.log10(HM)
                + 0.7 * HM
                + C
            )

        # Polynomial 3rd degree
        elif model == 7:
            p1 = -5.491e-06
            p2 = 0.002936
            p3 = -0.5004
            p4 = -70.57

            Lpl = (
                p1 * math.pow(self.dist, 3)
                + p2 * math.pow(self.dist, 2)
                + p3 * self.dist
                + p4
            )

        # Polynomial 6th degree
        elif model == 8:
            p1 = 3.69e-12
            p2 = 5.997e-11
            p3 = -1.381e-06
            p4 = 0.0005134
            p5 = -0.07318
            p6 = 4.254
            p7 = -171

            Lpl = (
                p1 * math.pow(self.dist, 6)
                + p2 * math.pow(self.dist, 5)
                + p3 * math.pow(self.dist, 4)
                + p4 * math.pow(self.dist, 3)
                + p5 * math.pow(self.dist, 2)
                + p6 * self.dist
                + p7
            )

        return Lpl
