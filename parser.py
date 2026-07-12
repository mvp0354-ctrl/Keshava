# parser.py
#
# Recursive-descent parser for Keshava.
# Converts a flat list of tokens (produced by lexer.py) into an AST
# built out of the node classes defined in ast_nodes.py.

from ast_nodes import (
    Program, VarDeclaration, Assignment, Print, If, While,
    Function, Return, FunctionCall, BinaryOp, Number, String,
    Boolean, Identifier, Input
)

# Datatype keywords that introduce a variable declaration.
DATATYPE_KINDS = ("INT", "STRING", "BOOL")

# Comparison / equality operators.
COMPARISON_KINDS = ("EQ", "NE", "LT", "GT", "LE", "GE")


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def peek(self, offset=0):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return (None, None)

    def current(self):
        return self.peek()

    def advance(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def check(self, kind):
        return self.peek()[0] == kind

    def is_string_literal(self, tok):
        # STRING is used both for the literal token ("...") and for the
        # 'Paatha' datatype keyword, since they share the same lexer kind.
        kind, value = tok
        return kind == "STRING" and value.startswith('"')

    def is_string_keyword(self, tok):
        kind, value = tok
        return kind == "STRING" and not value.startswith('"')

    def expect(self, kind):
        tok = self.peek()
        if tok[0] != kind:
            raise ParserError(
                f"Expected token {kind} but got {tok} at position {self.pos}"
            )
        return self.advance()

    def match(self, *kinds):
        if self.peek()[0] in kinds:
            return self.advance()
        return None

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def parse(self):
        self.expect("START")
        statements = []
        while not self.check("END"):
            statements.append(self.parse_statement())
        self.expect("END")
        return Program(statements)

    # ------------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------------

    def parse_block(self):
        self.expect("LBRACE")
        statements = []
        while not self.check("RBRACE"):
            statements.append(self.parse_statement())
        self.expect("RBRACE")
        return statements

    def parse_statement(self):
        kind, value = self.current()

        # Variable declaration: Sankhya / Paatha / Satyam <id> = <expr>
        if kind in DATATYPE_KINDS or self.is_string_keyword((kind, value)):
            return self.parse_var_declaration()

        if kind == "PRINT":
            return self.parse_print()

        if kind == "IF":
            return self.parse_if()

        if kind == "WHILE":
            return self.parse_while()

        if kind == "FUNCTION":
            return self.parse_function()

        if kind == "RETURN":
            return self.parse_return()

        if kind == "IDENTIFIER":
            # Could be an assignment or a bare function call statement.
            if self.peek(1)[0] == "ASSIGN":
                return self.parse_assignment()
            if self.peek(1)[0] == "LPAREN":
                call = self.parse_function_call()
                self.match("SEMICOLON")
                return call

        raise ParserError(f"Unexpected token {self.current()} at position {self.pos}")

    def parse_var_declaration(self):
        datatype_tok = self.advance()  # INT, STRING(keyword) or BOOL
        datatype = datatype_tok[1]
        name_tok = self.expect("IDENTIFIER")
        self.expect("ASSIGN")
        value = self.parse_expression()
        self.match("SEMICOLON")
        return VarDeclaration(datatype, name_tok[1], value)

    def parse_assignment(self):
        name_tok = self.expect("IDENTIFIER")
        self.expect("ASSIGN")
        value = self.parse_expression()
        self.match("SEMICOLON")
        return Assignment(name_tok[1], value)

    def parse_print(self):
        self.expect("PRINT")
        self.expect("LPAREN")
        value = self.parse_expression()
        self.expect("RPAREN")
        self.match("SEMICOLON")
        return Print(value)

    def parse_if(self):
        self.expect("IF")
        self.expect("LPAREN")
        condition = self.parse_expression()
        self.expect("RPAREN")
        true_block = self.parse_block()
        false_block = None
        if self.match("ELSE"):
            false_block = self.parse_block()
        return If(condition, true_block, false_block)

    def parse_while(self):
        self.expect("WHILE")
        self.expect("LPAREN")
        condition = self.parse_expression()
        self.expect("RPAREN")
        body = self.parse_block()
        return While(condition, body)

    def parse_function(self):
        self.expect("FUNCTION")
        name_tok = self.expect("IDENTIFIER")
        self.expect("LPAREN")
        params = []
        if not self.check("RPAREN"):
            params.append(self.expect("IDENTIFIER")[1])
            while self.match("COMMA"):
                params.append(self.expect("IDENTIFIER")[1])
        self.expect("RPAREN")
        body = self.parse_block()
        return Function(name_tok[1], params, body)

    def parse_return(self):
        self.expect("RETURN")
        value = None
        if not self.check("RBRACE"):
            value = self.parse_expression()
        self.match("SEMICOLON")
        return Return(value)

    def parse_function_call(self):
        name_tok = self.expect("IDENTIFIER")
        self.expect("LPAREN")
        args = []
        if not self.check("RPAREN"):
            args.append(self.parse_expression())
            while self.match("COMMA"):
                args.append(self.parse_expression())
        self.expect("RPAREN")
        return FunctionCall(name_tok[1], args)

    # ------------------------------------------------------------------
    # Expressions (precedence climbing)
    # ------------------------------------------------------------------

    def parse_expression(self):
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_term()
        while self.peek()[0] in COMPARISON_KINDS:
            op_tok = self.advance()
            right = self.parse_term()
            left = BinaryOp(left, op_tok[1], right)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.peek()[0] in ("PLUS", "MINUS"):
            op_tok = self.advance()
            right = self.parse_factor()
            left = BinaryOp(left, op_tok[1], right)
        return left

    def parse_factor(self):
        left = self.parse_primary()
        while self.peek()[0] in ("MULT", "DIV", "MOD"):
            op_tok = self.advance()
            right = self.parse_primary()
            left = BinaryOp(left, op_tok[1], right)
        return left

    def parse_primary(self):
        tok = self.current()
        kind, value = tok

        if kind == "NUMBER":
            self.advance()
            return Number(value)

        if self.is_string_literal(tok):
            self.advance()
            return String(value)

        if kind == "TRUE":
            self.advance()
            return Boolean(True)

        if kind == "FALSE":
            self.advance()
            return Boolean(False)

        if kind == "INPUT":
            self.advance()
            self.expect("LPAREN")
            self.expect("RPAREN")
            return Input()

        if kind == "LPAREN":
            self.advance()
            expr = self.parse_expression()
            self.expect("RPAREN")
            return expr

        if kind == "IDENTIFIER":
            if self.peek(1)[0] == "LPAREN":
                return self.parse_function_call()
            self.advance()
            return Identifier(value)

        raise ParserError(f"Unexpected token {tok} at position {self.pos}")
