from enum import Enum
from sys import path
from os.path import join, dirname, abspath
path.append(abspath(join(dirname(__file__), '..')))

from qubot.ui.ui_action import UIAction
from qubot.ui.ui_tree import UITreeNode

LARGE_REWARD = 10
MEDIUM_REWARD = 5
SMALL_REWARD = 1
NO_REWARD = 0
SMALL_PENALTY = -1
MEDIUM_PENALTY = -5
LARGE_PENALTY = -10

def encourage_exploration(action: UIAction, node: UITreeNode):
    if node.is_terminal():
        return LARGE_PENALTY
    elif not node.get_children():
        return NO_REWARD
    elif action == UIAction.LEFT_CLICK:
        return MEDIUM_REWARD
    return NO_REWARD

def discourage_exploration(action: UIAction, node: UITreeNode):
    if node.is_terminal():
        return LARGE_REWARD
    elif not node.get_children():
        return NO_REWARD
    elif action == UIAction.LEFT_CLICK:
        return SMALL_REWARD
    return NO_REWARD

def penalize_repeat_visits(action: UIAction, node: UITreeNode):
    if node.get_visits():
        return LARGE_PENALTY
    return encourage_exploration(action, node)

class QubotPresetRewardFunc(Enum):
    ENCOURAGE_EXPLORATION = encourage_exploration
    DISCOURAGE_EXPLORATION = discourage_exploration
    PENALIZE_REPEAT_VISITS = penalize_repeat_visits

int_to_reward_func = {
    1: QubotPresetRewardFunc.ENCOURAGE_EXPLORATION,
    2: QubotPresetRewardFunc.DISCOURAGE_EXPLORATION,
    3: QubotPresetRewardFunc.PENALIZE_REPEAT_VISITS,
}

str_to_reward_func = {
    "ENCOURAGE_EXPLORATION": QubotPresetRewardFunc.ENCOURAGE_EXPLORATION,
    "DISCOURAGE_EXPLORATION": QubotPresetRewardFunc.DISCOURAGE_EXPLORATION,
    "PENALIZE_REPEAT_VISITS": QubotPresetRewardFunc.PENALIZE_REPEAT_VISITS,
}
