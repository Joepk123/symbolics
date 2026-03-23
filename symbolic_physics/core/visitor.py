# core/visitor.py

import sympy as sp

def unwrap(expr):
    """Walks any SymPy AST and expands custom nodes exactly one layer."""
    if hasattr(expr, 'replace'):
        return expr.replace(
            lambda node: hasattr(node, 'definition') and node.definition != node,
            lambda node: node.definition
        )
    return expr

def targeted_expand(expr, target_type):
    """Standalone visitor to expand specific types within a standard SymPy tree."""
    if hasattr(expr, 'replace'):
        return expr.replace(
            lambda node: isinstance(node, target_type) and hasattr(node, 'definition') and node.definition != node,
            lambda node: node.definition
        )
    return expr