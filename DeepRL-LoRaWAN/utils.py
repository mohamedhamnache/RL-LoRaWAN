from config import config_dict
import numpy as np
from config import ch,tpx
import matplotlib.pyplot as plt

def SF_alloc_ch_utilization(NODES):
    sorted_nodes = []
    sorted_nodes = sorted(NODES, key=lambda x: x.dist, reverse=False)
    c_class = np.zeros(6, dtype=int)
    ch_len = len(ch)
    ch_u = np.zeros(ch_len, dtype=int)
    # print(c_class)
    for n in sorted_nodes:
        sf = n.sf
        # print(sf)
        config = config_dict[sf - 7]
        # print(config)
        for i in range(sf, 12):
            if n.snr < config["snr"] or n.rssi < config["sens"]:
                if n.sf < 12:
                    n.sf = n.sf + 1
                    n.packet.sf = n.sf
                    n.update_rectime(n.sf)
            config = config_dict[n.sf - 7]
        c_class[n.sf - 7] = c_class[n.sf - 7] + 1
        ch_index = ch.index(n.freq)
        ch_u[ch_index] = ch_u[ch_index] + 1
    return sorted_nodes, c_class, ch_u


def compute_sf_ch_utilization(nodes):
    sf_dist = np.zeros(6, dtype=int)
    tp_dist = np.zeros(5, dtype=int)
    ch_len = len(ch)
    ch_dist = np.zeros(ch_len, dtype=int)
    # print(ch_dist)
    # print(ch_len)
    # print_nodes(nodes)
    for n in nodes:
        sf = n.sf
        freq = n.freq
        tx = n.tx
        sf_dist[sf - 7] = sf_dist[sf - 7] + 1
        tp_index = tpx.index(tx)
        # print('index',tp_index)
        tp_dist[tp_index] = tp_dist[tp_index] + 1
    
        # print('Channel : ',freq)
        ch_index = ch.index(freq)
        # print('index',ch_index)
        ch_dist[ch_index] = ch_dist[ch_index] + 1
    return sf_dist,tp_dist, ch_dist

def energy_consumption(nodes):
    energy = (
                sum(
                    node.packet.rectime * TX[int(node.tx) + 2] * 3 * node.sent
                    for node in nodes
                )
                / 1e6
            )
    return energy

def print_nodes(nodes):
    for n in nodes:
        print("node_id: {} SF: {} TP: {} CH: {}".format(n.id, n.sf, n.tx, n.freq))
        
def reward_plot(rewards):
    plt.plot(rewards) 
    plt.show()
