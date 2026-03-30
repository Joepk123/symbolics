

import numpy as np
import sympy as sp
from sympy import pprint
from symbolics.core import Algebra, Ring, Field, VectorSpace, define_function
from symbolics.math.operators.differential.linear import LinearDifferentialOperator
from symbolics.math.linear_algebra.tensors import Matrix, Vector, DualVector
from symbolics.primitives.functions import Hermite
from symbolics.primitives.elementary.exponentials import Gaussian
from symbolics.math.linear_algebra.tensors import PauliZ
from symbolics.core.base_types import ExpandableConstant

sp.init_printing(use_unicode=True)

# 1. Define our spatial coordinate
x, y, z = sp.symbols('x y z')
n, m = sp.symbols('n m')


print("=== 1. TESTING FUNCTION ALGEBRA ===")
# Create two simple wavefunctions
F = define_function("F", sp.sin(x), x, default_symbol="f")
G = define_function("G", sp.cos(x), x, default_symbol="g")

f_inst = F(x)
g_inst = G(x)

print(f"Addition:       {f_inst + g_inst}")
print(f"Subtraction:    {f_inst - g_inst}")
print(f"Multiplication: {f_inst * g_inst}")
print(f"Division:       {f_inst / g_inst}")
""
print("\n=== 2. TESTING TENSOR ALGEBRA ===")
A = Matrix('A', 2, 2, symbol='A')
B = Matrix('B', 2, 2, symbol='B')

Hn = Hermite(n, x)
Hm = Hermite(m, y)
H3 = Hermite(3, x)
print(f"H3 symbol: {H3}")
print(f"H3 explicit: {H3.make_explicit()}")
print(f"H3 evaluated: {H3.evaluate()}")





print("\n=== 3. TESTING VECTORS & INNER PRODUCTS ===")
ket = Vector('v', 2, symbol=r'|v\rangle', elements = [Hn, Hm])
bra = DualVector('u', 2, symbol=r'\langle u|', elements = [Hn, Hm])

# This should trigger the `inner_product` rule defined in rules.py
inner = bra * ket
outer = ket * bra
Z = PauliZ()
new = Z*outer
print(new)
print(new.make_explicit())
#
print(inner.evaluate())
print(outer.evaluate())