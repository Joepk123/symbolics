import sympy as sp
from ...math.linear_algebra.tensors import Vector, DualVector, Matrix, CompositeVector, CompositeMatrix, CompositeDualVector
from ...core.base_types import ExpandableConstant

class Ket(Vector):
    """A quantum Ket in a Hilbert space."""
    def _latex(self, printer):
        return f"| {self.symbol_name} \\rangle"

    def _sympystr(self, printer):
        return f"|{self.symbol_name}>"

    def _pretty(self, printer):
        return printer._print(sp.Symbol(f"|{self.symbol_name}>"))

class Bra(DualVector):
    """A quantum Bra in a Hilbert space."""
    def _latex(self, printer):
        return f"\\langle {self.symbol_name} |"

    def _sympystr(self, printer):
        return f"<{self.symbol_name}|"

    def _pretty(self, printer):
        return printer._print(sp.Symbol(f"<{self.symbol_name}|"))

class Operator(Matrix):
    """A quantum Operator mapping between Hilbert spaces."""
    def _latex(self, printer):
        return f"\\hat{{{self.symbol_name}}}"

    def _sympystr(self, printer):
        return f"{self.symbol_name}^hat"

def physics_inner_product(bra, ket):
    from ...core.base_types import ExpandableConstant
    lazy_math = sp.MatMul(bra, ket)
    symbol = f"\\langle {bra.symbol_name} | {ket.symbol_name} \\rangle"
    return ExpandableConstant(expr=lazy_math, symbol=symbol)

def physics_outer_product(ket, bra):
    lazy_math = sp.MatMul(ket, bra)
    symbol = f"| {ket.symbol_name} \\rangle \\langle {bra.symbol_name} |"
    return CompositeMatrix(lazy_math, ket.rows, bra.cols, symbol=symbol)

def physics_operator_ket(op, ket):
    lazy_math = sp.MatMul(op, ket)
    symbol = f"\\hat{{{op.symbol_name}}} | {ket.symbol_name} \\rangle"
    return CompositeVector(lazy_math, ket.rows, symbol=symbol)

def physics_bra_operator(bra, op):
    lazy_math = sp.MatMul(bra, op)
    symbol = f"\\langle {bra.symbol_name} | \\hat{{{op.symbol_name}}}"
    return CompositeDualVector(lazy_math, op.cols, symbol=symbol)
