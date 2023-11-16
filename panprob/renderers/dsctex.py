"""Renders a problem to DSCTeX."""

from textwrap import dedent, indent

from .. import ast

from . import _util

# A problem is rendered from an AST to LaTeX by recursively rendering each node using a
# "node renderer". A node renderer is a function that takes 1) a node and 2) a callback
# function for rendering child nodes, and returns the LaTeX for the node. This module
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

# problems and subproblems -------------------------------------------------------------


@_renderer(ast.Problem)
def _render_problem(node: ast.Problem, render_child):
    contents = "\n".join(render_child(child) for child in node.children)
    contents = indent(contents, "    ")
    return dedent(
        r"""
        \begin{{prob}}
        {contents}
        \end{{prob}}
        """
    ).format(contents=contents)


# text ---------------------------------------------------------------------------------


@_renderer(ast.Text)
def _render_text(node: ast.Text, render_child):
    if node.bold:
        return rf"\textbf{{{node.text}}}"
    elif node.italic:
        return rf"\textit{{{node.text}}}"
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
        \begin{{minted}}{{{language}}}
        {code}
        \end{{minted}}
        """
    ).format(code=code, language=node.language)


@_renderer(ast.InlineCode)
def _render_inlinecode(node: ast.InlineCode, render_child):
    return rf"\mintinline{{{node.language}}}{{{node.code}}}"


# math ---------------------------------------------------------------------------------


@_renderer(ast.InlineMath)
def _render_inlinemath(node: ast.InlineMath, render_child):
    return rf"${node.latex}$"


@_renderer(ast.DisplayMath)
def _render_displaymath(node: ast.DisplayMath, render_child):
    latex = indent(node.latex, "    ")
    return dedent(
        r"""
        \[
        {latex}
        \]
        """
    ).format(latex=latex)


# solutions and response areas ---------------------------------------------------------


@_renderer(ast.TrueFalse)
def _render_truefalse(node: ast.TrueFalse, render_child):
    command = r"\Tf{}" if node.solution else r"\tF{}"
    return dedent(
        """
        {command}
        """
    ).format(command=command)


@_renderer(ast.Solution)
def _render_solution(node: ast.Solution, render_child):
    contents = "\n".join(render_child(child) for child in node.children)
    contents = indent(contents, "    ")
    return dedent(
        r"""
        \begin{{soln}}
        {contents}
        \end{{soln}}
        """
    ).format(contents=contents)


def _render_choice(node: ast.Choice, render_child):
    command = r"\correctchoice" if node.correct else r"\choice"
    contents = "".join(render_child(child) for child in node.children)
    contents = indent(contents, "    ")
    return (
        dedent(
            r"""
        {command} {{
        {contents}
        }}
        """
        )
        .format(command=command, contents=contents)
        .strip()
    )


@_renderer(ast.MultipleChoice)
def _render_multiplechoice(node: ast.MultipleChoice, render_child):
    choices = [_render_choice(child, render_child) for child in node.children]
    choices = indent("\n".join(choices), "    ")
    return dedent(
        r"""
        \begin{{choices}}
        {choices}
        \end{{choices}}
        """
    ).format(choices=choices)


@_renderer(ast.MultipleSelect)
def _render_multipleselect(node: ast.MultipleSelect, render_child):
    choices = [_render_choice(child, render_child) for child in node.children]
    choices = indent("\n".join(choices), "    ")
    return dedent(
        r"""
        \begin{{choices}}[rectangle]
        {choices}
        \end{{choices}}
        """
    ).format(choices=choices)


@_renderer(ast.InlineResponseBox)
def _render_inlineresponsebox(node: ast.InlineResponseBox, render_child):
    content = "".join(render_child(child) for child in node.children)
    return r"\inlineresponsebox{{{}}}".format(content)


# media --------------------------------------------------------------------------------


@_renderer(ast.ImageFile)
def _render_imagefile(node: ast.ImageFile, render_child):
    return dedent(
        r"""
        \includegraphics{{{path}}}
        """
    ).format(path=node.relative_path)


# renderer =============================================================================


def render(problem: ast.Problem, overrides=None) -> str:
    """Render a problem to a DSCTeX problem in LaTeX.

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
        The problem rendered as a LaTeX string.

    Notes
    -----
    A renderer function is called with two arguments:

        1. The node to render.
        2. A function that recursively renders a node to LaTeX by choosing the correct
           node renderer for each child node.

    It is expected to return an LaTeX string.

    """
    renderers = {**_RENDERERS, **(overrides or {})}

    def _render_node(node: ast.Node):
        if type(node) in renderers:
            return renderers[type(node)](node, _render_node)
        else:
            raise NotImplementedError(f"no DSCTeX renderer for {type(node)}")

    latex = _render_node(problem)
    return _util.collapse_empty_lines(latex)
