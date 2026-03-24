import sympy as sp
from ..core.base_types import ExpandableFunction
from ..operators.differential.linear import LinearDifferentialOperator

class Hermite(ExpandableFunction):
    """
    Symbolic representation of the n-th Physicist's Hermite Polynomial.
    """
    @property
    def definition(self):
        n = self.args[0]
        coord = self.args[1]
        
        # 1. Setup the internal dummy coordinate
        xi = sp.Dummy('xi')
        D_sym = sp.Symbol('D')
        
        # 2. Instantiate your DifferentialOperator for the n-th derivative
        Dn_op = LinearDifferentialOperator(xi, poly=D_sym**n)
        
        # 3. Apply the operator via the Rodrigues Formula
        gaussian = sp.exp(-xi**2)
        derivative_part = Dn_op(gaussian)
        
        formula = (-1)**n * sp.exp(xi**2) * derivative_part
        return formula.subs(xi, coord)

    def _repr_latex_(self):
        n = sp.latex(self.args[0])
        coord = sp.latex(self.args[1])
        return f"$H_{{{n}}}({coord})$"