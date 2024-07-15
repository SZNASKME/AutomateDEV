import sympy as sp

def simplify_logic_expression(expression: str) -> str:
    # Define symbols
    symbols = sp.symbols('A B C D E F G H I J K L M N O P Q R S T U V W X Y Z')
    
    # Convert the string expression to a sympy expression
    expr = sp.sympify(expression)
    
    # Simplify the logical expression
    simplified_expr = sp.simplify_logic(expr)
    
    # Convert the simplified expression back to a string
    simplified_str = str(simplified_expr)
    
    return simplified_str


def logic_gate(expression: str) -> str:
    # Define symbols
    symbols = sp.symbols('A B C D E F G H I J K L M N O P Q R S T U V W X Y Z')
    
    # Convert the string expression to a sympy expression
    expr = sp.sympify(expression)

    # Function to recursively convert sympy expressions to logic gates
    def expr_to_gates(expr):
        if isinstance(expr, sp.And):
            return f"AND({', '.join(expr_to_gates(arg) for arg in expr.args)})"
        elif isinstance(expr, sp.Or):
            return f"OR({', '.join(expr_to_gates(arg) for arg in expr.args)})"
        elif isinstance(expr, sp.Not):
            return f"NOT({expr_to_gates(expr.args[0])})"
        elif isinstance(expr, sp.Xor):
            return f"XOR({', '.join(expr_to_gates(arg) for arg in expr.args)})"
        else:
            return str(expr)

    # Convert the sympy expression to logic gates
    gates_expression = expr_to_gates(expr)
    
    return gates_expression


# Example usage
expression = "(A & B) | (~A & B)"
simplified_expression = simplify_logic_expression(expression)
print(simplified_expression)

gates_expression = logic_gate(expression)
print(gates_expression)