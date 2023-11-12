from textwrap import dedent, indent

from panprob.parsers.dsctex import parse
from panprob import ast

# problems =============================================================================


def test_parses_empty_problem():
    tree = parse(r"\begin{prob}\end{prob}")

    assert tree == ast.Problem()


def test_parses_problem_with_text_inside():
    tree = parse(r"\begin{prob}hello world\end{prob}")

    expected = ast.Problem(
        children=[
            ast.Text("hello world"),
        ]
    )

    assert tree == expected


def test_subproblems():
    tree = parse(
        dedent(
            r"""
            \begin{prob}
                This is the problem.

                \begin{subprobset}
                    \begin{subprob}
                        hello world
                    \end{subprob}

                    \begin{subprob}
                        goodbye world
                    \end{subprob}
                \end{subprobset}
            \end{prob}
            """
        )
    )

    expected = ast.Problem(
        children=[
            ast.Text("\n    This is the problem.\n\n    "),
            ast.Subproblem(
                children=[
                    ast.Text("\n            hello world\n        "),
                ]
            ),
            ast.Subproblem(
                children=[
                    ast.Text("\n            goodbye world\n        "),
                ]
            ),
        ]
    )

    assert tree == expected


# text formatting ======================================================================


def test_parses_problem_with_bold_text():
    tree = parse(
        dedent(
            r"""
            \begin{prob}
                hello \textbf{world}
            \end{prob}
            """
        )
    )

    assert tree == ast.Problem(
        children=[
            ast.Text("\n    hello "),
            ast.Text("world", bold=True),
        ]
    )


def parses_problem_with_italic_text():
    tree = parse(
        dedent(
            r"""
            \begin{prob}
                hello \textit{world}
            \end{prob}
            """
        )
    )

    assert tree == ast.Problem(
        children=[
            ast.Text("\n    hello "),
            ast.Text("world", italic=True),
        ]
    )


# math =================================================================================


def test_parses_problem_with_inline_math():
    tree = parse(
        dedent(
            r"""
            \begin{prob}
                hello $f(x) \geq 42$
            \end{prob}
            """
        )
    )

    assert tree == ast.Problem(
        children=[
            ast.Text("\n    hello "),
            ast.InlineMath(r"f(x) \geq 42"),
        ]
    )


def test_parses_problem_with_dollar_dollar_math():
    tree = parse(
        dedent(
            r"""
            \begin{prob}
                hello $$f(x) = 42$$
            \end{prob}
            """
        )
    )

    assert tree == ast.Problem(
        children=[
            ast.Text("\n    hello "),
            ast.DisplayMath("f(x) = 42"),
        ]
    )


def test_parses_problem_with_display_math():
    tree = parse(
        dedent(
            r"""
            \begin{prob}
                hello \[f(x) = 42\]
            \end{prob}
            """
        )
    )

    assert tree == ast.Problem(
        children=[
            ast.Text("\n    hello "),
            ast.DisplayMath("f(x) = 42"),
        ]
    )


# code =================================================================================


def test_parses_problem_with_minted_code_block():
    tree = parse(
        dedent(
            r"""
            \begin{prob}
                \begin{minted}{python}
                def f(x):
                    return x + 1
                \end{minted}
            \end{prob}
            """
        )
    )

    code = dedent(
        r"""
            def f(x):
                return x + 1
            """
    )
    assert tree == ast.Problem(children=[ast.Code("python", code)])


def test_parses_problem_with_mintinline_code():
    tree = parse(
        dedent(
            r"""
            \begin{prob}
                \mintinline{python}{def f(x): return x + 1}
            \end{prob}
            """
        )
    )

    assert tree == ast.Problem(
        children=[
            ast.InlineCode("python", "def f(x): return x + 1"),
        ]
    )


def test_inputminted(tmp_path):
    tree = parse(
        dedent(
            r"""
            \begin{prob}
                \inputminted{python}{code.py}
            \end{prob}
            """
        ),
    )

    assert tree == ast.Problem(
        children=[
            ast.CodeFile(
                "python",
                "code.py",
            )
        ]
    )


# response areas =======================================================================


def test_problem_with_multiple_choices():
    tree = parse(
        dedent(
            r"""
            \begin{prob}
                \begin{choices}
                    \choice hello \textbf{world}
                    \choice goodbye world
                    \correctchoice goodbye world
                \end{choices}
            \end{prob}
            """
        )
    )

    assert tree == ast.Problem(
        children=[
            ast.MultipleChoice(
                children=[
                    ast.Choice(
                        children=[
                            ast.Text(" hello "),
                            ast.Text("world", bold=True),
                        ]
                    ),
                    ast.Choice(
                        children=[
                            ast.Text(" goodbye world\n        "),
                        ]
                    ),
                    ast.Choice(
                        children=[
                            ast.Text(" goodbye world\n    "),
                        ],
                        correct=True,
                    ),
                ]
            )
        ]
    )


def test_problem_with_multiple_select():
    tree = parse(
        dedent(
            r"""
            \begin{prob}
                \begin{choices}[rectangle]
                    \choice hello \textbf{world}
                    \choice goodbye world
                    \correctchoice goodbye world
                \end{choices}
            \end{prob}
            """
        )
    )

    assert tree == ast.Problem(
        children=[
            ast.MultipleSelect(
                children=[
                    ast.Choice(
                        children=[
                            ast.Text(" hello "),
                            ast.Text("world", bold=True),
                        ]
                    ),
                    ast.Choice(
                        children=[
                            ast.Text(" goodbye world\n        "),
                        ]
                    ),
                    ast.Choice(
                        children=[
                            ast.Text(" goodbye world\n    "),
                        ],
                        correct=True,
                    ),
                ]
            )
        ]
    )


def test_problem_with_code_in_multiple_choice():
    tree = parse(
        dedent(
            r"""
            \begin{prob}
                \begin{choices}
                    \choice hello \textbf{world}
                    \choice \begin{minted}{python}
                    def f(x):
                        return x + 1
                    \end{minted}
                \end{choices}
            \end{prob}
            """
        )
    )

    expected = ast.Problem(
        children=[
            ast.MultipleChoice(
                children=[
                    ast.Choice(
                        children=[
                            ast.Text(" hello "),
                            ast.Text("world", bold=True),
                        ]
                    ),
                    ast.Choice(
                        children=[
                            ast.Code(
                                "python",
                                dedent(
                                    r"""
                                        def f(x):
                                            return x + 1
                                    """
                                ),
                            ),
                        ],
                    ),
                ]
            )
        ]
    )

    assert tree == expected


def test_problem_with_solution():
    tree = parse(
        dedent(
            r"""
            \begin{prob}
                hello world
                \begin{soln}
                    goodbye world
                \end{soln}
            \end{prob}
            """
        )
    )

    assert tree == ast.Problem(
        children=[
            ast.Text("\n    hello world\n    "),
            ast.Solution(
                children=[
                    ast.Text("\n        goodbye world\n    "),
                ]
            ),
        ]
    )


def test_problem_with_Tf():
    tree = parse(
        dedent(
            r"""
            \begin{prob}
                hello world
                \Tf{}
            \end{prob}
            """
        )
    )

    assert tree == ast.Problem(
        children=[
            ast.Text("\n    hello world\n    "),
            ast.TrueFalse(solution=True),
        ]
    )


def test_problem_with_tF():
    tree = parse(
        dedent(
            r"""
            \begin{prob}
                hello world
                \tF{}
            \end{prob}
            """
        )
    )

    assert tree == ast.Problem(
        children=[
            ast.Text("\n    hello world\n    "),
            ast.TrueFalse(solution=False),
        ]
    )


# media ================================================================================


def test_includegraphics(tmp_path):
    tree = parse(
        dedent(
            r"""
            \begin{prob}
                \includegraphics{image.png}
            \end{prob}
            """
        ),
    )

    assert tree == ast.Problem(
        children=[
            ast.ImageFile(
                relative_path="image.png",
            )
        ]
    )


# custom converters ====================================================================


def test_overriding_existing_converter():
    latex = r"""
    \begin{prob}
        \textbf{Testing}
    \end{prob}
    """

    def convert_textbf(node, children):
        return ast.Text("IT WORKED", italic=True)

    tree = parse(latex, command_converters={"textbf": convert_textbf})

    assert tree == ast.Problem(
        children=[
            ast.Text("IT WORKED", italic=True),
        ]
    )


def test_extending_with_new_converter():
    latex = r"""
    \begin{prob}
        \python{this}
    \end{prob}
    """

    def convert_python(command, children):
        return ast.InlineCode("python", command.args[0].raw_contents)

    tree = parse(latex, command_converters={"python": convert_python})

    assert tree == ast.Problem(
        children=[
            ast.InlineCode("python", "this"),
        ]
    )
