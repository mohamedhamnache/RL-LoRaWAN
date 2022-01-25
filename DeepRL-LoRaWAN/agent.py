from keras.models import Sequential
from keras.layers import Dense, Dropout, MaxPooling2D, Activation, Flatten
from collections import deque
import tensorflow as tf
from tensorflow import keras
import numpy as np
import random
from environment import Environment

from utils import SF_alloc_ch_utilization, print_nodes, reward_plot
from graph import node_Gen, SF_alloc_plot

nodes = node_Gen(100, display=False)
nodes, sf_distribution, ch_u = SF_alloc_ch_utilization(nodes)

train_episodes = 300
test_episodes = 100


class DQNAgent:
    def create_model(self, action_shape, state_shape):
        model = Sequential()
        learning_rate = 0.001
        init = tf.keras.initializers.HeUniform()

        model.add(
            Dense(
                14, input_shape=state_shape, activation="relu", kernel_initializer=init
            )
        )
        model.add(Dense(28, activation="relu", kernel_initializer=init))

        model.add(Dense(90 * 100, activation="linear", kernel_initializer=init))

        model.compile(
            loss=tf.keras.losses.Huber(),
            optimizer=tf.keras.optimizers.Adam(lr=learning_rate),
            metrics=["accuracy"],
        )
        return model

    def get_qs(self, model, state, step):
        return model.predict(state.reshape([1, state.shape[0]]))[0]

    def train(self, env, replay_memory, model, target_model, done):
        learning_rate = 0.7  # Learning rate
        discount_factor = 0.618

        MIN_REPLAY_SIZE = 1000
        if len(replay_memory) < MIN_REPLAY_SIZE:
            return

        batch_size = 64 * 2
        mini_batch = random.sample(replay_memory, batch_size)
        # print(len(mini_batch))
        # print(mini_batch)

        # current_states = np.array([transition[0] for transition in mini_batch],dtype=object)
        # print()
        current_states = np.array(
            np.array(
                [
                    transition[0]
                    for transition in mini_batch
                    if transition[0] is not None
                ]
            )
        )
        # print('states len : ',len(current_states))
        # current_states= np.array(current_states).astype("float32")
        # print(current_states)
        # current_states = np.asarray(current_states).astype(np.float32)
        current_qs_list = model.predict(current_states)
        # print(current_qs_list)
        # print('Current: ',len(current_qs_list))
        # print('Mini batch : ',len(mini_batch))
        new_current_states = np.array(
            [transition[3] for transition in mini_batch if transition[3] is not None]
        )
        future_qs_list = target_model.predict(new_current_states)
        # print()

        X = []
        Y = []
        for index, (observation, action, reward, new_observation, done) in enumerate(
            mini_batch
        ):
            if not done:
                max_future_q = reward + discount_factor * np.max(future_qs_list[index])
            else:
                max_future_q = reward

            current_qs = current_qs_list[index]
            # print('The current_qs : ',current_qs)
            # print('action : ',action)

            current_qs[index] = (1 - learning_rate) * current_qs[
                index
            ] + learning_rate * max_future_q

            X.append(observation)
            Y.append(current_qs)
        model.fit(
            np.array(X), np.array(Y), batch_size=batch_size, verbose=0, shuffle=True
        )


env = Environment(nodes, sf_distribution, ch_u)


agent = DQNAgent()


# agent.train()


def main():
    epsilon = 1  # Epsilon-greedy algorithm in initialized at 1 meaning every step is random at the start
    max_epsilon = 1  # You can't explore more than 100% of the time
    min_epsilon = 0.01  # At a minimum, we'll always explore 1% of the time
    decay = 0.01
    final_rewards = []
    # 1. Initialize the Target and Main models
    # Main Model (updated every 4 steps)
    print(env.observation_space.shape)
    print(env.action_space.shape)
    print_nodes(nodes)
    #SF_alloc_plot(nodes,10,5,display=True)
    model = agent.create_model(env.action_space.shape, env.observation_space.shape)
    print("Model Created !")
    # Target Model (updated every 100 steps)
    target_model = agent.create_model(
        env.action_space.shape, env.observation_space.shape
    )
    print("Target Model Created !")
    target_model.set_weights(model.get_weights())

    replay_memory = deque(maxlen=50_000)

    target_update_counter = 0

    # X = states, y = actions
    X = []
    y = []

    steps_to_update_target_model = 0

    for episode in range(train_episodes):
        print('Episode : ',episode)
        total_training_rewards = 0
        observation = env.reset()
        done = False
        while not done:
            steps_to_update_target_model += 1
            # if True:
            # env.render()

            random_number = np.random.rand()
            # 2. Explore using the Epsilon Greedy Exploration Strategy
            if random_number <= epsilon:
                # Explore
                # print('Explore')
                action = env.action_space.sample()
            else:

                # Exploit best known action
                # model dims are (batch, env.observation_space.n)
                # print('Exploit')
                encoded = observation
                encoded_reshaped = encoded.reshape([1, encoded.shape[0]])
                # print('model : ',model)
                # print('Encoded state : ',encoded_reshaped)
                predicted = model.predict(encoded_reshaped)
                action = np.argmax(predicted)
                action = env.ACTION_SPACE_GEN[action]
            new_observation, reward, done, info = env.step(action)
            replay_memory.append([observation, action, reward, new_observation, done])

            # 3. Update the Main Network using the Bellman Equation
            if steps_to_update_target_model % 4 == 0 or done:
                agent.train(env, replay_memory, model, target_model, done)

            observation = new_observation
            total_training_rewards += reward

            if done:
                print(
                    "Total training rewards: {} after n steps = {} with final reward = {}".format(
                        total_training_rewards, episode, reward
                    )
                )
                final_rewards.append(total_training_rewards)
                total_training_rewards += 1

                if steps_to_update_target_model >= 100:
                    print("Copying main network weights to the target network weights")
                    target_model.set_weights(model.get_weights())
                    steps_to_update_target_model = 0
                break

        epsilon = min_epsilon + (max_epsilon - min_epsilon) * np.exp(-decay * episode)
        #SF_alloc_plot(nodes,10,5,display=True)
    env.close()
    print_nodes(env.NODES)
    print(final_rewards)


if __name__ == "__main__":
    main()
