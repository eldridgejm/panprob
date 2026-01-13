from panprob.renderers.html import render
from panprob import ast

from textwrap import dedent


def test_no_space_after_bold():
    tree = ast.Paragraph(
        children=[
            ast.Text("Testing", bold=True),
            ast.Text("."),
        ]
    )

    assert render(tree) == "<p><b>Testing</b>.</p>"


def test_no_indentation_in_multiline_code_block():
    tree = ast.Problem(
        children=[
            ast.Code("python", code="def foo():\n    print('hello')"),
        ]
    )

    expected = dedent(
        """
        <div class="problem">
            <div class="problem-body">
        <pre class="code"><code>
        def foo():
            print('hello')
        </code></pre>

            </div>
        </div>
        """.strip(
            "\n"
        )
    )

    assert render(tree) == expected


def test_align_math():
    tree = ast.AlignMath("x &= 1 \\\\\ny &= 2", starred=False)

    assert render(tree) == '<div class="math">$$\\begin{align}x &= 1 \\\\\ny &= 2\\end{align}$$</div>'


def test_align_star_math():
    tree = ast.AlignMath("x &= 1 \\\\\ny &= 2", starred=True)

    assert render(tree) == '<div class="math">$$\\begin{align*}x &= 1 \\\\\ny &= 2\\end{align*}$$</div>'
