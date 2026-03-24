# core/algebra.py

from abc import ABC, abstractmethod
import inspect
from .mixin import ExpansionMixin

def _get_signature_counts(obj_or_cls):
    """
    Returns (idx_count, coord_count) for a given class or instance.
    Checks for cached metadata before falling back to introspection.
    """
    is_obj = not isinstance(obj_or_cls, type)
    target_cls = obj_or_cls.__class__ if is_obj else obj_or_cls

    if hasattr(target_cls, '_idx_count') and hasattr(target_cls, '_coord_count'):
        if is_obj and hasattr(obj_or_cls, 'args'):
            # Dynamically resolve exact arity for nested variadic instances
            return target_cls._idx_count, max(0, len(obj_or_cls.args) - target_cls._idx_count)
        return target_cls._idx_count, target_cls._coord_count
    
    sig = inspect.signature(target_cls.__new__)
    # Filter out non-mathematical arguments like 'cls' and 'symbol'
    params = [p for p in sig.parameters.values() 
              if p.name not in ('cls', 'args', 'kwargs', 'symbol')
              and p.kind in (p.POSITIONAL_OR_KEYWORD, p.POSITIONAL_ONLY)]
    
    # Design Contract: Primitives have 1 coordinate, which is the last argument.
    idx_count = max(0, len(params) - 1)
    coord_count = 1 if len(params) > 0 else 0
    
    return idx_count, coord_count

def _assemble_new_args(op_self, op_other):
    """
    Splits operand args into indices/coords and reassembles them for a composite object.
    Handles shared vs. tensor-product coordinates.
    """
    idx_A, _ = _get_signature_counts(op_self)
    idx_B, _ = _get_signature_counts(op_other)
    
    self_indices = op_self.args[:idx_A]
    self_coords = op_self.args[idx_A:]
    
    other_indices = op_other.args[:idx_B]
    other_coords = op_other.args[idx_B:]
    
    # Simple case: assume shared coordinates if they are identical
    new_coords = self_coords if self_coords == other_coords else self_coords + other_coords
    return self_indices + other_indices + new_coords

def _get_symbols_kwargs(op_self, op_other):
    """Extracts custom symbols to preserve them through factory routing."""
    kwargs = {}
    if getattr(op_self, '_custom_symbol', None): kwargs['sym_A'] = op_self._custom_symbol
    if getattr(op_other, '_custom_symbol', None): kwargs['sym_B'] = op_other._custom_symbol
    
    _, c_A = _get_signature_counts(op_self)
    _, c_B = _get_signature_counts(op_other)
    kwargs['_c_A'] = c_A
    kwargs['_c_B'] = c_B
    return kwargs

def _wrap_if_needed(obj):
    if isinstance(obj, ExpansionMixin):
        return obj
    import sympy as sp
    if isinstance(obj, (sp.Expr, int, float, complex)):
        from .base_types import SymPyWrapper
        return SymPyWrapper(sp.sympify(obj))
    return None

# ---------------------------------------------------------
# 1. GROUPS
# ---------------------------------------------------------
class Group(ABC):
    """The absolute base class for a mathematical Group."""
    @abstractmethod
    def operate(self, other): pass
    
    @abstractmethod
    def inverse(self): pass

class AdditiveGroup(ABC):
    """An Abelian Group using addition."""

    def operate(self, other):
        return self.__add__(other)
    
    def inverse(self):
        return self.__neg__()

    def __sub__(self, other):
        other_obj = _wrap_if_needed(other)
        if other_obj is None:
            return NotImplemented
            
        from .factory import CompositeSub
        CombinedClass = CompositeSub(self.__class__, other_obj.__class__)
        new_args = _assemble_new_args(self, other_obj)
        kwargs = _get_symbols_kwargs(self, other_obj)
        return CombinedClass(*new_args, **kwargs)

    def __add__(self, other):
        other_obj = _wrap_if_needed(other)
        if other_obj is None:
            return NotImplemented
            
        from .factory import CompositeSum
        CombinedClass = CompositeSum(self.__class__, other_obj.__class__)
        new_args = _assemble_new_args(self, other_obj)
        kwargs = _get_symbols_kwargs(self, other_obj)
        return CombinedClass(*new_args, **kwargs)

    def __radd__(self, other):
        """Commutative addition for Abelian Groups."""
        return self.__add__(other)

    def __rsub__(self, other):
        """Handles non-commutative subtraction order (other - self)."""
        other_obj = _wrap_if_needed(other)
        if other_obj is None:
            return NotImplemented
            
        from .factory import CompositeSub
        CombinedClass = CompositeSub(other_obj.__class__, self.__class__)
        new_args = _assemble_new_args(other_obj, self)
        kwargs = _get_symbols_kwargs(other_obj, self)
        return CombinedClass(*new_args, **kwargs)
    
    def __neg__(self):
        """Delegates the negation to SymPy's core algebra engine."""
        return self * -1


# ---------------------------------------------------------
# 2. RINGS
# ---------------------------------------------------------
class Ring(AdditiveGroup, ABC):
    """
    A Ring is an Additive Group equipped with multiplication.
    Multiplication does not guarantee division (no inverses).
    Ideal for: Differential Operators, Matrices.
    """
    def __mul__(self, other):
        other_obj = _wrap_if_needed(other)
        if other_obj is None:
            return NotImplemented
            
        from .factory import CompositeMul
        CombinedClass = CompositeMul(self.__class__, other_obj.__class__)
        new_args = _assemble_new_args(self, other_obj)
        kwargs = _get_symbols_kwargs(self, other_obj)
        return CombinedClass(*new_args, **kwargs)

    def __rmul__(self, other):
        """Preserves strict non-commutative operand order (other * self)."""
        other_obj = _wrap_if_needed(other)
        if other_obj is None:
            return NotImplemented
            
        from .factory import CompositeMul
        CombinedClass = CompositeMul(other_obj.__class__, self.__class__)
        new_args = _assemble_new_args(other_obj, self)
        kwargs = _get_symbols_kwargs(other_obj, self)
        return CombinedClass(*new_args, **kwargs)


# ---------------------------------------------------------
# 3. FIELDS
# ---------------------------------------------------------
class Field(Ring, ABC):
    """
    A Field is a Commutative Ring where non-zero elements can be divided.
    Ideal for: Real Numbers, Complex Numbers, Physical Constants.
    """
    def __truediv__(self, other):
        other_obj = _wrap_if_needed(other)
        if other_obj is None:
            return NotImplemented
            
        from .factory import CompositeDiv
        CombinedClass = CompositeDiv(self.__class__, other_obj.__class__)
        new_args = _assemble_new_args(self, other_obj)
        kwargs = _get_symbols_kwargs(self, other_obj)
        return CombinedClass(*new_args, **kwargs)

    def __rtruediv__(self, other):
        """Handles non-commutative division order (other / self)."""
        other_obj = _wrap_if_needed(other)
        if other_obj is None:
            return NotImplemented
            
        from .factory import CompositeDiv
        CombinedClass = CompositeDiv(other_obj.__class__, self.__class__)
        new_args = _assemble_new_args(other_obj, self)
        kwargs = _get_symbols_kwargs(other_obj, self)
        return CombinedClass(*new_args, **kwargs)


# ---------------------------------------------------------
# 4. VECTOR SPACES
# ---------------------------------------------------------
class VectorSpace(AdditiveGroup, ABC):
    """
    A Vector Space allows addition and scaling by a scalar (Field element).
    """
    def __mul__(self, scalar):
        """Right scalar multiplication: vector * scalar"""
        scalar_obj = _wrap_if_needed(scalar)
        if scalar_obj is None:
            return NotImplemented
        from .factory import CompositeMul
        CombinedClass = CompositeMul(self.__class__, scalar_obj.__class__)
        new_args = _assemble_new_args(self, scalar_obj)
        kwargs = _get_symbols_kwargs(self, scalar_obj)
        return CombinedClass(*new_args, **kwargs)

    def __rmul__(self, scalar):
        """Left scalar multiplication: scalar * vector"""
        scalar_obj = _wrap_if_needed(scalar)
        if scalar_obj is None:
            return NotImplemented
        from .factory import CompositeMul
        CombinedClass = CompositeMul(scalar_obj.__class__, self.__class__)
        new_args = _assemble_new_args(scalar_obj, self)
        kwargs = _get_symbols_kwargs(scalar_obj, self)
        return CombinedClass(*new_args, **kwargs)

    def __truediv__(self, scalar):
        """Scaling by the inverse of a scalar."""
        scalar_obj = _wrap_if_needed(scalar)
        if scalar_obj is None:
            return NotImplemented
        from .factory import CompositeDiv
        CombinedClass = CompositeDiv(self.__class__, scalar_obj.__class__)
        new_args = _assemble_new_args(self, scalar_obj)
        kwargs = _get_symbols_kwargs(self, scalar_obj)
        return CombinedClass(*new_args, **kwargs)


# ---------------------------------------------------------
# 5. ALGEBRAS
# ---------------------------------------------------------
class Algebra(Ring, VectorSpace, ABC):
    """
    An Algebra over a Field. 
    It is a Vector Space that also allows elements to be multiplied with each other.
    """
    def __truediv__(self, other):
        other_obj = _wrap_if_needed(other)
        if other_obj is None:
            return NotImplemented
            
        from .factory import CompositeDiv
        CombinedClass = CompositeDiv(self.__class__, other_obj.__class__)
        new_args = _assemble_new_args(self, other_obj)
        kwargs = _get_symbols_kwargs(self, other_obj)
        return CombinedClass(*new_args, **kwargs)

    def __rtruediv__(self, other):
        """Handles non-commutative division order (other / self)."""
        other_obj = _wrap_if_needed(other)
        if other_obj is None:
            return NotImplemented
            
        from .factory import CompositeDiv
        CombinedClass = CompositeDiv(other_obj.__class__, self.__class__)
        new_args = _assemble_new_args(other_obj, self)
        kwargs = _get_symbols_kwargs(other_obj, self)
        return CombinedClass(*new_args, **kwargs)