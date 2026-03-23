# test
import sympy as sp
import operator
import inspect

# Factories
## Functions

def _get_index_count(target_cls):
    """Counts expected indices (Total parameters minus 1 coordinate)."""
    sig = inspect.signature(target_cls.__new__)
    params = [p for p in sig.parameters.values() 
              if p.name not in ('cls', 'args', 'kwargs')
              and p.kind in (p.POSITIONAL_OR_KEYWORD, p.POSITIONAL_ONLY)]
    return max(0, len(params) - 1)

def _get_signature_counts(target_cls):
    """
    Returns (idx_count, coord_count) for a given class.
    Checks for cached metadata before falling back to introspection.
    """
    # 1. If it's a factory-generated class, it already knows its shape!
    if hasattr(target_cls, '_idx_count') and hasattr(target_cls, '_coord_count'):
        return target_cls._idx_count, target_cls._coord_count
    
    # 2. If it's a base primitive, inspect the __new__ signature
    sig = inspect.signature(target_cls.__new__)
    params = [p for p in sig.parameters.values() 
              if p.name not in ('cls', 'args', 'kwargs')
              and p.kind in (p.POSITIONAL_OR_KEYWORD, p.POSITIONAL_ONLY)]
    
    # By our Design Contract: Primitives have exactly 1 coordinate at the end.
    idx_count = max(0, len(params) - 1)
    coord_count = 1 if len(params) > 0 else 0
    
    return idx_count, coord_count

def unwrap(expr):
    """
    The Universal Visitor for Stratified Evaluation.
    Walks any SymPy AST and expands DefinedFunction nodes exactly one layer.
    """
    # 1. Base Case: If the expression is already a pure DefinedFunction
    if isinstance(expr, DefinedFunction):
        return expr.definition
        
    # 2. Tree Traversal: If it's a standard SymPy node (like Mul or Add)
    if hasattr(expr, 'replace'):
        # We use SymPy's .replace() as our AST walker.
        # It finds any DefinedFunction and swaps it with its immediate definition.
        return expr.replace(
            lambda node: isinstance(node, DefinedFunction),
            lambda node: node.definition
        )
        
    # 3. Fallback: If it's an indivisible leaf (like a raw Integer or Symbol)
    return expr

def BaseAlgebraicFactory(ClassA, ClassB, op_func, op_symbol, label=None):
    # Extract the exact shape of the child classes
    idx_A, coord_A_count = _get_signature_counts(ClassA)
    idx_B, coord_B_count = _get_signature_counts(ClassB)
    
    BaseClass = [cls for cls in ClassA.__mro__ if cls.__name__ == 'DefinedFunction'][0]
    
    class CombinedFunction(BaseClass):
        # --- STATEFUL METADATA ---
        # The class permanently remembers its required signature
        _idx_count = idx_A + idx_B
        _coord_count = coord_A_count + coord_B_count
        
        def __new__(cls, *args, **kwargs):
            instance = super().__new__(cls, *args, **kwargs)
            instance._args = args
            instance._kwargs = kwargs
            return instance

        @property
        def definition(self):
            # Split arguments strictly by the known index count
            indices = self._args[:self._idx_count]
            coords = self._args[self._idx_count:]
            
            ind_A = indices[:idx_A]
            ind_B = indices[idx_A:]
            
            # --- THE ASYMMETRIC COORDINATE ROUTER ---
            if len(coords) == self._coord_count:
                # 1. Independent Routing: Perfect match for Tensor Products
                # e.g., (x, y, z) routed as (x, y) to ClassA and (z) to ClassB
                coord_A = coords[:coord_A_count]
                coord_B = coords[coord_A_count:]
                
            elif len(coords) == coord_A_count and coord_A_count == coord_B_count:
                # 2. Perfect Sharing: Both functions expect the exact same spatial dimensions
                # e.g., (x, y) given to both A(x, y) and B(x, y)
                coord_A, coord_B = coords, coords
                
            elif len(coords) == 1:
                # 3. 1D Broadcast Fallback: Share the single coordinate everywhere
                coord_A = coords * coord_A_count
                coord_B = coords * coord_B_count
                
            else:
                raise ValueError(
                    f"Coordinate mismatch in {self.__class__.__name__}. "
                    f"Expected {self._coord_count} (independent) or {coord_A_count} (shared). "
                    f"Got {len(coords)}."
                )
            
            
            part_a = ClassA(*(ind_A + tuple(coord_A)), **self._kwargs)
            part_b = ClassB(*(ind_B + tuple(coord_B)), **self._kwargs)
            
            # SymPy strips custom attributes, so we use the immutable class name!
            is_struct_a = part_a.__class__.__name__.startswith('Combined_')
            is_struct_b = part_b.__class__.__name__.startswith('Combined_')
            
            expr_a = part_a.definition if is_struct_a else part_a
            expr_b = part_b.definition if is_struct_b else part_b
            
            return op_func(expr_a, expr_b)

        def _repr_latex_(self):
            tex_indices = [sp.latex(a) for a in self._args[:self._idx_count]]
            tex_coords = ", ".join([sp.latex(c) for c in self._args[self._idx_count:]])
            
            lbl = label if label else f"{ClassA.__name__}{op_symbol}{ClassB.__name__}"
            if "{" in lbl and "}" in lbl:
                formatted_label = lbl.format(*tex_indices)
                return f"${formatted_label}({tex_coords})$"
            if tex_indices:
                idx_str = ", ".join(tex_indices)
                return f"${lbl}_{{{idx_str}}}({tex_coords})$"
            return f"${lbl}({tex_coords})$"

    CombinedFunction.__name__ = f"Combined_{ClassA.__name__}_{ClassB.__name__}"
    return CombinedFunction


# Actual classes
## --- The Thin Wrappers for Functions ---
def FunctionSum(A, B, label=None):
    return BaseAlgebraicFactory(A, B, operator.add, "+", label)

def FunctionSub(A, B, label=None):
    return BaseAlgebraicFactory(A, B, operator.sub, "-", label)

def FunctionMul(A, B, label=None):
    return BaseAlgebraicFactory(A, B, operator.mul, "", label)

def FunctionDiv(A, B, label=None):
    return BaseAlgebraicFactory(A, B, operator.truediv, "/", label)

## --- 1. Function Metaclasses ---
## Inherits from SymPy's function metaclass to ensure math engine compatibility
class FunctionAlgebraMeta(type(sp.Function)):
    """Base Metaclass for additive functional structures."""
    def __add__(cls, other):
        return FunctionSum(cls, other)
    def __sub__(cls, other):
        return FunctionSub(cls, other)

class FunctionMeta(FunctionAlgebraMeta):
    """Metaclass for Functions: Supports +, -, *, /."""
    def __mul__(cls, other):
        return FunctionMul(cls, other)
    def __truediv__(cls, other):
        return FunctionDiv(cls, other)

# --- 2. Operator Metaclass ---
class OperatorMeta(type):
    """Metaclass for the Ring of Differential Operators."""
    def __add__(cls, other):
        return OperatorSumFactory(cls, other)
    
    def __sub__(cls, other):
        return OperatorSubFactory(cls, other)
    
    def __mul__(cls, other):
        return OperatorCompositionFactory(cls, other)

# --- 3. Base Operator Class (Moved UP) ---
class DifferentialOperator(metaclass=OperatorMeta):
    """Base class for linear differential operators with constant coefficients."""
    def __init__(self, variable, poly=None):
        self.x = variable
        self.D = sp.Symbol('D')
        self.poly = sp.sympify(poly) if poly is not None else self.D

    def __call__(self, target_expr):
        """Maps D^n -> d^n/dx^n (target)."""
        
        # ... (Your existing smart expansion logic here) ...

        expanded_poly = sp.expand(self.poly)
        
        # --- NEW: Symbolic Exponent Bypass ---
        if isinstance(expanded_poly, sp.Pow) and expanded_poly.base == self.D:
            # Wrap in a tuple so SymPy knows 'exp' is a count, not a spatial coordinate
            return sp.Derivative(target_expr, (self.x, expanded_poly.exp)).doit()
        elif expanded_poly == self.D:
            return sp.diff(target_expr, self.x, 1)
        # -------------------------------------
        
        # Original logic for integer-based formal polynomials (e.g., D^2 + 2D)
        p = sp.Poly(expanded_poly, self.D)
        
        result = 0
        for power, coeff in zip(p.monoms(), p.coeffs()):
            n_pow = power[0] 
            if n_pow == 0:
                result += coeff * target_expr
            else:
                result += coeff * sp.diff(target_expr, (self.x, n_pow))
                
        return result

    def _repr_latex_(self):
        tex_poly = sp.latex(self.poly).replace('D', r'\partial_{' + sp.latex(self.x) + '}')
        return f"$\\hat{{L}} = {tex_poly}$"

# --- 4. Operator Factories ---
def OperatorSumFactory(OpA, OpB):
    class SumOp(DifferentialOperator):
        def __init__(self, variable, **kwargs):
            inst_a, inst_b = OpA(variable), OpB(variable)
            super().__init__(variable, poly=sp.expand(inst_a.poly + inst_b.poly))
    SumOp.__name__ = f"Sum_{OpA.__name__}_{OpB.__name__}"
    return SumOp

def OperatorSubFactory(OpA, OpB):
    class SubOp(DifferentialOperator):
        def __init__(self, variable, **kwargs):
            inst_a, inst_b = OpA(variable), OpB(variable)
            super().__init__(variable, poly=sp.expand(inst_a.poly - inst_b.poly))
    SubOp.__name__ = f"Sub_{OpA.__name__}_{OpB.__name__}"
    return SubOp

def OperatorCompositionFactory(OpA, OpB):
    class CompOp(DifferentialOperator):
        def __init__(self, variable, **kwargs):
            inst_a, inst_b = OpA(variable), OpB(variable)
            super().__init__(variable, poly=sp.expand(inst_a.poly * inst_b.poly))
    CompOp.__name__ = f"Comp_{OpA.__name__}_{OpB.__name__}"
    return CompOp

## Defined functions.
class DefinedFunction(sp.Function, metaclass=FunctionMeta):
    @property
    def definition(self):
        """Returns the first layer of definition."""
        return self

    def unwrap(self):
        """
        Executes a single layer of macro expansion.
        Allows Object-Oriented calling syntax: psi.unwrap()
        """
        # Delegate to the Universal Visitor to ensure safe traversal
        return unwrap(self)

    def deep_expand(self):
        """
        Recursively evaluates all layers of the function down to its Normal Form.
        """
        expr = self.definition
        previous_expr = None
        
        # Loop until the expression stops changing (Normal Form reached)
        while expr != previous_expr:
            previous_expr = expr
            if hasattr(expr, 'replace'):
                # Find any DefinedFunction node that hasn't been expanded and expand it
                expr = expr.replace(
                    lambda e: isinstance(e, DefinedFunction) and e.definition != e,
                    lambda e: e.definition
                )
        
        # Call .doit() to evaluate the pending derivatives from the Rodrigues formula
        return expr.doit()

class AliasedState(sp.Expr):
    """
    A Decorator node that masks an underlying SymPy expression with a custom LaTeX symbol.
    """
    def __new__(cls, expression, latex_label):
        # SymPy strictly requires all internal arguments to be SymPy objects.
        # We convert your string label into a purely visual SymPy Symbol.
        sym_label = sp.Symbol(latex_label)
        return super().__new__(cls, expression, sym_label)

    @property
    def definition(self):
        """Returns the masked expression."""
        return self.args[0]

    @property
    def label(self):
        """Returns the visual symbol."""
        return self.args[1]

    def deep_expand(self):
        """Passes the expansion request through the mask to the underlying math."""
        expr = self.definition
        
        if hasattr(expr, 'deep_expand'):
            return expr.deep_expand()
        elif hasattr(expr, 'replace'):
            # Walk through the SymPy Mul/Add tree and expand any DefinedFunctions
            return expr.replace(
                lambda e: hasattr(e, 'deep_expand'),
                lambda e: e.deep_expand()
            )
        return expr

    def _repr_latex_(self):
        # Renders the assigned symbol when displayed alone
        return f"${sp.latex(self.label)}$"
    
    def _latex(self, printer):
        # Renders the assigned symbol when embedded in larger equations
        return printer.doprint(self.label)