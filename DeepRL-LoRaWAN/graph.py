import matplotlib.pyplot as plt
import matplotlib.cm as cm
from device import *
import pickle
import os

# Node generation and Plot Function


def node_Gen(nrNodes, display):
    NODES = []
    x = []
    y = []
    rssi = []
    dist = []

    for i in range(nrNodes):
        device = Device(i)
        NODES.append(device)

        x.append(NODES[i].x)
        y.append(NODES[i].y)
        rssi.append(NODES[i].rssi)
        dist.append(NODES[i].dist)
    pickle.dump(NODES, open("data/nodes.p", "wb"))
    if display:
        fig, ax = plt.subplots()
        ax.plot(x, y, "ro")
        ax.plot(0, 0, "bo")
        for i in range(6):
            v1 = np.linspace((-RAY / 6) * (i + 1), (RAY / 6) * (i + 1), 100)
            v2 = np.linspace((-RAY / 6) * (i + 1), (RAY / 6) * (i + 1), 100)
            X, Y = np.meshgrid(v1, v2)
            F = X ** 2 + Y ** 2 - ((RAY / 6) * (i + 1)) ** 2

            ax.contour(X, Y, F, [0], colors="k", linestyles="dashed", linewidths=1)
        ax.set_aspect(1)
        plt.show()

    return NODES


# SF Allocation Display

# RA-Lora Plot
def SF_alloc_plot(sorted_nodes, exp, k, display=False, save=False):
    groups = []
    for s in range(7, 13):
        group = []
        posx = []
        posy = []
        for n in sorted_nodes:
            if n.sf == s:
                posx.append(n.x)
                posy.append(n.y)

        group.append(posx)
        group.append(posy)
        groups.append(group)
        group = []
    # print(groups)
    colors = ["ro", "go", "bo", "yo", "co", "mo"]
    # print(len(groups[3][0]))
    # print(len(groups[3][1]))
    fig, ax = plt.subplots()
    for g, c in zip(groups, colors):
        ax.plot(g[0], g[1], c)

    ax.plot(0, 0, "ko")

    for i in range(6):
        v1 = np.linspace((-RAY / 6) * (i + 1), (RAY / 6) * (i + 1), 100)
        v2 = np.linspace((-RAY / 6) * (i + 1), (RAY / 6) * (i + 1), 100)
        X, Y = np.meshgrid(v1, v2)
        F = X ** 2 + Y ** 2 - ((RAY / 6) * (i + 1)) ** 2

        ax.contour(X, Y, F, [0], colors="k", linestyles="dashed", linewidths=1)
    ax.set_aspect(1)
    if save:
        if not os.path.exists("reports/graphics/{}".format(exp)):
            os.mkdir("reports/graphics/{}".format(exp))
        plt.savefig("reports/graphics/{}/sf_alloc_{}".format(exp, k))
    if display:
        plt.show()
    plt.close()
