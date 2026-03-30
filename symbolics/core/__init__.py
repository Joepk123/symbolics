# core/__init__.py

# 1. Pure Math
from .algebra import Group, AdditiveGroup, Ring, Field, VectorSpace, Algebra

# 2. Execution & Tree Traversal
from .mixin import ExpansionMixin
from .visitor import make_explicit, evaluate_target, evaluate
from .factory import CoordinateAlgebraFactory, CompositeSum, CompositeSub, CompositeMul, CompositeDiv
from .registry import register_operation, resolve_operation

# 3. Base Expandable Types
from .base_types import ExpandableConstant, ExpandableFunction, ExpandableOperator, define_function, EvaluatedFunction, ExpandableTensor, TensorWrapper, ExpandableMatrix, MatrixWrapper

# Define exactly what is exposed when someone imports from `core`
__all__ = [
    # Math
    'Group', 'AdditiveGroup', 'Ring', 'Field', 'VectorSpace', 'Algebra',
    # Engine
    'ExpansionMixin', 'make_explicit', 'evaluate_target', 'evaluate',
    'CoordinateAlgebraFactory', 'CompositeSum', 'CompositeSub', 'CompositeMul', 'CompositeDiv',
    'register_operation', 'resolve_operation',
    # Base Types
    'ExpandableConstant', 'ExpandableFunction', 'ExpandableOperator', 'define_function', 'EvaluatedFunction', 'ExpandableTensor', 'TensorWrapper', 'ExpandableMatrix', 'MatrixWrapper'
]

# Load physics rules into the registry
from . import rules
