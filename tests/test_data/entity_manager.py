class Entity:
    def __init__(self, name=""):
        self.name = name

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name


class EntityManager:
    def __init__(self):
        self.entities = {}

    def register_entity(self, name, entity):
        if name and entity:
            if not name in self.entities.keys():
                self.entities[name] = entity

    def remove_entity(self, name):
        if name in self.entities.keys():
            del self.entities[name]

    def get_entity(self, name):
        if name in self.entities.keys():
            return self.entities[name]



entity_manager = EntityManager()