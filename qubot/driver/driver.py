from typing import Optional, Set, Dict
from selenium import webdriver
from selenium.webdriver import ActionChains
from sys import path
from os import getcwd
from os.path import join, dirname
path.append(join(dirname(__file__), '../../..'))

from qubot.ui.ui_action import UIAction
from qubot.ui.ui_tree import UITree, UITreeNode
from qubot.utils.errors import inline_try, try_again_on_fail
from qubot.utils.input_generation import generate_input
from qubot.utils.io import write_pickle, safe_filename
from qubot.stats.stats import Stats

class Driver:

    PKL_CACHE = ".driver_cache"

    STAT_URLS_VISITED = "urls_visited"
    STAT_ELEMENTS_ENCOUNTERED = "elements_encountered"
    STAT_ELEMENTS_NAVIGATED = "elements_navigated"
    STAT_ELEMENTS_LEFT_CLICKED = "elements_left_clicked"
    STAT_ELEMENTS_INPUTTED = "elements_inputted"
    STAT_CRASH_DETECTED = "crash_detected"

    def __init__(self, input_values: Dict[str, str] = None, use_cache=True):
        self.__driver = webdriver.Firefox()
        self.__input_values = input_values
        self.__stats = Stats(str(self.__class__))
        self.__use_cache = use_cache
        self.__last_tree = None

    def open(self, url: str):
        self.__driver.get(url)

    def construct_tree(self, url: str = None, deep=True, max_urls_to_visit=10) -> UITree:
        visited_urls: Set[str] = set()

        def on_url_visit():
            self.open(url)
            visited_urls.add(url)
            self.__last_tree = self.__visit(visited_urls, deep=deep, max_urls_to_visit=max_urls_to_visit)
            if self.__use_cache:
                write_pickle(join(getcwd(), Driver.PKL_CACHE, safe_filename(url)), {
                    "stats": self.__stats,
                    "last_tree": self.__last_tree
                })

        if url:
            if self.__use_cache:
                raise Exception("caching not yet implemented! sorry...")
                # driver_from_pkl = read_pickle(join(getcwd(), Driver.PKL_CACHE, safe_filename(url)))
                # print(driver_from_pkl)
                # if driver_from_pkl:
                #     self.stats = driver_from_pkl["stats"]
                #     self.last_tree = driver_from_pkl["last_tree"]
                # else:
                #     on_url_visit()
            else:
                on_url_visit()

        return self.__last_tree

    def get_stats(self) -> Stats:
        return self.__stats

    def __visit(self, visited_urls: Set[str] = None, visited_nodes: Set[str] = None, deep=False, max_urls_to_visit=10) -> UITree:
        if not visited_urls:
            visited_urls = set()
        if not visited_nodes:
            visited_nodes = set()

        # Get root tag
        html_tag = self.__driver.find_elements_by_tag_name("html")[0]
        root = UITreeNode(html_tag)
        tree = UITree(root)

        def visit_dfs(action: UIAction, node: UITreeNode, driver: Driver):
            if node.get_id() in visited_nodes:
                return

            self.__stats.record(Driver.STAT_ELEMENTS_ENCOUNTERED, str(node))

            visited_nodes.add(node.get_id())

            if not deep or action == UIAction.NAVIGATE:
                child_tags = node.get_element().find_elements_by_css_selector("*")
                for child_tag in child_tags:
                    node.add_transition(child_tag)
                for act, child in node.get_transition_tuples():
                    visit_dfs(act, child, driver)
            else:
                def visit_new_page():
                    sub_driver = Driver()
                    sub_driver.open(driver.__driver.current_url)

                    if action == UIAction.LEFT_CLICK:
                        sub_driver.__left_click(node)
                        self.__stats.record(Driver.STAT_ELEMENTS_LEFT_CLICKED, str(node))
                    elif action == UIAction.INPUT:
                        sub_driver.__input(node)
                        self.__stats.record(Driver.STAT_ELEMENTS_INPUTTED, str(node))
                    else:
                        self.__stats.record(Driver.STAT_ELEMENTS_NAVIGATED, str(node))

                    sub_html_tag = sub_driver.__driver.find_elements_by_tag_name("html")[0]

                    if sub_driver.__driver.current_url not in visited_urls and len(visited_urls) < max_urls_to_visit:
                        self.__stats.record(Driver.STAT_URLS_VISITED, sub_driver.__driver.current_url)
                        visited_urls.add(sub_driver.__driver.current_url)

                        sub_child_tags = sub_html_tag.find_elements_by_css_selector("*")
                        for sub_child_tag in sub_child_tags:
                            node.add_transition(sub_child_tag)
                        for sub_act, sub_child in node.get_transition_tuples():
                            visit_dfs(sub_act, sub_child, sub_driver)

                    del sub_driver

                def on_fail():
                    self.__stats.record(Driver.STAT_CRASH_DETECTED, {
                        "on_action": action.name,
                        "element": str(node)
                    })

                try_again_on_fail(visit_new_page, 10, 10, on_fail)

        visit_dfs(UIAction.NAVIGATE, root, self)

        return tree

    def __find_node_in_dom(self, node: UITreeNode) -> Optional[UITreeNode]:
        """
        Finds a node in the current DOM, in case the passed-in node has had its window displaced.
        :param node: The node to find.
        :return: The same node in the current window or None.
        """
        shallow_tree = self.__visit(deep=False)
        _, node_in_dom = shallow_tree.find_node_by_hash(node.get_hash())
        return node_in_dom

    def __left_click(self, node: UITreeNode):
        node_in_dom = self.__find_node_in_dom(node)
        if node_in_dom:
            if inline_try(lambda: ActionChains(self.__driver).click(node_in_dom.get_element()).perform()):
                self.__stats.record(Driver.STAT_CRASH_DETECTED, {
                    "on_action": "LEFT_CLICK",
                    "element": str(node_in_dom)
                })

    def __input(self, node: UITreeNode):
        node_in_dom = self.__find_node_in_dom(node)
        value = generate_input(node.get_element(), self.__input_values)
        if node_in_dom:
            if inline_try(lambda: ActionChains(self.__driver).send_keys(value).perform()):
                self.__stats.record(Driver.STAT_CRASH_DETECTED, {
                    "on_action": "INPUT",
                    "element": str(node_in_dom)
                })

    def __del__(self):
        """
        Destroy the driver when the application quits.
        """
        self.__driver.quit()
