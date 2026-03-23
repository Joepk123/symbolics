import sympy as sp

class LinearDifferentialOperator:
    def __init__(self, variable, poly_expr=None):
        self.x = variable
        self.D = sp.Symbol(r'\hat{D}_{}')
        
        # Logic: If it's a Poly, convert to Expr. If None, use D.
        if isinstance(poly_expr, sp.Poly):
            self.poly = poly_expr.as_expr()
        elif poly_expr is not None:
            self.poly = sp.sympify(poly_expr)
        else:
            self.poly = self.D

    @classmethod
    def from_poly(cls, variable, sympy_poly):
        """
        Creates an operator directly from a SymPy Poly object.
        Extracts the expression and the coordinate variable.
        """
        return cls(variable, sympy_poly.as_expr())

    # --- Operator Overloading ---
    def __add__(self, other):
        if isinstance(other, (int, float, sp.Basic)):
            return LinearDifferentialOperator(self.x, self.poly + other)
        return LinearDifferentialOperator(self.x, self.poly + other.poly)

    def __mul__(self, other):
        # Composition of operators: (D+1)(D-1) = D^2 - 1
        if isinstance(other, LinearDifferentialOperator):
            return LinearDifferentialOperator(self.x, sp.expand(self.poly * other.poly))
        # If multiplying by a constant/expression, treat as scaling
        return LinearDifferentialOperator(self.x, self.poly * other)

    def __pow__(self, n):
        return LinearDifferentialOperator(self.x, self.poly**n)
    
    # --- Unary Negation (-L) ---
    def __neg__(self):
        """Handles the unary minus: -L"""
        return LinearDifferentialOperator(self.x, -self.poly)

    # --- Binary Subtraction (L1 - L2) ---
    def __sub__(self, other):
        """Handles the binary minus: L1 - L2"""
        if isinstance(other, (int, float, sp.Basic)):
            return LinearDifferentialOperator(self.x, self.poly - other)
        # Check if it's another LDO instance
        if isinstance(other, LinearDifferentialOperator):
            return LinearDifferentialOperator(self.x, self.poly - other.poly)
        return NotImplemented

    # --- Right-side Subtraction (5 - L) ---
    def __rsub__(self, other):
        """Handles subtraction when the LDO is on the right side."""
        # This is equivalent to -(self - other)
        return (-self) + other
    # --- Execution ---
    def __call__(self, f_expr):
        """Applies the operator to a SymPy expression."""
        # Explicitly set the generator so SymPy knows D is the variable
        p = sp.Poly(self.poly, self.D)
        result = 0
        
        # SymPy terms are (powers_tuple, coefficient)
        for powers, coeff in p.terms():
            # powers is a tuple, e.g., (2,) for D^2. We take the first element.
            deg = powers[0]
            
            # Mapping D^n -> d^n/dx^n
            # We use coeff (the SymPy object) instead of coeffs[0]
            result += coeff * sp.diff(f_expr, self.x, int(deg))
            
        return result

    def _repr_latex_(self):
        """
        This is the magic method Jupyter/VS Code looks for.
        It must return a string wrapped in $$ or $$.
        """
        # Convert the internal polynomial to LaTeX via SymPy's printer
        latex_str = sp.latex(self.poly)
        return f"${latex_str}$"

    def __repr__(self):
        return f"Op({self.poly})"