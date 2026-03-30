import sympy as sp
from symbolics.math.linear_algebra.tensors import Matrix, Vector, DualVector, PauliZ

def reproduce():
    # Using the same symbols as in the user's report (including their typos for faithfulness)
    ket = Vector('v', 2, symbol=r'|v\r\angle')
    bra = DualVector('u', 2, symbol=r'\l\angle u|')
    Z = PauliZ()
    
    outer = ket * bra
    print(f"Outer symbol: {outer.symbol_name}")
    
    new = Z * outer
    print(f"New symbol: {new.symbol_name}")
    print(f"LaTeX output: {sp.latex(new)}")

if __name__ == "__main__":
    reproduce()
