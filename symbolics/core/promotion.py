# core/promotion.py

from .algebra import Field, Ring, Algebra, VectorSpace
from .base_types import ExpandableConstant, ExpandableFunction, ExpandableOperator, ExpandableTensor, ExpandableMatrix

# ---------------------------------------------------------
# TYPE PROMOTION REGISTRY
# ---------------------------------------------------------
# Defines what happens when two different mathematical structures interact.
# Format: {(TypeA, TypeB): DominantType}
PROMOTION_RULES = {
    # 1. Same types retain their identity
    (Algebra, Algebra): Algebra,
    (Ring, Ring): Ring,
    (Field, Field): Field,
    (VectorSpace, VectorSpace): VectorSpace,

    # 2. Field (Scalars) are absorbed by everything else
    (Algebra, Field): Algebra,
    (Field, Algebra): Algebra,
    
    (Ring, Field): Ring,
    (Field, Ring): Ring,
    
    (VectorSpace, Field): VectorSpace,
    (Field, VectorSpace): VectorSpace,

    # 3. Operators acting on Functions (Ring * Algebra)
    # The result of an operator acting on a function is a new function!
    (Ring, Algebra): Algebra,
    (Algebra, Ring): TypeError, # Mathematically undefined (Operators act to the right)
}

def resolve_promoted_base(ClassA, ClassB):
    """
    Analyzes the MRO of two classes to find their abstract mathematical types,
    consults the registry, and returns the correct promoted base class.
    """
    # 1. Identify the abstract mathematical type for ClassA
    type_A = next((t for t in (Algebra, Field, Ring, VectorSpace) if issubclass(ClassA, t)), None)
    
    # 2. Identify the abstract mathematical type for ClassB
    type_B = next((t for t in (Algebra, Field, Ring, VectorSpace) if issubclass(ClassB, t)), None)

    if not type_A or not type_B:
        raise TypeError(f"Cannot promote types: {ClassA.__name__} or {ClassB.__name__} lacks a mathematical base.")

    # 3. Consult the registry
    promoted_math_type = PROMOTION_RULES.get((type_A, type_B))
    
    if promoted_math_type is TypeError:
        raise TypeError(f"Operation between {type_A.__name__} and {type_B.__name__} is mathematically undefined.")
    
    if promoted_math_type is None:
        raise NotImplementedError(f"No promotion rule defined for {type_A.__name__} and {type_B.__name__}.")

    # 4. Return the correct concrete base type that corresponds to the promoted abstract type
    if promoted_math_type in (Algebra, VectorSpace):
        # If either operand was a Tensor, the result is a Tensor Algebra.
        if issubclass(ClassA, ExpandableMatrix) or issubclass(ClassB, ExpandableMatrix):
            return ExpandableMatrix
        elif issubclass(ClassA, ExpandableTensor) or issubclass(ClassB, ExpandableTensor):
            return ExpandableTensor
        return ExpandableFunction
    elif promoted_math_type is Ring:
        return ExpandableOperator
    elif promoted_math_type is Field:
        return ExpandableConstant
    else:
        # This case should be rare, but it's better to be explicit.
        raise TypeError(f"Promotion resolution failed: No concrete base type for {promoted_math_type.__name__}.")