
%load_ext autoreload
%autoreload 2

import sympy as sp
from sympy import pprint
from symbolics.core import Algebra, Ring, Field, VectorSpace, define_function
from symbolics.operators.differential.linear import LinearDifferentialOperator
from symbolics.primitives.functions import Hermite
from symbolics.primitives.elementary.exponentials import Gaussian
from symbolics.core.base_types import ExpandableTensor

class Matrix(ExpandableTensor):
    """A general NxM Matrix mapping."""
    def __new__(cls, name, rows, cols, symbol=None, **kwargs):
        return super().__new__(cls, name, rows, cols, symbol=symbol, **kwargs)

class Vector(ExpandableTensor):
    """A strictly N x 1 Column Vector."""
    def __new__(cls, name, rows, symbol=None, **kwargs):
        # Force the column dimension to 1 to establish vector geometry
        return super().__new__(cls, name, rows, 1, symbol=symbol, **kwargs)


sp.init_printing(use_unicode=True)

# 1. Define our spatial coordinate
x, y, z = sp.symbols('x y z')

# 2. Define gamma dynamically instead of manually typing a whole class!
z_dummy = sp.Symbol('z')
gamma = sp.Function('gamma')(z)

n, m = sp.symbols('n m')
# D
Hn = Hermite(n, x)
Hn = Hn.evaluate()
H2 = Hn.subs(n, 2)
N = sp.Symbol('N') # Abstract dimension size

# Create an N x N matrix and an N x 1 column vector
M = Matrix('M', N, N)
v = Vector('v', N)

# Left multiplication: M * v
state = M * v
