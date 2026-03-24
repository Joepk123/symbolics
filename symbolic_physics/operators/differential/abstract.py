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
        # 1. Create a hidden dummy function if one isn't provided
        F = dummy_func if dummy_func else sp.Function(r'\Phi')(variable)
        
        # 2. Store the abstract template tree
        template = sp.sympify(expr_template) if expr_template is not None else F
        
        # 3. Lock them into the SymPy AST
        obj = super().__new__(cls, variable, template, F, **kwargs)
        return obj

    @property
    def variable(self):
        """The spatial coordinate (e.g., x)"""
        return self.args[0]

    @property
    def template(self):
        """The abstract mathematical template, e.g., Derivative(Phi(x), x)**2"""
        return self.args[1]

    @property
    def dummy_func(self):
        """The placeholder function Phi(x)"""
        return self.args[2]

    # ---------------------------------------------------------
    # NON-LINEAR EXECUTION & COMPOSITION
    # ---------------------------------------------------------
    def __call__(self, target_expr):
        """
        Executes the non-linear operator.
        Replaces Phi(x) with the target expression and evaluates derivatives.
        """
        # Substitute the dummy function with the actual target (e.g., a Gaussian)
        applied_expr = self.template.subs(self.dummy_func, target_expr)
        
        # Trigger SymPy's calculus engine
        return applied_expr.doit()

    def __mul__(self, other):
        """
        Operator Composition: N1 * N2 means N1(N2(F)).
        SymPy handles the heavy lifting of nesting the templates!
        """
        if isinstance(other, AbstractDifferentialOperator) and self.variable == other.variable:
            # We compose them by substituting the second operator's template into the first!
            new_template = self.template.subs(self.dummy_func, other.template)
            return AbstractDifferentialOperator(self.variable, new_template, self.dummy_func)
            
        return super().__mul__(other)