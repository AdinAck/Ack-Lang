from atexit import register
from curses.ascii import isalpha, isdigit
from sys import argv
from rich import print
from utils.infix2postfix import Infix2Postfix

from utils.lexer import Lexer
from utils.tokens import Type, Variable, Operator, Literal, EOL

from typing import Generator, Optional
    
class Compiler:
    lexer: Lexer
    
    register_map: dict[int, str]
    register_counter: int
    
    memory_map: dict[str, int]
    memory_counter: int
    
    setup: list[str]
    body: list[str]
    wrap_up: list[str]
    
    def __init__(self, filename: str):
        self.lexer = Lexer(filename)
        
        self.register_map = {}
        self.register_counter = 10
        
        self.memory_map = {}
        self.memory_counter = 0
        
        self.setup = []
        self.body = []
        self.wrap_up = []
        
    def compile(self, filename: str):
        iterator = self.lexer.parse_statements()
        
        for s in iterator:
            if isinstance(s, Type):
                self.instantiate(s, iterator)
            elif isinstance(s, Variable):
                self.assign(s, iterator)
            
            self.body.append('')
        
        # memory map
        for var, loc in self.memory_map.items():
            self.setup.append(f'// {var}: {loc}')
        
        self.setup.append('')
        
        stack_size: int = (self.memory_counter // 16) * 16
        
        self.write(self.setup, f'subi sp, sp, #{stack_size}', f'allocate {stack_size} bytes on the stack')
        
        self.setup.append('')
        
        # wrap-up
        for var in self.memory_map:
            if (reg := self.reg_of(var)):
                self.write(self.wrap_up, f'stur x{reg}, [sp, #{self.memory_map[self.register_map[reg]]}]', f'store {var}')
        
        self.wrap_up.append('')
        
        self.write(self.wrap_up, f'addi sp, sp, #{stack_size}', f'deallocate {stack_size} bytes from the stack')
        
        # write out
        with open(filename, 'w') as f:
            for line in self.setup + self.body + self.wrap_up:
                f.write(line + '\n')
    
    def write(self, section: list[str], instruction: str, comment: Optional[str] = None):
        section.append(instruction + (f'\t// {comment}' if comment else ''))
    
    def allocate_register(self, var: Variable) -> tuple[int, bool]:
        if (current := self.reg_of(var.symbol)) is None:
            if (reg := self.register_counter) in self.register_map: # save variable if need be
                if (symbol := self.register_map[reg]) not in self.memory_map: # must be expression
                    self.memory_map[symbol] = self.memory_counter
                    self.memory_counter += 8
                                
                self.write(self.body, f'stur x{reg}, [sp, #{self.memory_map[symbol]}]', f'store {self.register_map[reg]}')
            
            if var.symbol in self.memory_map:
                # load variable into register
                self.write(self.body, f'ldur x{reg}, [sp, #{self.memory_map[var.symbol]}]', f'load {var.symbol}')
            
            self.register_map[reg] = var.symbol
            
            if self.register_counter >= 15: # wrap register_counter
                self.register_counter = 10
            else:
                self.register_counter += 1
        
            return reg, False
        else:
            return current, True
        
    def reg_of(self, symbol: str) -> Optional[int]:
        """
        TODO: This is implemented awfully, please refactor.
        """
        for reg, _var in self.register_map.items():
            if _var == symbol:
                return reg

        return None
    
    def is_int(self, symbol: str) -> bool:
        try:
            int(symbol)
            return True
        except:
            return False
    
    def assign(self, var: Variable, iterator: Generator):
        operator: Operator = next(iterator)
        
        if operator.symbol == '=':
            expr = []
        elif operator.symbol == '+=':
            expr = [var.symbol, '+']
        elif operator.symbol == '-=':
            expr = [var.symbol, '-']
        elif operator.symbol == '*=':
            expr = [var.symbol, '*']
        else:
            raise NotImplementedError()
        
        while (token := next(iterator)) is not EOL:
            segment = [piece if piece != '' else '(' for piece in token.symbol.split('(')]
            segment = [piece if piece != '' else ')' for slice in segment for piece in slice.split(')')]
            
            expr += segment
        
        # evaluate expression to store into variable
        postfix: list[str] = Infix2Postfix.process(expr)
        if len(postfix) == 1: # simple value assignment
            reg, _ = self.allocate_register(var)
            
            comment = f'{var.symbol} = {postfix[0]}'
            if (x := int(postfix[0])) < 0:
                self.write(self.body, f'subi x{reg}, xzr, #{-x}', comment)
            else:
                self.write(self.body, f'addi x{reg}, xzr, #{x}', comment)
                
        else:
            self.complex_assign(postfix, var)
    
    def complex_assign(self, postfix: list[str], target: Variable):
        if len(postfix) <= 2:
            return
        
        a = None
        b = None
        op = None
        
        for i, op in enumerate(postfix):
            if op in Infix2Postfix.OPERATORS:
                a = postfix[i-2]
                b = postfix[i-1]
                
                if i < len(postfix) - 1:
                    postfix = postfix[:i-2] + [a+b+op] + postfix[i+1:]
                else:
                    postfix = postfix[:i-2] + [a+b+op]
                
                break
        
        if a is not None and b is not None and op is not None:
            var = Variable(a+b+op)
        else:
            raise NotImplementedError()
        
        assigning: bool = len(postfix) == 1 # assigning to target
        
        if assigning: 
            var = target
        
        # determine which register contains the variable to be assigned to, and allocate a new register if need be
        reg, exists = self.allocate_register(var)
        
        if exists and var != target:
            self.complex_assign(postfix, target)
            return
        
        match op:
            case '+':
                instruction = 'add'
            case '-':
                instruction = 'sub'
            case '*':
                instruction = 'mul'
            case _:
                raise NotImplementedError()
                
        if assigning:
            comment = f'{var.symbol} = {a}{b}{op}'
        else:
            comment = f'x{reg} = {a}{b}{op}'
        
        if not self.is_int(a) and not self.is_int(b): # both in registers
            self.write(self.body, f'{instruction} x{reg}, x{self.reg_of(a)}, x{self.reg_of(b)}', comment)
        elif not self.is_int(a): # b is literal
            if instruction == 'add':
                if (x := int(b)) < 0:
                    self.write(self.body, f'subi x{reg}, x{self.reg_of(a)}, #{-x}', comment)
                else:
                    self.write(self.body, f'addi x{reg}, x{self.reg_of(a)}, #{x}', comment)
            elif instruction == 'sub':
                if (x := int(b)) < 0:
                    self.write(self.body, f'addi x{reg}, x{self.reg_of(a)}, #{-x}', comment)
                else:
                    self.write(self.body, f'subi x{reg}, x{self.reg_of(a)}, #{x}', comment)
            elif instruction == 'mul':
                if (x := int(b)) < 0:
                    self.write(self.body, f'subi x{reg}, xzr, #{-x}', f'x{reg} = {x}')
                else:
                    self.write(self.body, f'addi x{reg}, xzr, #{x}', f'x{reg} = {x}')
                
                self.write(self.body, f'mul x{reg}, x{reg}, x{self.reg_of(a)}', comment)
            else:
                raise NotImplementedError()
        elif not self.is_int(b): # a is literal
            if instruction == 'add':
                if (x := int(a)) < 0:
                    self.write(self.body, f'subi x{reg}, x{self.reg_of(b)}, #{-x}', comment)
                else:
                    self.write(self.body, f'addi x{reg}, x{self.reg_of(b)}, #{x}', comment)
            elif instruction == 'sub':
                if (x := int(a)) < 0:
                    self.write(self.body, f'addi x{reg}, x{self.reg_of(b)}, #{-x}', comment)
                else:
                    self.write(self.body, f'subi x{reg}, x{self.reg_of(b)}, #{x}', comment)
            elif instruction == 'mul':
                if (x := int(a)) < 0:
                    self.write(self.body, f'subi x{reg}, xzr, #{-x}', f'x{reg} = {x}')
                else:
                    self.write(self.body, f'addi x{reg}, xzr, #{x}', f'x{reg} = {x}')
                
                self.write(self.body, f'mul x{reg}, x{reg}, x{self.reg_of(b)}', comment)
            else:
                raise NotImplementedError()
        else: # both are literal
            if instruction == 'add':
                if (x := int(a) + int(b)) < 0:
                    self.write(self.body, f'subi x{reg}, xzr, #{-x}', comment)
                else:
                    self.write(self.body, f'addi x{reg}, xzr, #{x}', comment)
            elif instruction == 'sub':
                if (x := int(a) - int(b)) < 0:
                    self.write(self.body, f'addi x{reg}, xzr, #{-x}', comment)
                else:
                    self.write(self.body, f'subi x{reg}, xzr, #{x}', comment)
            elif instruction == 'mul':
                if (x := int(a)) < 0:
                    self.write(self.body, f'subi x{reg}, xzr, #{-x}', f'x{reg} = {x}')
                else:
                    self.write(self.body, f'addi x{reg}, xzr, #{x}', f'x{reg} = {x}')
                if (y := int(b)) < 0:
                    self.write(self.body, f'subi x9, xzr, #{-y}', f'x9 = {y}')
                else:
                    self.write(self.body, f'addi x9, xzr, #{y}', f'x9 = {y}')
                    
                self.write(self.body, f'mul x{reg}, x{reg}, x9', comment)
            else:
                raise NotImplementedError()
        
        self.complex_assign(postfix, target)
        
    def instantiate(self, type: Type, iterator: Generator):
        if type.symbol == 'long':
            var: Variable = next(iterator)
            
            self.assign(var, iterator)
            
            # update tracking
            self.memory_map[var.symbol] = self.memory_counter
            self.memory_counter += 8
        else:
            raise NotImplementedError()
            
if __name__ == '__main__':
    c = Compiler('example.ack')
    c.compile('example.s')
    # c = Compiler(argv[1])
    # c.compile(argv[2])