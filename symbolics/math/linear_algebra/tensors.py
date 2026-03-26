import sympy as sp
from ...core.base_types import ExpandableMatrix

class Matrix(ExpandableMatrix):
    """A general NxM Matrix mapping."""
    def __new__(cls, *args, symbol=None, **kwargs):
        name, rows, cols = str(args[0]), args[1], args[2]
        return super().__new__(cls, name, rows, cols, symbol=symbol, **kwargs)

class Vector(ExpandableMatrix):
    """A strictly N x 1 Column Vector."""
    def __new__(cls, *args, symbol=None, **kwargs):
        name, rows = str(args[0]), args[1]
        # Force the column dimension to 1 to establish vector geometry
        return super().__new__(cls, name, rows, 1, symbol=symbol, **kwargs)
    
    def dagger(self):
        pass

class DualVector(ExpandableMatrix):
    """A strictly 1 x N Row Vector (Dual Vector / Functional)."""
    def __new__(cls, *args, symbol=None, **kwargs):
        name = str(args[0])
        # SymPy reconstructs with (name, rows, cols). User calls with (name, cols).
        cols = args[2] if len(args) >= 3 else args[1]
        return super().__new__(cls, name, 1, cols, symbol=symbol, **kwargs)

class PauliZ(Matrix):
    """The Pauli Z Operator Matrix."""
    def __new__(cls, *args, symbol=r'\sigma_z', **kwargs):
        # Explicitly lock dimensions to 2x2, and pass 'PauliZ' as the SymPy name
        return super().__new__(cls, 'PauliZ', 2, 2, symbol=symbol, **kwargs)

    @property
    def definition(self):
        """Returns the explicit elements of the matrix."""
        # We use an ImmutableMatrix so it safely integrates into SymPy's AST caching.
        return sp.ImmutableMatrix([[1, 0], [0, -1]])