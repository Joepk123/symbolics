CAS Architecture Refactor Guide: Type Dispatch Registry & AST Composites
Overview
We are shifting the mathematical routing of the CAS from abstract type-guessing (promotion.py) to a concrete, centralized Type Dispatch Registry (registry.py and rules.py). We are also cleanly separating "Class Generators" (for making new function templates) from "Instance Nodes" (for doing live algebra in the notebook).

Step 1: Delete Obsolete Files
Action: Delete the following file entirely.

symbolics/core/promotion.py

Step 2: Implement the Registry Core
File: symbolics/core/registry.py
Action: Overwrite with the MRO-based dispatcher.

Python
# symbolics/core/registry.py

_OPERATION_MAP = {}

def register_operation(left_type, right_type, op_symbol, func):
    """Registers a mathematical rule for two types."""
    _OPERATION_MAP[(left_type, right_type, op_symbol)] = func

def resolve_operation(left_obj, right_obj, op_symbol):
    """Looks up and executes the rule for the given objects using MRO fallback."""
    for left_class in type(left_obj).mro():
        for right_class in type(right_obj).mro():
            rule = _OPERATION_MAP.get((left_class, right_class, op_symbol))
            if rule:
                return rule(left_obj, right_obj)
                
    return NotImplemented
Step 3: Route Blueprints to the Registry
File: symbolics/core/blueprints.py
Action: Overwrite to delegate all math to the registry.

Python
# symbolics/core/blueprints.py

from .registry import resolve_operation

class AdditiveBlueprint:
    def __add__(self, other): return resolve_operation(self, other, '+')
    def __radd__(self, other): return resolve_operation(other, self, '+')
    def __sub__(self, other): return self.__add__(-other)

class MultiplicativeBlueprint:
    def __mul__(self, other): return resolve_operation(self, other, '*')
    def __rmul__(self, other): return resolve_operation(other, self, '*')

class DivisibleBlueprint:
    def __truediv__(self, other): return resolve_operation(self, other, '/')
    def __rtruediv__(self, other): return resolve_operation(other, self, '/')
Step 4: Update the Mathematical Hierarchy
File: symbolics/core/algebra.py
Action: Inject the blueprints directly into the math hierarchy.

Python
# symbolics/core/algebra.py
from abc import ABC
import sympy as sp
from .blueprints import AdditiveBlueprint, MultiplicativeBlueprint, DivisibleBlueprint

# ... (keep _get_signature_counts and other helpers) ...

class AdditiveGroup(AdditiveBlueprint, ABC): pass
class Ring(AdditiveGroup, MultiplicativeBlueprint, ABC): pass
class Field(Ring, DivisibleBlueprint, ABC): pass
class VectorSpace(AdditiveGroup, ABC): pass
class Algebra(Ring, VectorSpace, ABC): pass
Step 5: Clean Up Base Types
File: symbolics/core/base_types.py
Action: Remove explicit blueprint inheritances from the base classes, as they now inherit them from Algebra, Field, etc.

Python
# symbolics/core/base_types.py

# ... (keep imports) ...

class ExpandableConstant(Expandable, sp.Expr, Field, metaclass=CASMeta):
    pass # Inherits +, -, *, / from Field

class ExpandableFunction(Expandable, sp.Expr, Algebra, metaclass=CASMeta):
    pass # Inherits +, -, * from Algebra

class ExpandableOperator(Expandable, sp.Expr, Ring, metaclass=CASMeta):
    # ... keep your target_var and __call__ logic ...
    def __truediv__(self, other):
        raise TypeError("Division is undefined for Operator Rings.")
    def __rtruediv__(self, other):
        raise TypeError("Division is undefined for Operator Rings.")
Step 6: Add The Alias Method to Expandable
File: symbolics/core/expandable.py
Action: Add the alias method to the Expandable class to allow users to rename composite math nodes.

Python
# symbolics/core/expandable.py
# (Inside the Expandable class, add this method)

    def alias(self, new_symbol):
        """
        Returns a copy of this object with a new visual symbol, 
        preserving the underlying mathematical definition.
        """
        if hasattr(self, 'rows'):
            cols = getattr(self, 'cols', 1)
            new_obj = type(self)(self.definition, self.rows, cols, symbol=new_symbol)
            new_obj._is_sum = False # Clears sum formatting flag
            return new_obj
            
        return type(self)(*self.args, symbol=new_symbol)
Step 7: Refactor the Factory (Classes vs. Instances)
File: symbolics/core/factory.py
Action: Remove promotion imports. Simplify BaseClass resolution. Add ASTCompositeNode and instance helpers.

Python
# symbolics/core/factory.py
import sympy as sp
import inspect
import operator
from .mixin import ExpansionMixin
from .algebra import Field, Ring, Algebra, _get_signature_counts

_FACTORY_CACHE = {}

def CoordinateAlgebraFactory(ClassA, ClassB, op_func, op_symbol, label=None):
    # ... (Keep your mathematical firewall logic) ...
    
    # NEW BASE CLASS RESOLUTION (Replaces promotion.py)
    if issubclass(ClassA, Field) and issubclass(ClassB, Field):
        BaseClass = ClassA
    elif issubclass(ClassA, Field):
        BaseClass = ClassB
    elif issubclass(ClassB, Field):
        BaseClass = ClassA
    else:
        BaseClass = ClassA 

    # ... (Keep the rest of CombinedFunction logic exactly the same) ...

# 1. CLASS GENERATORS (For defining new function types)
def generate_sum_class(A, B, label=None): return CoordinateAlgebraFactory(A, B, operator.add, "+", label)
def generate_sub_class(A, B, label=None): return CoordinateAlgebraFactory(A, B, operator.sub, "-", label)
def generate_mul_class(A, B, label=None): return CoordinateAlgebraFactory(A, B, operator.mul, "", label)
def generate_div_class(A, B, label=None): return CoordinateAlgebraFactory(A, B, operator.truediv, "/", label)

# 2. INSTANCE NODES (For live notebook algebra)
class ASTCompositeNode(sp.Expr):
    def __new__(cls, obj_A, obj_B, op_symbol):
        instance = super().__new__(cls, obj_A, obj_B)
        instance._op_symbol = op_symbol
        return instance
        
    def _latex(self, printer):
        A, B = self.args
        return f"\\left( {printer.doprint(A)} {self._op_symbol} {printer.doprint(B)} \\right)"

def add_instances(A, B): return ASTCompositeNode(A, B, "+")
def sub_instances(A, B): return ASTCompositeNode(A, B, "-")
def mul_instances(A, B): return ASTCompositeNode(A, B, "")
def div_instances(A, B): return ASTCompositeNode(A, B, "/")
Step 8: Upgrade Tensor Classes & Add Composites
File: symbolics/math/linear_algebra/tensors.py
Action: Fix Vector.__new__ argument counting. Add is_sum flags. Add CompositeMatrix and CompositeVector.

Python
# symbolics/math/linear_algebra/tensors.py
import sympy as sp
from ...core.base_types import ExpandableMatrix

class Matrix(ExpandableMatrix):
    def __new__(cls, *args, symbol=None, is_sum=False, **kwargs):
        obj = super().__new__(cls, str(args[0]), args[1], args[2], symbol=symbol, **kwargs)
        obj._is_sum = is_sum
        return obj

class Vector(ExpandableMatrix):
    def __new__(cls, *args, symbol=None, is_sum=False, **kwargs):
        # Handle SymPy rebuilding with 3 args
        obj = super().__new__(cls, str(args[0]), args[1], 1, symbol=symbol, **kwargs)
        obj._is_sum = is_sum
        return obj

class DualVector(ExpandableMatrix):
    def __new__(cls, *args, symbol=None, is_sum=False, **kwargs):
        cols = args[2] if len(args) >= 3 else args[1]
        obj = super().__new__(cls, str(args[0]), 1, cols, symbol=symbol, **kwargs)
        obj._is_sum = is_sum
        return obj

# --- COMPOSITE WRAPPERS (To safely hold AST Math Trees) ---
class CompositeMatrix(Matrix):
    def __new__(cls, ast_node, rows, cols, symbol=None, is_sum=False, **kwargs):
        name = f"CompMat_{hash(ast_node)}"
        obj = super().__new__(cls, name, rows, cols, symbol=symbol, is_sum=is_sum, **kwargs)
        obj._ast_node = ast_node
        return obj

    @property
    def definition(self): return self._ast_node

class CompositeVector(Vector):
    def __new__(cls, ast_node, rows, symbol=None, is_sum=False, **kwargs):
        name = f"CompVec_{hash(ast_node)}"
        obj = super().__new__(cls, name, rows, symbol=symbol, is_sum=is_sum, **kwargs)
        obj._ast_node = ast_node
        return obj

    @property
    def definition(self): return self._ast_node
Step 9: Write the Physics Rules
File: symbolics/core/rules.py
Action: Define the exact behavior and format formatting for functions, constants, and tensors.

Python
# symbolics/core/rules.py
import sympy as sp
from .registry import register_operation
from .base_types import ExpandableFunction, ExpandableConstant, ExpandableTensor
from ..math.linear_algebra.tensors import CompositeMatrix, CompositeVector, Vector, DualVector
from .factory import add_instances, sub_instances, mul_instances, div_instances

# --- FUNCTIONS ---
register_operation(ExpandableFunction, ExpandableFunction, '+', add_instances)
register_operation(ExpandableFunction, ExpandableFunction, '-', sub_instances)
register_operation(ExpandableFunction, ExpandableFunction, '*', mul_instances)
register_operation(ExpandableFunction, ExpandableFunction, '/', div_instances)

# --- TENSORS ---
def add_tensors(t1, t2):
    lazy_math = sp.MatAdd(t1, t2)
    WrapperClass = CompositeVector if t1.cols == 1 else CompositeMatrix
    return WrapperClass(lazy_math, t1.rows, t1.cols, symbol=f"{t1.symbol_name} + {t2.symbol_name}", is_sum=True)

def sub_tensors(t1, t2):
    lazy_math = sp.MatAdd(t1, sp.MatMul(sp.Integer(-1), t2))
    WrapperClass = CompositeVector if t1.cols == 1 else CompositeMatrix
    return WrapperClass(lazy_math, t1.rows, t1.cols, symbol=f"{t1.symbol_name} - {t2.symbol_name}", is_sum=True)

def scale_tensor(scalar, t1):
    sym = t1.symbol_name
    if getattr(t1, '_is_sum', False):
        sym = f"\\left( {sym} \\right)"
    
    lazy_math = sp.MatMul(scalar, t1)
    WrapperClass = CompositeVector if t1.cols == 1 else CompositeMatrix
    return WrapperClass(lazy_math, t1.rows, t1.cols, symbol=f"{scalar.symbol_name} {sym}")

def inner_product(dual_vec, vec):
    lazy_math = sp.MatMul(dual_vec, vec)
    return ExpandableConstant(expr=lazy_math, symbol=f"\\langle {dual_vec.name} | {vec.name} \\rangle")

register_operation(ExpandableTensor, ExpandableTensor, '+', add_tensors)
register_operation(ExpandableTensor, ExpandableTensor, '-', sub_tensors)
register_operation(ExpandableConstant, ExpandableTensor, '*', scale_tensor)
register_operation(ExpandableTensor, ExpandableConstant, '*', lambda t, c: scale_tensor(c, t))
register_operation(DualVector, Vector, '*', inner_product)
Step 10: Trigger the Registry on Boot
File: symbolics/__init__.py
Action: Add the import at the bottom of the file to populate the memory map instantly.

Python
# symbolics/__init__.py
# ... existing imports ...

# Load physics rules into the registry
from .core import rules