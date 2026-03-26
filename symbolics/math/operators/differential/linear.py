import sympy as sp
from .abstract import AbstractDifferentialOperator

class LinearDifferentialOperator(AbstractDifferentialOperator):
    """
    A strictly linear operator: Sum[ c_n(x) * d^n/dx^n ].
    Inherits template execution but adds analytic dictionary-based algebra.
    """
    def __new__(cls, *args, symbol=None, **kwargs):
        variable = args[0]
        
        # Determine if this is a user initialization or a SymPy AST reconstruction
        is_user_init = False
        terms_dict = None
        
        if len(args) == 2:
            is_user_init = True
        elif len(args) >= 3:
            # If the second argument is a dict, or the third is a string, it is user init.
            # (SymPy reconstruction passes a dummy function as the third argument)
            if isinstance(args[1], dict) or isinstance(args[2], str):
                is_user_init = True
        
        if is_user_init:
            arg1 = args[1]
            
            if isinstance(arg1, dict):
                terms_dict = arg1
            else:
                # Treat arg1 as a SymPy expression and project it into a polynomial
                poly = sp.Poly(arg1, variable)
                # sp.Poly.as_dict() returns keys as tuples of degrees, e.g., {(2,): 1, (1,): -10}
                terms_dict = {deg[0]: coeff for deg, coeff in poly.as_dict().items()}
            
            # If a third positional argument was provided, treat it as the symbol string
            if len(args) >= 3 and symbol is None:
                symbol = args[2]
                
            # Build the linear template programmatically
            F = sp.Function(r'\Phi')(variable)
            template = sum(sp.sympify(c) * (F if n == 0 else sp.Derivative(F, (variable, n))) 
                           for n, c in terms_dict.items())
            
            # Pass to Abstract base, explicitly passing the symbol
            return super().__new__(cls, variable, expr_template=template, dummy_func=F, symbol=symbol, **kwargs)

        # SymPy reconstruction fallback
        return super().__new__(cls, *args, symbol=symbol, **kwargs)

    @property
    def terms_dict(self):
        """
        Reconstructs the {order: coefficient} dictionary from the template.
        Useful if you ever need to inspect the operator's components analytically.
        """
        terms = {}
        # Expand to ensure terms are separated by addition
        expanded_template = sp.expand(self.template)
        
        # Helper to extract from a single term
        def _extract_term(term):
            if not term.has(self.dummy_func):
                return
            # Check for derivatives
            derivs = term.atoms(sp.Derivative)
            if derivs:
                for d in derivs:
                    if d.expr == self.dummy_func:
                        order = d.derivative_count
                        coeff = term.subs(d, 1)
                        terms[order] = terms.get(order, 0) + coeff
            else:
                # It's a 0th order term (just the function)
                coeff = term.subs(self.dummy_func, 1)
                terms[0] = terms.get(0, 0) + coeff

        if isinstance(expanded_template, sp.Add):
            for arg in expanded_template.args:
                _extract_term(arg)
        else:
            _extract_term(expanded_template)
            
        return terms

    @property
    def terms(self):
        """Helper to get the {order: coefficient} dictionary."""
        return self.terms_dict 

    # # ---------------------------------------------------------
    # # ANALYTIC REDUCTION (Bypassing the Factory)
    # # ---------------------------------------------------------
    
    # def __add__(self, other):
    #     if isinstance(other, LinearDifferentialOperator) and self.variable == other.variable:
    #         # Merge dictionaries: {n: c1} + {n: c2} -> {n: c1 + c2}
    #         new_terms = self.terms.copy()
    #         for n, coeff in other.terms.items():
    #             new_terms[n] = new_terms.get(n, 0) + coeff
    #         return LinearDifferentialOperator(self.variable, new_terms)
    #     return super().__add__(other)

    # def __mul__(self, other):
    #     # 1. Scalar multiplication (e.g., 2 * D)
    #     if not hasattr(other, 'definition'): 
    #         new_terms = {n: coeff * other for n, coeff in self.terms.items()}
    #         return LinearDifferentialOperator(self.variable, new_terms)

    #     # 2. Operator Composition (e.g., D * D)
    #     if isinstance(other, LinearDifferentialOperator) and self.variable == other.variable:
    #         new_terms = {}
    #         for n, c1 in self.terms.items():
    #             for m, c2 in other.terms.items():
    #                 # (c1 * D^n) * (c2 * D^m) = (c1 * c2) * D^(n+m)
    #                 order = n + m
    #                 new_terms[order] = new_terms.get(order, 0) + (c1 * c2)
    #         return LinearDifferentialOperator(self.variable, new_terms)
            
    #     return super().__mul__(other)

    # def __pow__(self, n):
    #     """Handles D**n by repeated composition."""
    #     if not isinstance(n, int) or n < 0:
    #         raise ValueError("Operator power must be a non-negative integer.")
    #     if n == 0:
    #         return LinearDifferentialOperator(self.variable, {0: 1}) # Identity
        
    #     res = self
    #     for _ in range(n - 1):
    #         res = res * self
    #     return res