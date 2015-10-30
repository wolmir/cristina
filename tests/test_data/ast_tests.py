import ast
#import sys
import symtable
import lib2to3
from radon.complexity import cc_visit_ast
from astmonkey import visitors


class CloneVisitor(ast.NodeVisitor):
    def visit_Attribute(self, node):
        print "\t\t" + ast.dump(node)
        self.generic_visit(node)

    def visit_Call(self, node):
        self.generic_visit(node)

class DNAVisitor(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        print "\t" + node.name
        if node.name == "clone":
            print "\t\t" + ast.dump(node)
            CloneVisitor().visit(node)
            cc_result = cc_visit_ast(node)[0]
            print cc_result.name + ": " + str(cc_result.classname) + " " + str(cc_result.complexity)

class GameVisitor(ast.NodeVisitor):
    def visit_ClassDef(self, node):
        print node.name
        if node.name == "DNA":
            DNAVisitor().visit(node)
        return None

class StmtVisitor(ast.NodeVisitor):
    def visit(self, node):
        if hasattr(node, 'lineno'):
            node.lineno = 0
        self.generic_visit(node)


def prettify_dump(tree_dump, tab='    '):
    parentheses = 0
    brackets = 0
    current_tabs = 0
    pretty_dump = ""
    for c in range(len(tree_dump)):
        if tree_dump[c] == '(' and tree_dump[c + 1] != ')':
            parentheses += 1
            current_tabs += 1
            pretty_dump += " (\n" + (tab * current_tabs)
        elif tree_dump[c] == ')' and tree_dump[c - 1] != '(':
            parentheses -= 1
            current_tabs -= 1
            pretty_dump += "\n" + (tab * current_tabs) + ")\n" + (tab * current_tabs)
        elif tree_dump[c] == '[' and tree_dump[c + 1] != ']':
            brackets += 1
            current_tabs += 1
            pretty_dump += " [\n" + (tab * current_tabs)
        elif tree_dump[c] == ']' and tree_dump[c - 1] != '[':
            brackets -= 1
            current_tabs -= 1
            pretty_dump += "\n" + (tab * current_tabs) + "]\n" + (tab * current_tabs)
        elif tree_dump[c] == ',':
            pretty_dump += ',\n' + (tab * current_tabs)
        elif tree_dump[c] == ' ':
            pretty_dump += ''
        else:
            pretty_dump += tree_dump[c]
    return pretty_dump


def main():
    #print lib2to3.__dict__
    with open("game.py") as source_file:
        code = source_file.read()
        ast_node = ast.parse(code)
        print ast.dump(ast_node)
        StmtVisitor().visit(ast_node)
        #print visitors.to_source(ast_node)
        #GameVisitor().visit(ast_node)
        #print prettify_dump(ast.dump(ast_node))
        # symbol_table = symtable.symtable(code, "game.py", 'exec')
        # print symbol_table.get_identifiers()
        # print ""
        # nspc = symbol_table.lookup('Plant').get_namespace().lookup('__setstate__').get_namespace()
        # for symbol in nspc.get_identifiers():
        #     print symbol
        #     print "\t" + str(nspc.lookup(symbol).is_local())
        # print ("ahhdksadas" in symbol_table.get_identifiers())


if __name__ == '__main__':
    main()