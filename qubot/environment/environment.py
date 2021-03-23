from random import choice
from typing import Callable, Tuple, Optional
from gym import spaces, Env as GymEnvironment
from sys import path
from os.path import join, dirname
path.append(join(dirname(__file__), '../..'))

from qubot.ui.ui_action import UIAction
from qubot.ui.ui_tree import UITree, UITreeNode
from qubot.stats.stats import Stats

class Environment(GymEnvironment):
    METADATA = {'render.modes': ['human']}

    STAT_STEP_COUNT = "step_count"
    STAT_REWARD_SUM = "reward_sum"

    def __init__(self, tree: UITree, reward_func: Callable[[UIAction, UITreeNode], int], step_limit=1000):
        super().__init__()
        self._tree = tree
        self.__reward_func = reward_func

        self._current_node = self._tree.get_root()
        self._stats = Stats(str(self.__class__))
        self._stats.empty_counter(Environment.STAT_STEP_COUNT)
        self._stats.empty_events(Environment.STAT_REWARD_SUM)

        self._tree.hash_tree()
        self._step_limit = step_limit
        self.__history = {}
        for node_hash in self._tree.get_hash():
            self.__history[node_hash] = {}

        # Actions are an embedding of nodes
        self.action_space = spaces.Discrete(tree.get_node_count())

        # Observe an embedding of nodes
        self.observation_space = spaces.Discrete(tree.get_node_count())

    def step(self, action_tuple: Tuple[Optional[UIAction], Optional[UITreeNode]]):
        action, next_node = action_tuple[0], action_tuple[1]

        # Increase overall step count
        self._stats.increment(Environment.STAT_STEP_COUNT)

        # Decrease reward every step
        reward = self.__get_reward(action, next_node)
        self._stats.increment(Environment.STAT_REWARD_SUM, reward)

        # We're done if the next node is None, we've hit a terminal node, we can't travel to any more nodes, or we've hit the step limit
        done = next_node is None or next_node.is_terminal() or (not next_node.get_children() and not next_node.get_parent()) or self._stats.get(Environment.STAT_STEP_COUNT) == self._step_limit

        # Record the next observation as an embedding
        if next_node is not None:
            self.__record_transition_in_history(self._current_node, next_node, action)
            self._current_node = next_node
        obs = self.get_state_embedding()

        return obs, reward, done, {}

    def get_state(self) -> UITreeNode:
        return self._current_node

    def get_state_embedding(self) -> int:
        return self._tree.get_node_embedding(self._current_node)

    def get_stats(self) -> Stats:
        return self._stats

    def get_next_explorative_transition_tuple(self) -> Tuple[Optional[UIAction], Optional[UITreeNode]]:
        """
        Returns a random transition tuple based on the current state.
        :return: A UIAction and UITreeNode in a tuple.
        """
        transition_tuples = self._current_node.get_transition_tuples()
        if transition_tuples:
            return choice(transition_tuples)
        return None, None

    def get_next_exploitative_transition_tuple(self) -> Tuple[Optional[UIAction], Optional[UITreeNode]]:
        """
        Returns an exploitative (most likely) transition tuple based on the current state.
        :return: A UIAction and UITreeNode in a tuple.
        """

        likely_action, likely_node = self.__get_likely_transition_tuple_from_history(self._current_node)
        if likely_action is None or likely_node is None:
            return self.get_next_explorative_transition_tuple()
        return likely_action, likely_node

    def reset(self):
        self._current_node = self._tree.get_root()
        self._stats.empty_counter(Environment.STAT_STEP_COUNT)
        self._stats.empty_counter(Environment.STAT_REWARD_SUM)
        self.__history = {}
        for node_hash in self._tree.get_hash():
            self.__history[node_hash] = {}
        return self._current_node

    def render(self, mode='human', close=False):
        print("Steps:          %d" % self._stats.get(Environment.STAT_STEP_COUNT))
        print("Current reward: %d" % self._stats.get(Environment.STAT_REWARD_SUM))

    def __get_reward(self, action: UIAction, node: UITreeNode):
        if action is None or node is None:
            return 0
        return self.__reward_func(action, node)

    def __record_transition_in_history(self, from_node: UITreeNode, to_node: UITreeNode, action: UIAction):
        if to_node.get_hash() not in self.__history[from_node.get_hash()]:
            self.__history[from_node.get_hash()][to_node.get_hash()] = [1, action, to_node]
        else:
            self.__history[from_node.get_hash()][to_node.get_hash()][0] += 1

    def __get_transition_from_history(self, from_node: UITreeNode, to_node: UITreeNode) -> Tuple[int, Optional[UIAction]]:
        if to_node.get_hash() not in self.__history[from_node.get_hash()]:
            return 0, None
        return self.__history[from_node.get_hash()][to_node.get_hash()][:2]

    def __get_likely_transition_tuple_from_history(self, from_node: UITreeNode) -> Tuple[Optional[UIAction], Optional[UITreeNode]]:
        if len(self.__history[from_node.get_hash()].keys()) == 0:
            return None, None
        max_transitions = 0
        max_action = None
        max_to_node = None
        for to_node_hash in self.__history[from_node.get_hash()]:
            num_transitions, action, to_node = self.__history[from_node.get_hash()][to_node_hash]
            if num_transitions > max_transitions:
                max_transitions = num_transitions
                max_action = action
                max_to_node = to_node
        return max_action, max_to_node
