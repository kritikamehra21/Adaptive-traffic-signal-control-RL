# reward.py
import traci

def calculate_reward(prev_wait_time, curr_wait_time):
    """
    Reward = reduction in total waiting time.
    Positive if waiting time decreased, negative otherwise.
    """
    reward = prev_wait_time - curr_wait_time
    return reward
