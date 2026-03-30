import sys
import os
import sympy as sp

# Ensure we can import symbolics from the current directory
sys.path.append(os.getcwd())

from symbolics.math.linear_algebra.tensors import Matrix, Vector, DualVector, PauliZ
from symbolics.primitives.functions import Hermite

# Define symbols
x, y = sp.symbols('x y')
n, m = sp.symbols('n m')

# Create Hermite functions
Hn = Hermite(n, x)
Hm = Hermite(m, y)

# Create Vectors/Matrices
ket = Vector('v', 2, symbol=r'|v\rangle', elements=[Hn, Hm])
bra = DualVector('u', 2, symbol=r'\langle u|', elements=[Hn, Hm])
Z = PauliZ()

# Perform algebra
outer = ket * bra
new = Z * outer

print("--- Current Behavior ---")
print("new LaTeX representation:")
print(sp.latex(new))
print("\nnew.make_explicit() LaTeX:")
explicit = new.make_explicit()
print(sp.latex(explicit))
print("\nType of explicit:")
print(type(explicit))

# Show evaluate() for comparison (should expand Hermite)
print("\nnew.evaluate() LaTeX (expands Hermite):")
evaluated = new.evaluate()
print(sp.latex(evaluated))
