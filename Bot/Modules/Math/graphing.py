import matplotlib.pyplot
from sympy import symbols, sympify, lambdify
import numpy as np
from matplotlib import pyplot as plt


class Graphing:
    def __init__(self, console):
        self.console = console
        pass

    def graph_2d(self, function):
        self.console.log("Graphing 2d function...")
        values = np.linspace(-20, 20, 1000)
        x = symbols('x')
        function = sympify(function)
        f = lambdify(x, function, modules=['numpy'])
        output = f(values)
        plt.clf()
        plt.plot(values, output, color='black', linewidth=2)
        plt.title(f"Gráfico de f(x) = {function}")
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.grid(True)
        plt.savefig("graph_2d.jpg")
        plt.close()



