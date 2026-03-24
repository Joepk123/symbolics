# core/base_types.py

import sympy as sp
from .mixin import ExpansionMixin
from .algebra import Field, Algebra, Ring
from .blueprints import AdditiveBlueprint, MultiplicativeBlueprint, DivisibleBlueprint

# ---------------------------------------------------------
# 1. SCALARS & CONSTANTS
# ---------------------------------------------------------
class ExpandableConstant(ExpansionMixin, Field, AdditiveBlueprint, MultiplicativeBlueprint, DivisibleBlueprint, sp.Symbol):
    """
    Mathematically: A Field element.
    Implementation: Routes +, -, *, / through the factory.
    """
    def __new__(cls, name, **kwargs):
        return super().__new__(cls, name, **kwargs)

# ---------------------------------------------------------
# 2. FUNCTIONS
# ---------------------------------------------------------
class ExpandableFunction(ExpansionMixin, Algebra, AdditiveBlueprint, MultiplicativeBlueprint, DivisibleBlueprint, sp.Function):
    """
    Mathematically: An Algebra over a Field.
    Implementation: Can be added (superposition) and multiplied (tensor products), 
    and division is allowed (e.g., normalization constants). 
    All operations are intercepted and handled by the Factory.
    """
    pass

# ---------------------------------------------------------
# 3. LINEAR OPERATORS
# ---------------------------------------------------------
class ExpandableOperator(ExpansionMixin, Ring, AdditiveBlueprint, MultiplicativeBlueprint, sp.Expr):
    """
    Mathematically: A Ring.
    Implementation: Supports +, -, and * (composition). 
    Crucially, DivisibleBlueprint is ABSENT.
    """
    def __new__(cls, variable, *args, **kwargs):
        obj = super().__new__(cls, variable, *args, **kwargs)
        obj.target_var = variable
        return obj

    def __call__(self, target_expr):
        raise NotImplementedError("Operators must define a __call__ method.")

    # We must explicitly block SymPy's innate division for Expr objects
    def __truediv__(self, other):
        raise TypeError("Division is undefined for Operator Rings.")

    def __rtruediv__(self, other):
        raise TypeError("Division is undefined for Operator Rings.")


class ExpandableTensor(sp.MatrixExpr, ExpansionMixin, Algebra):
    """
    Mathematically: A Matrix Algebra.
    Implementation: Inherits from sp.MatrixExpr for native matrix math 
    (MatAdd, MatMul, Trace, Transpose).
    
    Notice we DO NOT include AdditiveBlueprint or MultiplicativeBlueprint!
    We let SymPy handle the strict rules of matrix arithmetic natively, 
    but we keep ExpansionMixin so we can unwrap() custom tensor definitions.
    """
    def __new__(cls, name, n, m, **kwargs):
        # MatrixExpr usually requires a name and dimensions (rows, cols)
        obj = super().__new__(cls, name, n, m, **kwargs)
        return obj

    # We block division because matrix division is undefined 
    # (you must multiply by the inverse instead).
    def __truediv__(self, other):
        return NotImplemented

    def __rtruediv__(self, other):
        return NotImplemented