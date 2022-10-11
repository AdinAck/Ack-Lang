class Infix2Postfix:
    OPERATORS: set[str] = {'+', '-', '*', '/', '(', ')', '^'}
    PRIORITY: dict[str, int] = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
    
    @classmethod
    def process(cls, expr: list[str]) -> list[str]:
        stack: list[str] = []
        output: list[str] = []

        for char in expr:
            if char not in cls.OPERATORS:
                output += [char]

            elif char == '(':
                stack.append('(')

            elif char == ')':
                while stack and stack[-1] != '(':
                    output += stack.pop()
                
                stack.pop()
                
            else: 
                while stack and stack[-1] != '(' and cls.PRIORITY[char] <= cls.PRIORITY[stack[-1]]:
                    output += stack.pop()
                
                stack.append(char)
                
        while stack:
            output += stack.pop()

        return output