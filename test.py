%load_ext autoreload
%autoreload 2

import sympy as sp
from sympy import pprint
from symbolics import LinearDifferentialOperator, ExpandableFunction, evaluate
sp.init_printing(use_unicode=True)
# 1. Define our spatial coordinate
x = sp.Symbol('x')

# 2. Define a quick test wavefunction (using your base class!)
class MyTestWave(ExpandableFunction):
    def __new__(cls, coord, **kwargs):
        return super().__new__(cls, coord, **kwargs)
    
    @property
    def definition(self):
        # Let's use sin(x) as the explicit math
        return sp.sin(self.args[0])
    
    def _pretty(self, printer):
        """Controls the Unicode/ASCII art output (pprint)."""
        from sympy.printing.pretty.stringpict import prettyForm
        # This draws the symbol and its arguments: Ψ(x)
        pform = printer._print(sp.Symbol(self.symbol_name))
        args = [printer._print(arg) for arg in self.args]
        return prettyForm(*pform.parens()) # Adds parentheses around args

    def _latex(self, printer):
        """Controls the beautiful MathJax/LaTeX output in Notebooks."""
        arg_str = ", ".join([printer._print(arg) for arg in self.args])
        return f"{self.symbol_name}\\left({arg_str}\\right)"

# Example Usage in main.py
from symbolics import LinearDifferentialOperator

x = sp.Symbol('x')
# Define momentum operator with a custom hat symbol
p_hat = LinearDifferentialOperator(x, {1: -sp.I}, symbol=r'\hat{p}')
psi = ExpandableFunction(x)