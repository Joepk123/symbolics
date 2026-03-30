from .operators import Ket, Bra, Operator, physics_inner_product, physics_outer_product, physics_operator_ket, physics_bra_operator
from ...core.registry import register_operation

# Register physics-specific operations for Bra-Ket logic
register_operation(Bra, Ket, '*', physics_inner_product)
register_operation(Ket, Bra, '*', physics_outer_product)
register_operation(Operator, Ket, '*', physics_operator_ket)
register_operation(Bra, Operator, '*', physics_bra_operator)

__all__ = ['Ket', 'Bra', 'Operator']
