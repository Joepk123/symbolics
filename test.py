
%load_ext autoreload
%autoreload 2

import numpy as np
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
alpha = sp.symbols('alpha')

x, alpha = sp.symbols('x alpha')

def f(x: float) -> int:
    return np.sin(x)

Matrix()