import numpy as np
from random import uniform, choice

from typing import Callable, List, Tuple, Optional

from qubot.ui import UIAction, UITree, UITreeNode
from .environment import Environment


class QLearningEnvironment(Environment):
    EPSILON_RANGE = (0.01, 1.0)

    def __init__(self, tree: UITree, reward_func: Callable[[UIAction, UITreeNode], int], alpha: float, gamma: float,
                 epsilon: float, decay: float = 0.1, step_limit=1000):
        super().__init__(tree, reward_func, step_limit)
        self.__alpha = alpha
        self.__gamma = gamma
        self.__original_epsilon = epsilon
        self.__epsilon = epsilon
        self.__decay = decay
        self.__Q = np.zeros((self.observation_space.n, self.action_space.n))
        self.__training_rewards = []
        self.__epsilon_history = []
        self.__testing_rewards = []
        self.__testing_penalties = []

    def train(self, episode_count: int):
        print("Training on %d episodes..." % episode_count)
        total_training_rewards = 0
        for episode in range(episode_count):
            self.__soft_reset()
            for step in range(self._step_limit):
                state_embedding = self.get_state_embedding()
                action, node_action = self.__get_next_transition()

                new_state_embedding, reward, done, info = self.step((action, node_action))

                total_training_rewards += reward

                if action is not None:
                    action_embedding = self._tree.get_node_embedding(node_action)
                    self.__Q[state_embedding, action_embedding]\
                        += self.__alpha * (reward + self.__gamma * np.max(self.__Q[new_state_embedding]) - self.__Q[state_embedding, action_embedding])

                if done or step == self._step_limit - 1:
                    self.__update_epsilon(episode)

                    self.__training_rewards.append(total_training_rewards)
                    self.__epsilon_history.append(self.__epsilon)

                    break
        print("Training done.")

    def test(self, episode_count: int):
        print("Testing on %d episodes..." % episode_count)
        total_testing_rewards = 0
        total_testing_penalty = 0
        for episode in range(episode_count):
            self.__soft_reset()

            for step in range(self._step_limit):
                action, node_action = self.__get_next_transition()

                new_state_embedding, reward, done, info = self.step((action, node_action))

                # Record reward
                total_testing_rewards += reward
                # Record penalty
                if reward < 0:
                    total_testing_penalty += 1

                if done or step == self._step_limit - 1:
                    # print("E%8d: (reward: %d, penalty: %d, # steps: %d)" % (episode + 1, total_testing_rewards, total_testing_penalty, step + 1))
                    self.__testing_rewards.append(total_testing_rewards)
                    self.__testing_penalties.append(total_testing_penalty)

                    break
        print("Testing done.")

    def render(self, mode='human', close=False):
        print("=============================")
        print("Q-learning agent")
        print("=============================")
        print("Steps:                 % 6d" % self._step_count)
        print("Alpha:                % 1.4f" % self.__alpha)
        print("Gamma:                % 1.4f" % self.__gamma)
        print("Original epsilon:     % 1.4f" % self.__original_epsilon)
        print("Current epsilon:      % 1.4f" % self.__epsilon)
        print("Decay:                % 1.4f" % self.__decay)
        print("Training rewards:      % 6d" % sum(self.__training_rewards))
        print("Training score:       % 1.4f" % (0 if not self.__training_rewards else float(sum(self.__training_rewards) / len(self.__training_rewards))))
        print("Testing rewards:       % 6d" % sum(self.__testing_rewards))
        print("Testing score:        % 1.4f" % (0 if not self.__testing_rewards else float(sum(self.__testing_rewards) / len(self.__testing_rewards))))
        print("Testing penalties:     % 6d" % sum(self.__testing_penalties))
        print("Testing penalty rate: % 1.4f" % (0 if not self.__testing_penalties else float(sum(self.__testing_penalties) / len(self.__testing_penalties))))

    def reset(self):
        self.__training_rewards = []
        self.__epsilon_history = []
        self.__testing_rewards = []
        self.__testing_penalties = []
        self.__epsilon = self.__original_epsilon
        return super().reset()

    def get_training_rewards_history(self) -> List[int]:
        return self.__training_rewards

    def get_testing_rewards_history(self) -> List[int]:
        return self.__testing_rewards

    def get_testing_penalties_history(self) -> List[int]:
        return self.__testing_penalties

    def get_epsilon_history(self) -> List[float]:
        return self.__epsilon_history

    def __soft_reset(self):
        self._current_node = self._tree.get_root()
        self.__history = {}
        for node_hash in self._tree.get_hash():
            self.__history[node_hash] = {}
        return self._current_node

    def __get_exploitive_transition_tuple(self) -> Tuple[Optional[UIAction], Optional[UITreeNode]]:
        state = self.get_state()
        state_embedding = self.get_state_embedding()

        # Construct a list of nodes to transition to, along with their action
        action_embedding = np.argmax(self.__Q[state_embedding, :])
        embedded_node = self._tree.get_node_from_embedding(action_embedding)

        for potential_action, potential_node in state.get_transition_tuples():
            if potential_node.get_hash() == embedded_node.get_hash():
                return potential_action, potential_node

        return None, None

    def __get_next_transition(self) -> Tuple[Optional[UIAction], Optional[UITreeNode]]:
        # Determine whether to choose an exploitative of random action
        exp_tradeoff = uniform(0, 1)

        action, node_action = None, None
        if exp_tradeoff >= self.__epsilon:
            # Exploitative action
            action, node_action = self.__get_exploitive_transition_tuple()
            if action is None:
                exp_tradeoff = self.__epsilon - 1  # workaround to get to next if-condition

        if exp_tradeoff < self.__epsilon:
            # Random action
            action, node_action = self.get_next_explorative_transition_tuple()

        if (not action or not node_action) and self._current_node and self._current_node.get_parent():
            # Try going back up the tree
            action = UIAction.NAVIGATE
            node_action = self._current_node.get_parent()

        return action, node_action

    def __update_epsilon(self, episode_number: int):
        self.__epsilon = QLearningEnvironment.EPSILON_RANGE[0] + (
                QLearningEnvironment.EPSILON_RANGE[1] - QLearningEnvironment.EPSILON_RANGE[0]) * np.exp(
                - self.__decay * episode_number)
