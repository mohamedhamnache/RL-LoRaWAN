from graph import node_Gen
from environment import Environment
from utils import SF_alloc_ch_utilization, print_nodes

nodes = node_Gen(5, display=False)
nodes, sf_distribution, ch_u = SF_alloc_ch_utilization(nodes)

print("SF Utilization: ", sf_distribution)
print("Channel Utilization: ", ch_u)

print_nodes(nodes)
env = Environment(nodes, sf_distribution, ch_u)

done = False

i = 0
while i < 5:
    action = env.action_space.sample()
    print("Action {} : {}".format(i, action))
    state, reward, done, info = env.step(action)
    print("Reward {} : {}".format(i, reward))
    i = i + 1
