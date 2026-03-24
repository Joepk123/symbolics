# primitives/exponentials.py

class Gaussian(ExpandableFunction):
    """
    Symbolic representation of a Gaussian envelope.
    Because it inherits ExpandableFunction, it automatically acts as an Algebra 
    and routes +, -, *, / through your Factory.
    """
    @property
    def definition(self):
        coord = self.args[0]
        return sp.exp(-coord**2)