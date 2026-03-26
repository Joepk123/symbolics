# core/rules.py
"""
This script defines mathematical operations and what the output will be of such an operation.
"""
from .registry import register_operation
from .base_types import ExpandableFunction, ExpandableOperator, ExpandableConstant, ExpandableTensor
from .factory import CompositeSum, CompositeSub, CompositeMul, CompositeDiv

# --- Functions ---
def add_functions(f1, f2):
    return CompositeSum(f1, f2)

def sub_functions(f1, f2):
    return CompositeSub(f1, f2)

def mul_functions(f1, f2):
    return CompositeMul(f1, f2)

def div_functions(f1, f2):
    return CompositeDiv(f1, f2)

register_operation(ExpandableFunction, ExpandableFunction, '+', add_functions)
register_operation(ExpandableFunction, ExpandableFunction, '-', sub_functions)
register_operation(ExpandableFunction, ExpandableFunction, '*', mul_functions)
register_operation(ExpandableFunction, ExpandableFunction, '/', div_functions)


# --- Vectors ---
def add_vectors(v1, v2):
    return