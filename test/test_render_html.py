from panprob.renderers.html import render
from panprob import ast


def test_no_space_after_bold():
    tree = ast.Paragraph(children=[
        ast.Text("Testing", bold=True),
        ast.Text("."),
        ])

    assert render(tree) == '<p><b>Testing</b>.</p>'
