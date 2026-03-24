
import sympy as sp
from sympy import pprint
from symbolics import LinearDifferentialOperator, ExpandableFunction, evaluate
from symbolics.primitives.functions import Hermite

sp.init_printing(use_unicode=True)
# 1. Define our spatial coordinate
x = sp.Symbol('x')
n, m = sp.symbols('n m')
# D
D = LinearDifferentialOperator(x, {1: 1}, 'D_1')
L = LinearDifferentialOperator(x, {1: 2}, 'L')

Hn = Hermite(n, x)*Hermite(m, x)
Hn