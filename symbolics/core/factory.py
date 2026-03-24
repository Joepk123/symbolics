# core/factory.py

import sympy as sp
import inspect
import operator
from .mixin import ExpansionMixin
from .promotion import resolve_promoted_base
from .algebra import Field, Ring, Algebra, _get_signature_counts


def CoordinateAlgebraFactory(ClassA, ClassB, op_func, op_symbol, label=None):
    """
    Strictly handles pointwise algebra for coordinate-based mappings (Vector Spaces, Algebras).
    """
    # ---------------------------------------------------------
    # THE MATHEMATICAL FIREWALL
    # ---------------------------------------------------------
    # This check prevents pure Rings (like Operators) from being processed
    # by the pointwise coordinate factory. Algebras and Fields are also Rings,
    # but they have coordinate structures and should be allowed.
    is_op_A = issubclass(ClassA, Ring) and not issubclass(ClassA, (Algebra, Field))
    is_op_B = issubclass(ClassB, Ring) and not issubclass(ClassB, (Algebra, Field))
    if is_op_A or is_op_B:
        op_name = ClassA.__name__ if is_op_A else ClassB.__name__
        raise TypeError(
            f"CoordinateAlgebraFactory intercepted a pure Ring ({op_name}). "
            "Operators are endomorphisms and lack pointwise spatial coordinates. "
            "They must process their own internal AST algebra rather than using the pointwise factory."
        )

    idx_A, coord_A_count = _get_signature_counts(ClassA)
    idx_B, coord_B_count = _get_signature_counts(ClassB)
    
    BaseClass = resolve_promoted_base(ClassA, ClassB)
    
    class CombinedFunction(BaseClass):
        _idx_count = idx_A + idx_B
        _coord_count = coord_A_count + coord_B_count 
        
        def __new__(cls, *args, **kwargs):
            sym_A = kwargs.pop('sym_A', None)
            sym_B = kwargs.pop('sym_B', None)
            c_A = kwargs.pop('_c_A', coord_A_count)
            c_B = kwargs.pop('_c_B', coord_B_count)
            
            instance = BaseClass.__new__(cls, *args, **kwargs)
            instance._args = args
            instance._kwargs = kwargs
            instance._sym_A = sym_A
            instance._sym_B = sym_B
            instance._c_A = c_A
            instance._c_B = c_B
            return instance

        def _get_parts(self):
            indices = self._args[:self._idx_count]
            coords = self._args[self._idx_count:]
            
            ind_A = indices[:idx_A]
            ind_B = indices[idx_A:]
            
            # Using dynamically injected arities protects infinitely nested trees
            c_A, c_B = self._c_A, self._c_B

            if issubclass(ClassA, Field):
                coord_A = ()
                coord_B = coords
            elif issubclass(ClassB, Field):
                coord_A = coords
                coord_B = ()
            elif len(coords) == c_A + c_B:
                coord_A = coords[:c_A]
                coord_B = coords[c_A:]
            elif len(coords) == c_A and c_A == c_B:
                coord_A, coord_B = coords, coords
            elif len(coords) == 1:
                coord_A = coords * c_A
                coord_B = coords * c_B
            else:
                raise ValueError(f"Coordinate mismatch. Expected {c_A + c_B} or {c_A}, got {len(coords)}")

            kwargs_A = dict(self._kwargs)
            if self._sym_A is not None: kwargs_A['symbol'] = self._sym_A
            
            kwargs_B = dict(self._kwargs)
            if self._sym_B is not None: kwargs_B['symbol'] = self._sym_B
            
            part_a = ClassA(*(ind_A + tuple(coord_A)), **kwargs_A)
            part_b = ClassB(*(ind_B + tuple(coord_B)), **kwargs_B)
            return part_a, part_b

        @property
        def definition(self):
            return self.structural_expr

        @property
        def structural_expr(self):
            """
            Returns an inert SymPy node representing the exact mathematical structure 
            of this composite object. This makes the underlying structure fully known 
            and accessible to standard SymPy traversal!
            """
            part_a, part_b = self._get_parts()
            
            if op_symbol == "+": 
                return sp.Add(part_a, part_b, evaluate=False)
            elif op_symbol == "-": 
                return sp.Add(part_a, sp.Mul(sp.Integer(-1), part_b, evaluate=False), evaluate=False)
            elif op_symbol == "": 
                return sp.Mul(part_a, part_b, evaluate=False)
            elif op_symbol == "/": 
                return sp.Mul(part_a, sp.Pow(part_b, sp.Integer(-1), evaluate=False), evaluate=False)
            return None

        def _latex(self, printer):
            if label:
                tex_indices = [printer.doprint(a) for a in self._args[:self._idx_count]]
                tex_coords = ", ".join([printer.doprint(c) for c in self._args[self._idx_count:]])
                if "{" in label and "}" in label:
                    return f"{label.format(*tex_indices)}\\left({tex_coords}\\right)"
                if tex_indices:
                    return f"{label}_{{{', '.join(tex_indices)}}}\\left({tex_coords}\\right)"
                return f"{label}\\left({tex_coords}\\right)"
            
            # Delegate completely to SymPy's native AST printer
            node = self.structural_expr
            if node is not None:
                return printer.doprint(node)
                
            part_a, part_b = self._get_parts()
            return f"{printer.doprint(part_a)} {op_symbol} {printer.doprint(part_b)}"

        def _sympystr_(self, printer):
            if label:
                return f"{label}({', '.join([printer.doprint(a) for a in self._args])})"
            
            node = self.structural_expr
            if node is not None:
                return printer.doprint(node)
                
            part_a, part_b = self._get_parts()
            return f"{printer.doprint(part_a)} {op_symbol} {printer.doprint(part_b)}"

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