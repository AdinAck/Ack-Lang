import re
from webbrowser import Opera

from utils.tokens import EOL, Fragment, Type, Operator, Literal, Variable

class Lexer:
    statements: list[str]
    
    SPECIAL_CHARS: str = ''
    DELIMITER: str = '\n}{'
    WHITESPACE: str = ' \t\r\n'
    
    def __init__(self, filename: str):
        with open(filename, 'r') as f:
            raw = f.read()
        
        self.statements = [s.strip(self.WHITESPACE) for s in re.split(f'[{self.DELIMITER}]', raw)]
    
    def parse_statements(self):
        for statement in self.statements:
            x = [token for token in statement.split(' ') if token]
            yield from self.parse_statement(x)
    
    def parse_statement(self, statement: list[str]):
        for token in statement:
            if Type.check(token):
                yield Type(token)
            elif Variable.check(token):
                yield Variable(token)
            elif Operator.check(token):
                yield Operator(token)
            elif Literal.check(token):
                yield Literal(token)
            else:
                yield Fragment(token)
        
        yield EOL