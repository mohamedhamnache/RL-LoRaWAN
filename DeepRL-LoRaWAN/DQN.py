import gym

from stable_baselines3 import A2C

from environment import Environment
from utils import SF_alloc_ch_utilization, print_nodes, reward_plot
from graph import node_Gen, SF_alloc_plot


nodes = node_Gen(10, display=False)
nodes, sf_distribution, ch_u = SF_alloc_ch_utilization(nodes)

env = Environment(nodes, sf_distribution, ch_u)

model = A2C("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=25000)
model.save("a2c_cartpole")

del model # remove to demonstrate saving and loading

model = A2C.load("a2c_cartpole")

obs = env.reset()
while True:
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    