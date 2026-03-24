# core/algebra.py

from abc import ABC, abstractmethod
from .blueprints import AdditiveBlueprint, MultiplicativeBlueprint, DivisibleBlueprint
# ---------------------------------------------------------
# 1. GROUPS
# ---------------------------------------------------------
class Group(ABC):
    """The absolute base class for a mathematical Group."""
    @abstractmethod
    def operate(self, other): pass
    
    @abstractmethod
    def inverse(self): pass

class AdditiveGroup(AdditiveBlueprint, ABC):
    """An Abelian Group using addition."""
    @abstractmethod
    def __neg__(self): pass

    def operate(self, other):
        return self.__add__(other)
    
    def inverse(self):
        return self.__neg__()

    def __sub__(self, other):
        """Free behavior: a - b = a + (-b)"""
        return self.__add__(other.__neg__())


# ---------------------------------------------------------
# 2. RINGS
# ---------------------------------------------------------
class Ring(AdditiveGroup, MultiplicativeBlueprint, ABC):
    """
    A Ring is an Additive Group equipped with multiplication.
    Multiplication does not guarantee division (no inverses).
    Ideal for: Differential Operators, Matrices.
    """
    pass


# ---------------------------------------------------------
# 3. FIELDS
# ---------------------------------------------------------
class Field(Ring, DivisibleBlueprint, ABC):
    """
    A Field is a Commutative Ring where non-zero elements can be divided.
    Ideal for: Real Numbers, Complex Numbers, Physical Constants.
    """
    pass


# ---------------------------------------------------------
# 4. VECTOR SPACES
# ---------------------------------------------------------
class VectorSpace(AdditiveGroup, ABC):
    """
    A Vector Space allows addition and scaling by a scalar (Field element).
    """
    @abstractmethod
    def __mul__(self, scalar):
        """Right scalar multiplication: vector * scalar"""
        pass

    @abstractmethod
    def __rmul__(self, scalar):
        """Left scalar multiplication: scalar * vector"""
        pass

    @abstractmethod
    def __truediv__(self, scalar):
        """Scaling by the inverse of a scalar."""
        pass


# ---------------------------------------------------------
# 5. ALGEBRAS
# ---------------------------------------------------------
class Algebra(Ring, ABC):
    """
    An Algebra over a Field. 
    It is a Vector Space that also allows elements to be multiplied with each other.
    """
    pass