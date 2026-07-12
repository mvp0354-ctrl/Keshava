# interpreter.py
#
# Tree-walking interpreter for Keshava.
# Executes the AST produced by parser.py.

from ast_nodes import (
    Program, VarDeclaration, Assignment, Print, If, While,
    Function, Return, FunctionCall, BinaryOp, Number, String,
    Boolean, Identifier, Input
)


class ReturnSignal(Exception):
    """Used internally to unwind the call stack on a return statement."""
    def __init__(self, value):
        self.value = value


class msmRuntimeError(Exception):
    pass


class Environment:
    """A single scope of variables, chained to its parent scope."""

    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def declare(self, name, value):
        self.vars[name] = value

    def get(self, name):
        env = self
        while env is not None:
            if name in env.vars:
                return env.vars[name]
            env = env.parent
        raise msmRuntimeError(f"Undefined variable '{name}'")

    def set(self, name, value):
        env = self
        while env is not None:
            if name in env.vars:
                env.vars[name] = value
                return
            env = env.parent
        # If it was never declared, define it in the current scope.
        self.vars[name] = value


class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.functions = {}

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def run(self, program: Program):
        for statement in program.statements:
            self.execute(statement, self.global_env)

    # ------------------------------------------------------------------
    # Statement execution
    # ------------------------------------------------------------------

    def execute(self, node, env):
        method_name = f"exec_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise msmRuntimeError(f"No exec method for node type {type(node).__name__}")
        return method(node, env)

    def exec_VarDeclaration(self, node: VarDeclaration, env):
        value = self.evaluate(node.value, env)
        if isinstance(node.value, Input):
            value = self.coerce_input_value(value, node.datatype)
        env.declare(node.name, value)

    def exec_Assignment(self, node: Assignment, env):
        value = self.evaluate(node.value, env)
        if isinstance(node.value, Input):
            value = self.coerce_input_value(value, None)
        env.set(node.name, value)

    def exec_Print(self, node: Print, env):
        value = self.evaluate(node.value, env)
        print(self.stringify(value))

    def exec_If(self, node: If, env):
        if self.evaluate(node.condition, env):
            self.execute_block(node.true_block, Environment(env))
        elif node.false_block is not None:
            self.execute_block(node.false_block, Environment(env))

    def exec_While(self, node: While, env):
        while self.evaluate(node.condition, env):
            self.execute_block(node.body, Environment(env))

    def exec_Function(self, node: Function, env):
        self.functions[node.name] = node

    def exec_Return(self, node: Return, env):
        value = self.evaluate(node.value, env) if node.value is not None else None
        raise ReturnSignal(value)

    def exec_FunctionCall(self, node: FunctionCall, env):
        # A function call used as a standalone statement.
        self.call_function(node, env)

    def execute_block(self, statements, env):
        for statement in statements:
            self.execute(statement, env)

    # ------------------------------------------------------------------
    # Expression evaluation
    # ------------------------------------------------------------------

    def evaluate(self, node, env):
        method_name = f"eval_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise msmRuntimeError(f"No eval method for node type {type(node).__name__}")
        return method(node, env)

    def eval_Number(self, node: Number, env):
        return node.value

    def eval_String(self, node: String, env):
        return node.value

    def eval_Boolean(self, node: Boolean, env):
        return node.value

    def eval_Input(self, node: Input, env):
        return input()

    def eval_Identifier(self, node: Identifier, env):
        return env.get(node.name)

    def eval_FunctionCall(self, node: FunctionCall, env):
        return self.call_function(node, env)

    def eval_BinaryOp(self, node: BinaryOp, env):
        left = self.evaluate(node.left, env)
        right = self.evaluate(node.right, env)
        op = node.operator

        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            return left / right
        if op == "%":
            return left % right
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        if op == "<":
            return left < right
        if op == ">":
            return left > right
        if op == "<=":
            return left <= right
        if op == ">=":
            return left >= right

        raise msmRuntimeError(f"Unknown operator '{op}'")

    # ------------------------------------------------------------------
    # Function calls
    # ------------------------------------------------------------------

    def call_function(self, node: FunctionCall, env):
        if node.name not in self.functions:
            raise msmRuntimeError(f"Undefined function '{node.name}'")

        func = self.functions[node.name]
        if len(func.params) != len(node.arguments):
            raise msmRuntimeError(
                f"Function '{node.name}' expects {len(func.params)} argument(s), "
                f"got {len(node.arguments)}"
            )

        call_env = Environment(self.global_env)
        for param, arg_expr in zip(func.params, node.arguments):
            call_env.declare(param, self.evaluate(arg_expr, env))

        try:
            self.execute_block(func.body, call_env)
        except ReturnSignal as ret:
            return ret.value

        return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def stringify(value):
        if value is True:
            return "Satya"
        if value is False:
            return "Asatya"
        if value is None:
            return ""
        return str(value)

    @staticmethod
    def coerce_input_value(value, datatype):
        if datatype in {"Sankhya", "INT"}:
            return int(value)
        if datatype in {"Satyam", "BOOL"}:
            return str(value).strip().lower() in {"true", "satya", "1", "yes"}
        return str(value)
