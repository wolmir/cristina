import pyclbr
import os
import sys
import symtable
import ast
from radon.complexity import cc_visit_ast


class ModuleFunctionSymbolExtractor(ast.NodeVisitor):
    def __init__(self, node, function_table, module_table):
        ast.NodeVisitor.__init__(self)
        self.node = node
        self.function_table = function_table
        self.module_table = module_table
        self.instance_references = set([])
        self.foreign_references = set([])
        self.local_structures = {}

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Call):
            self.foreign_references.add(node.attr)
            self.generic_visit(node)
            return
        variable_name = node.value.id
        variable_symbol = self.function_table.lookup(variable_name)
        attribute_name = node.attr
        if not variable_name in self.module_table.get_identifiers():
            if variable_symbol.is_local() or variable_symbol.is_parameter():
                if variable_name in self.local_structures.keys():
                    self.local_structures[variable_name].add(attribute_name)
                else:
                    self.local_structures[variable_name] = {attribute_name}
        else:
            self.instance_references.add(attribute_name)
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if self.function_table.lookup(node.func.id).is_imported():
                self.foreign_references.add(node.func.id)
        self.generic_visit(node)

    def extract(self):
        self.visit(self.node)
        for variable_name in self.local_structures.keys():
            self.foreign_references.add(tuple(self.local_structures[variable_name]))


class ModuleForeignSymbolExtractor(ast.NodeVisitor):
    def __init__(self, node, symbol_table):
        ast.NodeVisitor.__init__(self)
        self.node = node
        self.symbol_table = symbol_table
        self.foreign_references = set([])
        self.instance_references = set([])
        self.functions = set([])

    def visit_FunctionDef(self, node):
        self.functions.add(node.name)
        function_table = self.symbol_table.lookup(node.name).get_namespace()
        function_extractor = ModuleFunctionSymbolExtractor(node, function_table, self.symbol_table)
        function_extractor.extract()
        self.instance_references |= function_extractor.instance_references
        self.foreign_references |= function_extractor.instance_references

    def extract(self):
        self.visit(self.node)


class MethodSymbolsExtractor(ast.NodeVisitor):
    def __init__(self, node, symbol_table, debug=False):
        ast.NodeVisitor.__init__(self)
        self.node = node
        self.symbol_table = symbol_table
        self.debug = debug
        self.instance_references = set([])
        self.foreign_references = {'<unknown>': set([]), '<functions>': set([])}
        self.method_namespaces = {}
        self.local_structures = {}
        self.function_calls = 0

    def visit_Attribute(self, node):
        # if self.debug:
        #     print ast.dump(node)
        if not isinstance(node.value, ast.Name):
            if isinstance(node.value, ast.Str):
                return None
            value_name = self.visit(node.value)
            if value_name in self.foreign_references.keys():
                self.foreign_references[value_name].add(node.attr)
            else:
                self.foreign_references[value_name] = {node.attr}
            #print node.attr
            return value_name + "." + node.attr
        try:
            variable_name = node.value.id
        except AttributeError:
            print ast.dump(node)
            raise
        # if self.debug:
        #     print ast.dump(node)
        try:
            variable_symbol = self.symbol_table.lookup(variable_name)
        except KeyError:
            print ast.dump(node)
            raise
        attribute_name = node.attr
        if variable_name != 'self':
            if variable_symbol.is_local() or variable_symbol.is_parameter():
                variable_name = self.node.name + "::" + variable_name
            if variable_name in self.local_structures.keys():
                self.local_structures[variable_name].add(attribute_name)
            else:
                self.local_structures[variable_name] = {attribute_name}
        else:
            self.instance_references.add(attribute_name)
        return variable_name + "." + attribute_name

    def visit_Call(self, node):
        self.function_calls += 1
        if self.debug:
            print ast.dump(node)
        ret_value = None
        if not isinstance(node.func, ast.Name):
            ret_value = self.visit(node.func)
        else:
            self.foreign_references['<functions>'].add(node.func.id)
            ret_value = node.func.id
        for arg in node.args:
            self.visit(arg)
        for kword in node.keywords:
            self.visit(kword)
        if node.starargs:
            self.visit(node.starargs)
        if node.kwargs:
            self.visit(node.kwargs)
        return ret_value

    def visit_Subscript(self, node):
        self.visit(node.slice)
        if not isinstance(node.value, ast.Name):
            return self.visit(node.value)
        return node.value.id

    def visit_FunctionDef(self, node):
        if node.name != self.node.name:
            try:
                method_namespaces = self.symbol_table.lookup(node.name).get_namespaces()
                method_table = method_namespaces[0]
                if len(method_namespaces) > 1:
                    if node.name in self.method_namespaces.keys():
                        method_table = method_namespaces[self.method_namespaces[node.name]]
                        self.method_namespaces[node.name] += 1
                    else:
                        self.method_namespaces[node.name] = 0
                method_extractor = MethodSymbolsExtractor(node, method_table, self.debug)
                method_extractor.extract()
                self.instance_references |= method_extractor.instance_references
                for reference in method_extractor.foreign_references.keys():
                    if reference in self.foreign_references.keys():
                        self.foreign_references[reference] |= method_extractor.foreign_references[reference]
                    else:
                        self.foreign_references[reference] = method_extractor.foreign_references[reference]
            except (ValueError, KeyError):
                print node.name
                # print self.symbol_table.lookup(node.name).get_namespaces()[0].get_identifiers()
                # print self.symbol_table.lookup(node.name).get_namespaces()[1].get_identifiers()
                raise
        else:
            self.generic_visit(node)

    def extract(self):
        try:
            # if self.debug:
            #     print self.node.name
            #     print ast.dump(self.node)
            self.visit(self.node)
            # if self.debug:
            #     print ""
            for variable_name in self.local_structures.keys():
                if variable_name in self.foreign_references.keys():
                    self.foreign_references[variable_name] |= self.local_structures[variable_name]
                else:
                    self.foreign_references[variable_name] = self.local_structures[variable_name]
        except (AttributeError, KeyError, TypeError):
            print ast.dump(self.node)
            print self.symbol_table.get_identifiers()
            raise


class InstanceSymbolsExtractor(ast.NodeVisitor):
    def __init__(self, node, symbol_table, debug=False):
        ast.NodeVisitor.__init__(self)
        self.node = node
        self.symbol_table = symbol_table
        self.debug = debug
        self.methods = set([])
        self.method_namespaces = {}
        self.method_complexities = {}
        self.instance_references = set([])
        self.instance_variables_per_method = {}
        self.foreign_references = {}
        self.function_calls = 0

    def visit_FunctionDef(self, node):
        if node.name != '__init__':
            self.methods.add(node.name)
        try:
            method_namespaces = self.symbol_table.lookup(node.name).get_namespaces()
            # if self.debug:
            #     print len(method_namespaces)
            method_table = method_namespaces[0]
            if len(method_namespaces) > 1:
                if node.name in self.method_namespaces.keys():
                    method_table = method_namespaces[self.method_namespaces[node.name]]
                    self.method_namespaces[node.name] += 1
                else:
                    self.method_namespaces[node.name] = 1
            method_extractor = MethodSymbolsExtractor(node, method_table, self.debug)
            method_extractor.extract()
            instance_variables_in_method = method_extractor.instance_references - self.methods
            self.instance_references |= instance_variables_in_method
            self.instance_variables_per_method[node.name] = instance_variables_in_method
            for reference in method_extractor.foreign_references.keys():
                    if reference in self.foreign_references.keys():
                        self.foreign_references[reference] |= method_extractor.foreign_references[reference]
                    else:
                        self.foreign_references[reference] = method_extractor.foreign_references[reference]
            cc_result = cc_visit_ast(node)[0]
            self.method_complexities[node.name] = cc_result.complexity
            if self.debug:
                print cc_result.name + ": " + str(cc_result.complexity)
            self.function_calls += method_extractor.function_calls
        except ValueError:
            print node.name
            print self.symbol_table.lookup(node.name).get_namespaces()[0].get_identifiers()
            print self.symbol_table.lookup(node.name).get_namespaces()[1].get_identifiers()
            raise

    def extract(self):
        try:
            self.visit(self.node)
        except (AttributeError, KeyError):
            print ast.dump(self.node)
            raise


class ClassNodeFinder(ast.NodeVisitor):
    def __init__(self, node):
        ast.NodeVisitor.__init__(self)
        self.class_name = ""
        self.root_node = node
        self.class_node = None

    def visit_ClassDef(self, node):
        if node.name == self.class_name:
            self.class_node = node

    def find(self, class_name):
        self.class_name = class_name
        self.visit(self.root_node)
        return self.class_node


class CKClass:
    def __init__(self, name, descriptor, symbol_table, ast_node):
        self.name = name
        self.descriptor = descriptor
        self.symbol_table = symbol_table
        self.instance_variables = set([])
        self.methods = set([])
        self.foreign_references = {}
        self.coupled_structures = set([])
        self.instance_variables_per_method = {}
        self.method_complexities = {}
        self.function_calls = 0
        self.ast_node = ast_node
        self.depth_of_inheritance_tree = 0
        self.number_of_children = 0
        self.coupling_between_objects = 0
        self.lack_of_cohesion_of_methods = 0
        self.weighted_methods_per_class = 0
        self.response_for_class = 0

    def measure_depth_of_inheritance_tree(self):
        self.depth_of_inheritance_tree = self.get_dit_recursively(self.descriptor, 0)

    def get_dit_recursively(self, current_class, current_depth):
        # if type(current_class) == str:
        #     print current_class
        if current_class == "object":
            return current_depth - 1
        if current_class == "Exception":
            return current_depth
        if len(current_class.super) == 0:
            return current_depth
        max_depth = current_depth
        for super_class in current_class.super:
            depth = self.get_dit_recursively(super_class, current_depth + 1)
            max_depth = max(depth, max_depth)
        return max_depth

    def extract_references(self):
        try:
            debug = False
            # if self.name == 'DNA':
            #     debug = True
            symbol_extractor = InstanceSymbolsExtractor(self.ast_node, self.symbol_table, debug)
            try:
                symbol_extractor.extract()
            except TypeError:
                print self.name
                raise
            self.foreign_references = symbol_extractor.foreign_references
            try:
                self.foreign_references['<unknown>'].remove(self.name)
            except KeyError:
                pass
            reference_tuples = [tuple(self.foreign_references[reference])
                                for reference in self.foreign_references.keys()]
            self.coupled_structures = set(reference_tuples)
            # if self.name == 'Game':
            #     for game_var in self.foreign_references.keys():
            #         print game_var + ": " + str(self.foreign_references[game_var])
            self.instance_variables = symbol_extractor.instance_references
            self.methods = symbol_extractor.methods
            self.instance_variables_per_method = symbol_extractor.instance_variables_per_method
            self.method_complexities = symbol_extractor.method_complexities
            self.function_calls = symbol_extractor.function_calls
        except ValueError:
            print self.name
            raise

    def has_symbol(self, symbol):
        if type(symbol) == str:
            return symbol in self.instance_variables or symbol in self.methods
        for sym in symbol:
            if not sym in self.instance_variables:
                if not sym in self.methods:
                    return False
        return True

    def get_foreign_symbols(self):
        return self.foreign_references

    def measure_coupling_between_objects(self, class_list):
        # if self.name == 'DNA':
        #     print self.foreign_references
        self.coupling_between_objects = len(self.coupled_structures)
        # for ck_class in class_list:
        #     for symbol in self.foreign_references:
        #         if ck_class.has_symbol(symbol) and ck_class.name != self.name:
        #             self.coupling_between_objects += 1
        #             break

    def measure_lack_of_cohesion_of_methods(self):
        ideal_cohesion = len(self.instance_variables) * len(self.methods)
        if ideal_cohesion > 0:
            real_cohesion = 0.0
            for instance_variable in self.instance_variables:
                methods_using_variable = set([method for method in self.methods
                                              if instance_variable in self.instance_variables_per_method[method]])
                real_cohesion += len(methods_using_variable)
            self.lack_of_cohesion_of_methods = 1.0 - (real_cohesion / ideal_cohesion)

    def measure_weighted_methods_per_class(self):
        self.weighted_methods_per_class = sum([self.method_complexities[method] for method in self.methods])

    def measure_response_for_class(self):
        self.response_for_class = self.function_calls + len(self.methods)



class CKModule(CKClass):
    def __init__(self, name="", path=None, file_name="<unknown>", code=None):
        CKClass.__init__(self, name, None, None, None)
        self.path = path
        self.descriptor = pyclbr.readmodule_ex(self.name, path)
        self.file_name = file_name
        self.code = code
        if self.code:
            self.symbol_table = symtable.symtable(self.code, self.file_name, 'exec')
            self.ast_node = ast.parse(self.code, self.file_name)
        self.classes = {}
        class_node_finder = ClassNodeFinder(self.ast_node)
        for class_name in self.descriptor.keys():
            class_descriptor = self.descriptor[class_name]
            if isinstance(class_descriptor, pyclbr.Class):
                if class_descriptor.module == self.name:
                    class_table = self.symbol_table.lookup(class_name).get_namespace()
                    class_node = class_node_finder.find(class_name)
                    ck_class = CKClass(class_name, class_descriptor, class_table, class_node)
                    ck_class.extract_references()
                    self.classes[self.name + "." + class_name] = ck_class

    def measure_depth_of_inheritance_tree(self):
        #print "Module: " + self.name
        for class_name in self.classes.keys():
            ck_class = self.classes[class_name]
            ck_class.measure_depth_of_inheritance_tree()

    def has_symbol(self, symbol):
        if type(symbol).__name__ == 'str':
            return symbol in self.symbol_table.get_identifiers()
        for sym in symbol:
            if not sym in self.symbol_table.get_identifiers():
                return False
        return True


class CKProject(CKClass):
    @staticmethod
    def get_modules(arg, dirname, names):
        for name in names:
            if name.endswith(".py"):
                #print dirname + " " + name
                module_name = name
                file_name = os.path.join(dirname, name)
                if dirname != arg.project_path:
                    module_name = file_name
                    module_name = module_name.split(arg.project_path)[1]
                    module_name = module_name[len(os.sep):]
                    module_name = module_name.replace(os.sep, '.')
                module_code = open(file_name).read()
                ck_module = CKModule(module_name[:-3], arg.path, file_name, module_code)
                arg.modules.append(ck_module)
                arg.classes.update(ck_module.classes)

    def __init__(self, name="", project_path=None, path=None):
        CKClass.__init__(self, name, None, None, None)
        self.path = (path or []) + [project_path]
        self.project_path = project_path
        self.classes = {}
        self.modules = []
        os.path.walk(self.project_path, CKProject.get_modules, self)

    def measure_depth_of_inheritance_tree(self):
        for ck_module in self.modules:
            ck_module.measure_depth_of_inheritance_tree()

    def measure_number_of_children(self):
        for class_name in self.classes.keys():
            ck_class = self.classes[class_name]
            super_classes = ck_class.descriptor.super
            for super_class in super_classes:
                if type(super_class) != str:
                    full_name = super_class.module + "." + super_class.name
                    self.classes[full_name].number_of_children += 1

    def has_class(self, class_name):
        for full_name in self.classes.keys():
            if full_name.split(".")[1] == class_name:
                return True
        return False

    def measure_coupling_between_objects(self, class_list):
        ck_class_list = [self.classes[class_name] for class_name in self.classes]
        for ck_class in ck_class_list:
            ck_class.measure_coupling_between_objects(ck_class_list + self.modules)

    def measure_lack_of_cohesion_of_methods(self):
        ck_class_list = [self.classes[class_name] for class_name in self.classes]
        for ck_class in ck_class_list:
            ck_class.measure_lack_of_cohesion_of_methods()

    def measure_weighted_methods_per_class(self):
        ck_class_list = [self.classes[class_name] for class_name in self.classes]
        for ck_class in ck_class_list:
            ck_class.measure_weighted_methods_per_class()

    def measure_response_for_class(self):
        ck_class_list = [self.classes[class_name] for class_name in self.classes]
        for ck_class in ck_class_list:
            ck_class.measure_response_for_class()


def __tests():
    # ck_module = CKModule("game", [os.path.join(os.getcwd(), "tests", "Mutagenesis", "Code")])
    # for ck_class in ck_module.classes:
    #     print ck_class.name + ":"
    #     ck_class.measure_depth_of_inheritance_tree()
    #     print "\tDIT: " + str(ck_class.depth_of_inheritance_tree)
    # print ""
    this = os.path.dirname(__file__)
    sys.path.insert(0, os.path.join(this, "tests", "Mutagenesis", "Code"))
    ck_project = CKProject("Mutagenesis", os.path.join(this, "tests", "Mutagenesis", "Code"), None)
    ck_project.measure_depth_of_inheritance_tree()
    ck_project.measure_number_of_children()
    ck_project.measure_coupling_between_objects(None)
    ck_project.measure_lack_of_cohesion_of_methods()
    ck_project.measure_weighted_methods_per_class()
    ck_project.measure_response_for_class()
    for ck_module in ck_project.modules:
        print "Module: " + ck_module.name
        for ck_class in ck_module.classes.keys():
            print "\t" + ck_class + ":"
            print "\t\tDIT: " + str(ck_module.classes[ck_class].depth_of_inheritance_tree)
            print "\t\tNOC: " + str(ck_module.classes[ck_class].number_of_children)
            print "\t\tCBO: " + str(ck_module.classes[ck_class].coupling_between_objects)
            print "\t\tLCOM: " + str(ck_module.classes[ck_class].lack_of_cohesion_of_methods)
            print "\t\tWMC: " + str(ck_module.classes[ck_class].weighted_methods_per_class)
            print "\t\tRFC: " + str(ck_module.classes[ck_class].response_for_class)
            print ""
        print ""


if __name__ == '__main__':
    __tests()