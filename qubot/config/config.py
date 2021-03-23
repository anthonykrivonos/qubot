from typing import List


class QubotConfigTerminalInfo:
    """
    Abstracts information on the terminal nodes to find.
    """
    def __init__(self, terminal_ids: List[str] = None, terminal_classes: List[str] = None, terminal_contains_text: List[str] = None):
        self.terminal_ids = terminal_ids if terminal_ids is not None else []
        self.terminal_classes = terminal_classes if terminal_classes is not None else []
        self.terminal_contains_text = terminal_contains_text if terminal_contains_text is not None else []


class QubotConfigModelParameters:
    """
    Abstracts information on the Q-Learning model parameters.
    """
    def __init__(self, alpha=0.5, gamma=0.6, epsilon=1, decay=0.01, train_episodes=1000, test_episodes=100, step_limit=100):
        """
        Initializes the model configuration parameters.
        :param alpha: Higher alpha => consider more recent information (learning rate).
        :param gamma: Higher gamma => long term rewards.
        :param epsilon: Higher epsilon => favor exploitation.
        :param decay: Higher decay => epsilon decreases faster (more randomness).
        :param train_episodes: The number of episodes to train Qubot on.
        :param test_episodes: The number of episodes to test Qubot on.
        :param step_limit: Maximum number of steps to take before force-exiting the episode.
        """
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.decay = decay
        self.train_episodes = train_episodes
        self.test_episodes = test_episodes
        self.step_limit = step_limit

class QubotDriverParameters:
    """
    Abstracts information on the Selenium Driver parameters.
    """

    def __init__(self, use_cache: bool = False, max_urls: int = 10):
        """
        Initializes the Selenium configuration parameters.
        :param use_cache: Use the cache when scraping the website under test?
        :param max_urls: Maximum number of recursive URLs to visit during scraping.
        """
        self.use_cache = use_cache
        self.max_urls = max_urls
