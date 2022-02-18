import numpy as np


class Synapse:

    def __init__(self):
        self.bias = 0
        self.input = 0
        self.output = 0
        self.targets = []
        self.sources = []
        self.weights = np.ones(1)
        

    def _reset_(self):
        output = self.bias

    def _emit_(self):
        for target in self.targets:
            target._receive(self, self.input)

    def _receive(self, source, intensity):
        if source in self.sources:
            index = self.sources.index(source)
            self.input += self.weights[index] * intensity
        print(self.input)


    

        





