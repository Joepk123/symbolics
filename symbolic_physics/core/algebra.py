# core/algebra.py

from abc import ABC, abstractmethod

# ---------------------------------------------------------
# 1. GROUPS
# ---------------------------------------------------------
class Group(ABC):
    """
    The absolute base class for a mathematical Group.
    It does not assume addition or multiplication, only that 
    elements can be combined and inverted.
    """
    @abstractmethod
    def operate(self, other):
        """The defining binary operation of the group."""
        pass
    
    @abstractmethod
    def inverse(self):
        """Returns the group inverse of this element."""
        pass

class AdditiveGroup(Group):
    """
    An Abelian (commutative) Group where the binary operation is addition (+), 
    and the inverse is negation (-).
    """
    @abstractmethod
    def __add__(self, other): 
        pass

    @abstractmethod
    def __neg__(self): 
        pass

    def operate(self, other):
        """Maps the abstract group operation to Python's addition."""
        return self.__add__(other)
    
    def inverse(self):
        """Maps the abstract group inverse to Python's negation."""
        return self.__neg__()

    # --- Free Behavior ---
    # Because we know this is an Additive Group, we can automatically 
    # define subtraction for all child classes!
    def __sub__(self, other):
        """a - b is strictly defined as a + (-b)"""
        return self.__add__(other.__neg__())

class MultiplicativeGroup(Group):
    """
    A Group where the binary operation is multiplication (*), 
    and the inverse is the reciprocal (1/x).
    """
    @abstractmethod
    def __mul__(self, other): 
        pass

    @abstractmethod
    def __invert__(self): 
        """Using Python's bitwise NOT (~) as a stand-in for multiplicative inverse, 
        or you could use a custom .reciprocal() method."""
        pass

    # --- Fulfilling the Group Contract ---
    def operate(self, other):
        return self.__mul__(other)
    
    def inverse(self):
        return self.__invert__()

    # --- Free Behavior ---
    def __truediv__(self, other):
        """a / b is strictly defined as a * (b^-1)"""
        return self.__mul__(other.__invert__())


# ---------------------------------------------------------
# 2. RINGS
# ---------------------------------------------------------
class Ring(AdditiveGroup):
    """
    A Ring is an Additive Group that also supports multiplication.
    Multiplication does not necessarily have to be commutative.
    (Note: Division is NOT guaranteed in a Ring).
    Examples: Matrices, Linear Operators, Polynomials.
    """
    @abstractmethod
    def __mul__(self, other): pass


# ---------------------------------------------------------
# 3. FIELDS
# ---------------------------------------------------------
class Field(Ring):
    """
    A Field is a Commutative Ring where every non-zero element 
    has a multiplicative inverse (division is allowed).
    Examples: Real Numbers, Complex Numbers, Rational Functions.
    """
    @abstractmethod
    def __truediv__(self, other): pass


# ---------------------------------------------------------
# 4. VECTOR SPACES & ALGEBRAS
# ---------------------------------------------------------
class Vector(AdditiveGroup):
    """
    A Vector Space element. It can be added/subtracted with other vectors,
    and multiplied by a scalar (an element from a Field).
    """
    @abstractmethod
    def __mul__(self, scalar): 
        """Scalar multiplication from the right."""
        pass

    @abstractmethod
    def __rmul__(self, scalar): 
        """Scalar multiplication from the left."""
        pass

class AlgebraElement(Vector, Ring):
    """
    An Algebra over a Field. 
    It is a Vector Space that also allows multiplication between its own elements
    (e.g., the tensor product of two wavefunctions, or composition of operators).
    """
    pass