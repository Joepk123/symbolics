# core/expandable.py

import sympy as sp
from .mixin import ExpansionMixin

class Expandable(ExpansionMixin):
    """
    The fundamental base for all physics objects. 
    Handles metadata (symbols), printing, and evaluation.
    """
    def __new__(cls, *args, symbol=None, **kwargs):
        # 1. Filter out metadata from SymPy's positional args
        obj = super().__new__(cls, *args)
        
        # 2. Store the visual identity
        obj._custom_symbol = symbol if symbol else cls.__name__
        return obj

    @property
    def symbol_name(self):
        return self._custom_symbol

    def _latex(self, printer):
        """Standardized LaTeX: \Psi(x) or \hbar"""
        if not self.args:
            return self._custom_symbol
        arg_str = ", ".join([printer._print(arg) for arg in self.args])
        return r"{}\left({}\right)".format(self._custom_symbol, arg_str)

    def _pretty(self, printer):
        """Standardized Unicode printing."""
        from sympy.printing.pretty.stringpict import prettyForm
        pform = printer._print(sp.Symbol(self._custom_symbol))
        if not self.args:
            return pform
        args = [printer._print(arg) for arg in self.args]
        return prettyForm(*pform.parens())

    def __getnewargs_ex__(self):
        """Ensures symbols survive SymPy reconstruction (e.g., 2*Psi)."""
        return (self.args, {"symbol": self._custom_symbol})