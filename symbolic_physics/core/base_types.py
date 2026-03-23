# core/base_types.py

import sympy as sp
from .mixin import ExpansionMixin
from .blueprints import Additive, Multiplicative, Divisible

class ExpandableFunction(sp.Function, ExpansionMixin, Additive, Multiplicative, Divisible):
    """
    Base class for wavefunctions (Hermite, Gaussian). 
    Supports full arithmetic (+, -, *, /) and deep expansion.
    """
    # Note: Logic for these operators will be handled by the Factory later.
    pass

class ExpandableOperator(ExpansionMixin, Additive, Multiplicative):
    """
    Base class for operators (DifferentialOperator).
    Supports +, -, and * (composition), but NOT division.
    """
    def __init__(self, variable, poly=None):
        self.x = variable
        self.D = sp.Symbol('D')
        self.poly = sp.sympify(poly) if poly is not None else self.D

    def __mul__(self, other):
        """Implemented as operator composition (e.g., D * D = D^2)."""
        if isinstance(other, ExpandableOperator):
            return self.__class__(self.x, sp.expand(self.poly * other.poly))
        return self.poly * other