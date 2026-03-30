# operators/differential.py

import sympy as sp
from ....core.base_types import ExpandableOperator

# ---------------------------------------------------------
# VISUAL PROXY
# ---------------------------------------------------------
class OperatorDisplayProxy(sp.Expr):
    """
    A visual proxy that hides the dummy function.
    Mathematically, an operator requires an operand to correctly apply the product rule 
    and chain rule. This class maintains the AST structure internally while rendering cleanly.
    """
    def __new__(cls, template, dummy_func):
        return super().__new__(cls, template, dummy_func)

    @property
    def template(self): return self.args[0]
    
    @property
    def dummy_func(self): return self.args[1]

    def _latex(self, printer):
        raw_latex = printer._print(self.template)
        dummy_latex = printer._print(self.dummy_func)
        
        cleaned = raw_latex.replace(dummy_latex, "").strip()
        if cleaned.endswith("+") or cleaned.endswith("-"):
            cleaned += " 1"
        elif cleaned == "":
            cleaned = "1"
        return cleaned

    def _pretty(self, printer):
        from sympy.printing.pretty.stringpict import prettyForm # Add this import
        
        raw = printer._print(self.template)
        dummy = printer._print(self.dummy_func)
        cleaned = str(raw).replace(str(dummy), "").strip()
        
        if cleaned.endswith("+") or cleaned.endswith("-"):
            cleaned += " 1"
        elif cleaned == "":
            cleaned = "1"
            
        return prettyForm(cleaned) # Wrap the return value

    def _sympystr(self, printer):
        return self._pretty(printer)

    def doit(self, **kwargs):
        return self.template.doit(**kwargs)
        
    def subs(self, *args, **kwargs):
        return self.template.subs(*args, **kwargs)
    
    def __mul__(self, other):
        from ....core.base_types import ExpandableFunction
        
        # 1. Operator * Operator -> New AST Operator
        if isinstance(other, AbstractDifferentialOperator) and self.variable == other.variable:
            new_template = self.template.subs(self.dummy_func, other.template)
            return self.__class__(self.variable, new_template, self.dummy_func)
            
        # 2. Operator * Function -> Mathematical Application
        if isinstance(other, ExpandableFunction):
            return self.__call__(other)
            
        return super().__mul__(other)


# ---------------------------------------------------------
# ABSTRACT DIFFERENTIAL OPERATOR
# ---------------------------------------------------------
class AbstractDifferentialOperator(ExpandableOperator):
    """
    A fully generalized operator capable of representing non-linear mappings.
    Example: N(f) = (df/dx)^2 + sin(f)
    """
    def __new__(cls, variable, expr_template=None, dummy_func=None, symbol=None, **kwargs):
        F = dummy_func if dummy_func else sp.Function(r'\Phi')(variable)
        template = sp.sympify(expr_template) if expr_template is not None else F
        
        return super().__new__(cls, variable, template, F, symbol=symbol, **kwargs)

    @property
    def variable(self): return self.args[0]

    @property
    def template(self): return self.args[1]

    @property
    def dummy_func(self): return self.args[2]

    @property
    def definition(self):
        """Provides the explicit mathematical template wrapped in a visual proxy."""
        return OperatorDisplayProxy(self.template, self.dummy_func)
    def __add__(self, other):
        from ....core.promotion import resolve_promoted_base
        
        if isinstance(other, AbstractDifferentialOperator) and self.variable == other.variable:
            resolve_promoted_base(self.__class__, other.__class__)
            new_template = self.template + other.template
            return self.__class__(self.variable, new_template, self.dummy_func)
            
        return super().__add__(other)

    def __sub__(self, other):
        from ....core.promotion import resolve_promoted_base
        
        if isinstance(other, AbstractDifferentialOperator) and self.variable == other.variable:
            resolve_promoted_base(self.__class__, other.__class__)
            new_template = self.template - other.template
            return self.__class__(self.variable, new_template, self.dummy_func)
            
        return super().__sub__(other)
    
    def __call__(self, target_expr):
        return self.template.subs(self.dummy_func, target_expr)

    def __mul__(self, other):
        if isinstance(other, AbstractDifferentialOperator) and self.variable == other.variable:
            new_template = self.template.subs(self.dummy_func, other.template)
            return AbstractDifferentialOperator(self.variable, new_template, self.dummy_func)
        return super().__mul__(other)

    # ---------------------------------------------------------
    # DYNAMIC PRINTING FOR UNNAMED OPERATORS
    # ---------------------------------------------------------
    def _latex(self, printer):
        if self._custom_symbol is not None:
            return self._custom_symbol
        return printer._print(OperatorDisplayProxy(self.template, self.dummy_func))

    def _pretty(self, printer):
        if self._custom_symbol is not None:
            return printer._print(sp.Symbol(self._custom_symbol))
        return printer._print(OperatorDisplayProxy(self.template, self.dummy_func))

    def _sympystr(self, printer):
        if self._custom_symbol is not None:
            return self._custom_symbol
        return printer._print(OperatorDisplayProxy(self.template, self.dummy_func))
