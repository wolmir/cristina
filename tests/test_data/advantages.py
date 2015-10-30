import advantage_system
import characters
from entity_manager import entity_manager
from utils import d6
from utils import assert_type


class LaserSword(advantage_system.Advantage):
    def __init__(self):
        advantage_system.Advantage.__init__(self)
        self.light_saber_mode = True
        self.name = "Laser Sword"

    def assign_to(self, action_manager):
        """
        :param action_manager: characters.Character
        """
        assert_type(action_manager, characters.Character)
        advantage_system.Advantage.assign_to(self, action_manager)
        self.action_manager.set_action("attack with force", self.sword_attack_action)
        self.action_manager.set_action("attack with light saber", self.light_saber_attack_action)

    def sword_attack_action(self, args):
        target = entity_manager.get_entity(args[0])
        if self.action_manager.is_giant() and not target.is_giant():
            self.sword_attack_giant_normal(target)
        elif not self.action_manager.is_giant() and target.is_giant():
            self.sword_attack_normal_giant(target)
        else:
            self.sword_attack(target)

    def light_saber_attack_action(self, args):
        target = entity_manager.get_entity(args[0])
        if self.action_manager.is_giant() and not target.is_giant():
            self.light_saber_attack_giant_normal(target)
        elif not self.action_manager.is_giant() and target.is_giant():
            self.light_saber_attack_normal_giant(target)
        else:
            self.light_saber_attack(target)

    def sword_attack(self, target):
        assert_type(target, characters.Character)
        attacker = self.action_manager
        if attacker.check_skill():
            damage = d6(2) + attacker.get_force()
            defense = target.get_armor()
            target.apply_damage(damage - defense)

    def sword_attack_normal_giant(self, target):
        assert_type(target, characters.Character)
        attacker = self.action_manager
        if attacker.check_skill():
            damage = d6(2) + attacker.get_force()
            defense = (target.get_armor() * 4)
            target.apply_damage(damage - defense)

    def sword_attack_giant_normal(self, target):
        assert_type(target, characters.Character)
        attacker = self.action_manager
        if d6() == 1:
            damage = d6(2) + (attacker.get_force() * 4)
            defense = target.get_armor()
            target.apply_damage(damage - defense)

    def light_saber_attack(self, target):
        assert_type(target, characters.Character)
        attacker = self.action_manager
        if self.light_saber_mode and attacker.check_skill():
            damage = d6(3) + attacker.get_force()
            defense = target.get_armor()
            target.apply_damage(damage - defense)
            self.light_saber_mode = False

    def light_saber_attack_normal_giant(self, target):
        assert_type(target, characters.Character)
        attacker = self.action_manager
        if self.light_saber_mode and attacker.check_skill():
            damage = d6(3) + attacker.get_force()
            defense = (target.get_armor() * 4)
            target.apply_damage(damage - defense)
            self.light_saber_mode = False

    def light_saber_attack_giant_normal(self, target):
        assert_type(target, characters.Character)
        attacker = self.action_manager
        if self.light_saber_mode and d6() == 1:
            damage = d6(3) + (attacker.get_force() * 4)
            defense = target.get_armor()
            target.apply_damage(damage - defense)
            self.light_saber_mode = False

    def reset(self):
        self.light_saber_mode = True


class WeaponCombo(advantage_system.Advantage):
    def __init__(self):
        advantage_system.Advantage.__init__(self)
        self.name = "Weapon Combo"
        self.already_used = False

    def assign_to(self, action_manager):
        assert_type(action_manager, characters.Character)
        advantage_system.Advantage.assign_to(self, action_manager)
        self.action_manager.set_action("weapon combo", self.combo_attack_action)

    def combo_attack_action(self, args):
        attackers = [entity_manager.get_entity(attacker_name) for attacker_name in args[:-1]] + [self.action_manager]
        target = entity_manager.get_entity(args[-1])
        self.combo_attack(attackers, target)

    def combo_attack(self, attackers, target):
        assert_type(target, characters.Character)
        if all([character.has_advantage(self.name) for character in attackers]) and not self.already_used:
            best_skill = max([character.get_skill() for character in attackers])
            if d6() <= best_skill:
                combo_fire_power = sum([character.get_fire_power() for character in attackers])
                damage = d6(1) + combo_fire_power
                defense = target.get_armor()
                target.apply_damage(damage - defense)
                self.already_used = True

    def reset(self):
        self.already_used = False


class HelperRobot(advantage_system.Advantage):
    def __init__(self, robot_character):
        advantage_system.Advantage.__init__(self)
        self.name = "Helper Robot"
        self.robot_character = robot_character

    def assign_to(self, action_manager):
        assert_type(action_manager, characters.Character)
        advantage_system.Advantage.assign_to(self, action_manager)
        self.action_manager.set_action("command robot", self.command_robot_action)

    def command_robot_action(self, args):
        self.robot_character.parse_command(" ".join(args))


class GiantRobot(advantage_system.Advantage):
    def __init__(self, giant_robot_character):
        advantage_system.Advantage.__init__(self)
        self.name = "Giant Robot"
        self.giant_robot_character = giant_robot_character
        self.called = False

    def enter_robot_action(self, args):
        self.giant_robot_character.set_manual_control()
        self.action_manager.set_action("pilot robot", self.pilot_robot_action)
        self.action_manager.set_action("exit robot", self.exit_robot_action)
        self.action_manager.remove_action("enter robot")

    def exit_robot_action(self, args):
        self.giant_robot_character.set_auto_control()
        self.action_manager.remove_action("pilot robot")
        self.action_manager.remove_action("exit robot")
        self.action_manager.set_action("enter robot", self.enter_robot_action)

    def pilot_robot_action(self, args):
        self.giant_robot_character.parse_command(" ".join(args))

    def call_robot_action(self, args):
        self.called = True
        self.action_manager.remove_action("call giant robot")

    def new_turn(self):
        if self.called:
            self.called = False
            self.action_manager.set_action("enter robot", self.enter_robot_action)

    def assign_to(self, action_manager):
        advantage_system.Advantage.assign_to(self, action_manager)
        self.action_manager.set_action("call giant robot", self.call_robot_action)


class CombatVehicle(advantage_system.Advantage):
    def __init__(self, vehicle):
        advantage_system.Advantage.__init__(self)
        self.name = "Combat Vehicle"
        self.vehicle = vehicle
        self.called = False

    def enter_vehicle_action(self, args):
        self.vehicle.set_manual_control()
        self.action_manager.set_action("pilot vehicle", self.pilot_vehicle_action)
        self.action_manager.set_action("exit vehicle", self.exit_vehicle_action)
        self.action_manager.remove_action("enter vehicle")

    def exit_vehicle_action(self, args):
        self.vehicle.set_auto_control()
        self.action_manager.remove_action("pilot vehicle")
        self.action_manager.remove_action("exit vehicle")
        self.action_manager.set_action("enter vehicle", self.enter_vehicle_action)

    def pilot_vehicle_action(self, args):
        self.vehicle.parse_command(" ".join(args))

    def call_vehicle_action(self, args):
        self.called = True
        self.action_manager.remove_action("call vehicle")

    def new_turn(self):
        if self.called:
            self.called = False
            self.action_manager.set_action("enter vehicle", self.enter_vehicle_action)

    def assign_to(self, action_manager):
        advantage_system.Advantage.assign_to(self, action_manager)
        self.action_manager.set_action("call vehicle", self.call_vehicle_action)


class GiantVehicle(advantage_system.Advantage):
    def __init__(self, giant_vehicle_character):
        advantage_system.Advantage.__init__(self)
        self.name = "Giant Vehicle"
        self.giant_vehicle_character = giant_vehicle_character
        self.called = False

    def enter_vehicle_action(self, args):
        self.giant_vehicle_character.set_manual_control()
        self.action_manager.set_action("pilot vehicle", self.pilot_vehicle_action)
        self.action_manager.set_action("exit vehicle", self.exit_vehicle_action)
        self.action_manager.remove_action("enter vehicle")

    def exit_vehicle_action(self, args):
        self.giant_vehicle_character.set_auto_control()
        self.action_manager.remove_action("pilot vehicle")
        self.action_manager.remove_action("exit vehicle")
        self.action_manager.set_action("enter vehicle", self.enter_vehicle_action)

    def pilot_vehicle_action(self, args):
        self.giant_vehicle_character.parse_command(" ".join(args))

    def call_vehicle_action(self, args):
        self.called = True
        self.action_manager.remove_action("call giant vehicle")

    def new_turn(self):
        if self.called:
            self.called = False
            self.action_manager.set_action("enter vehicle", self.enter_vehicle_action)

    def assign_to(self, action_manager):
        advantage_system.Advantage.assign_to(self, action_manager)
        self.action_manager.set_action("call giant vehicle", self.call_vehicle_action)


class FiftyMetersTall(advantage_system.Advantage):
    def __init__(self):
        advantage_system.Advantage.__init__(self)

    def grow_up_action(self, args):
        self.action_manager.grow_up()

    def shrink_down_action(self, args):
        self.action_manager.shrink_down()

    def assign_to(self, action_manager):
        advantage_system.Advantage.assign_to(self, action_manager)
        self.action_manager.set_action("grow up", self.grow_up_action)
        self.action_manager.set_action("shrink down", self.shrink_down_action)


class DevastatingBlow(advantage_system.Advantage):
    def __init__(self):
        advantage_system.Advantage.__init__(self)
        self.already_used = False

    def devastating_blow_force_action(self, args):
        target = entity_manager.get_entity(args[0])
        if not self.already_used:
            self.devastating_blow_force(target)
            self.already_used = True

    def devastating_blow_force(self, target):
        assert_type(target, characters.Character)
        if self.action_manager.check_skill():
            damage = (d6() + self.action_manager.get_force()) * 2
            defense = target.get_armor()
            target.apply_damage(damage - defense)

    def devastating_blow_fire_power(self, target):
        assert_type(target, characters.Character)
        if self.action_manager.check_skill():
            damage = (d6() + self.action_manager.get_force()) * 2
            defense = target.get_armor()
            target.apply_damage(damage - defense)

    def reset(self):
        self.already_used = False