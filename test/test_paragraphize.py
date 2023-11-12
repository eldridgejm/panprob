"""Tests for ast.postprocessors.paragraphize."""

from panprob import ast
from panprob.ast.postprocessors import paragraphize


def test_wraps_isolated_text_nodes_into_paragraphs():
    tree = ast.Problem(children=[ast.Text("This is text.")])

    result = paragraphize(tree)

    assert result == ast.Problem(
        children=[ast.Paragraph(children=[ast.Text("This is text.")])]
    )


def test_splits_text_nodes_at_newlines():
    tree = ast.Problem(
        children=[
            ast.Text("One\n\nTwo\n\nThree"),
        ]
    )

    result = paragraphize(tree)

    assert result == ast.Problem(
        children=[
            ast.Paragraph(children=[ast.Text("One")]),
            ast.Paragraph(children=[ast.Text("Two")]),
            ast.Paragraph(children=[ast.Text("Three")]),
        ]
    )


def test_preserves_text_styling():
    tree = ast.Problem(
        children=[
            ast.Text("This is "),
            ast.Text("bold", bold=True),
            ast.Text(" and "),
            ast.Text("italic", italic=True),
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
