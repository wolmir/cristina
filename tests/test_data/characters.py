import action
from utils import d6


class Character(action.ActionManager):
    def __init__(self, points=150):
        action.ActionManager.__init__(self)
        self.points = points
        self.force = 0
        self.skill = 0
        self.endurance = 0
        self.armor = 0
        self.fire_power = 0
        self.hit_points = 0
        self.advantages = {}
        self.disadvantages = []
        self.giant = False

    def check_force(self):
        return d6() <= self.force

    def check_skill(self):
        return d6() < self.skill

    def check_endurance(self):
        return d6() < self.endurance

    def check_fire_power(self):
        return d6() < self.fire_power

    def get_force(self):
        return self.force

    def get_armor(self):
        return self.armor

    def set_armor(self, armor):
        self.armor = armor

    def get_skill(self):
        return self.skill

    def get_fire_power(self):
        return self.fire_power

    def set_hit_points(self, hp):
        self.hit_points = hp

    def is_giant(self):
        return self.giant

    def grow_up(self):
        self.giant = True

    def shrink_down(self):
        self.giant = False

    def apply_damage(self, damage):
        if damage > 0:
            self.hit_points = max(self.hit_points - damage, 0)

    def has_advantage(self, advantage):
        return advantage in self.advantages.keys()

    def parse_command(self, command):
        if self.hit_points > 0:
            action.ActionManager.parse_command(self, command)
        else:
            print self.name + " is dead or inactive."


class Vehicle(Character):
    def __init__(self, points=10, max_occupants=1):
        Character.__init__(self, points)
        self.occupants = []
        self.max_occupants = max_occupants
        self.manned = False

    def enter_vehicle(self, character):
        if len(self.occupants) < self.max_occupants:
            self.occupants.append((character, character.get_armor()))
            character.set_armor(self.get_armor() + character.get_armor())

    def exit_vehicle(self, character):
        for i in range(len(self.occupants)):
            if self.occupants[i][0] == character:
                character.set_armor(self.occupants[i][1])
                del self.occupants[i]
                break

    def set_manual_control(self):
        self.manned = True

    def set_auto_control(self):
        self.manned = False


class GiantRobot(Vehicle):
    def __init__(self, points=10, max_occupants=1):
        Vehicle.__init__(self, points, max_occupants)
        self.giant = True