import json
import data

class GameInventory:
    def __init__(self):
        self.data = None
        self.file = data.filepath('inventory.json')
        fp = open(self.file, 'r')
        self.data = json.load(fp)
        fp.close()

    def save(self):
        fp = open(self.file, 'w')
        json.dump(self.data, fp)
        fp.close()