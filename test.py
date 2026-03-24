
import sympy as sp
from sympy import pprint
from symbolics import LinearDifferentialOperator, ExpandableFunction, evaluate
sp.init_printing(use_unicode=True)
# 1. Define our spatial coordinate
x = sp.Symbol('x')
# D
D = LinearDifferentialOperator(x, {1: 1}, symbol=r"\hat{p}")