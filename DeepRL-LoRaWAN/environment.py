import simpy
import numpy as np
import math
import gym
from gym import spaces

# from gym.spaces import Discrete, Box
import numpy as np
import random
from config import N, CR, PL, BW, p, ch

from config import rho_max, tp_max, tp_min, config_dict
from utils import compute_sf_ch_utilization


class Environment(gym.Env):
    def __init__(self, nodes, SF_dist_init, Ch_dist_init):

        """ Environment Parameter"""

        super(Environment, self).__init__()

        self.NODES = nodes
        self.N = len(self.NODES)
        self.TP_SET = [2, 5, 8, 11, 14]
        self.SF_SET = [7, 8, 9, 10, 11, 12]
        self.CH_SET = ["868.1", "868.3", "868.5"]
        self.ACTION_SPACE_GEN = self.action_space_generator()
        self.ACTION_SPACE_SIZE = len(self.ACTION_SPACE_GEN)
        self.STATE_SPACE = []
        self.SF_DIST = SF_dist_init
        self.ENERGY = 1
        self.CH_DIST = Ch_dist_init

        """ Simulation Parameters"""
        AVGSENDTIME = 100
        self.action_space = spaces.Box(
            np.array([0, 7, 0, 0]), np.array([self.N - 1, 12, 4, 2]), dtype=np.int32
        )
        # self.observation_space = spaces.Box(np.array([0,7,0,0,-10,-135]), np.array([N,12,4,2,10,-70]),dtype =np.int)
        self.observation_space = spaces.Box(
            np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
            np.array(
                [
                    self.N,
                    self.N,
                    self.N,
                    self.N,
                    self.N,
                    self.N,
                    self.N,
                    self.N,
                    self.N,
                    self.N,
                    self.N,
                    self.N,
                    self.N,
                    self.N,
                ]
            ),
            dtype=np.int32,
        )
        self.condition = 0

    def action_space_generator(self):
        action_space = []

        for n in range(self.N):

            for sf in self.SF_SET:

                for tp in range(len(self.TP_SET)):

                    for ch in range(len(self.CH_SET)):
                        action_space.append([n, sf, tp, ch])
        return action_space

    def toa(self, sf, cr, pl, bw):
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

    def rho_compute(self, sf, n):
        return (self.toa(sf, CR, PL, BW) * n) / p

    def reward_function(self, rho, u_ch, tp):
        return (rho_max) / (rho * u_ch) + ((tp_max - tp) / (tp_max - tp_min))

    def reward_function_zero(self, tp):
        return (tp_max - tp) / (tp_max - tp_min)

    def compute_der(self, sf_dist):
        der = 0
        for index in range(len(sf_dist)):
            rho = self.rho_compute(self.SF_SET[index], sf_dist[index])
            der_sf = math.exp(-2 * rho)
            der = der + (der_sf * sf_dist[index])
        return (der / self.N) * 100

    def reset(self):
        sf_dist, tp_dist, u_ch = compute_sf_ch_utilization(self.NODES)
        state = np.concatenate((sf_dist, tp_dist, u_ch))
        self.condition = 0
        return state

    def step(self, action):
        # print('Step : ',self.condition)
        # print('Action : ',action)
        # assert self.action_space.contains(action)
        reward = 0
        node = self.NODES[action[0]]
        old_sf = node.sf
        old_tp = node.tx
        old_ch = node.freq
        new_sf = action[1]
        new_tp = self.TP_SET[action[2]]
        new_ch = action[3]

        sf_dist, tp_dist, u_ch = compute_sf_ch_utilization(self.NODES)
        der = self.compute_der(sf_dist)
        #print("DER : ", der)
        config = config_dict[new_sf - 7]
        # print("config : ", config)
        rho = self.rho_compute(new_sf, sf_dist[new_sf - 7])
        # print('rho',rho)
        # print("node snr : {} rssi : {}".format(node.snr, node.rssi))
        # print("node old sf : {} new sf: {}".format(old_sf, new_sf))
        if node.snr < config["snr"] or node.rssi < config["sens"]:
            reward = -1

        else:

            if rho > 0 and u_ch[new_ch] > 0:
                reward = self.reward_function(rho, u_ch[new_ch], new_tp)
            else:
                reward = self.reward_function_zero(new_tp)

            self.NODES[action[0]].sf = new_sf
            self.NODES[action[0]].freq = ch[new_ch]
            self.NODES[action[0]].tx = new_tp

            sf_dist[old_sf - 7] = sf_dist[old_sf - 7] - 1
            sf_dist[new_sf - 7] = sf_dist[new_sf - 7] + 1

            old_tp_index = self.TP_SET.index(old_tp)
            new_tp_index = self.TP_SET.index(new_tp)
            tp_dist[old_tp_index] = tp_dist[old_tp_index] - 1
            tp_dist[new_tp_index] = tp_dist[new_tp_index] + 1

            old_ch_index = ch.index(old_ch)
            new_ch_index = new_ch
            u_ch[old_ch_index] = u_ch[old_ch_index] - 1
            u_ch[new_ch_index] = u_ch[new_ch_index] + 1
        # print(sf_dist)
        # print(tp_dist)
        # print(u_ch)

        # print('Reward = ',reward)
        new_state = np.concatenate((sf_dist, tp_dist, u_ch))
        # print('')
        done = False
        self.condition = self.condition + 1
        if self.condition == 100:
            done = True
        #if der > 95:
            #done = True

        info = ""

        return new_state, reward, done, info

    def render(self):
        pass

    def close(self):
        pass
