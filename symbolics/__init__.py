# symbolics/__init__.py

# 1. Core Tools (Engine & Base Types)
from .core import (
    ExpandableConstant,
    ExpandableFunction,
    ExpandableOperator,
    make_explicit,
    evaluate_target,
    evaluate
)

# 2. Operators
from .operators import (
    LinearDifferentialOperator,
    AbstractDifferentialOperator
)

# 3. Primitives 
# (Uncomment these once you save the files in primitives/elementary/ and primitives/special/)
# from .primitives.elementary.exponentials import Gaussian
# from .primitives.special.polynomials import Hermite

# Define the public API of the entire library
__all__ = [
    # Core
    'ExpandableConstant',
    'ExpandableFunction',
    'ExpandableOperator',
    'make_explicit',
    'evaluate_target',
    'evaluate',
    
    # Operators
    'LinearDifferentialOperator',
    'AbstractDifferentialOperator',
    
    # Primitives
    # 'Gaussian',
    # 'Hermite'
]