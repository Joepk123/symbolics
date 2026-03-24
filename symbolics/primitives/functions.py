import sympy as sp
from ..core.base_types import ExpandableFunction

class Hermite(ExpandableFunction):
    """
    Physicists' Hermite Polynomials H_n(x).
    Evaluated lazily via Rodrigues' formula.
    """
    def __new__(cls, n, coord, symbol=None, **kwargs):
        # SymPy Expr requires us to explicitly intercept and save custom attributes
        obj = ExpandableFunction.__new__(cls, n, coord, **kwargs)
        obj._custom_symbol = symbol
        return obj

    @property
    def definition(self):
        n = self.args[0]
        coord = self.args[1]
        
        from ..operators.differential.linear import LinearDifferentialOperator
        
        # 1. Instantiate the operator for the n-th derivative: d^n/d(coord)^n
        # The dictionary {n: 1} maps the n-th degree to a coefficient of 1.
        Dn = LinearDifferentialOperator(coord, {n: 1})
        
        # 2. Define the Gaussian operand
        gaussian = sp.exp(-coord**2)
        
        # 3. Apply the operator to create an unevaluated SymPy Derivative AST
        derivative_ast = Dn(gaussian)
        
        # 4. Assemble and return the explicit Rodrigues' formula
        return (sp.Integer(-1)**n) * sp.exp(coord**2) * derivative_ast

    
    def _latex(self, printer):
        """Renders the standard LaTeX representation: H_n(x) or a custom symbol."""
        sym = self._custom_symbol if self._custom_symbol else "H"
        n = printer.doprint(self.args[0])
        coord = printer.doprint(self.args[1])
        return f"{sym}_{{{n}}}\\left({coord}\\right)"

    def _sympystr_(self, printer):
        sym = self._custom_symbol if self._custom_symbol else "H"
        n = printer.doprint(self.args[0])
        coord = printer.doprint(self.args[1])
        return f"{sym}_{n}({coord})"
