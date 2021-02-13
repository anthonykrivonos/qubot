from qubot.ui import UIAction, UITreeNode
from qubot.environment import QLearningEnvironment
from qubot.driver import Driver

driver = Driver()
tree = driver.construct_tree("https://upmed-starmen.web.app/", deep=True)
# tree.set_terminal_node(html_class="Home_subtitle__3_lpZ")
tree.set_terminal_node(html_class="SignIn_login_hcp__qYuvP")

def reward_func(action: UIAction, node: UITreeNode):
    if node.is_terminal():
        return 100
    elif not node.get_children():
        return -1
    elif action == UIAction.LEFT_CLICK:
        return 5
    return 0

alpha = 0.5     # higher alpha   ==> consider more recent information (learning rate)
gamma = 0.6     # higher gamma   ==> long term rewards
epsilon = 1     # higher epsilon ==> favor exploitation
decay = 0.01    # higher decay   ==> epsilon decreases faster (more randomness)

train_episodes = 1000
test_episodes = 100
max_steps = 100

env = QLearningEnvironment(tree, reward_func, alpha, gamma, epsilon, decay, max_steps)
env.reset()

env.train(train_episodes)
# tree.unset_terminal_node(html_class="Home_subtitle__3_lpZ")
# tree.set_terminal_node(html_class="Home_landing_img__25n7m")
tree.unset_terminal_node(html_class="SignIn_login_hcp__qYuvP")
tree.set_terminal_node(html_class="SignIn_tile_img__1VCWa")
env.test(test_episodes)
env.render()
