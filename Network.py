import numpy as np
import Synapse as Sy

class Network:

    def __init__(self, l):
        self.n = len(l)
        self.list = []
        for i in range(self.n):
            _list = []
            for j in range(l[i]):
                _list.append(Sy.Synapse())
            self.list.append(_list)
        for i in range(self.n-1):
            for s in self.list[i]:
                s.targets = self.list[i+1]
            for s in self.list[i+1]:
                s.sources = self.list[i]
                s.weights = np.ones(len(self.list[i]))
    
    def _emit_(self):
        for i in range(self.n - 1):
            for s in self.list[i]:
                s._emit_()

    def _receive_(self, intensity):
        self.list[0][0].input = intensity + self.list[0][0].bias


