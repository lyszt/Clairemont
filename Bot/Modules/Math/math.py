import numpy as np
from matplotlib import pyplot as plt
from sympy import (
    symbols, sympify, lambdify, simplify, latex, expand, diff, integrate,
    solve, limit, factor, Matrix, SympifyError
)

class Math:
    """
    A class containing a suite of static methods for symbolic mathematics,
    including simplification, expansion, calculus, equation solving, and

    matrix algebra.
    """
    @staticmethod
    def simplify(expression: str):
        """Simplifies a mathematical expression."""
        try:
            return simplify(sympify(expression))
        except (SympifyError, TypeError, SyntaxError) as e:
            return f"Error: Invalid expression. {e}"

    @staticmethod
    def expand(polynomial: str):
        """Expands a polynomial expression."""
        try:
            return expand(sympify(polynomial))
        except (SympifyError, TypeError, SyntaxError) as e:
            return f"Error: Invalid expression. {e}"

    @staticmethod
    def factor(expression: str):
        """Factors a mathematical expression."""
        try:
            return factor(sympify(expression))
        except (SympifyError, TypeError, SyntaxError) as e:
            return f"Error: Invalid expression. {e}"

    @staticmethod
    def differentiate(expression: str, variable: str = 'x'):
        """
        Differentiates an expression with respect to a variable.
        Defaults to differentiating with respect to 'x'.
        """
        try:
            var_sym = symbols(variable)
            return diff(sympify(expression), var_sym)
        except (SympifyError, TypeError, SyntaxError) as e:
            return f"Error: Invalid expression or variable. {e}"

    @staticmethod
    def integrate(expression: str, variable: str = 'x', lower_bound=None, upper_bound=None):
        """
        Computes the integral of an expression.
        Performs definite integration if lower and upper bounds are provided.
        Otherwise, performs indefinite integration.
        """
        try:
            var_sym = symbols(variable)
            expr = sympify(expression)
            if lower_bound is not None and upper_bound is not None:
                # Definite integral
                return integrate(expr, (var_sym, sympify(lower_bound), sympify(upper_bound)))
            else:
                # Indefinite integral
                return integrate(expr, var_sym)
        except (SympifyError, TypeError, SyntaxError) as e:
            return f"Error: Invalid expression or bounds. {e}"

    @staticmethod
    def solve_equation(equation: str, variable: str = 'x'):
        """
        Solves an equation for a given variable.
        Assumes the equation is set to equal zero.
        Example: 'x**2 - 4' will solve x**2 - 4 = 0.
        """
        try:
            var_sym = symbols(variable)
            # The user can provide an equation like 'x**2 - 1' or 'Eq(x**2, 1)'
            # sympify can handle both. If it's just an expression, it assumes it's equal to 0.
            return solve(sympify(equation), var_sym)
        except (SympifyError, TypeError, SyntaxError) as e:
            return f"Error: Invalid equation. {e}"

    @staticmethod
    def calculate_limit(expression: str, variable: str, point: str):
        """Calculates the limit of an expression as a variable approaches a point."""
        try:
            var_sym = symbols(variable)
            return limit(sympify(expression), var_sym, sympify(point))
        except (SympifyError, TypeError, SyntaxError) as e:
            return f"Error: Invalid expression, variable, or point. {e}"

    @staticmethod
    def matrix_determinant(matrix_str: str):
        """Calculates the determinant of a matrix. Input as a list of lists, e.g., '[[1,2],[3,4]]'."""
        try:
            mat = Matrix(sympify(matrix_str))
            return mat.det()
        except Exception as e:
            return f"Error processing matrix: {e}"

    @staticmethod
    def matrix_inverse(matrix_str: str):
        """Calculates the inverse of a matrix. Input as a list of lists."""
        try:
            mat = Matrix(sympify(matrix_str))
            if not mat.is_square:
                return "Error: Matrix must be square to have an inverse."
            if mat.det() == 0:
                return "Error: Matrix is singular and has no inverse."
            return mat.inv()
        except Exception as e:
            return f"Error processing matrix: {e}"

    @staticmethod
    def matrix_eigenvals(matrix_str: str):
        """Finds the eigenvalues of a matrix. Input as a list of lists."""
        try:
            mat = Matrix(sympify(matrix_str))
            if not mat.is_square:
                return "Error: Matrix must be square to find eigenvalues."
            return mat.eigenvals()
        except Exception as e:
            return f"Error processing matrix: {e}"

    @staticmethod
    def save_latex_to_image(expression: str, filename: str, dpi: int = 300):
        """Renders a LaTeX mathematical expression to an image file."""
        try:
            # Sympify the expression first to handle potential errors
            latex_expr = latex(sympify(expression))
            expression_to_render = f"${latex_expr}$"
        except (SympifyError, TypeError, SyntaxError) as e:
            print(f"Error: Could not parse expression. {e}")
            return

        fig, ax = plt.subplots(figsize=(2, 1))
        ax.axis('off')
        ax.text(0.5, 0.5, expression_to_render, size=25, ha='center', va='center')

        try:
            fig.savefig(filename, dpi=dpi, bbox_inches='tight', pad_inches=0.1, transparent=True)
            print(f"Successfully saved expression to '{filename}'")
        except Exception as e:
            print(f"An error occurred while saving the image: {e}")

        plt.close(fig)

