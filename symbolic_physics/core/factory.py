# core/factory.py

import sympy as sp
import inspect
import operator
from .mixin import ExpansionMixin

def _get_signature_counts(target_cls):
    """
    Returns (idx_count, coord_count) for a given class.
    Checks for cached metadata before falling back to introspection.
    """
    # 1. If it's a factory-generated class, it already knows its shape!
    if hasattr(target_cls, '_idx_count') and hasattr(target_cls, '_coord_count'):
        return target_cls._idx_count, target_cls._coord_count
    
    # 2. If it's a base primitive, inspect the __new__ signature
    sig = inspect.signature(target_cls.__new__)
    params = [p for p in sig.parameters.values() 
              if p.name not in ('cls', 'args', 'kwargs')
              and p.kind in (p.POSITIONAL_OR_KEYWORD, p.POSITIONAL_ONLY)]
    
    # By our Design Contract: Primitives have exactly 1 coordinate at the end.
    idx_count = max(0, len(params) - 1)
    coord_count = 1 if len(params) > 0 else 0
    
    return idx_count, coord_count

def BaseAlgebraicFactory(ClassA, ClassB, op_func, op_symbol, label=None):
    # Extract the exact shape of the child classes
    idx_A, coord_A_count = _get_signature_counts(ClassA)
    idx_B, coord_B_count = _get_signature_counts(ClassB)
    
    # --- FIX: DYNAMIC BASE RESOLUTION ---
    # Find the most specific shared class that includes ExpansionMixin
    common_bases = [
        cls for cls in ClassA.__mro__ 
        if cls in ClassB.__mro__ and issubclass(cls, ExpansionMixin)
    ]
    
    if not common_bases:
        raise TypeError(
            f"Cannot combine {ClassA.__name__} and {ClassB.__name__}: "
            "They do not share a common Expandable base class."
        )
        
    BaseClass = common_bases[0]
    # ------------------------------------
    
    class CombinedFunction(BaseClass):
        # --- STATEFUL METADATA ---
        _idx_count = idx_A + idx_B
        _coord_count = coord_A_count + coord_B_count
        
        def __new__(cls, *args, **kwargs):
            instance = super().__new__(cls, *args, **kwargs)
            instance._args = args
            instance._kwargs = kwargs
            return instance

        @property
        def definition(self):
            # Split arguments strictly by the known index count
            indices = self._args[:self._idx_count]
            coords = self._args[self._idx_count:]
            
            ind_A = indices[:idx_A]
            ind_B = indices[idx_A:]
            
            # --- THE ASYMMETRIC COORDINATE ROUTER ---
            if len(coords) == self._coord_count:
                coord_A = coords[:coord_A_count]
                coord_B = coords[coord_A_count:]
                
            elif len(coords) == coord_A_count and coord_A_count == coord_B_count:
                coord_A, coord_B = coords, coords
                
            elif len(coords) == 1:
                coord_A = coords * coord_A_count
                coord_B = coords * coord_B_count
                
            else:
                raise ValueError(
                    f"Coordinate mismatch in {self.__class__.__name__}. "
                    f"Expected {self._coord_count} (independent) or {coord_A_count} (shared). "
                    f"Got {len(coords)}."
                )
            
            part_a = ClassA(*(ind_A + tuple(coord_A)), **self._kwargs)
            part_b = ClassB(*(ind_B + tuple(coord_B)), **self._kwargs)
            
            # SymPy strips custom attributes, so we use the immutable class name!
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
    return BaseAlgebraicFactory(A, B, operator.add, "+", label)

def CompositeSub(A, B, label=None):
    return BaseAlgebraicFactory(A, B, operator.sub, "-", label)

def CompositeMul(A, B, label=None):
    return BaseAlgebraicFactory(A, B, operator.mul, "", label)

def CompositeDiv(A, B, label=None):
    return BaseAlgebraicFactory(A, B, operator.truediv, "/", label)