import sympy as sp
from ..core.base_types import ExpandableFunction
from ..operators.differential.abstract import LinearDifferentialOperator # Assuming you moved your operator here

class Gaussian(ExpandableFunction):
    """
    Symbolic representation of a Gaussian envelope.
    Because it inherits ExpandableFunction, it automatically acts as an Algebra 
    and routes +, -, *, / through your Factory.
    """
    def __new__(cls, coordinate, **kwargs):
        # sp.Function automatically handles the *args coordinate routing
        return super().__new__(cls, coordinate, **kwargs)
    
    @property
    def definition(self):
        coord = self.args[0]
        return sp.exp(-coord**2)

class Hermite(ExpandableFunction):
    """
    Symbolic representation of the n-th Physicist's Hermite Polynomial.
    """
    def __new__(cls, n, x, **kwargs):
        return super().__new__(cls, n, x, **kwargs)

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