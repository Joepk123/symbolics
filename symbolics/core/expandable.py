# core/expandable.py

import sympy as sp
from .mixin import ExpansionMixin
from .algebra import Algebra, Field, Ring, VectorSpace

class Expandable(ExpansionMixin):
    """
    The fundamental base for all physics objects. 
    Handles metadata (symbols), printing, and evaluation.
    """

    is_commutative = False
    _op_priority = 100.0

    def __new__(cls, *args, symbol=None, **kwargs):
        # 1. Filter out metadata from SymPy's positional args
        obj = super().__new__(cls, *args)
        # We no longer force "cls.__name__". If no symbol is given, it stays None.
        obj._custom_symbol = symbol 
        return obj

    @property
    def math_type(self):
        """
        Returns the highest-level abstract mathematical type of this object.
        Resolves by checking the instance against Algebra, Field, Ring, and VectorSpace.
        """
        return next((t for t in (Algebra, Field, Ring, VectorSpace) if isinstance(self, t)), None)

    @property
    def symbol_name(self):
        # Fallback for base expandable items (like wavefunctions)
        return self._custom_symbol if self._custom_symbol else self.__class__.__name__

    def _latex(self, printer):
        sym = self.symbol_name
        if not self.args:
            return sym
        arg_str = ", ".join([printer._print(arg) for arg in self.args])
        return r"{}\left({}\right)".format(sym, arg_str)

    def _pretty(self, printer):
        from sympy.printing.pretty.stringpict import prettyForm
        pform = printer._print(sp.Symbol(self.symbol_name))
        if not self.args:
            return pform
        args = [printer._print(arg) for arg in self.args]
        return prettyForm(*pform.parens())

    def __getnewargs_ex__(self):
        return (self.args, {"symbol": self._custom_symbol})