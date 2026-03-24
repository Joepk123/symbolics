# symbolic_physics/core/blueprints.py

from .mixin import ExpansionMixin

class AdditiveBlueprint:
    def __add__(self, other):
        if not isinstance(other, ExpansionMixin):
            return NotImplemented # Let SymPy handle raw numbers/symbols
            
        from .factory import CompositeSum
        CombinedClass = CompositeSum(self.__class__, other.__class__)
        return CombinedClass(*(self.args + other.args))

    def __sub__(self, other):
        if not isinstance(other, ExpansionMixin):
            return NotImplemented
            
        from .factory import CompositeSub
        CombinedClass = CompositeSub(self.__class__, other.__class__)
        return CombinedClass(*(self.args + other.args))

class MultiplicativeBlueprint:
    def __mul__(self, other):
        if not isinstance(other, ExpansionMixin):
            return NotImplemented
            
        from .factory import CompositeMul
        CombinedClass = CompositeMul(self.__class__, other.__class__)
        return CombinedClass(*(self.args + other.args))

class DivisibleBlueprint:
    def __truediv__(self, other):
        if not isinstance(other, ExpansionMixin):
            return NotImplemented
            
        from .factory import CompositeDiv
        CombinedClass = CompositeDiv(self.__class__, other.__class__)
        return CombinedClass(*(self.args + other.args))