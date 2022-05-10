import gym

from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common import make_vec_env
from stable_baselines import A2C

from environment import Environment

# Parallel environments
env = Environment()

model = A2C(MlpPolicy, env, verbose=1)
model.learn(total_timesteps=25000)


obs = env.reset()
while True:
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    env.render()