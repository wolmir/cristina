from astmonkey import visitors, transformers


def ast_to_source_file(ast_node, file_path):
    with open(file_path, 'w') as source_file:
        source_code = visitors.to_source(ast_node)
        source_file.write(source_code)


def __tests():
    import ast
    with open('tests/function_def_test.py') as test_code:
        test_node = ast.parse(test_code.read())
        node = transformers.ParentNodeTransformer().visit(test_node)
        visitor = visitors.GraphNodeVisitor()
        visitor.visit(node)

        visitor.graph.write_png('graph.png')
        # atc_visitor = AstToCodeVisitor()
        # atc_visitor.visit(test_node)
        # print ast.dump(test_node)
        # print atc_visitor.code_so_far


if __name__ == '__main__':
    __tests()


# class AstToCodeVisitor(ast.NodeVisitor):
#     def __init__(self, tab='    '):
#         ast.NodeVisitor.__init__(self)
#         self.tab = tab
#         self.code_so_far = ""
#         self.current_tab_number = 0
#
#     def visit_Module(self, node):
#         for stmt in node.body:
#             self.visit(stmt)
#             self.increment_code('\n')
#
#     def visit_Interactive(self, node):
#         for stmt in node.body:
#             self.visit(stmt)
#             self.increment_code('\n')
#
#     def visit_Expression(self, node):
#         self.visit(node.body)
#
#     def visit_FunctionDef(self, node):
#         if len(node.decorator_list) > 0:
#             for decorator in node.decorator_list:
#                 self.increment_code(self.get_current_tabulation() + '@')
#                 local_tab = self.current_tab_number
#                 self.current_tab_number = 0
#                 self.visit(decorator)
#                 self.current_tab_number = local_tab
#                 self.increment_code('\n')
#         self.increment_code(self.get_current_tabulation() + 'def ')
#         self.increment_code(node.name + '(')
#         local_tab = self.current_tab_number
#         self.current_tab_number = 0
#         arguments = node.args
#         simple_arguments = arguments.args
#         complex_arguments = []
#         if len(arguments.defaults) > 0:
#             simple_arguments = arguments.args[:-len(arguments.defaults)]
#             complex_arguments = arguments.args[-len(arguments.defaults):]
#         for simple_arg in simple_arguments:
#             self.visit(simple_arg)
#             self.increment_code(', ')
#         if len(complex_arguments) > 0:
#             for defaulted_arg_index in range(len(complex_arguments)):
#                 defaulted_arg = complex_arguments[defaulted_arg_index]
#                 self.visit(defaulted_arg)
#                 self.increment_code('=')
#                 self.visit(arguments.defaults[defaulted_arg_index])
#                 self.increment_code(', ')
#         if arguments.vararg:
#             self.increment_code('*' + arguments.vararg)
#             self.increment_code(', ')
#         if arguments.kwarg:
#             self.increment_code('**' + arguments.kwarg)
#             self.increment_code(', ')
#         self.code_so_far = self.code_so_far[:-2]
#         self.increment_code('):\n')
#         self.current_tab_number = local_tab
#         self.current_tab_number += 1
#         for statement in node.body:
#             self.visit(statement)
#             self.increment_code('\n')
#         self.increment_code('\n')
#         self.current_tab_number -= 1
#
#     def visit_Import(self, node):
#         self.increment_code(self.get_current_tabulation() + "import ")
#         for alias in node.names:
#             self.code_so_far += alias.name
#             if alias.asname:
#                 self.increment_code(" as " + alias.asname)
#             self.increment_code(', ')
#         self.code_so_far = self.code_so_far[:-2]
#
#     def visit_ImportFrom(self, node):
#         self.increment_code(self.get_current_tabulation() + "from ")
#         if node.module:
#             self.increment_code(node.module)
#         else:
#             self.increment_code('.' * node.level)
#         self.increment_code(" import ")
#         for alias in node.names:
#             self.increment_code(alias.name)
#             if alias.asname:
#                 self.increment_code(" as " + alias.asname)
#             self.increment_code(', ')
#         self.code_so_far = self.code_so_far[:-2]
#
#     def visit_ClassDef(self, node):
#         if len(node.decorator_list) > 0:
#             for decorator in node.decorator_list:
#                 self.increment_code(self.get_current_tabulation() + '@')
#                 local_tab = self.current_tab_number
#                 self.current_tab_number = 0
#                 self.visit(decorator)
#                 self.current_tab_number = local_tab
#                 self.increment_code('\n')
#         self.increment_code(self.get_current_tabulation() + "class ")
#         self.increment_code(node.name)
#         if len(node.bases) > 0:
#             self.increment_code('(')
#             for base in node.bases:
#                 local_tab = self.current_tab_number
#                 self.current_tab_number = 0
#                 self.visit(base)
#                 self.current_tab_number = local_tab
#             self.increment_code(')')
#         self.increment_code(':\n')
#         self.current_tab_number += 1
#         for stmt in node.body:
#             self.visit(stmt)
#             self.increment_code('\n')
#         self.increment_code('\n')
#         self.current_tab_number -= 1
#
#     def visit_Return(self, node):
#         self.increment_code(self.get_current_tabulation() + 'return')
#         if node.value:
#             self.increment_code(' ')
#             local_tab = self.current_tab_number
#             self.current_tab_number = 0
#             self.visit(node.value)
#             self.current_tab_number = local_tab
#
#     def visit_Delete(self, node):
#         self.increment_code(self.get_current_tabulation() + 'del ')
#         local_tab = self.current_tab_number
#         self.current_tab_number = 0
#         for target in node.targets:
#             self.visit(target)
#             self.increment_code(', ')
#         self.code_so_far = self.code_so_far[:-2]
#         self.current_tab_number = local_tab
#
#     def visit_Assign(self, node):
#         self.increment_code(self.get_current_tabulation())
#         local_tab = self.current_tab_number
#         self.current_tab_number = 0
#         for target in node.targets:
#             self.visit(target)
#             self.increment_code(', ')
#         self.code_so_far = self.code_so_far[:-2]
#         self.increment_code(' = ')
#         self.visit(node.value)
#         self.current_tab_number = local_tab
#
#     def visit_AugAssign(self, node):
#         self.increment_code(self.get_current_tabulation())
#         local_tab = self.current_tab_number
#         self.current_tab_number = 0
#         self.visit(node.target)
#         self.increment_code(' ')
#         self.visit(node.op)
#         self.increment_code('= ')
#         self.visit(node.value)
#         self.current_tab_number = local_tab
#
#     def visit_Print(self, node):
#         self.increment_code(self.get_current_tabulation() + 'print ')
#         local_tab = self.current_tab_number
#         self.current_tab_number = 0
#         if node.dest:
#             self.increment_code('>> ')
#             self.visit(node.dest)
#             self.increment_code(', ')
#         for value in node.values:
#             self.visit(value)
#             self.increment_code(', ')
#         if node.nl:
#             self.code_so_far = self.code_so_far[:-2]
#         else:
#             self.code_so_far = self.code_so_far[:-1]
#         self.current_tab_number = local_tab
#
#     def visit_For(self, node):
#         self.increment_code(self.get_current_tabulation() + 'for ')
#         local_tab = self.current_tab_number
#         self.current_tab_number = 0
#         self.visit(node.target)
#         self.increment_code(' in ')
#         self.visit(node.iter)
#         self.increment_code(':\n')
#         self.current_tab_number = local_tab + 1
#         for stmt in node.body:
#             self.visit(stmt)
#             self.increment_code('\n')
#         self.current_tab_number -= 1
#         if len(node.orelse) > 0:
#             self.increment_code(self.get_current_tabulation() + 'else:\n')
#             self.current_tab_number += 1
#             for stmt in node.orelse:
#                 self.visit(stmt)
#                 self.increment_code('\n')
#             self.current_tab_number -= 1
#
#     def visit_While(self, node):
#         self.increment_code(self.get_current_tabulation() + 'while ')
#         local_tab = self.current_tab_number
#         self.current_tab_number = 0
#         self.visit(node.test)
#         self.increment_code(':\n')
#         self.current_tab_number = local_tab + 1
#         for stmt in node.body:
#             self.visit(stmt)
#             self.increment_code('\n')
#         self.current_tab_number -= 1
#         if len(node.orelse) > 0:
#             self.increment_code(self.get_current_tabulation() + 'else:\n')
#             self.current_tab_number += 1
#             for stmt in node.orelse:
#                 self.visit(stmt)
#                 self.increment_code('\n')
#             self.current_tab_number -= 1
#
#     def visit_If(self, node):
#         self.increment_code(self.get_current_tabulation() + 'if ')
#         local_tab = self.current_tab_number
#         self.current_tab_number = 0
#         self.visit(node.test)
#         self.increment_code(':\n')
#         self.current_tab_number = local_tab + 1
#         for stmt in node.body:
#             self.visit(stmt)
#             self.increment_code('\n')
#         self.current_tab_number -= 1
#         if len(node.orelse) > 0:
#             self.increment_code(self.get_current_tabulation() + 'else:\n')
#             self.current_tab_number += 1
#             for stmt in node.orelse:
#                 self.visit(stmt)
#                 self.increment_code('\n')
#             self.current_tab_number -= 1
#
#     def visit_With(self, node):
#         self.increment_code(self.get_current_tabulation() + 'with ')
#         local_tab = self.current_tab_number
#         self.current_tab_number = 0
#         self.visit(node.context_expr)
#         if node.optional_vars:
#             self.increment_code(' as ')
#             self.visit(node.optional_vars)
#         self.increment_code(':\n')
#         self.current_tab_number = local_tab + 1
#         for stmt in node.body:
#             self.visit(stmt)
#             self.increment_code('\n')
#         self.current_tab_number -= 1
#
#     def visit_Raise(self, node):
#         self.increment_code(self.get_current_tabulation() + 'raise ')
#         local_tab = self.current_tab_number
#         self.current_tab_number = 0
#         if node.type:
#             self.visit(node.type)
#         if node.inst:
#             self.increment_code(', ')
#             self.visit(node.inst)
#         if node.tback:
#             self.increment_code(', ')
#             self.visit(node.tback)
#         self.current_tab_number = local_tab
#
#     def visit_Name(self, node):
#         self.increment_code(self.get_current_tabulation() + node.id)
#
#     def get_current_tabulation(self):
#         return self.current_tab_number * self.tab
#
#     def increment_code(self, code):
#         self.code_so_far += code