# We try to construct the Hilbert spaces used in FB microcavities.
%load_ext autoreload
%autoreload 2
import numpy as np
from math import factorial
import sympy as sp
from symbolics_singlescript import *
x, y, z = sp.symbols('x y z')
n, m = sp.symbols('n m')
gamma = sp.Function('gamma')(z) 

class Gaussian(DefinedFunction):
    def __new__(cls, coordinate, **kwargs):
        return super().__new__(cls, coordinate, **kwargs)
    
    @property
    def definition(self):
        # self.args[0] is the coordinate passed in
        coord = self.args[0]
        return sp.exp(-coord**2)

class Hermite(DefinedFunction):
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
        
        # 2. Instantiate YOUR DifferentialOperator for the n-th derivative
        Dn_op = DifferentialOperator(xi, poly=D_sym**n)
        
        # 3. Apply the operator via the Rodrigues Formula
        gaussian = sp.exp(-xi**2)
        derivative_part = Dn_op(gaussian)
        
        formula = (-1)**n * sp.exp(xi**2) * derivative_part
        
        return formula.subs(xi, coord)

    def _repr_latex_(self):
        n = sp.latex(self.args[0])
        coord = sp.latex(self.args[1])
        return f"$H_{{{n}}}({coord})$"
    
    def _latex(self, printer):
        n = printer.doprint(self.args[0])
        coord = printer.doprint(self.args[1])
        return f"H_{{{n}}}({coord})"



x, y, z, n, m = sp.symbols('x y z n m')

# DoubleHermite expects: 2 indices, 2 coords
# Re-run these to inject the flag!
DoubleHermite = FunctionMul(Hermite, Hermite)
HGnm = FunctionMul(DoubleHermite, Gaussian, label='HG')
psi_nm = HGnm(n, m, x, y, z)
psi_nm.definition