# part1_optimizer.py
# Program to detect redundant computations, dead code, strength reduction, and copy propagation

import re

def constant_fold(expr: str) -> str:
    """Evaluate constant arithmetic expressions if possible."""
    try:
        return str(eval(expr, {}, {}))
    except Exception:
        return expr

def simplify(expr: str) -> str:
    """Apply algebraic simplifications and strength reduction."""
    expr = re.sub(r'\b(\w+)\s*\*\s*1\b', r'\1', expr)
    expr = re.sub(r'\b1\s*\*\s*(\w+)\b', r'\1', expr)
    expr = re.sub(r'\b(\w+)\s*\+\s*0\b', r'\1', expr)
    expr = re.sub(r'\b0\s*\+\s*(\w+)\b', r'\1', expr)
    expr = re.sub(r'\b(\w+)\s*\-\s*0\b', r'\1', expr)

    expr = re.sub(r'\b(\w+)\s*\*\s*0\b', '0', expr)
    expr = re.sub(r'\b0\s*\*\s*(\w+)\b', '0', expr)

    return expr

def copy_propagation(lines: list[str]) -> list[str]:
    """Replace variable copies like y=x in later expressions, but keep needed assigns."""
    replacements = {}
    result = []

    for line in lines:
        var, expr = [p.strip() for p in line.split("=")]

        # Replace expr if it uses a copy variable
        for old, new in replacements.items():
            expr = re.sub(rf'\b{old}\b', new, expr)

        if re.fullmatch(r"[a-zA-Z_]\w*", expr):
            # It's a pure copy like y = x
            replacements[var] = expr
            # Still keep it if this var is directly used later
            result.append(f"{var} = {expr}")
        else:
            result.append(f"{var} = {expr}")

    # Second pass: replace inside result
    final = []
    for line in result:
        var, expr = [p.strip() for p in line.split("=")]
        for old, new in replacements.items():
            expr = re.sub(rf'\b{old}\b', new, expr)
        final.append(f"{var} = {expr}")

    # Remove truly unused pure copies
    used_vars = set()
    for line in reversed(final):
        _, expr = [p.strip() for p in line.split("=")]
        used_vars.update(re.findall(r"[a-zA-Z_]\w*", expr))
    cleaned = [line for line in final if line.split("=")[0].strip() in used_vars or line == final[-1]]

    return cleaned

def optimize(code_lines: list[str]) -> list[str]:
    optimized_lines = []

    for line in code_lines:
        var, expr = [p.strip() for p in line.split("=")]
        expr = constant_fold(expr)
        expr = simplify(expr)
        optimized_lines.append(f"{var} = {expr}")

    optimized_lines = copy_propagation(optimized_lines)
    return optimized_lines

if __name__ == "__main__":
    code = [
        "x = 2 * 8",
        "y = x * 1",
        "z = y + 0"
    ]

    print("Before optimization:")
    for line in code:
        print(line)

    optimized = optimize(code)

    print("\nAfter optimization:")
    for line in optimized:
        print(line)
