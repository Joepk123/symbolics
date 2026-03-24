# core/__init__.py

# 1. Pure Math
from .algebra import Group, AdditiveGroup, Ring, Field, VectorSpace, Algebra

# 2. Execution & Tree Traversal
from .mixin import ExpansionMixin
from .visitor import make_explicit, evaluate_target, evaluate
from .factory import CoordinateAlgebraFactory, CompositeSum, CompositeSub, CompositeMul, CompositeDiv
from .promotion import resolve_promoted_base, PROMOTION_RULES

# 3. Base Expandable Types
from .base_types import ExpandableConstant, ExpandableFunction, ExpandableOperator, define_function, EvaluatedFunction

# Define exactly what is exposed when someone imports from `core`
__all__ = [
    # Math
    'Group', 'AdditiveGroup', 'Ring', 'Field', 'VectorSpace', 'Algebra',
    # Engine
    'ExpansionMixin', 'make_explicit', 'evaluate_target', 'evaluate',
    'CoordinateAlgebraFactory', 'CompositeSum', 'CompositeSub', 'CompositeMul', 'CompositeDiv',
    'resolve_promoted_base', 'PROMOTION_RULES',
    # Base Types
    'ExpandableConstant', 'ExpandableFunction', 'ExpandableOperator', 'define_function', 'EvaluatedFunction'
]