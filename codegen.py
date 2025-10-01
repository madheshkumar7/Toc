# part2_codegen.py
# Program to translate arithmetic expressions into stack machine code

def precedence(op: str) -> int:
    """Return operator precedence."""
    if op in ('+', '-'):
        return 1
    if op in ('*', '/'):
        return 2
    return 0

def infix_to_postfix(expression: str) -> list[str]:
    """Convert infix expression to postfix (Reverse Polish Notation)."""
    stack = []
    output = []
    tokens = list(expression.replace(" ", ""))  # split by characters

    for token in tokens:
        if token.isalnum():  # operand
            output.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        else:  # operator
            while stack and precedence(stack[-1]) >= precedence(token):
                output.append(stack.pop())
            stack.append(token)

    while stack:
        output.append(stack.pop())

    return output

def generate_stack_code(postfix: list[str]) -> list[str]:
    """Generate stack machine instructions from postfix expression."""
    code = []
    for token in postfix:
        if token.isalnum():
            code.append(f"PUSH {token}")
        elif token == '+':
            code.append("ADD")
        elif token == '-':
            code.append("SUB")
        elif token == '*':
            code.append("MUL")
        elif token == '/':
            code.append("DIV")
    return code

if __name__ == "__main__":
    expr = "(a+b)*c"

    print("Input expression:", expr)

    postfix = infix_to_postfix(expr)
    print("Postfix expression:", " ".join(postfix))

    code = generate_stack_code(postfix)
    print("\nGenerated stack machine code:")
    for line in code:
        print(line)
