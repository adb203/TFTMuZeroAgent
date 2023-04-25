import numpy as np
import config
import ray
from Models.replay_muzero_buffer import ReplayBuffer
from sklearn import preprocessing


class BufferWrapper:
    def __init__(self, global_buffer):
        self.buffers = {"player_" + str(i): ReplayBuffer(global_buffer) for i in range(config.NUM_PLAYERS)}

    def reset(self):
        for key in self.buffers.keys():
            self.buffers[key].reset()
    
    def store_replay_buffer(self, key, *args):
        self.buffers[key].store_replay_buffer(args[0], args[1], args[2], args[3], args[4])

    def get_prev_action(self, key):
        self.buffers[key].get_prev_action()
    
    def get_reward_sequence(self, key):
        self.buffers[key].get_reward_sequence()
    
    def set_reward_sequence(self, key, *args):
        self.buffers[key].set_reward_sequence(args[0])

    def rewardNorm(self):
        reward_dat = []
        rewardLens = []

        for b in self.buffers.values():
            # clip rewards to prevent outliers from skewing results
            rewards = b.get_reward_sequence()
            rewards = np.clip(rewards, -3, 3)
            # store length of array to allocate elements later after normalization
            rewardLens.append(len(rewards))
            reward_dat.append(rewards)

        # reshape array of arrays of rewards to a single array
        # this reshaping should leave data from each reward array in order
        reward_dat = np.array(reward_dat, dtype=object)
        reward_dat = np.hstack(reward_dat)
        # normalize the values from this array w/ sklearn
        reward_dat = preprocessing.scale(reward_dat)
        # reassign normalized values back into original arrays
        index = 0
        for i, b in enumerate(self.buffers.values()):
            b.set_reward_sequence(reward_dat[index: index + rewardLens[i]])
            index += rewardLens[i]
    
    def store_global_buffer(self):
        max_lenght = 0
        for b in self.buffers.values():
            max_lenght = max(max_lenght, b.get_len())
        for b in self.buffers.values():
            b.store_global_buffer(max_lenght)
    