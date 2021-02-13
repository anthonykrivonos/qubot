from typing import Optional, Set
from selenium import webdriver
from selenium.webdriver import ActionChains

from qubot.ui import UIAction, UITree, UITreeNode
from qubot.utils import inline_try, try_again_on_fail

class Driver:

    def __init__(self):
        self.__driver = webdriver.Firefox()

    def open(self, url: str):
        self.__driver.get(url)

    def construct_tree(self, url: str = None, deep=True) -> UITree:
        visited_urls: Set[str] = set()
        if url:
            self.open(url)
            visited_urls.add(url)
        return self.__visit(visited_urls, deep=deep)

    def __visit(self, visited_urls: Set[str] = None, visited_nodes: Set[str] = None, deep=False) -> UITree:
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

                    sub_html_tag = sub_driver.__driver.find_elements_by_tag_name("html")[0]

                    if sub_driver.__driver.current_url not in visited_urls:
                        visited_urls.add(sub_driver.__driver.current_url)

                        sub_child_tags = sub_html_tag.find_elements_by_css_selector("*")
                        for sub_child_tag in sub_child_tags:
                            node.add_transition(sub_child_tag)
                        for sub_act, sub_child in node.get_transition_tuples():
                            visit_dfs(sub_act, sub_child, sub_driver)

                    del sub_driver
                try_again_on_fail(visit_new_page, 10, 10)

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
            inline_try(lambda: ActionChains(self.__driver).click(node_in_dom.get_element()).perform())

    def __del__(self):
        """
        Destroy the driver when the application quits.
        """
        self.__driver.quit()
