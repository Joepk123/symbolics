# core/factory.py

import sympy as sp
import inspect
import operator
from .mixin import ExpansionMixin
from .promotion import resolve_promoted_base
from .algebra import Field, Ring

def _get_signature_counts(target_cls):
    """
    Returns (idx_count, coord_count) for a given class.
    Checks for cached metadata before falling back to introspection.
    """
    if hasattr(target_cls, '_idx_count') and hasattr(target_cls, '_coord_count'):
        return target_cls._idx_count, target_cls._coord_count
    
    sig = inspect.signature(target_cls.__new__)
    params = [p for p in sig.parameters.values() 
              if p.name not in ('cls', 'args', 'kwargs')
              and p.kind in (p.POSITIONAL_OR_KEYWORD, p.POSITIONAL_ONLY)]
    
    idx_count = max(0, len(params) - 1)
    coord_count = 1 if len(params) > 0 else 0
    
    return idx_count, coord_count


def CoordinateAlgebraFactory(ClassA, ClassB, op_func, op_symbol, label=None):
    """
    Strictly handles pointwise algebra for coordinate-based mappings (Vector Spaces, Algebras).
    """
    # ---------------------------------------------------------
    # THE MATHEMATICAL FIREWALL
    # ---------------------------------------------------------
    if issubclass(ClassA, Ring) or issubclass(ClassB, Ring):
        raise TypeError(
            f"CoordinateAlgebraFactory intercepted a Ring ({ClassA.__name__} or {ClassB.__name__}). "
            "Operators are endomorphisms and lack pointwise spatial coordinates. "
            "They must process their own internal AST algebra rather than using the pointwise factory."
        )

    idx_A, coord_A_count = _get_signature_counts(ClassA)
    idx_B, coord_B_count = _get_signature_counts(ClassB)
    
    BaseClass = resolve_promoted_base(ClassA, ClassB)
    
    class CombinedFunction(BaseClass):
        _idx_count = idx_A + idx_B
        _coord_count = max(coord_A_count, coord_B_count) 
        
        def __new__(cls, *args, **kwargs):
            instance = super().__new__(cls, *args, **kwargs)
            instance._args = args
            instance._kwargs = kwargs
            return instance

        @property
        def definition(self):
            indices = self._args[:self._idx_count]
            coords = self._args[self._idx_count:]
            
            ind_A = indices[:idx_A]
            ind_B = indices[idx_A:]
            
            if issubclass(ClassA, Field):
                coord_A = ()
                coord_B = coords
            elif issubclass(ClassB, Field):
                coord_A = coords
                coord_B = ()
            elif len(coords) == self._coord_count:
                coord_A = coords[:coord_A_count]
                coord_B = coords[coord_A_count:]
            elif len(coords) == coord_A_count and coord_A_count == coord_B_count:
                coord_A, coord_B = coords, coords
            elif len(coords) == 1:
                coord_A = coords * coord_A_count
                coord_B = coords * coord_B_count
            else:
                raise ValueError("Coordinate mismatch.")
            
            part_a = ClassA(*(ind_A + tuple(coord_A)), **self._kwargs)
            part_b = ClassB(*(ind_B + tuple(coord_B)), **self._kwargs)
            
            is_struct_a = part_a.__class__.__name__.startswith('Combined_')
            is_struct_b = part_b.__class__.__name__.startswith('Combined_')
            
            expr_a = part_a.definition if is_struct_a else part_a
            expr_b = part_b.definition if is_struct_b else part_b
            
            return op_func(expr_a, expr_b)

        def _repr_latex_(self):
            tex_indices = [sp.latex(a) for a in self._args[:self._idx_count]]
            tex_coords = ", ".join([sp.latex(c) for c in self._args[self._idx_count:]])
            
            lbl = label if label else f"{ClassA.__name__}{op_symbol}{ClassB.__name__}"
            if "{" in lbl and "}" in lbl:
                formatted_label = lbl.format(*tex_indices)
                return f"${formatted_label}({tex_coords})$"
            if tex_indices:
                idx_str = ", ".join(tex_indices)
                return f"${lbl}_{{{idx_str}}}({tex_coords})$"
            return f"${lbl}({tex_coords})$"

    CombinedFunction.__name__ = f"Combined_{ClassA.__name__}_{ClassB.__name__}"
    return CombinedFunction


def CompositeSum(A, B, label=None):
    return CoordinateAlgebraFactory(A, B, operator.add, "+", label)

def CompositeSub(A, B, label=None):
    return CoordinateAlgebraFactory(A, B, operator.sub, "-", label)

def CompositeMul(A, B, label=None):
    return CoordinateAlgebraFactory(A, B, operator.mul, "", label)

def CompositeDiv(A, B, label=None):
    return CoordinateAlgebraFactory(A, B, operator.truediv, "/", label)