# symbolic_physics/core/blueprints.py

from .mixin import ExpansionMixin

class AdditiveBlueprint:
    def __add__(self, other):
        if not isinstance(other, ExpansionMixin):
            return NotImplemented # Let SymPy handle raw numbers/symbols
            
        from .factory import CompositeSum
        CombinedClass = CompositeSum(self.__class__, other.__class__)
        return CombinedClass(*(self.args + other.args))

    def __radd__(self, other):
        """Commutative addition for Abelian Groups."""
        return self.__add__(other)

    def __sub__(self, other):
        if not isinstance(other, ExpansionMixin):
            return NotImplemented
            
        from .factory import CompositeSub
        CombinedClass = CompositeSub(self.__class__, other.__class__)
        return CombinedClass(*(self.args + other.args))

    def __rsub__(self, other):
        """Handles non-commutative subtraction order (other - self)."""
        if not isinstance(other, ExpansionMixin):
            return NotImplemented
            
        from .factory import CompositeSub
        # Notice the order reversal for the factory to preserve mathematical structure
        CombinedClass = CompositeSub(other.__class__, self.__class__)
        return CombinedClass(*(other.args + self.args))
    
    def __neg__(self):
        """
        Satisfies the AdditiveGroup abstract method requirement.
        Delegates the negation to SymPy's core algebra engine by multiplying by -1.
        """
        return self * -1


class MultiplicativeBlueprint:
    def __mul__(self, other):
        if not isinstance(other, ExpansionMixin):
            return NotImplemented
            
        from .factory import CompositeMul
        CombinedClass = CompositeMul(self.__class__, other.__class__)
        return CombinedClass(*(self.args + other.args))

    def __rmul__(self, other):
        """
        Satisfies the VectorSpace abstract method for left scalar multiplication.
        Preserves strict non-commutative operand order (other * self).
        """
        if not isinstance(other, ExpansionMixin):
            return NotImplemented
            
        from .factory import CompositeMul
        CombinedClass = CompositeMul(other.__class__, self.__class__)
        return CombinedClass(*(other.args + self.args))


class DivisibleBlueprint:
    def __truediv__(self, other):
        if not isinstance(other, ExpansionMixin):
            return NotImplemented
            
        from .factory import CompositeDiv
        CombinedClass = CompositeDiv(self.__class__, other.__class__)
        return CombinedClass(*(self.args + other.args))

    def __rtruediv__(self, other):
        """Handles non-commutative division order (other / self)."""
        if not isinstance(other, ExpansionMixin):
            return NotImplemented
            
        from .factory import CompositeDiv
        CombinedClass = CompositeDiv(other.__class__, self.__class__)
        return CombinedClass(*(other.args + self.args))