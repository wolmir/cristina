import action
import utils


class Advantage:
    def __init__(self):
        self.action_manager = None
        self.name = ""

    def assign_to(self, action_manager):
        utils.assert_type(action_manager, action.ActionManager)
        self.action_manager = action_manager

    def reset(self):
        pass

    def get_name(self):
        return self.name