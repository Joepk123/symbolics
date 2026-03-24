# operators/differential/linear.py

import sympy as sp
from .abstract import AbstractDifferentialOperator

class LinearDifferentialOperator(AbstractDifferentialOperator):
    """
    A linear differential operator that can absorb algebraic operations 
    to remain a single LinearDifferentialOperator object.
    """
    def __new__(cls, variable, terms_dict, **kwargs):
        # ... (keep your existing __new__ logic here) ...
        return super().__new__(cls, variable, expr_template=template, dummy_func=F, **kwargs)

    @property
    def terms(self):
        """Helper to get the {order: coefficient} dictionary."""
        # This uses the extraction logic we discussed previously
        return self.terms_dict 

    # ---------------------------------------------------------
    # ANALYTIC REDUCTION (Bypassing the Factory)
    # ---------------------------------------------------------
    
    def __add__(self, other):
        if isinstance(other, LinearDifferentialOperator) and self.variable == other.variable:
            # Merge dictionaries: {n: c1} + {n: c2} -> {n: c1 + c2}
            new_terms = self.terms.copy()
            for n, coeff in other.terms.items():
                new_terms[n] = new_terms.get(n, 0) + coeff
            return LinearDifferentialOperator(self.variable, new_terms)
        return super().__add__(other)

    def __mul__(self, other):
        # 1. Scalar multiplication (e.g., 2 * D)
        if not hasattr(other, 'definition'): 
            new_terms = {n: coeff * other for n, coeff in self.terms.items()}
            return LinearDifferentialOperator(self.variable, new_terms)

        # 2. Operator Composition (e.g., D * D)
        # Note: This assumes constant coefficients for simplicity in this D^2 example.
        if isinstance(other, LinearDifferentialOperator) and self.variable == other.variable:
            new_terms = {}
            for n, c1 in self.terms.items():
                for m, c2 in other.terms.items():
                    # (c1 * D^n) * (c2 * D^m) = (c1 * c2) * D^(n+m)
                    order = n + m
                    new_terms[order] = new_terms.get(order, 0) + (c1 * c2)
            return LinearDifferentialOperator(self.variable, new_terms)
            
        return super().__mul__(other)

    def __pow__(self, n):
        """Handles D**n by repeated composition."""
        if not isinstance(n, int) or n < 0:
            raise ValueError("Operator power must be a non-negative integer.")
        if n == 0:
            return LinearDifferentialOperator(self.variable, {0: 1}) # Identity
        
        res = self
        for _ in range(n - 1):
            res = res * self
        return res