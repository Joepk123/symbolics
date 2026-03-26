
%load_ext autoreload
%autoreload 2

import sympy as sp
from sympy import pprint
from symbolics.core import Algebra, Ring, Field, VectorSpace, define_function
from symbolics.math.operators.differential.linear import LinearDifferentialOperator
from symbolics.math.linear_algebra.tensors import Matrix, Vector, DualVector
from symbolics.primitives.functions import Hermite
from symbolics.primitives.elementary.exponentials import Gaussian
from symbolics.math.linear_algebra.tensors import PauliZ
"""
make_explicit,
evaluate_target,
evaluate
"""

sp.init_printing(use_unicode=True)

# 1. Define our spatial coordinate
x, y, z = sp.symbols('x y z')

# 2. Define gamma dynamically instead of manually typing a whole class!
z_dummy = sp.Symbol('z^\\dagger')
gamma = sp.Function('gamma')(z)

n, m = sp.symbols('n m')
# D
# Create arbitrary symbolic elements for your vector
alpha, beta = sp.symbols('alpha beta')

# Instantiate the vector, passing the elements in!
state = Vector('v', 2, elements=[alpha, beta])
M = Matrix('M', 2, 2, elements=[[x, x], [y, y]])

# Define a DualVector (1x2 row vector)
dual_state = DualVector('w', 2, elements=[[x, y]])

# ---------------------------------------------------------
# MATHEMATICAL OPERATIONS
# ---------------------------------------------------------
# 1. Inner Product (1x2 * 2x1 -> 1x1 Matrix)
inner_product = dual_state * state
print("Inner Product:")
display(inner_product.evaluate())

# 2. Outer Product / Tensor Product (2x1 * 1x2 -> 2x2 Matrix)
outer_product = state * dual_state
print("Outer Product:")
display(outer_product.evaluate())

# 3. Multiply it against the PauliZ operator
Z = PauliZ()
result = Z * state

# This will perfectly evaluate Z into its 2x2 grid, evaluate the state 
# into its 2x1 grid, and physically compute the matrix multiplication!
display(result.evaluate())
