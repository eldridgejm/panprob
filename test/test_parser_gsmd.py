from textwrap import dedent, indent

from panprob.parsers.gsmd import parse
from panprob import ast


def print_ast(node, indent=0):
    print("  " * indent + type(node).__name__)
    if hasattr(node, "children"):
        for child in node.children:
            print_ast(child, indent + 1)


def test_simple_problem():
    md = dedent(
        """
        This is the problem.
        """
    )

    expected = ast.Problem(
        children=[
            ast.Text("\n"),
            ast.Paragraph(children=[ast.Text("This is the problem.")]),
        ]
    )

    assert parse(md) == expected


def test_bold_text():
    md = dedent(
        """
        This is the **problem here**.
        """
    )

    expected = ast.Problem(
        children=[
            ast.Text("\n"),
            ast.Paragraph(
                children=[
                    ast.Text("This is the "),
                    ast.Text("problem here", bold=True),
                    ast.Text("."),
                ]
            ),
        ]
    )

    assert parse(md) == expected


def test_italic_text():
    md = dedent(
        """
        This is the *problem here*.
        """
    )

    expected = ast.Problem(
        children=[
            ast.Text("\n"),
            ast.Paragraph(
                children=[
                    ast.Text("This is the "),
                    ast.Text("problem here", italic=True),
                    ast.Text("."),
                ]
            ),
        ]
    )

    assert parse(md) == expected


def test_inline_code():
    md = dedent(
        """
        This is the `code`.
        """
    )

    expected = ast.Problem(
        children=[
            ast.Text("\n"),
            ast.Paragraph(
                children=[
                    ast.Text("This is the "),
                    ast.InlineCode("text", "code"),
                    ast.Text("."),
                ]
            ),
        ]
    )

    assert parse(md) == expected


def test_fenced_code_block():
    md = dedent(
        """
        This is the code:

        ```lua
        local x = 42
        ```
        """
    )

    expected = ast.Problem(
        children=[
            ast.Text("\n"),
            ast.Paragraph(
                children=[
                    ast.Text("This is the code:"),
                ]
            ),
            ast.Text("\n"),
            ast.Code("lua", "local x = 42\n"),
        ]
    )

    assert parse(md) == expected


def test_image():
    md = dedent(
        """
        ![alt text](images/foo.png)
        """
    )

    expected = ast.Problem(
        children=[
            ast.Text("\n"),
            ast.Paragraph(
                children=[
                    ast.ImageFile("images/foo.png"),
                ]
            ),
        ]
    )

    assert parse(md) == expected


def test_inline_math():
    md = dedent(
        """
        This is math: $$x^2$$.
        """
    )

    expected = ast.Problem(
        children=[
            ast.Text("\n"),
            ast.Paragraph(
                children=[
                    ast.Text("This is math: "),
                    ast.InlineMath("x^2"),
                    ast.Text("."),
                ]
            ),
        ]
    )

    assert parse(md) == expected


def test_solution():
    md = dedent(
        """
        This is a solution:

        [[Testing this]]
        """
    )

    expected = ast.Problem(
        children=[
            ast.Text("\n"),
            ast.Paragraph(
                children=[
                    ast.Text("This is a solution:"),
                ]
            ),
            ast.Text("\n"),
            ast.Solution(
                children=[
                    ast.Paragraph(
                        children=[
                            ast.Text("Testing this"),
                        ]
                    )
                ]
            ),
            ast.Text("\n"),
        ]
    )

    assert parse(md) == expected


def test_solution_contents_are_parsed():
    md = dedent(
        """
        This is a solution:

        [[Testing $$x = 42$$]]
        """
    )

    expected = ast.Problem(
        children=[
            ast.Text("\n"),
            ast.Paragraph(
                children=[
                    ast.Text("This is a solution:"),
                ]
            ),
            ast.Text("\n"),
            ast.Solution(
                children=[
                    ast.Paragraph(
                        children=[
                            ast.Text("Testing "),
                            ast.InlineMath("x = 42"),
                        ]
                    )
                ]
            ),
            ast.Text("\n"),
        ]
    )

    assert parse(md) == expected


def test_multiple_choices():
    md = dedent(
        """
        ( ) foo
        (x) bar
        ( ) baz
        """
    )

    expected = ast.Problem(
        children=[
            ast.Text("\n"),
            ast.MultipleChoice(
                children=[
                    ast.Choice(
                        children=[
                            ast.Text("foo"),
                        ]
                    ),
                    ast.Choice(
                        children=[
                            ast.Text("bar"),
                        ],
                        correct=True,
                    ),
                    ast.Choice(
                        children=[
                            ast.Text("baz"),
                        ]
                    ),
                ]
            ),
        ]
    )

    assert parse(md) == expected


def test_multiple_choices_parses_recursively():
    md = dedent(
        """
        ( ) foo $$x = 42$$
        (x) bar
        ( ) baz
        """
    )

    expected = ast.Problem(
        children=[
            ast.Text("\n"),
            ast.MultipleChoice(
                children=[
                    ast.Choice(
                        children=[
                            ast.Text("foo "),
                            ast.InlineMath("x = 42"),
                        ]
                    ),
                    ast.Choice(
                        children=[
                            ast.Text("bar"),
                        ],
                        correct=True,
                    ),
                    ast.Choice(
                        children=[
                            ast.Text("baz"),
                        ]
                    ),
                ]
            ),
        ]
    )

    assert parse(md) == expected


def test_multiple_select():
    md = dedent(
        """
        [ ] foo
        [x] bar
        [ ] baz
        """
    )

    expected = ast.Problem(
        children=[
            ast.Text("\n"),
            ast.MultipleSelect(
                children=[
                    ast.Choice(
                        children=[
                            ast.Text("foo"),
                        ]
                    ),
                    ast.Choice(
                        children=[
                            ast.Text("bar"),
                        ],
                        correct=True,
                    ),
                    ast.Choice(
                        children=[
                            ast.Text("baz"),
                        ]
                    ),
                ]
            ),
        ]
    )

    assert parse(md) == expected


def test_inline_response_box():
    md = dedent(
        """
        [____]($$f(x) = 42$$)
        """
    )

    expected = ast.Problem(
        children=[
            ast.Text("\n"),
            ast.InlineResponseBox(
                children=[
                    ast.InlineMath("f(x) = 42"),
                ]
            ),
            ast.Text("\n"),
        ]
    )

    assert parse(md) == expected
