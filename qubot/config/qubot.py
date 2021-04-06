from typing import Dict, Optional
from copy import copy, deepcopy
from sys import path
import os
from os.path import join, dirname
path.append(join(dirname(__file__), os.pardir))

from qubot.config.config import QubotConfigTerminalInfo, QubotConfigModelParameters, QubotDriverParameters
from qubot.environment.q_learning_environment import QLearningEnvironment
from qubot.driver.driver import Driver
from qubot.config.preset_rewards import QubotPresetRewardFunc, int_to_reward_func, str_to_reward_func
from qubot.stats.stats import Stats
from qubot.utils.io import read_json

class Qubot:

    STAT_CONSTRUCT_UI_TREE_TIME = "construct_ui_tree_time"
    STAT_TRAINING_TIME = "training_time"
    STAT_TESTING_TIME = "testing_time"

    def __init__(self, url_to_test: str, terminal_info_testing: QubotConfigTerminalInfo, terminal_info_training: QubotConfigTerminalInfo = None, driver_params: QubotDriverParameters = None, model_params: QubotConfigModelParameters = None, reward_func: QubotPresetRewardFunc = QubotPresetRewardFunc.ENCOURAGE_EXPLORATION, input_values: Dict[str, str] = None):
        self.__url_to_test = url_to_test
        self.__terminal_info_testing = terminal_info_testing
        self.__terminal_info_training = terminal_info_training if terminal_info_training is not None else copy(terminal_info_testing)
        self.__driver_info = driver_params if driver_params is not None else QubotDriverParameters()
        self.__model_info = model_params if model_params is not None else QubotConfigModelParameters()
        self.__input_values = input_values

        self.__driver = Driver(self.__input_values, use_cache=self.__driver_info.use_cache)
        self.__stats = Stats(str(self.__class__))

        self.__stats.start_timer(Qubot.STAT_CONSTRUCT_UI_TREE_TIME)
        self.__tree = self.__driver.construct_tree(self.__url_to_test, deep=True, max_urls_to_visit=self.__driver_info.max_urls)
        self.__stats.stop_timer(Qubot.STAT_CONSTRUCT_UI_TREE_TIME)

        self.__reward_func = reward_func

        self.__env = QLearningEnvironment(
            self.__tree,
            self.__reward_func,
            self.__model_info.alpha,
            self.__model_info.gamma,
            self.__model_info.epsilon,
            self.__model_info.decay,
            self.__model_info.step_limit
        )

    def run(self):
        self.train(verbose=False)
        self.test(verbose=True)

    def train(self, verbose=True):
        self.__env.reset()
        self.__set_terminal_nodes(True)

        self.__stats.start_timer(Qubot.STAT_TRAINING_TIME)
        self.__env.train(self.__model_info.train_episodes)
        self.__stats.stop_timer(Qubot.STAT_TRAINING_TIME)

        if verbose:
            self.__env.render()

    def test(self, verbose=True):
        self.__set_terminal_nodes(False)

        self.__stats.start_timer(Qubot.STAT_TESTING_TIME)
        self.__env.test(self.__model_info.test_episodes)
        self.__stats.stop_timer(Qubot.STAT_TESTING_TIME)

        if verbose:
            self.__env.render()

    def get_env(self) -> QLearningEnvironment:
        return self.__env

    def get_stats(self) -> Stats:
        return self.__stats.merge(self.__driver.get_stats().merge(self.__env.get_stats()))

    def __set_terminal_nodes(self, is_training=False):
        training_func = self.__tree.set_terminal_node if is_training else self.__tree.unset_terminal_node
        testing_func = self.__tree.set_terminal_node if not is_training else self.__tree.unset_terminal_node
        # Set for training
        for terminal_html_id in self.__terminal_info_training.terminal_ids:
            training_func(html_id=terminal_html_id)
        for terminal_html_class in self.__terminal_info_training.terminal_classes:
            training_func(html_class=terminal_html_class)
        for terminal_contains_test in self.__terminal_info_training.terminal_contains_text:
            training_func(contains_text=terminal_contains_test)
        # Set for testing
        for terminal_html_id in self.__terminal_info_testing.terminal_ids:
            testing_func(html_id=terminal_html_id)
        for terminal_html_class in self.__terminal_info_testing.terminal_classes:
            testing_func(html_class=terminal_html_class)
        for terminal_contains_test in self.__terminal_info_testing.terminal_contains_text:
            testing_func(contains_text=terminal_contains_test)

    def set_driver_config(self, driver_params: QubotDriverParameters = None, input_values: Dict[str, str] = None):
        self.__driver_info = driver_params if driver_params is not None else self.__driver_info
        self.__input_values = input_values if input_values is not None else self.__input_values
        if driver_params is not None or input_values is not None:
            self.__stats.start_timer(Qubot.STAT_CONSTRUCT_UI_TREE_TIME)
            self.__driver = Driver(self.__input_values, use_cache=self.__driver_info.use_cache)
            self.__tree = self.__driver.construct_tree(self.__url_to_test, deep=True,
                                                       max_urls_to_visit=self.__driver_info.max_urls)
            self.__stats.stop_timer(Qubot.STAT_CONSTRUCT_UI_TREE_TIME)

    def set_model_config(self, model_params: Optional[QubotConfigModelParameters] = None, reward_func: Optional[QubotPresetRewardFunc] = None):
        self.__model_info = model_params if model_params is not None else self.__model_info
        self.__reward_func = reward_func if reward_func is not None else self.__reward_func
        if model_params is not None or reward_func is not None:
            self.__env = QLearningEnvironment(
                self.__tree,
                self.__reward_func,
                self.__model_info.alpha,
                self.__model_info.gamma,
                self.__model_info.epsilon,
                self.__model_info.decay,
                self.__model_info.step_limit
            )

    @staticmethod
    def from_file(file_path: str):
        return Qubot.from_dict(read_json(file_path))

    @staticmethod
    def from_dict(config: Dict):
        if "url" not in config:
            raise Exception(".qu file missing 'url'")
        if not isinstance(config["url"], str):
            raise Exception("'url' in .qu file must be str")
        url = config["url"]
        if "terminal_info" not in config:
            raise Exception(".qu file missing 'terminal_info'")
        if not isinstance(config["terminal_info"], dict):
            raise Exception("'terminal_info' in .qu file must be a dict")

        def get_terminal_info(terminal_info: Dict) -> QubotConfigTerminalInfo:
            if "ids" not in terminal_info and "classes" not in terminal_info and "contains_text" not in terminal_info:
                raise Exception("'terminal_info', 'terminal_info.training', and/or 'terminal_info.testing' in .qu file must have 'ids', 'classes', and/or 'contains_text' properties")
            ids = terminal_info["ids"] if "ids" in terminal_info else []
            classes = terminal_info["classes"] if "classes" in terminal_info else []
            contains_text = terminal_info["contains_text"] if "contains_text" in terminal_info else []
            return QubotConfigTerminalInfo(ids, classes, contains_text)

        terminal_info_training = None
        terminal_info_testing = None
        if "training" in config["terminal_info"] or "testing" in config["terminal_info"]:
            if "training" in config["terminal_info"]:
                terminal_info_training = get_terminal_info(config["terminal_info"]["training"])
            if "testing" in config["terminal_info"]:
                terminal_info_testing = get_terminal_info(config["terminal_info"]["testing"])
            if not terminal_info_testing and terminal_info_training:
                terminal_info_testing = deepcopy(terminal_info_training)
        else:
            terminal_info_testing = get_terminal_info(config["terminal_info"])

        if "driver_parameters" not in config:
            driver_parameters = None
        else:
            driver_parameters = QubotDriverParameters(
                config["driver_parameters"]["use_cache"] if "use_cache" in config["driver_parameters"] else None,
                config["driver_parameters"]["max_urls"] if "max_urls" in config["driver_parameters"] else None,
            )

        if "model_parameters" not in config:
            model_parameters = None
        else:
            model_parameters = QubotConfigModelParameters(
                config["model_parameters"]["alpha"] if "alpha" in config["model_parameters"] else None,
                config["model_parameters"]["gamma"] if "gamma" in config["model_parameters"] else None,
                config["model_parameters"]["epsilon"] if "epsilon" in config["model_parameters"] else None,
                config["model_parameters"]["decay"] if "decay" in config["model_parameters"] else None,
                config["model_parameters"]["train_episodes"] if "train_episodes" in config["model_parameters"] else None,
                config["model_parameters"]["test_episodes"] if "test_episodes" in config["model_parameters"] else None,
                config["model_parameters"]["step_limit"] if "step_limit" in config["model_parameters"] else None,
            )
        if "reward_func" not in config:
            reward_func = None
        elif isinstance(config["reward_func"], str) and config["reward_func"] in str_to_reward_func:
            reward_func = str_to_reward_func[config["reward_func"]]
        elif int(config["reward_func"]) in int_to_reward_func:
            reward_func = int_to_reward_func[int(config["reward_func"])]
        else:
            reward_func = None
        input_values = config["input_values"] if "input_values" in config else None
        return Qubot(url, terminal_info_testing, terminal_info_training, driver_parameters, model_parameters, reward_func, input_values)
