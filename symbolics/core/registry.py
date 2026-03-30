# symbolics/core/registry.py

_OPERATION_MAP = {}

def register_operation(left_type, right_type, op_symbol, func):
    """Registers a mathematical rule for two types."""
    # Use string names instead of class references to survive Jupyter %autoreload!
    l_name = left_type if isinstance(left_type, str) else left_type.__name__
    r_name = right_type if isinstance(right_type, str) else right_type.__name__
    _OPERATION_MAP[(l_name, r_name, op_symbol)] = func

def resolve_operation(left_obj, right_obj, op_symbol):
    """Looks up and executes the rule for the given objects using MRO fallback."""
    for left_class in type(left_obj).mro():
        for right_class in type(right_obj).mro():
            rule = _OPERATION_MAP.get((left_class.__name__, right_class.__name__, op_symbol))
            if rule:
                return rule(left_obj, right_obj)
                
    return NotImplemented
