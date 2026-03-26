# core/registry.py

import operator

# symbolics/core/registry.py

_OPERATION_MAP = {}

def register_operation(left_type, right_type, op_symbol, func):
    """Registers a mathematical rule for two types."""
    _OPERATION_MAP[(left_type, right_type, op_symbol)] = func

def resolve_operation(left_obj, right_obj, op_symbol):
    """Looks up and executes the rule for the given objects."""
    # We use type() for exact matches, but you could use isinstance checks 
    # if you want to allow subclasses to automatically inherit rules.
    # For a CAS, checking against the MRO (Method Resolution Order) is safest.
    
    for left_class in type(left_obj).mro():
        for right_class in type(right_obj).mro():
            rule = _OPERATION_MAP.get((left_class, right_class, op_symbol))
            if rule:
                return rule(left_obj, right_obj)
                
    return NotImplemented