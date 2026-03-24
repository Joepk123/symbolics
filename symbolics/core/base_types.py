# core/base_types.py

import sympy as sp
from abc import ABCMeta

from .mixin import ExpansionMixin
from .algebra import Algebra, Ring  # <--- Added Ring here!
from .blueprints import AdditiveBlueprint, MultiplicativeBlueprint, DivisibleBlueprint

# ---------------------------------------------------------
# METACLASS FUSION
# ---------------------------------------------------------
class CASMeta(ABCMeta, type(sp.Expr)):
    pass

# ---------------------------------------------------------
# 1. SCALARS & CONSTANTS
# ---------------------------------------------------------
class ExpandableConstant(ExpansionMixin, sp.Expr, metaclass=CASMeta):
    """
    Mathematically: An element of a Field.
    Implementation: A named symbolic constant that can be expanded into a value.
    """
    def __new__(cls, symbol=None, **kwargs):
        # Constants don't usually take spatial coordinates in their AST args,
        # but we can store the symbol as a SymPy Symbol internally.
        name = symbol if symbol else cls.__name__
        obj = super().__new__(cls, **kwargs)
        obj._custom_symbol = name
        return obj

    @property
    def symbol_name(self):
        return self._custom_symbol

    def _latex(self, printer):
        """Render the constant as a LaTeX symbol: \hbar, \pi, etc."""
        return self._custom_symbol

    def _pretty(self, printer):
        """Render the constant as a Unicode symbol."""
        return printer._print(sp.Symbol(self._custom_symbol))

    def __getnewargs_ex__(self):
        """Preserve the symbol during SymPy algebraic reconstructions."""
        return ((), {"symbol": self._custom_symbol})

# ---------------------------------------------------------
# 2. FUNCTIONS
# ---------------------------------------------------------
class ExpandableFunction(
    ExpansionMixin, 
    AdditiveBlueprint, 
    MultiplicativeBlueprint, 
    DivisibleBlueprint, 
    sp.Expr, 
    Algebra, 
    metaclass=CASMeta
):
    def __new__(cls, *args, symbol=None, **kwargs):
        # We store the symbol in the 'assumptions' or a hidden attribute 
        # so it survives SymPy's immutable copying.
        obj = super().__new__(cls, *args, **kwargs)
        obj._custom_symbol = symbol if symbol else cls.__name__
        return obj

    def _latex(self, printer):
        """Standardizes LaTeX output for all functions: \Psi(x, y)"""
        arg_str = ", ".join([printer._print(arg) for arg in self.args])
        # If the symbol has a backslash, we treat it as a LaTeX command
        return f"{self._custom_symbol}\left({arg_str}\right)"

    def _pretty(self, printer):
        """Standardizes Unicode output for all functions: Ψ(x)"""
        from sympy.printing.pretty.stringpict import prettyForm
        # Try to use the symbol, fallback to class name
        pform = printer._print(sp.Symbol(self._custom_symbol))
        if not self.args:
            return pform
        args = [printer._print(arg) for arg in self.args]
        return prettyForm(*pform.parens())

    def __getnewargs_ex__(self):
        """Ensures the symbol is preserved during SymPy's internal rebuilds."""
        return (self.args, {"symbol": getattr(self, '_custom_symbol', None)})

# ---------------------------------------------------------
# 3. OPERATORS
# ---------------------------------------------------------
class ExpandableOperator(ExpansionMixin, Ring, AdditiveBlueprint, MultiplicativeBlueprint, sp.Expr, metaclass=CASMeta):
    def __new__(cls, variable, *args, symbol=None, **kwargs):
        obj = super().__new__(cls, variable, *args, **kwargs)
        # Default to a "hat" notation if no symbol is provided
        obj._custom_symbol = symbol if symbol else f"\\hat{{{cls.__name__[0]}}}"
        return obj

    def _latex(self, printer):
        """Renders as \hat{O} \Psi(x)"""
        return self._custom_symbol

    def _pretty(self, printer):
        """Renders the operator symbol in Unicode."""
        from sympy.printing.pretty.stringpict import prettyForm
        return printer._print(sp.Symbol(self._custom_symbol))

    def __getnewargs_ex__(self):
        return ((self.target_var,), {"symbol": self._custom_symbol})

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