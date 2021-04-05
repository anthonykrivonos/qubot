from enum import Enum
from sys import path
from os.path import join, dirname, abspath
path.append(abspath(join(dirname(__file__), '..')))

from qubot.ui.ui_action import UIAction
from qubot.ui.ui_tree import UITreeNode

LARGE_REWARD = 100
MEDIUM_REWARD = 10
SMALL_REWARD = 1
NO_REWARD = 0
SMALL_PENALTY = -1
MEDIUM_PENALTY = -10
LARGE_PENALTY = -100

def encourage_exploration(action: UIAction, node: UITreeNode):
    if node.is_terminal():
        return LARGE_PENALTY
    elif not node.get_children():
        return SMALL_PENALTY
    elif action == UIAction.LEFT_CLICK:
        return MEDIUM_REWARD
    return NO_REWARD

def discourage_exploration(action: UIAction, node: UITreeNode):
    if node.is_terminal():
        return LARGE_REWARD
    elif not node.get_children():
        return SMALL_PENALTY
    elif action == UIAction.LEFT_CLICK:
        return MEDIUM_REWARD
    return NO_REWARD

def heavily_encourage_exploration(action: UIAction, node: UITreeNode):
    if node.is_terminal():
        return SMALL_PENALTY
    elif not node.get_children():
        return SMALL_PENALTY
    elif action == UIAction.LEFT_CLICK:
        return LARGE_REWARD
    return SMALL_PENALTY

def heavily_discourage_exploration(action: UIAction, node: UITreeNode):
    if node.is_terminal():
        return SMALL_PENALTY
    elif not node.get_children():
        return SMALL_PENALTY
    elif action == UIAction.LEFT_CLICK:
        return LARGE_REWARD
    return SMALL_PENALTY

def reward_repeat_visits(action: UIAction, node: UITreeNode):
    if node.get_visits():
        return LARGE_REWARD
    return encourage_exploration(action, node)

def penalize_repeat_visits(action: UIAction, node: UITreeNode):
    if node.get_visits():
        return LARGE_PENALTY
    return encourage_exploration(action, node)

class QubotPresetRewardFunc(Enum):
    ENCOURAGE_EXPLORATION = encourage_exploration
    DISCOURAGE_EXPLORATION = discourage_exploration
    HEAVILY_ENCOURAGE_EXPLORATION = heavily_encourage_exploration
    HEAVILY_DISCOURAGE_EXPLORATION = heavily_discourage_exploration
    REWARD_REPEAT_VISITS = reward_repeat_visits
    PENALIZE_REPEAT_VISITS = penalize_repeat_visits

int_to_reward_func = {
    1: QubotPresetRewardFunc.ENCOURAGE_EXPLORATION,
    2: QubotPresetRewardFunc.DISCOURAGE_EXPLORATION,
    3: QubotPresetRewardFunc.HEAVILY_ENCOURAGE_EXPLORATION,
    4: QubotPresetRewardFunc.HEAVILY_DISCOURAGE_EXPLORATION,
    5: QubotPresetRewardFunc.REWARD_REPEAT_VISITS,
    6: QubotPresetRewardFunc.PENALIZE_REPEAT_VISITS,
}

str_to_reward_func = {
    "ENCOURAGE_EXPLORATION": QubotPresetRewardFunc.ENCOURAGE_EXPLORATION,
    "DISCOURAGE_EXPLORATION": QubotPresetRewardFunc.DISCOURAGE_EXPLORATION,
    "HEAVILY_ENCOURAGE_EXPLORATION": QubotPresetRewardFunc.HEAVILY_ENCOURAGE_EXPLORATION,
    "HEAVILY_DISCOURAGE_EXPLORATION": QubotPresetRewardFunc.HEAVILY_DISCOURAGE_EXPLORATION,
    "REWARD_REPEAT_VISITS": QubotPresetRewardFunc.REWARD_REPEAT_VISITS,
    "PENALIZE_REPEAT_VISITS": QubotPresetRewardFunc.PENALIZE_REPEAT_VISITS,
}
