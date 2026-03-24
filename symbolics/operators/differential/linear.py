import sympy as sp
from .abstract import AbstractDifferentialOperator

class LinearDifferentialOperator(AbstractDifferentialOperator):
    """
    A strictly linear differential operator: Sum[ c_n(x) * d^n/dx^n ].
    Inherits the robust dummy-template execution from AbstractDifferentialOperator.
    """
    def __new__(cls, variable, terms_dict, dummy_func=None, **kwargs):
        # 1. Standardize the dummy placeholder function
        F = dummy_func if dummy_func else sp.Function(r'\Phi')(variable)
        
        # 2. Programmatically build the linear mathematical template
        template = sp.Integer(0)
        for n, coeff in terms_dict.items():
            c_expr = sp.sympify(coeff)
            
            if n == 0:
                # 0th derivative is just multiplying the function by the coefficient
                template += c_expr * F
            else:
                # nth derivative applied to the dummy function
                template += c_expr * sp.Derivative(F, (variable, n))
                
        # 3. Pass the fully constructed linear template to the Abstract base class
        return super().__new__(cls, variable, expr_template=template, dummy_func=F, **kwargs)

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