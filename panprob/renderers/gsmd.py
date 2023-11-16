"""Renders a problem to Gradescope markdown."""

from textwrap import dedent, indent

from .. import ast, exceptions

from . import _util

# A problem is rendered from an AST to markdown by recursively rendering each node using a
# "node renderer". A node renderer is a function that takes 1) a node and 2) a callback
# function for rendering child nodes, and returns the markdown for the node. This module
# defines default node renderers for each node type in panprob.ast. These default
# renderers can be overridden by passing overrides to the render() function.

# The default node renderers are mapped to the node types they render by the _RENDERERS
# dictionary:

_RENDERERS = {}

# To make it easier to add a node to the _RENDERERS dictionary, we define a decorator
# that automatically adds a node renderer to the dictionary:


def _renderer(nodetype):
    def decorator(fn):
        _RENDERERS[nodetype] = fn
        return fn

    return decorator


# Renderers ============================================================================

# problems and subproblems ---------------------------------------------------------------


@_renderer(ast.Problem)
def _render_problem(node: ast.Problem, render_child):
    contents = "\n".join(render_child(child) for child in node.children)
    return dedent(contents)


# text ---------------------------------------------------------------------------------


@_renderer(ast.Text)
def _render_text(node: ast.Text, render_child):
    if node.bold:
        return rf"**{node.text}**"
    elif node.italic:
        return rf"*{node.text}*"
    else:
        return node.text


@_renderer(ast.Paragraph)
def _render_paragraph(node: ast.Paragraph, render_child):
    contents = "".join(render_child(child) for child in node.children)
    contents = dedent(contents)
    return dedent(
        rf"""
        {contents}
        """
    )


# code ---------------------------------------------------------------------------------


@_renderer(ast.Code)
def _render_code(node: ast.Code, render_child):
    code = node.code
    return dedent(
        r"""
        ```{language}
        {code}
        ```
        """
    ).format(code=code, language=node.language)


@_renderer(ast.InlineCode)
def _render_inlinecode(node: ast.InlineCode, render_child):
    return rf"`{node.code}`"


# math ---------------------------------------------------------------------------------


@_renderer(ast.InlineMath)
def _render_inlinemath(node: ast.InlineMath, render_child):
    return rf"$${node.latex}$$"


@_renderer(ast.DisplayMath)
def _render_displaymath(node: ast.DisplayMath, render_child):
    return dedent(
        r"""

        $${latex}$$

        """
    ).format(latex=node.latex)


# solutions and response areas ---------------------------------------------------------


@_renderer(ast.TrueFalse)
def _render_truefalse(node: ast.TrueFalse, render_child):
    if node.solution:
        return dedent(
            """
            (x) True
            ( ) False
            """
        )
    else:
        return dedent(
            """
            ( ) True
            (x) False
            """
        )


@_renderer(ast.Solution)
def _render_solution(node: ast.Solution, render_child):
    contents = "\n".join(render_child(child) for child in node.children)

    # we have to be a little careful, because Gradescope markdown solutions need to be
    # a single line of text. Instead, we'll render the contents, split into lines, and
    # wrap each line inside [[ ... ]]
    contents = _util.collapse_empty_lines(contents)
    lines = contents.split("\n")
    lines = "\n".join(f"[[{line}]]" for line in lines if line)

    return dedent(
        r"""

        {contents}

        """
    ).format(contents=lines)


def _render_choice(node: ast.Choice, render_child, rectangle=False):
    contents = "".join(render_child(child) for child in node.children).strip()

    # check that the contents are only a single line, because Gradescope markdown
    # does not support multi-line choice options
    if len(contents.split("\n")) > 1:
        raise ValueError(
            "Gradescope markdown does not support multi-line choice options"
        )

    if rectangle:
        return ("[x]" if node.correct else "[ ]") + " " + contents
    else:
        return ("(x)" if node.correct else "( )") + " " + contents


@_renderer(ast.MultipleChoice)
def _render_multiplechoice(node: ast.MultipleChoice, render_child):
    choices = "\n".join(_render_choice(child, render_child) for child in node.children)
    return dedent(
        r"""

        {choices}

        """
    ).format(choices=choices)


@_renderer(ast.MultipleSelect)
def _render_multipleselect(node: ast.MultipleSelect, render_child):
    choices = "\n".join(
        _render_choice(child, render_child, rectangle=True) for child in node.children
    )
    return dedent(
        r"""

        {choices}

        """
    ).format(choices=choices)


@_renderer(ast.InlineResponseBox)
def _render_inlineresponsebox(node: ast.InlineResponseBox, render_child):
    content = "".join(render_child(child) for child in node.children)
    return "\n" + r"[____]({content})".format(content=content) + "\n"


# media --------------------------------------------------------------------------------


@_renderer(ast.ImageFile)
def _render_imagefile(node: ast.ImageFile, render_child):
    return dedent(
        r"""
        ![]({path})
        """
    ).format(path=node.relative_path)


# renderer =============================================================================

_UNSUPPORTED = {
    ast.CodeFile: (
        "The problem contains a reference to a code file, but the "
        "Gradescope markdown renderer does not support this."
    ),
}


def render(problem: ast.Problem, overrides=None) -> str:
    """Render a problem in Gradescope markdown.

    This render is capable of rendering all node types from :mod:`panprob.ast`.

    Parameters
    ----------
    problem : ast.Problem
        The problem to render.
    overrides : dict, optional
        A dictionary mapping node types to functions that render them. If a node type
        is not in this dictionary, the default renderer is used. See below for the
        expected signature of these functions.

    Returns
    -------
    str
        The problem rendered as a markdown string.

    Notes
    -----
    A renderer function is called with two arguments:

        1. The node to render.
        2. A function that recursively renders a node to markdown by choosing the correct
           node renderer for each child node.

    It is expected to return an markdown string.

    """
    renderers = {**_RENDERERS, **(overrides or {})}

    def _render_node(node: ast.Node):
        if type(node) in _UNSUPPORTED:
            raise exceptions.Error(_UNSUPPORTED[type(node)])

        if type(node) in renderers:
            return renderers[type(node)](node, _render_node)
        else:
            raise exceptions.Error(
                f"no Gradescope markdown renderer for AST node '{type(node).__name__}'"
            )

    latex = _render_node(problem)
    return _util.collapse_empty_lines(latex)
