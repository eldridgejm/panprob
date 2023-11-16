from panprob.renderers.dsctex import render
from panprob import ast

from textwrap import dedent


def print_ast(node, indent=0):
    if isinstance(node, ast.Text):
        contents = " - " + node.text
    else:
        contents = ""

    print("  " * indent + type(node).__name__ + contents)
    if hasattr(node, "children"):
        for child in node.children:
            print_ast(child, indent + 1)


def test_on_simple_problem():
    tree = ast.Problem(
        children=[
            ast.Text("This is a simple problem."),
        ]
    )

    assert render(tree) == dedent(
        r"""
        \begin{prob}
            This is a simple problem.
        \end{prob}
        """
    )


def test_paragraph():
    tree = ast.Problem(
        children=[
            ast.Paragraph(
                children=[
                    ast.Text("This is a paragraph."),
                ]
            )
        ]
    )

    assert render(tree) == dedent(
        r"""
        \begin{prob}

            This is a paragraph.

        \end{prob}
        """
    )


def test_bold_text():
    tree = ast.Problem(
        children=[
            ast.Paragraph(
                children=[
                    ast.Text("This is some "),
                    ast.Text("bold text", bold=True),
                    ast.Text("."),
                ]
            )
        ]
    )

    assert render(tree) == dedent(
        r"""
        \begin{prob}

            This is some \textbf{bold text}.

        \end{prob}
        """
    )


def test_italic_text():
    tree = ast.Problem(
        children=[
            ast.Paragraph(
                children=[
                    ast.Text("This is some "),
                    ast.Text("italic text", italic=True),
                    ast.Text("."),
                ]
            )
        ]
    )

    assert render(tree) == dedent(
        r"""
        \begin{prob}

            This is some \textit{italic text}.

        \end{prob}
        """
    )


def test_inline_code():
    tree = ast.Problem(
        children=[
            ast.Paragraph(
                children=[
                    ast.Text("This is some code: "),
                    ast.InlineCode("python", "print('Hello, world!')"),
                ]
            )
        ]
    )

    assert render(tree) == dedent(
        r"""
        \begin{prob}

            This is some code: \mintinline{python}{print('Hello, world!')}

        \end{prob}
        """
    )


def test_code_block():
    tree = ast.Problem(
        children=[
            ast.Code(
                language="python",
                code=dedent(
                    """
                def main():
                    print("Hello, world!")
                """
                ),
            )
        ]
    )

    assert render(tree) == dedent(
        r"""
        \begin{prob}

            \begin{minted}{python}

            def main():
                print("Hello, world!")

            \end{minted}

        \end{prob}
        """
    )


def test_inline_math():
    tree = ast.Problem(
        children=[
            ast.Paragraph(
                children=[
                    ast.Text("This is some math: "),
                    ast.InlineMath("x^2 + y^2 = z^2"),
                ]
            )
        ]
    )

    assert render(tree) == dedent(
        r"""
        \begin{prob}

            This is some math: $x^2 + y^2 = z^2$

        \end{prob}
        """
    )


def test_display_math():
    tree = ast.Problem(
        children=[
            ast.Paragraph(
                children=[
                    ast.Text("This is some math:"),
                ]
            ),
            ast.DisplayMath("x^2 + y^2 = z^2"),
        ]
    )

    assert render(tree) == dedent(
        r"""
        \begin{prob}

            This is some math:

            \[
                x^2 + y^2 = z^2
            \]

        \end{prob}
        """
    )


def test_true_false():
    tree = ast.Problem(children=[ast.TrueFalse(True)])

    assert render(tree) == dedent(
        r"""
        \begin{prob}

            \Tf{}

        \end{prob}
        """
    )


def test_solution():
    tree = ast.Problem(
        children=[
            ast.Solution(
                children=[
                    ast.Paragraph(
                        children=[
                            ast.Text("This is a solution."),
                        ]
                    )
                ]
            )
        ]
    )

    assert render(tree) == dedent(
        r"""
        \begin{prob}

            \begin{soln}

                This is a solution.

            \end{soln}

        \end{prob}
        """
    )


def test_multiple_choice():
    tree = ast.Problem(
        children=[
            ast.MultipleChoice(
                children=[
                    ast.Choice(correct=False, children=[ast.Text("One")]),
                    ast.Choice(correct=False, children=[ast.Text("Two")]),
                    ast.Choice(correct=True, children=[ast.Text("Three")]),
                ]
            )
        ]
    )

    assert render(tree) == dedent(
        r"""
        \begin{prob}

            \begin{choices}
                \choice {
                    One
                }
                \choice {
                    Two
                }
                \correctchoice {
                    Three
                }
            \end{choices}

        \end{prob}
        """
    )


def test_multiple_select():
    tree = ast.Problem(
        children=[
            ast.MultipleSelect(
                children=[
                    ast.Choice(correct=False, children=[ast.Text("One")]),
                    ast.Choice(correct=False, children=[ast.Text("Two")]),
                    ast.Choice(correct=True, children=[ast.Text("Three")]),
                ]
            )
        ]
    )

    assert render(tree) == dedent(
        r"""
        \begin{prob}

            \begin{choices}[rectangle]
                \choice {
                    One
                }
                \choice {
                    Two
                }
                \correctchoice {
                    Three
                }
            \end{choices}

        \end{prob}
        """
    )


def test_inline_response_box():
    tree = ast.Problem(
        children=[
            ast.Paragraph(
                children=[
                    ast.Text("This is a response box: "),
                    ast.InlineResponseBox(
                        children=[
                            ast.Text("Solution"),
                        ]
                    ),
                ]
            )
        ]
    )

    assert render(tree) == dedent(
        r"""
        \begin{prob}

            This is a response box: \inlineresponsebox{Solution}

        \end{prob}
        """
    )


def test_image():
    tree = ast.Problem(
        children=[
            ast.ImageFile("./image.png"),
        ]
    )

    assert render(tree) == dedent(
        r"""
        \begin{prob}

            \includegraphics{./image.png}

        \end{prob}
        """
    )
