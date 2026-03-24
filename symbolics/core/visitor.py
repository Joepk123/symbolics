# core/visitor.py

import sympy as sp

def make_explicit(expr):
    """Walks any SymPy AST and expands custom nodes exactly one layer."""
    if hasattr(expr, 'replace'):
        return expr.replace(
            lambda node: hasattr(node, 'definition') and node.definition != node,
            lambda node: node.definition
        )
    return expr

def evaluate(expr):
    """
    Recursively unfolds all custom physics definitions inside ANY SymPy tree
    and evaluates the resulting calculus/algebra down to its Normal Form.
    """
    # If the object itself has the mixin method, just call it directly
    if hasattr(expr, 'definition') and type(expr).definition != property:
        expr = expr.definition
        
    previous_expr = None
    
    # 1. Recursively unfold all custom definitions
    while expr != previous_expr:
        previous_expr = expr
        if hasattr(expr, 'replace'):
            expr = expr.replace(
                lambda e: hasattr(e, 'definition') and e.definition != e,
                lambda e: e.definition
            )
            
    # 2. Execute the raw calculus (derivatives, integrals, etc.)
    return expr.doit() if hasattr(expr, 'doit') else expr

def evaluate_target(expr, target_type):
    """Standalone visitor to expand specific types within a standard SymPy tree."""
    if hasattr(expr, 'replace'):
        return expr.replace(
            lambda node: isinstance(node, target_type) and hasattr(node, 'definition') and node.definition != node,
            lambda node: node.definition
        )
    return expr