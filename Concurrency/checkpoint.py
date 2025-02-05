import config
from Models.MuZero_torch_agent import MuZeroNetwork as TFTNetwork
from Models.Muzero_default_agent import MuZeroDefaultNetwork as DefaultNetwork


# TODO: Add description / inputs when doing unit testing on this object
"""
Description - 
Inputs      -
"""
class Checkpoint:
    def __init__(self, epoch, q_score):
        self.epoch = epoch
        self.q_score = q_score

    # TODO: Add description / outputs when doing unit testing on this method
    """
    Description - 
    Outputs     - 
    """
    def get_model(self):
        if config.CHAMP_DECIDER:
            model = DefaultNetwork()
        else:
            model = TFTNetwork()
        if self.epoch == 0:
            return model.get_weights()
        else:
            model.tft_load_model(self.epoch)
            return model.get_weights()

    # TODO: Add description / inputs when doing unit testing on this method
    """
    Description - 
    Inputs      - 
    """
    def update_q_score(self, episode, prob):
        if episode != 0:
            self.q_score = self.q_score - (0.01 / (episode * prob))
        else:
            self.q_score = self.q_score - 0.01 / prob
        # setting a lower limit, so it's possible that it will get sampled at some small number
        if self.q_score < 0.001:
            self.q_score = 0.001
