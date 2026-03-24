# core/algebra.py

from abc import ABC, abstractmethod

# ---------------------------------------------------------
# 1. GROUPS
# ---------------------------------------------------------
class Group(ABC):
    """The absolute base class for a mathematical Group."""
    @abstractmethod
    def operate(self, other): pass
    
    @abstractmethod
    def inverse(self): pass

class AdditiveGroup(Group):
    """An Abelian Group using addition."""
    @abstractmethod
    def __add__(self, other): pass

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
class Ring(AdditiveGroup):
    """
    A Ring is an Additive Group equipped with multiplication.
    Multiplication does not guarantee division (no inverses).
    Ideal for: Differential Operators, Matrices.
    """
    @abstractmethod
    def __mul__(self, other):
        pass


# ---------------------------------------------------------
# 3. FIELDS
# ---------------------------------------------------------
class Field(Ring):
    """
    A Field is a Commutative Ring where non-zero elements can be divided.
    Ideal for: Real Numbers, Complex Numbers, Physical Constants.
    """
    @abstractmethod
    def __truediv__(self, other):
        pass


# ---------------------------------------------------------
# 4. VECTOR SPACES
# ---------------------------------------------------------
class VectorSpace(AdditiveGroup):
    """
    A Vector Space allows addition of its elements and scaling by a Field element.
    Ideal for: State vectors in Quantum Mechanics.
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
        """Dividing a vector by a scalar is scaling by its inverse."""
        pass


# ---------------------------------------------------------
# 5. ALGEBRAS
# ---------------------------------------------------------
class Algebra(VectorSpace, Ring):
    """
    An Algebra over a Field. 
    It is a Vector Space that also allows elements to be multiplied with each other.
    Ideal for: Continuous Functions (like Hermite and Gaussian wavefunctions).
    """
    # No new methods need to be defined! It inherits everything it needs 
    # from VectorSpace and Ring automatically.
    pass