from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

@dataclass
class Token(metaclass=ABCMeta):
    symbol: str
    
    @classmethod
    @abstractmethod
    def check(cls, symbol: str) -> bool:
        ...
        
    def __str__(self) -> str:
        return self.symbol

@dataclass
class Type(Token):
    @staticmethod
    def symbols() -> list[str]:
        return ['long']

    @classmethod
    def check(cls, symbol: str) -> bool:
        return symbol in cls.symbols()

@dataclass
class Variable(Token):
    @classmethod
    def check(cls, symbol: str) -> bool:
        return symbol[0].isalpha() and symbol.isalnum()

@dataclass
class Operator(Token):
    @staticmethod
    def symbols() -> list[str]:
        return ['=', '+', '-', '*', '+=', '-=', '*=', '<<', '>>']
    
    @classmethod
    def check(cls, symbol: str) -> bool:
        return symbol in cls.symbols()
    
@dataclass
class Literal(Token):
    @classmethod
    def check(cls, symbol: str) -> bool:
        return symbol.isnumeric()
    
    @property
    def value(self) -> int:
        return int(self.symbol)

class Fragment(Token):
    @classmethod
    def check(cls, symbol: str) -> bool:
        return True

class EOL:
    ...