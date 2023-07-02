import ray
import config
import time
import numpy as np
from collections import deque
from sys import getsizeof



@ray.remote
class GlobalBuffer:
    def __init__(self, storage_ptr):
        self.gameplay_experiences = deque(maxlen=10000)
        self.batch_size = config.BATCH_SIZE
        self.storage_ptr = storage_ptr

    # Might be a bug with the action_batch not always having correct dims
    def sample_batch(self):
        # Returns: a batch of gameplay experiences without regard to which agent.
        obs_tensor_batch, action_history_batch, target_value_batch, policy_mask_batch = [], [], [], []
        target_reward_batch, target_policy_batch, value_mask_batch, reward_mask_batch = [], [], [], []
        sample_set_batch = []
        for gameplay_experience in range(self.batch_size):
            observation, action_history, value_mask, reward_mask, policy_mask, \
            value, reward, policy, sample_set = self.gameplay_experiences.popleft()
            obs_tensor_batch.append(observation)
            action_history_batch.append(action_history[1:])
            value_mask_batch.append(value_mask)
            reward_mask_batch.append(reward_mask)
            policy_mask_batch.append(policy_mask)
            target_value_batch.append(value)
            target_reward_batch.append(reward)
            target_policy_batch.append(policy)
            sample_set_batch.append(sample_set)

        observation_batch = np.squeeze(np.asarray(obs_tensor_batch))
        action_history_batch = np.asarray(action_history_batch)
        target_value_batch = np.asarray(target_value_batch).astype('float32')
        target_reward_batch = np.asarray(target_reward_batch).astype('float32')
        value_mask_batch = np.asarray(value_mask_batch).astype('float32')
        reward_mask_batch = np.asarray(reward_mask_batch).astype('float32')
        policy_mask_batch = np.asarray(policy_mask_batch).astype('float32')

        return [observation_batch, action_history_batch, value_mask_batch, reward_mask_batch, policy_mask_batch,
                target_value_batch, target_reward_batch, target_policy_batch, sample_set_batch]

    def store_replay_sequence(self, sample):
        # Records a single step of gameplay experience
        # First few are self-explanatory
        # done is boolean if game is done after taking said action
        self.gameplay_experiences.append(sample)
        return True

    def available_batch(self):
        queue_length = len(self.gameplay_experiences)
        if queue_length >= self.batch_size and not ray.get(self.storage_ptr.get_trainer_busy.remote()):
            self.storage_ptr.set_trainer_busy.remote(True)
            print("len of the queue {} with size {}".format(queue_length, getsizeof(self.gameplay_experiences)))
            return True
        time.sleep(5)
        return False
