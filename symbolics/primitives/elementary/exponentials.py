# primitives/exponentials.py

import sympy as sp
from ...core.base_types import ExpandableFunction


class Gaussian(ExpandableFunction):
    """
    Symbolic representation of a Gaussian envelope.
    Because it inherits ExpandableFunction, it automatically acts as an Algebra 
    and routes +, -, *, / through your Factory.
    """
    def __new__(cls, coord, symbol=None, **kwargs):
        # We must explicitly define __new__ so the factory can introspect the coordinate count!
        obj = ExpandableFunction.__new__(cls, coord, **kwargs)
        obj._custom_symbol = symbol
        return obj

    @property
    def definition(self):
        coord = self.args[0]
        return sp.exp(-coord**2)