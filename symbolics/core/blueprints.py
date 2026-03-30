# symbolics/core/blueprints.py

from .registry import resolve_operation

class AdditiveBlueprint:
    def __add__(self, other): return resolve_operation(self, other, '+')
    def __radd__(self, other): return resolve_operation(other, self, '+')
    def __sub__(self, other): return resolve_operation(self, other, '-')
    def __rsub__(self, other): return resolve_operation(other, self, '-')

class MultiplicativeBlueprint:
    def __mul__(self, other): return resolve_operation(self, other, '*')
    def __rmul__(self, other): return resolve_operation(other, self, '*')

class DivisibleBlueprint:
    def __truediv__(self, other): return resolve_operation(self, other, '/')
    def __rtruediv__(self, other): return resolve_operation(other, self, '/')
