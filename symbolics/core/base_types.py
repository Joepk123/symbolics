# core/base_types.py

import sympy as sp
from abc import ABCMeta
from sympy.tensor.array import ImmutableDenseNDimArray
from sympy.tensor.array.expressions.array_expressions import ArraySymbol
from sympy.tensor.array import tensorproduct

from .mixin import ExpansionMixin
from .expandable import Expandable
from .algebra import Algebra, Ring, Field, AdditiveGroup

# ---------------------------------------------------------
# METACLASS FUSION
# ---------------------------------------------------------
class CASMeta(ABCMeta, type(sp.Function)):
    pass

class ExprMeta(ABCMeta, type(sp.Expr)):
    pass

# ---------------------------------------------------------
# 1. SCALARS & CONSTANTS
# ---------------------------------------------------------
class ExpandableConstant(Field, Expandable, sp.Expr, metaclass=ExprMeta):
    """
    Mathematically: An element of a Field.
    Implementation: A scalar mapping with an arity of 0. Inherits 
    printing logic natively from the Expandable parent class.
    """
    pass

class SymPyWrapper(ExpandableConstant):
    """
    Wraps a native SymPy expression or scalar so it can interact 
    with the CoordinateAlgebraFactory without consuming spatial coordinates.
    """
    _idx_count = 1
    _coord_count = 0

    def __new__(cls, expr, symbol=None, **kwargs):
        obj = ExpandableConstant.__new__(cls, sp.sympify(expr), **kwargs)
        obj._custom_symbol = symbol
        return obj

    @property
    def definition(self):
        return self.args[0]

    def _latex(self, printer):
        return printer.doprint(self.args[0])

    def _sympystr_(self, printer):
        return printer.doprint(self.args[0])

# ---------------------------------------------------------
# 2. FUNCTIONS
# ---------------------------------------------------------
class ExpandableFunction(Algebra, Expandable, sp.Function, metaclass=CASMeta):
    """
    Mathematically: An Algebra over a Field.
    Implementation: Automatically handles pointwise algebraic operations (+, -, *), 
    coordinate routing, and evaluation.
    """
    pass

def define_function(class_name, expr_template, *dummy_vars, default_symbol=None):
    """
    Dynamically generates a new ExpandableFunction subclass from a mathematical expression.
    """
    expr_temp = sp.sympify(expr_template)
    idx_c = max(0, len(dummy_vars) - 1)
    coord_c = 1 if len(dummy_vars) > 0 else 0

    def __new__(cls, *args, symbol=None, **kwargs):
        # Fallback to the default_symbol if the user doesn't provide one
        sym = symbol if symbol is not None else default_symbol
        # Pass the args safely up to the Expandable base class
        return ExpandableFunction.__new__(cls, *args, symbol=sym, **kwargs)

    @property
    def definition(self):
        # 2. FIXED: Proper indentation so this only runs during evaluation
        if len(self.args) != len(dummy_vars):
            raise ValueError(
                f"{class_name} expected {len(dummy_vars)} arguments "
                f"({', '.join(str(v) for v in dummy_vars)}), but got {len(self.args)}."
            )
            
        # Bind the dummy variables to the actual spatial coordinates passed in
        sub_dict = dict(zip(dummy_vars, self.args))
        return expr_temp.subs(sub_dict)
        
    cls_dict = {
        '__new__': __new__,
        'definition': definition,
        '_idx_count': idx_c,
        '_coord_count': coord_c,
        '__doc__': f"Auto-generated ExpandableFunction: {class_name}({', '.join(str(v) for v in dummy_vars)}) -> {expr_temp}"
    }
    
    # Generate the class dynamically using your custom CAS metaclass
    return CASMeta(class_name, (ExpandableFunction,), cls_dict)
    
    
class EvaluatedFunction(ExpandableFunction):
    """
    Wraps a fully evaluated SymPy expression while retaining the Algebra mathematical type 
    and preserving spatial coordinates for Factory routing.
    """
    _idx_count = 1
    _coord_count = 0

    def __new__(cls, expr, *coords, symbol=None, **kwargs):
        obj = ExpandableFunction.__new__(cls, sp.sympify(expr), *coords, **kwargs)
        obj._custom_symbol = symbol
        return obj

    @property
    def definition(self):
        return self.args[0]

    def _latex(self, printer):
        return printer.doprint(self.args[0])

    def _sympystr_(self, printer):
        return printer.doprint(self.args[0])

# ---------------------------------------------------------
# 3. OPERATORS
# ---------------------------------------------------------
class ExpandableOperator(Ring, Expandable, sp.Expr, metaclass=ExprMeta):
    """
    Mathematically: A Ring of Endomorphisms.
    Implementation: Supports structural composition (*) but strictly blocks division.
    """
    
    @property
    def target_var(self):
        """Safely retrieves the target variable from SymPy's immutable args."""
        return self.args[0]

    def __call__(self, target_expr):
        raise NotImplementedError("Operators must define a __call__ method.")

    # We must explicitly block SymPy's innate division for Expr objects
    def __truediv__(self, other):
        raise TypeError("Division is undefined for Operator Rings.")

    def __rtruediv__(self, other):
        raise TypeError("Division is undefined for Operator Rings.")
    
    # Visual overrides ensuring internal AST templates are hidden
    def _latex(self, printer):
        return self._custom_symbol if self._custom_symbol else self.__class__.__name__

    def _pretty(self, printer):
        sym = self._custom_symbol if self._custom_symbol else self.__class__.__name__
        return printer._print(sp.Symbol(sym))

    def _sympystr_(self, printer):
        return self._custom_symbol if self._custom_symbol else self.__class__.__name__

# ---------------------------------------------------------
# 4. TENSORS
# ---------------------------------------------------------
class ExpandableTensor(Algebra, Expandable, ArraySymbol, metaclass=ExprMeta):
    """
    Mathematically: An element of a Tensor Algebra.
    Implementation: A multidimensional array mapping supporting non-commutative algebra.
    """
    def __new__(cls, *args, symbol=None, elements=None, **kwargs):
        # SymPy AST reconstruction strictly passes *args as (name, *dims).
        # We rigorously cast args[0] to a Python str to prevent SymPy Str type errors!
        name, dims = str(args[0]), args[1:]
        # ArraySymbol natively handles arbitrary dimensional validation (name, *dims)
        obj = super().__new__(cls, name, *dims, **kwargs)
        # Allow symbol to be None for dynamically generated unnamed tensors
        obj._custom_symbol = symbol 
        obj._elements = elements
        return obj

    @property
    def definition(self):
        if hasattr(self, '_elements') and self._elements is not None:
            return ImmutableDenseNDimArray(self._elements)
        return self

    @property
    def symbol_name(self):
        """Safely resolves the visual identity for dynamic or explicitly named tensors."""
        if self._custom_symbol is not None:
            return self._custom_symbol
        # Fallback to the MatrixExpr's internal name or the minted class name
        name_arg = self.args[0]
        return str(name_arg) if name_arg else self.__class__.__name__

    def _latex(self, printer):
        """Renders the Tensor symbol (conventionally bolded in LaTeX)."""
        return f"\\mathbf{{{self.symbol_name}}}"

    def _pretty(self, printer):
        """Renders the Tensor symbol for console output."""
        return printer._print(sp.Symbol(self.symbol_name))

    def _sympystr_(self, printer):
        """Overrides generic string casting to prevent raw SymPy internal prints."""
        return self.symbol_name

    def __getnewargs_ex__(self):
        # ArraySymbol args are (name, *shape)
        return ((str(self.args[0]), *self.shape), {"symbol": self._custom_symbol, "elements": self._elements})

    def __truediv__(self, other):
        return NotImplemented

    def __rtruediv__(self, other):
        return NotImplemented

    def __add__(self, other):
        return TensorWrapper(sp.Add(self, other))
    def __radd__(self, other):
        return TensorWrapper(sp.Add(other, self))
    def __sub__(self, other):
        return TensorWrapper(sp.Add(self, sp.Mul(sp.Integer(-1), other)))
    def __mul__(self, other):
        # Safely handle commutative scalar scaling vs Non-commutative Tensor Products
        if isinstance(other, (sp.Expr, int, float, complex)) and not getattr(other, 'is_Matrix', False) and not isinstance(other, (ArraySymbol, sp.MatrixExpr)):
            return TensorWrapper(sp.Mul(self, other))
        return TensorWrapper(tensorproduct(self, other))
    def __rmul__(self, other):
        if isinstance(other, (sp.Expr, int, float, complex)) and not getattr(other, 'is_Matrix', False) and not isinstance(other, (ArraySymbol, sp.MatrixExpr)):
            return TensorWrapper(sp.Mul(other, self))
        return TensorWrapper(tensorproduct(other, self))

class TensorWrapper(Algebra, Expandable, sp.Expr, metaclass=ExprMeta):
    """
    Wraps native SymPy array/tensor expressions to preserve 
    the Object-Oriented evaluate() method and route matrix algebra correctly.
    """
    def __new__(cls, expr, symbol=None, **kwargs):
        obj = sp.Expr.__new__(cls, expr)
        obj._custom_symbol = symbol
        return obj

    @property
    def shape(self):
        return self.args[0].shape if hasattr(self.args[0], 'shape') else ()

    @property
    def definition(self):
        return self.args[0]

    def _latex(self, printer):
        return printer.doprint(self.args[0])

    def _sympystr_(self, printer):
        return printer.doprint(self.args[0])

    def __add__(self, other): return TensorWrapper(sp.Add(self, other))
    def __radd__(self, other): return TensorWrapper(sp.Add(other, self))
    def __sub__(self, other): return TensorWrapper(sp.Add(self, sp.Mul(sp.Integer(-1), other)))
    
    def __mul__(self, other): 
        if isinstance(other, (sp.Expr, int, float, complex)) and not getattr(other, 'is_Matrix', False) and not isinstance(other, (ArraySymbol, sp.MatrixExpr)):
            return TensorWrapper(sp.Mul(self, other))
        return TensorWrapper(tensorproduct(self, other))
        
    def __rmul__(self, other): 
        if isinstance(other, (sp.Expr, int, float, complex)) and not getattr(other, 'is_Matrix', False) and not isinstance(other, (ArraySymbol, sp.MatrixExpr)):
            return TensorWrapper(sp.Mul(other, self))
        return TensorWrapper(tensorproduct(other, self))

    def __truediv__(self, other): return NotImplemented
    def __rtruediv__(self, other): return NotImplemented

# ---------------------------------------------------------
# 5. MATRICES (2D TENSORS)
# ---------------------------------------------------------
class ExpandableMatrix(Algebra, Expandable, sp.MatrixSymbol, metaclass=ExprMeta):
    """
    Mathematically: An element of a Matrix Algebra (Rank-2 Tensor).
    Implementation: A 2D mapping supporting strict non-commutative matrix algebra.
    """
    def __new__(cls, *args, symbol=None, elements=None, **kwargs):
        name, rows, cols = str(args[0]), args[1], args[2]
        obj = super().__new__(cls, name, rows, cols, **kwargs)
        obj._custom_symbol = symbol 
        obj._elements = elements
        return obj

    @property
    def definition(self):
        if hasattr(self, '_elements') and self._elements is not None:
            return sp.ImmutableMatrix(self._elements)
        return self

    @property
    def symbol_name(self):
        if self._custom_symbol is not None: return self._custom_symbol
        name_arg = self.args[0]
        return str(name_arg) if name_arg else self.__class__.__name__

    def _latex(self, printer): return f"\\mathbf{{{self.symbol_name}}}"
    def _pretty(self, printer): return printer._print(sp.Symbol(self.symbol_name))
    def _sympystr_(self, printer): return self.symbol_name

    def __getnewargs_ex__(self):
        return ((str(self.args[0]), self.rows, self.cols), {"symbol": self._custom_symbol, "elements": self._elements})

    def __truediv__(self, other): return NotImplemented
    def __rtruediv__(self, other): return NotImplemented

    def __add__(self, other): return MatrixWrapper(sp.MatAdd(self, other))
    def __radd__(self, other): return MatrixWrapper(sp.MatAdd(other, self))
    def __sub__(self, other): return MatrixWrapper(sp.MatAdd(self, sp.MatMul(sp.Integer(-1), other)))
    def __mul__(self, other): return MatrixWrapper(sp.MatMul(self, other))
    def __rmul__(self, other): return MatrixWrapper(sp.MatMul(other, self))

class MatrixWrapper(Algebra, Expandable, sp.MatrixExpr, metaclass=ExprMeta):
    """Wraps native SymPy matrix expressions (MatMul/MatAdd) for delayed AST execution."""
    def __new__(cls, expr, symbol=None, **kwargs):
        obj = sp.Expr.__new__(cls, expr)
        obj._custom_symbol = symbol
        return obj

    @property
    def shape(self): return self.args[0].shape
    @property
    def definition(self): return self.args[0]
    def _latex(self, printer): return printer.doprint(self.args[0])
    def _sympystr_(self, printer): return printer.doprint(self.args[0])

    def __add__(self, other): return MatrixWrapper(sp.MatAdd(self, other))
    def __radd__(self, other): return MatrixWrapper(sp.MatAdd(other, self))
    def __sub__(self, other): return MatrixWrapper(sp.MatAdd(self, sp.MatMul(sp.Integer(-1), other)))
    def __mul__(self, other): return MatrixWrapper(sp.MatMul(self, other))
    def __rmul__(self, other): return MatrixWrapper(sp.MatMul(other, self))
    def __truediv__(self, other): return NotImplemented
    def __rtruediv__(self, other): return NotImplemented