"""Tests for postprocessors.paragraphize."""

from panprob import ast
from panprob.postprocessors import paragraphize


def test_preserves_text_styling():
    tree = ast.Problem(
        children=[
            ast.Blob(children=[ast.Text("This is ")]),
            ast.Blob(children=[ast.Text("bold", bold=True)]),
            ast.Blob(children=[ast.Text(" and ")]),
            ast.Blob(children=[ast.Text("italic", italic=True)]),
        ]
    )

    result = paragraphize(tree)

    assert result == ast.Problem(
        children=[
            ast.Paragraph(
                children=[
                    ast.Text("This is "),
                    ast.Text("bold", bold=True),
                    ast.Text(" and "),
                    ast.Text("italic", italic=True),
                ]
            ),
        ]
    )


def test_leaves_isolated_paragraphs_alone():
    tree = ast.Problem(children=[ast.Paragraph(children=[ast.Text("Testing")])])
    result = paragraphize(tree)
    assert result == tree
