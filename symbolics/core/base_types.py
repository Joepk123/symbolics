# core/base_types.py

import sympy as sp
from abc import ABCMeta

from .mixin import ExpansionMixin
from .expandable import Expandable
from .algebra import Algebra, Ring, Field, AdditiveGroup
from .blueprints import AdditiveBlueprint, MultiplicativeBlueprint, DivisibleBlueprint

# ---------------------------------------------------------
# METACLASS FUSION
# ---------------------------------------------------------
class CASMeta(ABCMeta, type(sp.Expr)):
    pass

# ---------------------------------------------------------
# 1. SCALARS & CONSTANTS
# ---------------------------------------------------------
class ExpandableConstant(Expandable, sp.Expr, Field, metaclass=CASMeta):
    """
    Mathematically: An element of a Field.
    Implementation: A named symbolic constant that can be expanded into a value.
    """
    pass

# ---------------------------------------------------------
# 2. FUNCTIONS
# ---------------------------------------------------------
class ExpandableFunction(Expandable, sp.Expr, Algebra, metaclass = CASMeta):
    """
    Mathematically: An Algebra.
    Implementation: Automatically handles +, -, *, symbols, and evaluate().
    """
    pass

# ---------------------------------------------------------
# 3. OPERATORS
# ---------------------------------------------------------
class ExpandableOperator(Expandable, sp.Expr, Ring, metaclass=CASMeta):
    """
    Mathematically: A Ring.
    Implementation: Supports composition (*) but blocks division.
    """
    
    @property
    def target_var(self):
        """Safely retrieves the target variable from SymPy's immutable args."""
        return self.args[0]

    def __call__(self, target_expr):
        raise NotImplementedError("Operators must define a __call__ method.")

    # We must explicitly block SymPy's innate division for Expr objects
    def __truediv__(self, other):
        raise TypeError("Division is undefined for Operator Rings.")

    def __rtruediv__(self, other):
        raise TypeError("Division is undefined for Operator Rings.")

# ---------------------------------------------------------
# 4. TENSORS
# ---------------------------------------------------------
class ExpandableTensor(ExpansionMixin, Algebra, sp.MatrixExpr, metaclass=CASMeta):
    def __new__(cls, name, n, m, symbol=None, **kwargs):
        # MatrixExpr requires a name string for its internal logic
        obj = super().__new__(cls, name, n, m, **kwargs)
        obj._custom_symbol = symbol if symbol else name
        return obj

    def _latex(self, printer):
        """Renders the Tensor symbol (usually bold in LaTeX)."""
        return f"\\mathbf{{{self._custom_symbol}}}"

    def _pretty(self, printer):
        """Renders the Tensor symbol."""
        return printer._print(sp.Symbol(self._custom_symbol))

    def __getnewargs_ex__(self):
        # MatrixExpr args are (name, rows, cols)
        return ((self.args[0], self.rows, self.cols), {"symbol": self._custom_symbol})

    def __truediv__(self, other):
        return NotImplemented

    def __rtruediv__(self, other):
        return NotImplemented