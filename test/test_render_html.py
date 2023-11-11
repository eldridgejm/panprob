from panprob.renderers.html.problem import render

from panprob import types


def test_no_space_after_bold():
    tree = types.Paragraph(children=[
        types.BoldText("Testing"),
        types.NormalText("."),
        ])

    assert render(tree) == '<p><b>Testing</b>.</p>'
