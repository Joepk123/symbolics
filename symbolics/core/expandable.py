# core/expandable.py

import sympy as sp
from .mixin import ExpansionMixin

class Expandable(sp.Expr, ExpansionMixin):
    """
    The fundamental base for all physics objects. 
    Handles metadata (symbols), printing, and evaluation.
    """
    def __new__(cls, *args, symbol=None, **kwargs):
        # 1. Filter out metadata from SymPy's positional args
        obj = super().__new__(cls, *args)
        # We no longer force "cls.__name__". If no symbol is given, it stays None.
        obj._custom_symbol = symbol 
        return obj

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