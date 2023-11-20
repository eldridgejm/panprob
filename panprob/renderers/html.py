"""Renders a problem to HTML."""

from textwrap import dedent
from uuid import uuid4

from .. import ast, exceptions

# A problem is rendered from an AST to HTML by recursively rendering each node using
# "node renderer". A node renderer is a function that takes 1) a node and 2) a callback
# function for rendering child nodes, and returns the HTML for the node. This module
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
    subprob_counter = 1
    rendered_children = []
    for child in node.children:
        if isinstance(child, ast.Subproblem):
            rendered_children.append(
                _render_subproblem(child, subprob_counter, render_child)
            )
            subprob_counter += 1
        else:
            rendered_children.append(render_child(child))

    contents = "\n".join(rendered_children)

    return dedent(
        """
        <div class="problem">
            <div class="problem-body">
        {contents}
            </div>
        </div>
        """.strip(
            "\n"
        )
    ).format(contents=contents)


def _render_subproblem(node: ast.Subproblem, counter: int, render_child):
    contents = "\n".join(render_child(child) for child in node.children)

    return dedent(
        """
        <div class="subproblem">
            <h3 class="subproblem-id">Part {counter})</h3>
        {contents}
        </div>
        """.strip(
            "\n"
        )
    ).format(counter=counter, contents=contents)


# text ---------------------------------------------------------------------------------


@_renderer(ast.Text)
def _render_text(node: ast.Text, render_child):
    text = node.text
    if node.bold:
        text = f"<b>{text}</b>"
    if node.italic:
        text = f"<i>{text}</i>"
    return text


@_renderer(ast.Paragraph)
def _render_paragraph(node: ast.Paragraph, render_child):
    contents = "".join(render_child(child) for child in node.children)
    return f"<p>{contents}</p>"


# code ---------------------------------------------------------------------------------


@_renderer(ast.Code)
def _render_code(node: ast.Code, render_child):
    return dedent(
        """
            <pre class="code"><code>
            {code}
            </code></pre>
            """.strip(
            "\n"
        )
    ).format(code=node.code)


@_renderer(ast.InlineCode)
def _render_inlinecode(node: ast.InlineCode, render_child):
    return f'<span class="inline-code"><code>{node.code}</code></span>'


# math ---------------------------------------------------------------------------------


@_renderer(ast.InlineMath)
def _render_inlinemath(node: ast.InlineMath, render_child):
    return f'<span class="math">\\({node.latex}\\)</span>'


@_renderer(ast.DisplayMath)
def _render_displaymath(node: ast.DisplayMath, render_child):
    return f'<div class="math">\\[{node.latex}\\]</div>'


# solutions and response areas ---------------------------------------------------------


@_renderer(ast.TrueFalse)
def _render_truefalse(node: ast.TrueFalse, render_child):
    return dedent(
        """
        <div class="true-false">
            <input type="radio" name="true-false" value="true" /> True
            <input type="radio" name="true-false" value="false" /> False
        </div>
    """
    )


@_renderer(ast.Solution)
def _render_solution(node: ast.Solution, render_child):
    contents = "\n".join(render_child(child) for child in node.children)
    return dedent(
        """
        <details>
            <summary>Solution</summary>
        {contents}
        </details>
        """.strip(
            "\n"
        )
    ).format(contents=contents)


def _render_choice(node: ast.Choice, kind: str, render_child):
    contents = "\n".join(render_child(child) for child in node.children)
    # return f'<div class="choice"><input type="{kind}" />{contents}</div>'
    # place the checkbox/radio on the same line as the contents
    return f'<div class="choice"><label><input name="choice" class="choice" type="{kind}" />{contents}</label></div>'


@_renderer(ast.MultipleChoice)
def _render_multiplechoice(node: ast.MultipleChoice, render_child):
    # radio buttons
    contents = "\n".join(
        _render_choice(child, "radio", render_child) for child in node.children
    )
    return f'<div class="multiple-choices"><form>{contents}</form></div>'


@_renderer(ast.MultipleSelect)
def _render_multipleselect(node: ast.MultipleSelect, render_child):
    contents = "\n".join(
        _render_choice(child, "checkbox", render_child) for child in node.children
    )
    return f'<div class="multiple-select">{contents}</div>'


@_renderer(ast.InlineResponseBox)
def _render_inlineresponsebox(node: ast.InlineResponseBox, render_child):
    uuid = str(uuid4())

    answer = "\n".join(render_child(child) for child in node.children)

    return dedent(
        f"""
        <span class="inline-response-box">
            <span id="answer-{uuid}" style="display: none">{answer}</span>
            <span id="button-{uuid}">
                <button
                    type="button"
                    onclick="
                        document.getElementById('answer-{uuid}').style.display = 'inline-block';
                        document.getElementById('button-{uuid}').style.display = 'none'
                    "
                >
                    Show Answer
                </button>
            </span>
        </span>
        """
    )


# media --------------------------------------------------------------------------------


@_renderer(ast.ImageFile)
def _render_imagefile(node: ast.ImageFile, render_child):
    return (
        f'<center><div class="image"><img src="{node.relative_path}" /></div></center>'
    )


# render() =============================================================================


def render(problem: ast.Problem, overrides=None) -> str:
    """Render a problem to HTML.

    This renderer is capable of rendering all node types from
    :mod:`panprob.ast`, except for the special nodes :class:`panprob.ast.Blob`
    and :class:`panprob.ast.ParBreak`, which should not appear in the AST.

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
        The problem rendered as an HTML string.

    Raises
    ------
    RenderError
        If there is an issue rendering this tree, such as when an unkown AST
        node type is encountered.

    Notes
    -----
    A renderer function is called with two arguments:

        1. The node to render.
        2. A function that recursively renders a node to HTML by choosing the correct
           node renderer for each child node.

    It is expected to return an HTML string.

    """
    renderers = {**_RENDERERS, **(overrides or {})}

    def _render_node(node: ast.Node):
        if type(node) in renderers:
            return renderers[type(node)](node, _render_node)
        else:
            raise exceptions.RenderError(f"no HTML renderer for {type(node)}")

    return _render_node(problem)
