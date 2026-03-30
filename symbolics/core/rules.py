# symbolics/core/rules.py
import sympy as sp
from .registry import register_operation
from .base_types import ExpandableFunction, ExpandableConstant, ExpandableTensor, ExpandableMatrix, ExpandableOperator
from ..math.linear_algebra.tensors import CompositeMatrix, CompositeVector, CompositeDualVector, Vector, DualVector, Matrix
from .factory import add_instances, sub_instances, mul_instances, div_instances

# ---------------------------------------------------------
# 1. SCALARS & FUNCTIONS
# ---------------------------------------------------------
# Basic Function algebra
register_operation(ExpandableFunction, ExpandableFunction, '+', add_instances)
register_operation(ExpandableFunction, ExpandableFunction, '-', sub_instances)
register_operation(ExpandableFunction, ExpandableFunction, '*', mul_instances)
register_operation(ExpandableFunction, ExpandableFunction, '/', div_instances)

# Scalar-Function pointwise scaling/algebra
register_operation(ExpandableConstant, ExpandableFunction, '+', add_instances)
register_operation(ExpandableFunction, ExpandableConstant, '+', lambda f, c: add_instances(f, c))
register_operation(ExpandableConstant, ExpandableFunction, '-', sub_instances)
register_operation(ExpandableFunction, ExpandableConstant, '-', lambda f, c: sub_instances(f, c))
register_operation(ExpandableConstant, ExpandableFunction, '*', mul_instances)
register_operation(ExpandableFunction, ExpandableConstant, '*', lambda f, c: mul_instances(f, c))
register_operation(ExpandableFunction, ExpandableConstant, '/', div_instances)

# ---------------------------------------------------------
# 2. TENSORS & MATRICES
# ---------------------------------------------------------
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
    return ExpandableConstant(expr=lazy_math, symbol=f"{dual_vec.symbol_name} {vec.symbol_name}")

def outer_product(vec, dual_vec):
    lazy_math = sp.MatMul(vec, dual_vec)
    # An N x 1 Vector multiplied by a 1 x M DualVector creates an N x M Matrix
    return CompositeMatrix(lazy_math, vec.rows, dual_vec.cols, symbol=f"{vec.symbol_name} {dual_vec.symbol_name}")

def mul_matrices(m1, m2):
    lazy_math = sp.MatMul(m1, m2)
    m1_sym = f"\\left( {m1.symbol_name} \\right)" if getattr(m1, '_is_sum', False) else m1.symbol_name
    m2_sym = f"\\left( {m2.symbol_name} \\right)" if getattr(m2, '_is_sum', False) else m2.symbol_name
    symbol = f"{m1_sym} {m2_sym}"

    # Result is a column vector (e.g., Matrix * Vector)
    if m2.cols == 1:
        return CompositeVector(lazy_math, m1.rows, symbol=symbol)
    
    # Result is a row vector (e.g., DualVector * Matrix)
    if m1.rows == 1:
        return CompositeDualVector(lazy_math, m2.cols, symbol=symbol)

    # Default case: result is a general matrix
    return CompositeMatrix(lazy_math, m1.rows, m2.cols, symbol=symbol)

# Register Tensor/Matrix rules
register_operation(ExpandableTensor, ExpandableTensor, '+', add_tensors)
register_operation(ExpandableTensor, ExpandableTensor, '-', sub_tensors)
register_operation(ExpandableConstant, ExpandableTensor, '*', scale_tensor)
register_operation(ExpandableTensor, ExpandableConstant, '*', lambda t, c: scale_tensor(c, t))

register_operation(ExpandableMatrix, ExpandableMatrix, '+', add_tensors)
register_operation(ExpandableMatrix, ExpandableMatrix, '-', sub_tensors)
register_operation(ExpandableConstant, ExpandableMatrix, '*', scale_tensor)
register_operation(ExpandableMatrix, ExpandableConstant, '*', lambda t, c: scale_tensor(c, t))

register_operation(ExpandableMatrix, ExpandableMatrix, '*', mul_matrices)

register_operation(DualVector, Vector, '*', inner_product)
register_operation(Vector, DualVector, '*', outer_product)

# ---------------------------------------------------------
# 3. OPERATORS
# ---------------------------------------------------------
def operator_add(op1, op2):
    from ..math.operators.differential.abstract import AbstractDifferentialOperator
    # Fallback to base logic if variables match
    if isinstance(op1, AbstractDifferentialOperator) and isinstance(op2, AbstractDifferentialOperator):
        if op1.variable == op2.variable:
            new_template = op1.template + op2.template
            return type(op1)(op1.variable, new_template, op1.dummy_func)
    return NotImplemented

def operator_composition(op1, op2):
    from ..math.operators.differential.abstract import AbstractDifferentialOperator
    # op1 * op2 -> op1(op2(f))
    if isinstance(op1, AbstractDifferentialOperator) and isinstance(op2, AbstractDifferentialOperator):
        if op1.variable == op2.variable:
            new_template = op1.template.subs(op1.dummy_func, op2.template)
            return type(op1)(op1.variable, new_template, op1.dummy_func)
    return NotImplemented

def apply_operator(op, target):
    # op * target -> call op(target)
    return op(target)

# Operator-Operator algebra
register_operation(ExpandableOperator, ExpandableOperator, '+', operator_add)
register_operation(ExpandableOperator, ExpandableOperator, '-', lambda op1, op2: operator_add(op1, -1 * op2))
register_operation(ExpandableOperator, ExpandableOperator, '*', operator_composition)

# Operator-Function interaction (Application)
register_operation(ExpandableOperator, ExpandableFunction, '*', apply_operator)

# Scalar-Operator scaling
register_operation(ExpandableConstant, ExpandableOperator, '*', lambda c, op: op.__class__(op.variable, c * op.template, op.dummy_func))
register_operation(ExpandableOperator, ExpandableConstant, '*', lambda op, c: op.__class__(op.variable, c * op.template, op.dummy_func))
