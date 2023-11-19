from textwrap import dedent, indent

from panprob.parsers.dsctex import parse
from panprob import ast, exceptions

from pytest import raises

# problems =============================================================================


def test_parses_empty_problem():
    tree = parse(r"\begin{prob}\end{prob}")

    assert tree == ast.Problem()


def test_parses_problem_with_text_inside():
    tree = parse(r"\begin{prob}hello world\end{prob}")

    expected = ast.Problem(
        children=[
            ast.Paragraph(
                children=[
                    ast.Text("hello world"),
                ]
            ),
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
            ast.Paragraph(children=[ast.Text("This is the problem.")]),
            ast.Subproblem(
                children=[
                    ast.Paragraph(
                        children=[
                            ast.Text("hello world"),
                        ]
                    ),
                ]
            ),
            ast.Subproblem(
                children=[
                    ast.Paragraph(
                        children=[
                            ast.Text("goodbye world"),
                        ]
                    ),
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
            ast.Paragraph(
                children=[
                    ast.Text("hello "),
                    ast.Text("world", bold=True),
                ]
            ),
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
            ast.Paragraph(
                children=[
                    ast.Text("hello "),
                    ast.InlineMath(r"f(x) \geq 42"),
                ]
            ),
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
            ast.Paragraph(
                children=[
                    ast.Text("hello"),
                ]
            ),
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
            ast.Paragraph(
                children=[
                    ast.Text("hello"),
                ]
            ),
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
            ast.Paragraph(
                children=[
                    ast.InlineCode("python", "def f(x): return x + 1"),
                ]
            ),
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
                            ast.Paragraph(
                                children=[
                                    ast.Text("hello "),
                                    ast.Text("world", bold=True),
                                ]
                            ),
                        ]
                    ),
                    ast.Choice(
                        children=[
                            ast.Paragraph(
                                children=[
                                    ast.Text("goodbye world"),
                                ]
                            ),
                        ]
                    ),
                    ast.Choice(
                        children=[
                            ast.Paragraph(
                                children=[
                                    ast.Text("goodbye world"),
                                ]
                            ),
                        ],
                        correct=True,
                    ),
                ]
            )
        ]
    )


def test_problem_with_choices_spread_across_multiple_lines():
    tree = parse(
        dedent(
            r"""
            \begin{prob}
                \begin{choices}
                    \choice {

                        hello \textbf{world}

                    }
                    \choice {

                        goodbye world

                    }
                    \correctchoice {

                        ok world

                    }
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
                            ast.Paragraph(
                                children=[
                                    ast.Text("hello "),
                                    ast.Text("world", bold=True),
                                ]
                            ),
                        ]
                    ),
                    ast.Choice(
                        children=[
                            ast.Paragraph(
                                children=[
                                    ast.Text("goodbye world"),
                                ]
                            ),
                        ]
                    ),
                    ast.Choice(
                        children=[
                            ast.Paragraph(
                                children=[
                                    ast.Text("ok world"),
                                ]
                            ),
                        ],
                        correct=True,
                    ),
                ]
            )
        ]
    )


def test_problem_with_choices_spread_across_multiple_lines_with_empty_choices():
    tree = parse(
        dedent(
            r"""
            \begin{prob}
                \begin{choices}
                    \choice {

                    }
                    \choice {

                    }
                    \correctchoice {

                    }
                \end{choices}
            \end{prob}
            """
        )
    )

    assert tree == ast.Problem(
        children=[
            ast.MultipleChoice(
                children=[
                    ast.Choice(children=[]),
                    ast.Choice(children=[]),
                    ast.Choice(
                        children=[],
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
                            ast.Paragraph(
                                children=[
                                    ast.Text("hello "),
                                    ast.Text("world", bold=True),
                                ]
                            ),
                        ]
                    ),
                    ast.Choice(
                        children=[
                            ast.Paragraph(
                                children=[
                                    ast.Text("goodbye world"),
                                ]
                            ),
                        ]
                    ),
                    ast.Choice(
                        children=[
                            ast.Paragraph(
                                children=[
                                    ast.Text("goodbye world"),
                                ]
                            ),
                        ],
                        correct=True,
                    ),
                ]
            )
        ]
    )


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
            ast.Paragraph(
                children=[
                    ast.Text("hello world"),
                ]
            ),
            ast.Solution(
                children=[
                    ast.Paragraph(
                        children=[
                            ast.Text("goodbye world"),
                        ]
                    ),
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
            ast.Paragraph(
                children=[
                    ast.Text("hello world"),
                ]
            ),
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
            ast.Paragraph(
                children=[
                    ast.Text("hello world"),
                ]
            ),
            ast.TrueFalse(solution=False),
        ]
    )


def test_inline_response_box():
    tree = parse(
        dedent(
            r"""
            \begin{prob}
                The answer is: \inlineresponsebox[1in]{some math: $f(x) \geq 42$}
            \end{prob}
            """
        )
    )

    assert tree == ast.Problem(
        children=[
            ast.Paragraph(
                children=[
                    ast.Text("The answer is: "),
                    ast.InlineResponseBox(
                        children=[
                            ast.Text("some math: "),
                            ast.InlineMath(r"f(x) \geq 42"),
                        ]
                    ),
                ]
            ),
        ]
    )


def test_inline_responsebox_on_own_line_creates_a_new_paragraph():
    latex = dedent(
        r"""
        \begin{prob}

            And this is an inline response box:

            \inlineresponsebox{yes}

        \end{prob}
        """
    )

    tree = parse(latex)

    assert tree == ast.Problem(
        children=[
            ast.Paragraph(
                children=[
                    ast.Text("And this is an inline response box:"),
                ]
            ),
            ast.Paragraph(
                children=[
                    ast.InlineResponseBox(
                        children=[
                            ast.Text("yes"),
                        ]
                    )
                ]
            ),
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
        return ast.Paragraph(children=[ast.Text("IT WORKED", italic=True)])

    tree = parse(latex, command_converters={"textbf": convert_textbf})

    assert tree == ast.Problem(
        children=[
            ast.Paragraph(
                children=[
                    ast.Text("IT WORKED", italic=True),
                ]
            ),
        ]
    )


def test_extending_with_new_converter():
    latex = r"""
    \begin{prob}
        \python{this}
    \end{prob}
    """

    def convert_python(command, children):
        return ast.Paragraph(
            children=[ast.InlineCode("python", command.args[0].raw_contents)]
        )

    tree = parse(latex, command_converters={"python": convert_python})

    assert tree == ast.Problem(
        children=[
            ast.Paragraph(
                children=[
                    ast.InlineCode("python", "this"),
                ]
            ),
        ]
    )


# error handling =======================================================================


def test_raises_when_an_unknown_command_is_used():
    latex = r"""
    \begin{prob}
        \unknown{this}
    \end{prob}
    """

    with raises(exceptions.ParseError):
        parse(latex)


def test_raises_when_an_unknown_environment_is_used():
    latex = r"""
    \begin{prob}
        \begin{unknown}
            this
        \end{unknown}
    \end{prob}
    """

    with raises(exceptions.ParseError):
        parse(latex)


def test_raises_when_input_has_more_than_one_problem():
    latex = r"""
    \begin{prob}
        this
    \end{prob}

    \begin{soln}
        that
    \end{soln}
    """

    with raises(exceptions.ParseError):
        parse(latex)


def test_raises_when_the_problem_is_in_an_enviroment_that_isnt_a_problem():
    latex = r"""
    \begin{soln}
        testing
    \end{soln}
    """

    with raises(exceptions.ParseError):
        parse(latex)


def test_raises_if_inline_responsebox_doesnt_contain_single_paragraph():
    latex = r"""
    \begin{prob}
        \inlineresponsebox{
                this is the first paragraph

                and this is the second
        }
    \end{prob}
    """

    with raises(exceptions.ParseError):
        parse(latex)


def test_raises_when_input_is_blank():
    with raises(exceptions.ParseError):
        parse(
            dedent(
                """


                """
            )
        )
