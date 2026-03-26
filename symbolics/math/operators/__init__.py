# symbolics/operators/__init__.py

# 1. Differential Operators
from .differential import (
    AbstractDifferentialOperator, 
    LinearDifferentialOperator
)

# 2. Integral Operators (Future)
# from .integral import IntegralOperator

# 3. Matrix Operators (Future)
# from .matrix import SpinOperator

# Define the public API for the operators module
__all__ = [
    'AbstractDifferentialOperator',
    'LinearDifferentialOperator'
]