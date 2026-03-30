# core/algebra.py

from abc import ABC, abstractmethod
import inspect
from .mixin import ExpansionMixin
from .blueprints import AdditiveBlueprint, MultiplicativeBlueprint, DivisibleBlueprint

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

class AdditiveGroup(AdditiveBlueprint, ABC): pass

# ---------------------------------------------------------
# 2. RINGS
# ---------------------------------------------------------
class Ring(AdditiveGroup, MultiplicativeBlueprint, ABC): pass

# ---------------------------------------------------------
# 3. FIELDS
# ---------------------------------------------------------
class Field(Ring, DivisibleBlueprint, ABC): pass

# ---------------------------------------------------------
# 4. VECTOR SPACES
# ---------------------------------------------------------
class VectorSpace(AdditiveGroup, ABC): pass

# ---------------------------------------------------------
# 5. ALGEBRAS
# ---------------------------------------------------------
class Algebra(Ring, VectorSpace, ABC): pass
