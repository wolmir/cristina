import entity_manager


class CommandNotFound(Exception):
    pass


class ActionManager(entity_manager.Entity):
    def __init__(self, name=""):
        entity_manager.Entity.__init__(self, name)
        self.actions = {}

    def set_action(self, name, action_callback):
        self.actions[name] = action_callback

    def remove_action(self, name):
        if name in self.actions.keys():
            del self.actions[name]

    def perform_action(self, name, args):
        action_callback = self.actions[name]
        action_callback(args)

    def parse_command(self, command):
        command_parts = command.split()
        for part_index in range(len(command_parts)):
            if command_parts[part_index] in self.actions.keys():
                if part_index < (len(command_parts) - 1) and command_parts[part_index + 1] in self.actions.keys():
                    continue
                self.perform_action(" ".join(command_parts[:part_index + 1]), command_parts[part_index + 1:])
            raise CommandNotFound()