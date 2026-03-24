# core/base_types.py

import sympy as sp
from abc import ABCMeta

from .mixin import ExpansionMixin
from .expandable import Expandable
from .algebra import Algebra, Ring, Field, AdditiveGroup

# ---------------------------------------------------------
# METACLASS FUSION
# ---------------------------------------------------------
class CASMeta(ABCMeta, type(sp.Function)):
    pass

# ---------------------------------------------------------
# 1. SCALARS & CONSTANTS
# ---------------------------------------------------------
class ExpandableConstant(Field, Expandable, sp.Expr, metaclass=CASMeta):
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
    
    Args:
        class_name (str): The name of the generated class.
        expr_template: The SymPy expression defining the function.
        *dummy_vars: The dummy variables used in the template (indices first, coordinate last).
        default_symbol (str, optional): The default LaTeX symbol for printing.
        
    Returns:
        A new ExpandableFunction class perfectly integrated into the CAS environment.
    """
    expr_temp = sp.sympify(expr_template)
    idx_c = max(0, len(dummy_vars) - 1)
    coord_c = 1 if len(dummy_vars) > 0 else 0

    def __new__(cls, *args, symbol=None, **kwargs):
        sym = symbol if symbol is not None else default_symbol
        return ExpandableFunction.__new__(cls, *args, symbol=sym, **kwargs)

    @property
    def definition(self):
        sub_dict = dict(zip(dummy_vars, self.args))
        return expr_temp.subs(sub_dict)
        
    cls_dict = {
        '__new__': __new__,
        'definition': definition,
        '_idx_count': idx_c,
        '_coord_count': coord_c,
        '__doc__': f"Auto-generated ExpandableFunction: {class_name}({', '.join(str(v) for v in dummy_vars)}) -> {expr_temp}"
    }
    
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
class ExpandableOperator(Ring, Expandable, sp.Expr, metaclass=CASMeta):
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
class ExpandableTensor(Algebra, Expandable, sp.MatrixSymbol, metaclass=CASMeta):
    """
    Mathematically: An element of a Tensor Algebra.
    Implementation: A multidimensional array mapping supporting non-commutative algebra.
    """
    def __new__(cls, name, n, m, symbol=None, **kwargs):
        # MatrixSymbol natively handles dimensional validation (name, rows, cols)
        obj = super().__new__(cls, name, n, m, **kwargs)
        # Allow symbol to be None for dynamically generated unnamed tensors
        obj._custom_symbol = symbol 
        return obj

    @property
    def symbol_name(self):
        """Safely resolves the visual identity for dynamic or explicitly named tensors."""
        if self._custom_symbol is not None:
            return self._custom_symbol
        # Fallback to the MatrixExpr's internal name or the minted class name
        name_arg = self.args[0]
        return name_arg if name_arg else self.__class__.__name__

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
        # MatrixExpr args are (name, rows, cols)
        return ((self.args[0], self.rows, self.cols), {"symbol": self._custom_symbol})

    def __truediv__(self, other):
        return NotImplemented

    def __rtruediv__(self, other):
        return NotImplemented

    # ---------------------------------------------------------
    # NATIVE MATRIX ALGEBRA (Bypassing Pointwise Factory)
    # ---------------------------------------------------------
    def __add__(self, other):
        return sp.MatAdd(self, other)
    def __radd__(self, other):
        return sp.MatAdd(other, self)
    def __sub__(self, other):
        return sp.MatAdd(self, sp.MatMul(sp.Integer(-1), other))
    def __mul__(self, other):
        return sp.MatMul(self, other)
    def __rmul__(self, other):
        return sp.MatMul(other, self)