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

    def evaluate(self, expand=True, **kwargs):
        """Recursively evaluates all layers down to the Normal Form."""
        from .visitor import evaluate as visitor_eval
        import sympy as sp
        
        # 1. Unpack definitions and run standard SymPy calculus
        raw_expr = visitor_eval(self, **kwargs)
        
        # 2. Calculate as completely as possible, unless specified otherwise
        evaluated_expr = sp.expand(raw_expr) if expand else raw_expr
        
        # 3. Preserve the Expandable Object-Oriented Type
        from .algebra import Algebra, Field, VectorSpace, _get_signature_counts
        from .base_types import EvaluatedFunction, SymPyWrapper
        
        math_type = getattr(self, 'math_type', None)
        idx_c, _ = _get_signature_counts(self)
        coords = self.args[idx_c:]
        
        sym = getattr(self, '_custom_symbol', None)
        if math_type in (Algebra, VectorSpace):
            return EvaluatedFunction(evaluated_expr, *coords, symbol=sym)
        elif math_type is Field:
            return SymPyWrapper(evaluated_expr, symbol=sym)
            
        return evaluated_expr

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