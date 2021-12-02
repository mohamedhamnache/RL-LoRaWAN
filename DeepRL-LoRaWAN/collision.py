from config import SIR

### Collision Detection ################
"""

This Part Allows Collision Checking Between Two Packets :
 1- Timing Collision
 2- Frequency Collision
 3- SF Collision
 4- Capture Effect
 5- Imperfect SF Orthogonality
 
"""
########################### 1-Timining Collision #################


def timingCollision(env, p1, p2):
    Npream = 8
    Tpreamb = 2 ** p1.sf / (1.0 * p1.bw) * (Npream - 5)
    p2_end = p2.addTime + p2.rectime

    p1_cs = env.now + (Tpreamb / 1000.0)  # to sec

    """ print ("collision timing node {} ({},{},{}) node {} ({},{})".format(
        p1.nodeid, env.now - env.now, p1_cs - env.now, p1.rectime,
        p2.nodeid, p2.addTime - env.now, p2_end - env.now
    ))"""
    if p1_cs < p2_end:
        # p1 collided with p2 and lost
        # print ("not late enough")
        return True
    # print ("saved by the preamble")
    return False


######################### 2-Frequency Collision #######################
def frequencyCollision(p1, p2):
    if abs(p1.freq - p2.freq) <= 120 and (p1.bw == 500 or p2.freq == 500):
        # print ("frequency coll 500")
        return True
    elif abs(p1.freq - p2.freq) <= 60 and (p1.bw == 250 or p2.freq == 250):
        # print( "frequency coll 250")
        return True
    else:
        if abs(p1.freq - p2.freq) <= 30:
            # print ("frequency coll 125")
            return True
        # else:
    # print ("no frequency coll")
    return False


####################### 3- SF Collision ###############################
def sfCollision(p1, p2):
    if p1.sf == p2.sf:
        # print ("collision sf node {} and node {}".format(p1.nodeid, p2.nodeid))
        return True
    # print ("no sf collision")
    return False


####################### 4-5 ############################################
def powerCollision_2(p1, p2):
    # powerThreshold = 6
    # print ("SF: node {0.nodeid} {0.sf} node {1.nodeid} {1.sf}".format(p1, p2))
    # print ("pwr: node {0.nodeid} {0.rssi:3.2f} dBm node {1.nodeid} {1.rssi:3.2f} dBm; diff {2:3.2f} dBm".format(p1, p2, round(p1.rssi - p2.rssi,2)))

    if p1.sf == p2.sf:

        if abs(p1.rssi - p2.rssi) < 6:
            # print ("collision pwr both node {} and node {}".format(p1.nodeid, p2.nodeid))
            # packets are too close to each other, both collide
            # return both packets as casualties
            """print(
                "power coll  cap : freq 1 : {} and freq 2 :{} ==> |{}| < {}".format(
                    p1.freq, p2.freq, abs(p1.rssi - p2.rssi), SIR[p1.sf - 7][p2.sf - 7]
                )
            )"""
            return (p1, p2)
        elif p1.rssi - p2.rssi < 6:
            # p2 overpowered p1, return p1 as casualty
            # print ("collision pwr node {} overpowered node {}".format(p2.nodeid, p1.nodeid))
            # print ("capture - p2 wins, p1 lost")
            """print(
                "power coll  cap : freq 1 : {} and freq 2 :{}  => {} < {}".format(
                    p1.freq, p2.freq, p1.rssi - p2.rssi, SIR[p1.sf - 7][p2.sf - 7]
                )
            )"""
            return (p1,)
        # print ("capture - p1 wins, p2 lost")
        # p2 was the weaker packet, return it as a casualty
        """print(
            "power coll  cap : freq 1 : {} and freq 2 :{} => {} > {}".format(
                p1.freq, p2.freq, p1.rssi - p2.rssi, SIR[p1.sf - 7][p2.sf - 7]
            )
        )"""
        return (p2,)
    else:

        if p1.rssi - p2.rssi > SIR[p1.sf - 7][p2.sf - 7]:

            # print ("P1 is OK")
            if p2.rssi - p1.rssi > SIR[p2.sf - 7][p1.sf - 7]:
                # print ("p2 is OK")
                return ()
            else:
                # print ("p2 is lost")
                # print("power coll  Imp : 2")
                return (p2,)

        else:

            # print ("p1 is lost")
            if p2.rssi - p1.rssi > SIR[p2.sf - 7][p1.sf - 7]:

                # print ("p2 is OK")
                # print("power coll  Imp : 1")
                return (p1,)
            else:
                # print ("p2 is lost")
                # print("opwer coll  cap : 1")
                return (p1, p2)


######################## Check Collision ############################
def checkcollision(env, packet, packetsAtBS, maxBSReceives, full_collision):
    col = 0  # flag needed since there might be several collisions for packet
    processing = 0
    for i in range(0, len(packetsAtBS)):
        if packetsAtBS[i].packet.processed == 1:
            processing = processing + 1
    if processing > maxBSReceives:
        # print ("too long:", len(packetsAtBS))
        packet.processed = 0
    else:
        packet.processed = 1

    if packetsAtBS:
        # print ("CHECK node {} (sf:{} bw:{} freq:{:.6e}) others: {}".format(
        # packet.nodeid, packet.sf, packet.bw, packet.freq,
        # len(packetsAtBS)))
        # print(len(packetsAtBS))
        for other in packetsAtBS:

            if other.id != packet.nodeid:
                # print (">> node {} (sf:{} bw:{} freq:{:.6e})".format(
                # other.id, other.packet.sf, other.packet.bw, other.packet.freq))
                if full_collision == 1 or full_collision == 2:

                    if frequencyCollision(packet, other.packet) and timingCollision(
                        env, packet, other.packet
                    ):
                        # check who collides in the power domain
                        if full_collision == 1:
                            # Capture effect
                            c = powerCollision_2(packet, other.packet)
                        else:
                            # Capture + Non-orthognalitiy SFs effects
                            c = powerCollision_2(packet, other.packet)
                        # mark all the collided packets
                        # either this one, the other one, or both
                        for p in c:
                            p.collided = 1
                            if p == packet:
                                col = 1

                    else:
                        # no freq or timing collision, all fimone
                        pass
                else:
                    # simple collision
                    if frequencyCollision(packet, other.packet) and sfCollision(
                        packet, other.packet
                    ):
                        packet.collided = 1
                        other.packet.collided = (
                            1  # other also got lost, if it wasn't lost already
                        )
                        col = 1
        return col
    return 0
