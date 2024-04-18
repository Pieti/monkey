from enum import IntEnum
from typing import Callable

from monkey import ast
from monkey.lexer import Lexer
from monkey.token import Token, TokenType


class Precedence(IntEnum):
    LOWEST = 1
    EQUALS = 2
    LESSGREATER = 3
    SUM = 4
    PRODUCT = 5
    PREFIX = 6
    CALL = 7
    INDEX = 8


PRECEDENCES: dict[TokenType, int] = {
    TokenType.EQ: Precedence.EQUALS,
    TokenType.NOT_EQ: Precedence.EQUALS,
    TokenType.LT: Precedence.LESSGREATER,
    TokenType.GT: Precedence.LESSGREATER,
    TokenType.PLUS: Precedence.SUM,
    TokenType.MINUS: Precedence.SUM,
    TokenType.SLASH: Precedence.PRODUCT,
    TokenType.ASTERISK: Precedence.PRODUCT,
    TokenType.LPAREN: Precedence.CALL,
    TokenType.LBRACKET: Precedence.INDEX,
}


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer: Lexer = lexer

        self.cur_token: Token = self.lexer.next_token()
        self.peek_token: Token = self.lexer.next_token()

        self.infix_parsers: dict[
            TokenType, Callable[[ast.Expression], ast.Expression]
        ] = {
            TokenType.PLUS: self.parse_infix_expression,
            TokenType.MINUS: self.parse_infix_expression,
            TokenType.SLASH: self.parse_infix_expression,
            TokenType.ASTERISK: self.parse_infix_expression,
            TokenType.EQ: self.parse_infix_expression,
            TokenType.NOT_EQ: self.parse_infix_expression,
            TokenType.LT: self.parse_infix_expression,
            TokenType.GT: self.parse_infix_expression,
            TokenType.LPAREN: self.parse_call_expression,
            TokenType.LBRACKET: self.parse_index_expression,
        }

        self.prefix_parsers: dict[TokenType, Callable[[], ast.Expression]] = {
            TokenType.IDENT: self.parse_identifier,
            TokenType.INT: self.parse_integer_literal,
            TokenType.BANG: self.parse_prefix_expression,
            TokenType.MINUS: self.parse_prefix_expression,
            TokenType.TRUE: self.parse_boolean,
            TokenType.FALSE: self.parse_boolean,
            TokenType.LPAREN: self.parse_grouped_expression,
            TokenType.IF: self.parse_if_expression,
            TokenType.FUNCTION: self.parse_function_literal,
            TokenType.STRING: self.parse_string_literal,
            TokenType.LBRACKET: self.parse_array_literal,
            TokenType.LBRACE: self.parse_hash_literal,
        }

    def next_token(self) -> None:
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def cur_token_is(self, token_type: TokenType) -> bool:
        return self.cur_token.type == token_type

    def peek_token_is(self, token_type: TokenType) -> bool:
        return self.peek_token.type == token_type

    def expect_peek(self, token_type: TokenType) -> bool:
        if self.peek_token_is(token_type):
            self.next_token()
            return True
        return False

    def parse_program(self) -> ast.Program:
        statements = []
        while not self.cur_token_is(TokenType.EOF):
            stmt = self.parse_statement()
            statements.append(stmt)
            self.next_token()
        return ast.Program(statements=statements)

    def parse_statement(self) -> ast.Statement:
        if self.cur_token_is(TokenType.LET):
            return self.parse_let_statement()

        if self.cur_token_is(TokenType.RETURN):
            return self.parse_return_statement()

        return self.parse_expression_statement()

    def parse_let_statement(self) -> ast.LetStatement:
        let_token = self.cur_token

        assert self.expect_peek(TokenType.IDENT), "Expected IDENT after LET"

        name = ast.Identifier(token=self.cur_token, value=self.cur_token.literal)

        assert self.expect_peek(TokenType.ASSIGN), "Expected ASSIGN after IDENT"

        self.next_token()
        value = self.parse_expression(Precedence.LOWEST)

        if self.peek_token_is(TokenType.SEMICOLON):
            self.next_token()

        return ast.LetStatement(token=let_token, name=name, value=value)

    def parse_return_statement(self) -> ast.ReturnStatement:
        cur_token = self.cur_token

        self.next_token()

        return_value = self.parse_expression(Precedence.LOWEST)

        if self.peek_token_is(TokenType.SEMICOLON):
            self.next_token()

        return ast.ReturnStatement(token=cur_token, value=return_value)

    def parse_expression_statement(self) -> ast.ExpressionStatement:
        cur_token = self.cur_token

        expression = self.parse_expression(Precedence.LOWEST)

        if self.peek_token_is(TokenType.SEMICOLON):
            self.next_token()

        return ast.ExpressionStatement(token=cur_token, expression=expression)

    def parse_expression(self, precedence: int) -> ast.Expression:
        prefix_parser = self.prefix_parsers[self.cur_token.type]
        left_exp = prefix_parser()

        while (
            not self.peek_token_is(TokenType.SEMICOLON)
            and precedence < self.peek_precedence()
        ):
            infix_parser = self.infix_parsers.get(self.peek_token.type)
            if infix_parser is None:
                return left_exp
            self.next_token()

            left_exp = infix_parser(left_exp)

        return left_exp

    def parse_infix_expression(self, left: ast.Expression) -> ast.Expression:
        precedence = self.cur_precedence()
        token = self.cur_token
        self.next_token()
        right = self.parse_expression(precedence)
        return ast.InfixExpression(
            token=token,
            left=left,
            operator=token.literal,
            right=right,
        )

    def parse_call_expression(self, function: ast.Expression) -> ast.Expression:
        cur_token = self.cur_token
        arguments = self.parse_expression_list(TokenType.RPAREN)
        return ast.CallExpression(
            token=cur_token, function=function, arguments=arguments
        )

    def parse_index_expression(self, left: ast.Expression) -> ast.Expression:
        cur_token = self.cur_token

        self.next_token()
        index = self.parse_expression(Precedence.LOWEST)

        assert self.expect_peek(TokenType.RBRACKET), "Expected RBRACKET after index"

        return ast.IndexExpression(token=cur_token, left=left, index=index)

    def peek_precedence(self) -> int:
        return PRECEDENCES.get(self.peek_token.type, Precedence.LOWEST)

    def cur_precedence(self) -> int:
        return PRECEDENCES.get(self.cur_token.type, Precedence.LOWEST)

    def parse_identifier(self) -> ast.Expression:
        return ast.Identifier(token=self.cur_token, value=self.cur_token.literal)

    def parse_integer_literal(self) -> ast.Expression:
        value = int(self.cur_token.literal)
        return ast.IntegerLiteral(token=self.cur_token, value=value)

    def parse_boolean(self) -> ast.Expression:
        return ast.Boolean(
            token=self.cur_token, value=self.cur_token_is(TokenType.TRUE)
        )

    def parse_prefix_expression(self) -> ast.Expression:
        cur_token = self.cur_token
        operator = self.cur_token.literal

        self.next_token()
        right = self.parse_expression(Precedence.PREFIX)

        return ast.PrefixExpression(token=cur_token, operator=operator, right=right)

    def parse_grouped_expression(self) -> ast.Expression:
        self.next_token()

        exp = self.parse_expression(Precedence.LOWEST)

        assert self.expect_peek(TokenType.RPAREN), "Expected RPAREN grouped expression"

        return exp

    def parse_if_expression(self) -> ast.Expression:
        cur_token = self.cur_token

        assert self.expect_peek(TokenType.LPAREN), "Expected LPAREN after IF"

        self.next_token()
        condition = self.parse_expression(Precedence.LOWEST)

        assert self.expect_peek(TokenType.RPAREN), "Expected RPAREN after condition"
        assert self.expect_peek(TokenType.LBRACE), "Expected LBRACE after RPAREN"

        consequence = self.parse_block_statement()

        alternative = None
        if self.peek_token_is(TokenType.ELSE):
            self.next_token()

            assert self.expect_peek(TokenType.LBRACE), "Expected LBRACE after ELSE"

            alternative = self.parse_block_statement()

        return ast.IfExpression(
            token=cur_token,
            condition=condition,
            consequence=consequence,
            alternative=alternative,
        )

    def parse_block_statement(self) -> ast.BlockStatement:
        cur_token = self.cur_token

        statements = []
        self.next_token()

        while not self.cur_token_is(TokenType.RBRACE) and not self.cur_token_is(
            TokenType.EOF
        ):
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self.next_token()

        return ast.BlockStatement(token=cur_token, statements=statements)

    def parse_function_literal(self) -> ast.Expression:
        cur_token = self.cur_token

        assert self.expect_peek(TokenType.LPAREN), "Expected LPAREN after FUNCTION"

        parameters = self.parse_function_parameters()

        assert self.expect_peek(TokenType.LBRACE), "Expected LBRACE after LPAREN"

        body = self.parse_block_statement()

        return ast.FunctionLiteral(token=cur_token, parameters=parameters, body=body)

    def parse_function_parameters(self) -> list[ast.Identifier]:
        identifiers: list[ast.Identifier] = []

        if self.peek_token_is(TokenType.RPAREN):
            self.next_token()
            return identifiers

        self.next_token()

        ident = ast.Identifier(token=self.cur_token, value=self.cur_token.literal)
        identifiers.append(ident)

        while self.peek_token_is(TokenType.COMMA):
            self.next_token()
            self.next_token()
            ident = ast.Identifier(token=self.cur_token, value=self.cur_token.literal)
            identifiers.append(ident)

        if not self.expect_peek(TokenType.RPAREN):
            return []
        return identifiers

    def parse_string_literal(self) -> ast.Expression:
        return ast.StringLiteral(token=self.cur_token, value=self.cur_token.literal)

    def parse_array_literal(self) -> ast.Expression:
        cur_token = self.cur_token

        elements = self.parse_expression_list(TokenType.RBRACKET)

        return ast.ArrayLiteral(token=cur_token, elements=elements)

    def parse_expression_list(self, end: TokenType) -> list[ast.Expression]:
        expressions: list[ast.Expression] = []

        if self.peek_token_is(end):
            self.next_token()
            return expressions

        self.next_token()
        expressions.append(self.parse_expression(Precedence.LOWEST))

        while self.peek_token_is(TokenType.COMMA):
            self.next_token()
            self.next_token()
            expressions.append(self.parse_expression(Precedence.LOWEST))

        if not self.expect_peek(end):
            return []
        return expressions

    def parse_hash_literal(self) -> ast.Expression:
        cur_token = self.cur_token

        pairs = {}
        while not self.peek_token_is(TokenType.RBRACE):
            self.next_token()
            key = self.parse_expression(Precedence.LOWEST)

            assert self.expect_peek(TokenType.COLON), "Expected COLON after key"

            self.next_token()
            value = self.parse_expression(Precedence.LOWEST)

            pairs[key] = value

            assert self.peek_token_is(TokenType.RBRACE) or self.expect_peek(
                TokenType.COMMA
            ), "Expected RBRACE or COMMA"

        assert self.expect_peek(TokenType.RBRACE), "Expected RBRACE after hash literal"
        return ast.HashLiteral(token=cur_token, pairs=pairs)
