from panprob.renderers.gsmd import render
from panprob import ast

from textwrap import dedent

from pytest import raises


def print_ast(node, indent=0):
    if isinstance(node, ast.Text):
        contents = " - " + node.text
    else:
        contents = ""

    print("  " * indent + type(node).__name__ + contents)
    if hasattr(node, "children"):
        for child in node.children:
            print_ast(child, indent + 1)


def test_text():
    tree = ast.Problem(
        children=[
            ast.Text("This is a simple problem."),
        ]
    )

    assert render(tree) == "This is a simple problem."


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
        This is a paragraph.
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
        This is some **bold text**.
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
        This is some *italic text*.
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
        This is some code: `print('Hello, world!')`
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
        ```python

        def main():
            print("Hello, world!")

        ```
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
        This is some math: $$x^2 + y^2 = z^2$$
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
        This is some math:

        $$x^2 + y^2 = z^2$$

        """
    )


def test_true_false():
    tree = ast.Problem(children=[ast.TrueFalse(True)])

    assert render(tree) == dedent(
        r"""
        (x) True
        ( ) False
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

        [[This is a solution.]]

        """
    )


def test_multiline_solution():
    tree = ast.Problem(
        children=[
            ast.Solution(
                children=[
                    ast.Paragraph(
                        children=[
                            ast.Text("This is a solution."),
                        ]
                    ),
                    ast.Paragraph(
                        children=[
                            ast.Text("This is another paragraph."),
                        ]
                    ),
                ]
            )
        ]
    )

    assert render(tree) == dedent(
        r"""

        [[This is a solution.]]
        [[This is another paragraph.]]

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

        ( ) One
        ( ) Two
        (x) Three

        """
    )


def test_trying_to_render_a_choice_with_multiple_lines_raises_an_error():
    tree = ast.Problem(
        children=[
            ast.MultipleChoice(
                children=[
                    ast.Choice(correct=False, children=[ast.Text("One\n\nTwo")]),
                    ast.Choice(correct=False, children=[ast.Text("Two")]),
                    ast.Choice(correct=True, children=[ast.Text("Three")]),
                ]
            )
        ]
    )

    with raises(ValueError):
        render(tree)


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

        [ ] One
        [ ] Two
        [x] Three

        """
    )


def test_inline_response_box():
    tree = ast.Problem(
        children=[
            ast.Paragraph(
                children=[
                    ast.Text("This is a response box:"),
                ]
            ),
            ast.InlineResponseBox(
                children=[
                    ast.Text("Solution"),
                ]
            ),
        ]
    )

    assert render(tree) == dedent(
        r"""
        This is a response box:

        [____](Solution)
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
        ![](./image.png)
        """
    )
