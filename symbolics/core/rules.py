# core/rules.py
"""
This script defines mathematical operations and what the output will be of such an operation.
"""
import sympy as sp
from .registry import register_operation
from .base_types import ExpandableFunction, ExpandableConstant, ExpandableTensor
from ..math.linear_algebra.tensors import CompositeMatrix, CompositeVector

# IMPORT THE NEW INSTANCE HELPERS
from .factory import add_instances, sub_instances, mul_instances, div_instances

# --- Functions ---
register_operation(ExpandableFunction, ExpandableFunction, '+', add_instances)
register_operation(ExpandableFunction, ExpandableFunction, '-', sub_instances)
register_operation(ExpandableFunction, ExpandableFunction, '*', mul_instances)
register_operation(ExpandableFunction, ExpandableFunction, '/', div_instances)


# --- Tensors ---
def scale_vector(scalar: ExpandableConstant, vec: CompositeVector):
    lazy_math = sp.MatMul(scalar, vec)
    
    # We use CompositeVector so the lazy_math is saved in the definition!
    return CompositeVector(
        ast_node=lazy_math, 
        rows=vec.rows, 
        symbol=f"{scalar.symbol_name}{vec.symbol_name}"
    )

def add_tensors(t1, t2):
    lazy_math = sp.MatAdd(t1, t2)
    
    # Dynamically choose the right composite wrapper
    WrapperClass = CompositeVector if t1.cols == 1 else CompositeMatrix
    
    return WrapperClass(
        ast_node=lazy_math, 
        rows=t1.rows, 
        cols=t1.cols, 
        symbol=f"\\left({t1.symbol_name} + {t2.symbol_name}\\right)"
    )

def sub_tensors(t1, t2):
    lazy_math = sp.MatAdd(t1, sp.MatMul(sp.Integer(-1), t2))
    return type(t1)(
        lazy_math, 
        t1.rows, 
        t1.cols, 
        symbol=f"{t1.symbol_name} - {t2.symbol_name}", 
        is_sum=True  # <--- Subtractions need brackets during multiplication too!
    )

def scale_tensor(scalar: ExpandableConstant, t1: ExpandableTensor) -> ExpandableTensor:
    """Scalar Multiplication"""
    lazy_math = sp.MatMul(scalar, t1)
    return type(t1)(lazy_math, t1.rows, t1.cols, symbol=f"{scalar.symbol_name}{t1.symbol_name}")

register_operation(ExpandableTensor, ExpandableTensor, '+', add_tensors)
register_operation(ExpandableTensor, ExpandableTensor, '-', sub_tensors)
register_operation(ExpandableConstant, ExpandableTensor, '*', scale_tensor)
register_operation(ExpandableTensor, ExpandableConstant, '*', lambda t, c: scale_tensor(c, t))


# --- Operators ---
