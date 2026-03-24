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
class ExpandableConstant(Field, Expandable, sp.Expr, metaclass=CASMeta):
    """
    Mathematically: An element of a Field.
    Implementation: A scalar mapping with an arity of 0. Inherits 
    printing logic natively from the Expandable parent class.
    """
    pass

# ---------------------------------------------------------
# 2. FUNCTIONS
# ---------------------------------------------------------
class ExpandableFunction(Algebra, Expandable, sp.Expr, metaclass=CASMeta):
    """
    Mathematically: An Algebra over a Field.
    Implementation: Automatically handles pointwise algebraic operations (+, -, *), 
    coordinate routing, and evaluation.
    """
    pass

# ---------------------------------------------------------
# 3. OPERATORS
# ---------------------------------------------------------
class ExpandableOperator(Ring, Expandable, sp.Expr, metaclass=CASMeta):
    """
    Mathematically: A Ring of Endomorphisms.
    Implementation: Supports structural composition (*) but strictly blocks division.
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
    
    # Visual overrides ensuring internal AST templates are hidden
    def _latex(self, printer):
        return self._custom_symbol if self._custom_symbol else self.__class__.__name__

    def _pretty(self, printer):
        sym = self._custom_symbol if self._custom_symbol else self.__class__.__name__
        return printer._print(sp.Symbol(sym))

    def _sympystr_(self, printer):
        return self._custom_symbol if self._custom_symbol else self.__class__.__name__

# ---------------------------------------------------------
# 4. TENSORS
# ---------------------------------------------------------
class ExpandableTensor(Algebra, Expandable, sp.MatrixExpr, metaclass=CASMeta):
    """
    Mathematically: An element of a Tensor Algebra.
    Implementation: A multidimensional array mapping supporting non-commutative algebra.
    """
    def __new__(cls, name, n, m, symbol=None, **kwargs):
        # MatrixExpr requires a name string for its internal logic
        obj = super().__new__(cls, name, n, m, **kwargs)
        # Allow symbol to be None for dynamically generated unnamed tensors
        obj._custom_symbol = symbol 
        return obj

    @property
    def symbol_name(self):
        """Safely resolves the visual identity for dynamic or explicitly named tensors."""
        if self._custom_symbol is not None:
            return self._custom_symbol
        # Fallback to the MatrixExpr's internal name or the minted class name
        name_arg = self.args[0]
        return name_arg if name_arg else self.__class__.__name__

    def _latex(self, printer):
        """Renders the Tensor symbol (conventionally bolded in LaTeX)."""
        return f"\\mathbf{{{self.symbol_name}}}"

    def _pretty(self, printer):
        """Renders the Tensor symbol for console output."""
        return printer._print(sp.Symbol(self.symbol_name))

    def _sympystr_(self, printer):
        """Overrides generic string casting to prevent raw SymPy internal prints."""
        return self.symbol_name

    def __getnewargs_ex__(self):
        # MatrixExpr args are (name, rows, cols)
        return ((self.args[0], self.rows, self.cols), {"symbol": self._custom_symbol})

    def __truediv__(self, other):
        return NotImplemented

    def __rtruediv__(self, other):
        return NotImplemented