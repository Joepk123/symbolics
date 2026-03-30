import sympy as sp
from ...core.base_types import ExpandableMatrix

class Matrix(ExpandableMatrix):
    """A general NxM Matrix mapping."""
    def __new__(cls, *args, symbol=None, is_sum=False, **kwargs):
        name, rows, cols = str(args[0]), args[1], args[2]
        obj = super().__new__(cls, name, rows, cols, symbol=symbol, **kwargs)
        obj._is_sum = is_sum
        return obj

    def make_explicit(self):
        """Unfolds the tensor expression into its explicit Matrix form, preserving symbolic elements."""
        from ...core.visitor import evaluate_target
        from ...core.base_types import ExpandableMatrix

        expr = self.definition
        previous = None
        while expr != previous:
            previous = expr
            expr = evaluate_target(expr, ExpandableMatrix)
        
        return expr.doit() if hasattr(expr, 'doit') else expr

class Vector(ExpandableMatrix):
    """A strictly N x 1 Column Vector."""
    def __new__(cls, *args, symbol=None, is_sum=False, **kwargs):
        name, rows = str(args[0]), args[1]
        # Force the column dimension to 1 to establish vector geometry
        obj = super().__new__(cls, name, rows, 1, symbol=symbol, **kwargs)
        obj._is_sum = is_sum
        return obj


    def make_explicit(self):
        """Unfolds the tensor expression into its explicit Matrix form, preserving symbolic elements."""
        from ...core.visitor import evaluate_target
        from ...core.base_types import ExpandableMatrix

        expr = self.definition
        previous = None
        while expr != previous:
            previous = expr
            expr = evaluate_target(expr, ExpandableMatrix)
        
        return expr.doit() if hasattr(expr, 'doit') else expr

class DualVector(ExpandableMatrix):
    """A strictly 1 x N Row Vector (Dual Vector / Functional)."""
    def __new__(cls, *args, symbol=None, is_sum=False, **kwargs):
        name = str(args[0])
        # SymPy reconstructs with (name, rows, cols). User calls with (name, cols).
        cols = args[2] if len(args) >= 3 else args[1]
        obj = super().__new__(cls, name, 1, cols, symbol=symbol, **kwargs)
        obj._is_sum = is_sum
        return obj

    def make_explicit(self):
        """Unfolds the tensor expression into its explicit Matrix form, preserving symbolic elements."""
        from ...core.visitor import evaluate_target
        from ...core.base_types import ExpandableMatrix

        expr = self.definition
        previous = None
        while expr != previous:
            previous = expr
            expr = evaluate_target(expr, ExpandableMatrix)
        
        return expr.doit() if hasattr(expr, 'doit') else expr

class CompositeDualVector(DualVector):
    """A wrapper that holds a lazy matrix operation resulting in a DualVector."""
    def __new__(cls, ast_node, cols, symbol=None, is_sum=False, **kwargs):
        name = str(f"CompDualVec_{hash(ast_node)}")
        obj = super().__new__(cls, name, cols, symbol=symbol, is_sum=is_sum, **kwargs)
        obj._ast_node = ast_node
        return obj

    @property
    def name(self):
        return str(self.args[0])

    @property
    def definition(self):
        return self._ast_node

class CompositeMatrix(Matrix):
    """A wrapper that holds a lazy matrix operation (like MatAdd or MatMul)."""
    def __new__(cls, ast_node, rows, cols, symbol=None, is_sum=False, **kwargs):
        # SymPy MatrixSymbol requires a string name, so we give it a safe dummy name
        name = str(f"CompMat_{hash(ast_node)}")
        obj = super().__new__(cls, name, rows, cols, symbol=symbol, is_sum=is_sum, **kwargs)
        # Store the actual math tree!
        obj._ast_node = ast_node
        return obj

    @property
    def name(self):
        return str(self.args[0])

    @property
    def definition(self):
        """When evaluated, unpack the hidden math tree!"""
        return self._ast_node

class CompositeVector(Vector):
    def __new__(cls, ast_node, rows, symbol=None, is_sum=False, **kwargs):
        name = str(f"CompVec_{hash(ast_node)}")
        obj = super().__new__(cls, name, rows, symbol=symbol, is_sum=is_sum, **kwargs)
        obj._ast_node = ast_node
        return obj

    @property
    def name(self):
        return str(self.args[0])

    @property
    def definition(self):
        return self._ast_node

class PauliZ(Matrix):
    """The Pauli Z Operator Matrix."""
    def __new__(cls, *args, symbol=r'\sigma_z', **kwargs):
        # Pass the elements directly to the superclass constructor
        elements = [[1, 0], [0, -1]]
        return super().__new__(cls, 'PauliZ', 2, 2, symbol=symbol, elements=elements, **kwargs)
