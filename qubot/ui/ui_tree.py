from typing import Tuple, List, Set, Optional, Dict, Callable
from hashlib import sha256
from selenium.webdriver.firefox.webelement import FirefoxWebElement
from sys import path
from os.path import join, dirname
path.append(join(dirname(__file__), '../..'))

from qubot.ui.ui_action import UIAction
from qubot.utils.input_generation import is_generatable_input

class UITreeNode:
    """
    A node within a UITree. Contains information on how to get to other nodes.
    """

    def __init__(self, element: FirefoxWebElement, is_terminal=False, parent=None):
        self.__element = element
        self.__id = self.__element.id
        self.__tag_name = self.__element.tag_name
        self.__content = self.__element.get_attribute('outerHTML')
        self.__html_id = self.__element.get_attribute("id")
        self.__html_class = self.__element.get_attribute("class")
        self.__hash = sha256(self.__content.encode('utf-8')).hexdigest()
        self.__transitions = {}
        self.__visit_count = 0
        self.__is_terminal = is_terminal  # is this a terminal state?
        self.__parent = parent

    def add_transition(self, element: FirefoxWebElement):
        if element.tag_name in ["a", "button"]:
            if UIAction.LEFT_CLICK not in self.__transitions:
                self.__transitions[UIAction.LEFT_CLICK] = []
            self.__transitions[UIAction.LEFT_CLICK].append(UITreeNode(element, parent=self))
        elif is_generatable_input(element):
            if UIAction.INPUT not in self.__transitions:
                self.__transitions[UIAction.INPUT] = []
            self.__transitions[UIAction.INPUT].append(UITreeNode(element, parent=self))
        else:
            if UIAction.NAVIGATE not in self.__transitions:
                self.__transitions[UIAction.NAVIGATE] = []
            self.__transitions[UIAction.NAVIGATE].append(UITreeNode(element, parent=self))

    def get_element(self) -> FirefoxWebElement:
        return self.__element

    def get_children(self) -> List:
        children = []
        for action in self.__transitions:
            for child in self.__transitions[action]:
                children.append(child)
        return children

    def get_transitions(self) -> dict:
        return self.__transitions

    def get_transition_tuples(self) -> List[Tuple[UIAction, any]]:
        tups = []
        for action, transitions in list(self.__transitions.items()):
            for t in transitions:
                tups.append((action, t))
        return tups

    def get_parent(self) -> Optional['UITreeNode']:
        return self.__parent

    def get_id(self) -> str:
        return self.__id

    def get_hash(self) -> str:
        return self.__hash

    def get_html_id(self) -> str:
        return self.__html_id

    def get_html_class(self) -> str:
        return self.__html_class

    def get_content(self) -> str:
        return self.__content

    def get_visits(self) -> int:
        return self.__visit_count

    def set_terminal(self, is_terminal: bool):
        self.__is_terminal = is_terminal

    def is_terminal(self) -> bool:
        return self.__is_terminal

    def increment_visits(self):
        self.__visit_count += 1

    def decrement_visits(self):
        self.__visit_count -= 1

    def set_visits(self, visit_count: int):
        self.__visit_count = visit_count

    def __str__(self):
        return "<%s id=\"%s\" class=\"%s\"> (%s)" % (self.__tag_name, self.__html_id, self.__html_class, self.__id)


class UITree:
    """
    A tree indicating the state of the web page.
    """

    def __init__(self, root: UITreeNode):
        self.__root = root
        self.__tree_map = {}
        self.__tree_embedding = []
        self.__tree_node_to_embedding = {}
        self.__tree_embedding_counter = 0

    def get_root(self) -> UITreeNode:
        return self.__root

    def get_hash(self) -> Dict[str, UITreeNode]:
        return self.__tree_map

    def get_node_count(self) -> int:
        return self.__tree_embedding_counter

    def get_node_embedding(self, node: UITreeNode, rehash_tree=True) -> int:
        if rehash_tree:
            self.hash_tree()
        return self.__tree_node_to_embedding[node.get_hash()]

    def get_nodes_embedding(self, nodes: List[UITreeNode], rehash_tree=True) -> List[int]:
        if rehash_tree:
            self.hash_tree()
        embedding = [0] * self.get_node_count()
        for node in nodes:
            node_embedding = self.__tree_node_to_embedding[node.get_hash()]
            embedding[node_embedding] = 1
        return embedding

    def get_nodes_from_embedding(self, embedding: List[int], rehash_tree=True):
        if rehash_tree:
            self.hash_tree()
        nodes = []
        for i, value in enumerate(embedding):
            if value > 0:
                nodes.append(self.__tree_embedding[i])
        return nodes

    def get_node_from_embedding(self, embedding: int, rehash_tree=True):
        if rehash_tree:
            self.hash_tree()
        return self.__tree_embedding[embedding]

    def contains_similar_node(self, node: UITreeNode, rehash_tree=True) -> bool:
        if rehash_tree:
            self.hash_tree()
        return node.get_hash() in self.__tree_map

    def find_node_by_hash(self, node_hash: str) -> Tuple[Optional[UIAction], Optional[UITreeNode]]:
        if node_hash not in self.__tree_map:
            self.hash_tree()
        if node_hash not in self.__tree_map:
            return None, None
        return self.__tree_map[node_hash]

    def set_terminal_node(self, node: UITreeNode = None, html_id: str = None, html_class: str = None, contains_text: str = None):
        if not node:
            node = self.__find_node_by_metadata(html_id, html_class, contains_text)
        if node:
            node.set_terminal(True)

    def unset_terminal_node(self, node: UITreeNode = None, html_id: str = None, html_class: str = None, contains_text: str = None):
        if not node:
            node = self.__find_node_by_metadata(html_id, html_class, contains_text)
        if node:
            node.set_terminal(False)

    def hash_tree(self):
        """
        Constructs a hash of the nodes in the UITree for easy access.
        """
        self.__tree_map = {}
        self.__tree_embedding = []
        self.__tree_node_to_embedding = {}
        self.__tree_embedding_counter = 0

        def add_to_tree_map(action: UIAction, node: UITreeNode):
            self.__tree_map[node.get_hash()] = (action, node)
            self.__tree_node_to_embedding[node.get_hash()] = self.__tree_embedding_counter
            self.__tree_embedding.append(node)
            self.__tree_embedding_counter += 1
            for action, child in node.get_transition_tuples():
                add_to_tree_map(action, child)

        add_to_tree_map(UIAction.NAVIGATE, self.__root)

    def __find_node_by_metadata(self, html_id: str = None, html_class: str = None, contains_text: str = None) -> Optional[UITreeNode]:
        visit_queue: List[UITreeNode] = []
        visited_set: Set[UITreeNode] = set()

        visit_queue.append(self.__root)
        visited_set.add(self.__root)

        while visit_queue:
            node = visit_queue.pop(0)

            if html_id and node.get_html_id() == html_id:
                return node
            elif html_class and node.get_html_class() == html_class:
                return node
            elif contains_text and contains_text in node.get_content():
                return node

            for _, child in node.get_transition_tuples():
                if child not in visited_set:
                    visited_set.add(child)
                    visit_queue.append(child)

        return None

    def for_each_pair(self, func: Callable[[UIAction, UITreeNode], None]):
        visited_nodes = set()

        def visit_dfs(action: UIAction, node: UITreeNode):
            func(action, node)
            for child_act, child_node in node.get_transition_tuples():
                if child_node.get_id() not in visited_nodes:
                    visited_nodes.add(child_node.get_id())
                    visit_dfs(child_act, child_node)

        visit_dfs(UIAction.NAVIGATE, self.__root)

    def print(self):
        def print_node(action: UIAction, node: UITreeNode, depth: int):
            print("%s%s%s: %s" % (''.join(['\t' for _ in range(depth)]), action.name, "" if not node.is_terminal() else " (TERMINAL)", node))
            for action, child in node.get_transition_tuples():
                print_node(action, child, depth + 1)
        print_node(UIAction.NAVIGATE, self.__root, 0)
