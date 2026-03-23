# core/blueprints.py

from abc import ABC, abstractmethod

class Additive(ABC):
    def __add__(self, other):
        from .factory import CompositeSum
        CombinedClass = CompositeSum(self.__class__, other.__class__)
        return CombinedClass(*(self.args + other.args))

    def __sub__(self, other):
        from .factory import CompositeSub
        CombinedClass = CompositeSub(self.__class__, other.__class__)
        return CombinedClass(*(self.args + other.args))

class Multiplicative(ABC):
    def __mul__(self, other):
        from .factory import CompositeMul
        CombinedClass = CompositeMul(self.__class__, other.__class__)
        return CombinedClass(*(self.args + other.args))

class Divisible(ABC):
    def __truediv__(self, other):
        from .factory import CompositeDiv
        CombinedClass = CompositeDiv(self.__class__, other.__class__)
        return CombinedClass(*(self.args + other.args))