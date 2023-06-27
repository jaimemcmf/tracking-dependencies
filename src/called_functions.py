import ast
from collections import deque
        
class FuncCallVisitor(ast.NodeVisitor):
    def __init__(self):
        self._name = deque()

    @property
    def name(self):
        return '.'.join(self._name)

    @name.deleter
    def name(self):
        self._name.clear()

    def visit_Name(self, node):
        self._name.appendleft(node.id)

    def visit_Attribute(self, node):
        try:
            self._name.appendleft(node.attr)
            self._name.appendleft(node.value.id)
        except AttributeError:
            self.generic_visit(node)


def get_func_calls(tree):
    l = []
    ret = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            l = []
            callvisitor = FuncCallVisitor()
            callvisitor.visit(node.func)
            l.append(callvisitor.name)
            for arg in node.args:
                try:
                    l.append(arg.id)
                except:
                    pass
                try:
                    l.append(arg.value)
                except:
                    pass
            ret.append(l)
            l.clear
    return ret
