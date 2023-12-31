from panprob import ast
from panprob.postprocessors import subsume_code


def test_subsume_code_reads_code_into_ast(tmpdir):
    with (tmpdir / "testing.py").open("w") as fileob:
        fileob.write("def foo():\n    print('hello world')\n")

    tree = ast.Problem(
        children=[
            ast.Paragraph(children=[ast.Text("This is some code:")]),
            ast.CodeFile("python", "testing.py"),
        ]
    )

    resulting_tree = subsume_code(tree, root=tmpdir)

    assert resulting_tree == ast.Problem(
        children=[
            ast.Paragraph(children=[ast.Text("This is some code:")]),
            ast.Code("python", "def foo():\n    print('hello world')\n"),
        ]
    )
