import sympy as sp
from symbolics.primitives.functions import Hermite

def reproduce():
    x = sp.Symbol('x')
    print("Instantiating Hermite(3, x)...")
    try:
        h = Hermite(3, x)
        print("Instantiation Success!")
        print(f"LaTeX: {sp.latex(h)}")
        
        print("\nEvaluating Hermite(3, x)...")
        evaluated = h.evaluate()
        print("Evaluation Success!")
        print(f"Evaluated: {sp.latex(evaluated)}")
    except Exception as e:
        print(f"Caught expected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reproduce()
