# Functions
import sympy as sp
from class_DifferentialOperator import LinearDifferentialOperator as LDO



def Hermite(n: int, x: sp.Symbol | sp.Expr) -> sp.Expr:
    xi = sp.Dummy('xi')
    D = LDO(xi)
    derivative = (-1)**n * sp.exp(xi**2) * (D**n)( sp.exp(-xi**2))
    return derivative.subs(xi, x)

def Gaussian(x: sp.Symbol | sp.Expr) -> sp.Expr:
    xi = sp.Dummy('xi')
    return sp.exp(-xi**2/sp.sqrt(2)).subs(xi, x)

def HermiteGaussian(n: int, x: sp.Symbol | sp.Expr) -> sp.Expr:
    xi = sp.Dummy('xi')
    product = Hermite(n, xi)*Gaussian(xi)
    Cn = sp.Symbol('C_n')
    Cn.definition = 1/(sp.pi**(1/4) * 2**n * sp.factorial(n))
    expression = Cn*product.subs(xi, x)
    return expression


x, y, z, xi = sp.symbols('x y z xi')
Hermite(10, y/x)

# Usage
D = LDO(xi)
p = sp.Poly(D.D**2 + 1, D.D)
L = LDO.from_poly(x, p)

lmao = HermiteGaussian(10,x)
lmao