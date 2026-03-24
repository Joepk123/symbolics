# core/base.py

import sympy as sp

class ExpansionMixin:
    """
    Universal behavior for JIT and Stratified Evaluation.
    """
    @property
    def definition(self):
        """Returns the immediate symbolic definition. Defaults to self."""
        return self

    def make_explicit(self):
        """Executes a single layer of macro expansion."""
        from .visitor import make_explicit 
        return make_explicit(self)

    def evaluate(self):
        """Recursively evaluates all layers down to the Normal Form."""
        expr = self.definition
        previous_expr = None
        
        while expr != previous_expr:
            previous_expr = expr
            if hasattr(expr, 'replace'):
                expr = expr.replace(
                    lambda e: hasattr(e, 'definition') and e.definition != e,
                    lambda e: e.definition
                )
        return expr.doit()

    def evaluate_target(self, target_type):
        """
        Selectively expands only nodes of a specific type (or tuple of types).
        """
        expr = self.definition
        
        if hasattr(expr, 'replace'):
            # Replace only if the node is an instance of the target_type
            expr = expr.replace(
                lambda node: isinstance(node, target_type) and hasattr(node, 'definition') and node.definition != node,
                lambda node: node.definition
            )
        return expr