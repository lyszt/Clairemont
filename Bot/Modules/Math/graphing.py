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
        try:
            function = sympify(function)
            f = lambdify(x, function, modules=['numpy'])
            output = f(values)
        except Exception as e:
            self.console.log(f"Error parsing or evaluating function: {e}")
            raise
        plt.clf()
        plt.plot(values, output, color='black', linewidth=2)
        plt.title(f"Gráfico de f(x) = {function}")
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.grid(True)
        plt.savefig("graph_2d.jpg")
        plt.close()

    def graph_3d(self, function):
        self.console.log("Graphing 3D function...")

        # Create grid over x and y
        x = np.linspace(-10, 10, 100)
        y = np.linspace(-10, 10, 100)
        X, Y = np.meshgrid(x, y)

        x, y = symbols('x y')
        try:
            expr = sympify(function)
            f = lambdify((x, y), expr, modules=['numpy'])
            Z = f(X, Y)
        except Exception as e:
            self.console.log(f"Error parsing or evaluating function: {e}")
            raise


        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(X, Y, Z, cmap='viridis')
        ax.set_title(f"f(x, y) = {function}")
        plt.savefig("graph_3d.jpg")
        plt.close()


