import matplotlib.pyplot
from sympy import symbols, sympify, lambdify, simplify
import numpy as np
from matplotlib import pyplot as plt

class Math:
    @staticmethod
    def simplify(expression: str):
        expression = simplify(sympify(expression))
        return expression

    @staticmethod
    def save_latex_to_image(expression: str, filename, dpi=300):
        """
        Renders a LaTeX mathematical expression to an image file.

        Args:
            filename (str): The path to save the output image (e.g., 'expression.png').
            dpi (int): The resolution of the output image in dots per inch.
        """
        expression = f"${expression}"
        fig, ax = plt.subplots(figsize=(2, 1))
        ax.axis('off')
        ax.text(0.5, 0.5, expression, size=25, ha='center', va='center')

        try:
            fig.savefig(filename, dpi=dpi, bbox_inches='tight', pad_inches=0.1, transparent=True)
            print(f"Successfully saved expression to '{filename}'")
        except Exception as e:
            print(f"An error occurred: {e}")

        plt.close(fig)

