class System:
    def __init__(self, name=""):
        self.name = name
        self.dit = 0
        self.noc = 0
        self.cbo = 0
        self.lcom = 0
        self.wmc = 0
        self. rfc = 0

    def pretty_info(self):
        info = self.name + ":\n"
        info += "\tDIT = " + str(self.dit) + "\n"
        info += "\tNOC = " + str(self.noc) + "\n"
        info += "\tCBO = " + str(self.cbo) + "\n"
        info += "\tLCOM = " + str(self.lcom) + "\n"
        info += "\tWMC = " + str(self.wmc) + "\n"
        info += "\tRFC = " + str(self.rfc) + "\n"
        return info


def get_number(string):
    return int(string.split("=")[1])


def is_class(string):
    if string and not string == "\n":
        return string.strip().split(":")[0] == "class"
    return False


def is_source_file(string):
    if string and not string == "\n":
        return not string.strip().split(":")[0] == "class"
    return False


def main():
    with open("measurements.txt") as measurements_file:
        measurements_file.readline()
        measurements_file.readline()
        current_system_name = measurements_file.readline()
        while current_system_name:
            current_system = System(current_system_name.strip())
            current_source_file = measurements_file.readline()
            while is_source_file(current_source_file):
                #print current_source_file
                current_class = measurements_file.readline()
                while is_class(current_class):
                    current_system.dit += get_number(measurements_file.readline().strip())
                    current_system.noc += get_number(measurements_file.readline().strip())
                    current_system.cbo += get_number(measurements_file.readline().strip())
                    current_system.lcom += get_number(measurements_file.readline().strip())
                    current_system.wmc += get_number(measurements_file.readline().strip())
                    current_system.rfc += get_number(measurements_file.readline().strip())
                    current_class = measurements_file.readline()
                current_source_file = measurements_file.readline()
            print current_system.pretty_info()
            current_system_name = measurements_file.readline()


if __name__ == '__main__':
    main()