# ast_nodes.py

class ASTNode:
    pass


# ===========================
# Program Node
# ===========================

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Program({self.statements})"


# ===========================
# Variable Declaration
# Example:
# Sankhya age = 20
# ===========================

class VarDeclaration(ASTNode):
    def __init__(self, datatype, name, value):
        self.datatype = datatype
        self.name = name
        self.value = value

    def __repr__(self):
        return f"VarDeclaration({self.datatype}, {self.name}, {self.value})"


# ===========================
# Assignment
# Example:
# age = age + 1
# ===========================

class Assignment(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"Assignment({self.name}, {self.value})"


# ===========================
# Print Statement
# Example:
# Likha(age)
# ===========================

class Print(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Print({self.value})"


# =================name==========
# If Statement
# ===========================

class If(ASTNode):
    def __init__(self, condition, true_block, false_block=None):
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block

    def __repr__(self):
        return f"If({self.condition})"


# ===========================
# While Loop
# ===========================

class While(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"While({self.condition})"


# ===========================
# Function
# ===========================

class Function(ASTNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

    def __repr__(self):
        return f"Function({self.name})"


# ===========================
# Return Statement
# ===========================

class Return(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Return({self.value})"


# ===========================
# Function Call
# ===========================

class FunctionCall(ASTNode):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def __repr__(self):
        return f"FunctionCall({self.name})"


# ===========================
# Binary Operation
# Example:
# a + b
# a > b
# ===========================

class BinaryOp(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"({self.left} {self.operator} {self.right})"


# ===========================
# Number
# ===========================

class Number(ASTNode):
    def __init__(self, value):
        self.value = int(value)

    def __repr__(self):
        return str(self.value)


# ===========================
# String
# ===========================

class String(ASTNode):
    def __init__(self, value):
        self.value = value.strip('"')

    def __repr__(self):
        return self.value


# ===========================
# Boolean
# ===========================

class Boolean(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)


# ===========================
# Identifier
# Example:
# age
# marks
# ===========================

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class Input(ASTNode):
    def __init__(self):
        pass

    def __repr__(self):
        return "Input()"