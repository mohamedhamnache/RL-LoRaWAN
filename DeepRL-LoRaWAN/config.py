import numpy as np

# Config
# log-distance loss model parameters

PTX = 14.0
GAMMA = 2.08
D0 = 40.0
VAR = 0  # variance ignored for now
LPLD0 = 127.41

# Gate way localisation
BSX = 0.0
BSY = 0.0
HM = 1.0  # m
HB = 15.0  # m

RAY = 600.0

# Created Nodes
NODES = []

packetlen = 20


BW = 125
PL = 30
CR = 1

p = 60
# Inter-SF Thresshold Mateix

IS7 = np.array([6, -8, -9, -9, -9, -9])
IS8 = np.array([-11, 6, -11, -12, -13, -13])
IS9 = np.array([-15, -13, 6, -13, -14, -15])
IS10 = np.array([-19, -18, -17, 6, -17, -18])
IS11 = np.array([-22, -22, -21, -20, 6, -20])
IS12 = np.array([-25, -25, -25, -24, -23, 6])
SIR = np.array([IS7, IS8, IS9, IS10, IS11, IS12])


config_dict = {
    0: {"sf": 7, "sens": -126.5, "snr": -7.5},
    1: {"sf": 8, "sens": -127.25, "snr": -10},
    2: {"sf": 9, "sens": -131.25, "snr": -12.5},
    3: {"sf": 10, "sens": -132.75, "snr": -15},
    4: {"sf": 11, "sens": -133.25, "snr": -17.5},
    5: {"sf": 12, "sens": -134.5, "snr": -20},
}

ch = [868100000, 868300000, 868500000]
tpx = [2, 5, 8, 11, 14]
MODEL = 6
SEED = 913

rho_max = 0.4
tp_max = 14
tp_min = 2

N = 100
