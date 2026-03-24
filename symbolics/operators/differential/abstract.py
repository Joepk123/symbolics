# operators/differential.py

import sympy as sp
from ...core.base_types import ExpandableOperator
from ...core.mixin import ExpansionMixin

class AbstractDifferentialOperator(ExpandableOperator):
    """
    A fully generalized operator capable of representing non-linear mappings.
    Example: N(f) = (df/dx)^2 + sin(f)
    """
    def __new__(cls, variable, expr_template=None, dummy_func=None, **kwargs):
        # 1. Standardize the dummy placeholder if not provided
        F = dummy_func if dummy_func else sp.Function(r'D')(variable)
        
        # 2. Convert string/expr template into a SymPy tree
        template = sp.sympify(expr_template) if expr_template is not None else F
        
        # 3. Pass to Expandable -> sp.Expr
        # Args: (variable, template, dummy_func)
        return super().__new__(cls, variable, template, F, **kwargs)

    @property
    def variable(self): return self.args[0]

    @property
    def template(self): return self.args[1]

    @property
    def dummy_func(self): return self.args[2]

    # ---------------------------------------------------------
    # NON-LINEAR EXECUTION & COMPOSITION
    # ---------------------------------------------------------
    def __call__(self, target_expr):
        """Replaces Phi(x) with the target expression (Wavefunction)."""
        # We don't call .doit()! We want it to stay a Derivative object for evaluate()
        return self.template.subs(self.dummy_func, target_expr)

    def __mul__(self, other):
        """Composition: N1 * N2 means N1(N2(F))."""
        if isinstance(other, AbstractDifferentialOperator) and self.variable == other.variable:
            # Substitute the second operator's template into the first's
            new_template = self.template.subs(self.dummy_func, other.template)
            return AbstractDifferentialOperator(self.variable, new_template, self.dummy_func)
        return super().__mul__(other)