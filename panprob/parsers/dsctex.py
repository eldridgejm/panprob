r"""Parser for problems written in LaTeX with the `DSCTeX` package.

A problem written with DSCTeX looks like the below:

.. code:: latex

    \begin{problem}
        What is the most famous building at UCSD?

        \begin{solution}
            Geisel Library, probably.
        \end{solution}
    \end{problem}

DSCTeX also supports multiple choice problems, True/False, etc.
See the `DSCTeX documentation <https://eldridgejm.github.io/dsctex>`_ for more
information about the source format.

"""

from dataclasses import dataclass
from typing import Union, List
import textwrap

import TexSoup

from .. import ast, util, postprocessors
from ..exceptions import ParseError


# To make it easy to extend, this module follows a two-step process to parse
# LaTeX into an AST of :mod:`panprob.ast` objects:
#
#     1. Parse the LaTeX source into a tree of Command, Environment, and str objects.
#     2. Convert each Command, Environment, and str object into an AST object
#        from :mod:`panprob.ast`.

# LaTeX AST ============================================================================

# The first step in parsing the LaTeX source into a panprob AST is to parse it into
# a "LaTeX AST" of Command, Environment, and str objects representing the component
# of the LaTeX source document. Unlike the panprob AST types, these types are very
# general, and can represent any arbitrary LaTeX commands and environments.

# The heavy-lifting of the parsing is done by the TexSoup package, and the Command
# and Environment types are just thin analogues of the TexSoup types TexSoup.TexCmd
# and TexSoup.TexEnv, but with much less functionality (so as to be easier to think
# about and to minimize the surface area of this module's public API).


@dataclass
class Command:
    r"""Represents a LaTeX command.

    Attributes
    ----------
    name: str
        The name of the command.
    args: List[Environment]
        The arguments to the command. Each entry will be an
        :class:`Environment` whose name is either "BraceGroup" or
        "BracketGroup", depending on whether the argument was a required
        argument or an optional argument, respectively.

    Example
    -------

    The LaTeX source :code:`\textbf{Hello}` will be parsed into a :class:`Command`
    object with name "textbf" and args:

    .. code:: python

        [
            Environment(
                name="BraceGroup",
                args=[],
                contents=[
                    "Hello",
                ],
                raw_contents="Hello"
            )
        ]

    For example, to access the text of the first argument.:

    .. code:: python

        cmd.args[0].raw_contents

    """

    name: str
    args: List["Environment"]


@dataclass
class Environment:
    """Represents a LaTeX environment.

    Attributes
    ----------
    name: str
        The name of the environment.
    args: List[Environment]
        The arguments to the environment. Each entry will be an Environment whose name
        is either "BraceGroup" or "BracketGroup", depending on whether the argument
        was a required argument or an optional argument, respectively.
    contents: List[Union[Command, Environment, str]]
        The contents of the environment as a list of parsed LaTeX objects.
    raw_contents: str
        The contents of the environment as a string of unparsed LaTeX.

    """

    name: str
    args: List["Environment"]
    contents: List[Union["Command", "Environment", str]]
    raw_contents: str


def _parse_source_into_latex_ast(latex: str) -> Environment:
    """Parse the LaTeX source into a tree of Command, Environment, and str objects.

    This function uses the TexSoup package to do the heavy lifting, but it returns
    simplified versions of the TexSoup types TexSoup.TexCmd and TexSoup.TexEnv.

    """

    soup = TexSoup.TexSoup(latex)

    def _ensure_environment(node) -> Environment:
        """Asserts that the node is an Environment and returns it."""
        assert isinstance(node, Environment)
        return node

    def _convert_soup_node(soup_node):
        """Convert a TexSoup node into a Command, Environment, or str object."""
        if isinstance(soup_node, str):
            return soup_node
        elif isinstance(soup_node, TexSoup.data.TexCmd):
            return Command(
                soup_node.name,
                args=[
                    _ensure_environment(_convert_soup_node(arg))
                    for arg in soup_node.args
                ],  # lsp: ignore
            )
        elif isinstance(soup_node, TexSoup.data.TexEnv):
            n_args = len(soup_node.args)
            return Environment(
                soup_node.name,
                args=[_convert_soup_node(arg) for arg in soup_node.args],
                contents=[
                    _convert_soup_node(child) for child in soup_node.contents[n_args:]
                ],
                raw_contents="".join(str(c) for c in soup_node.contents[n_args:]),
            )
        else:
            raise RuntimeError(f"Unknown TeXSoup type: {type(soup_node)}")

    return _ensure_environment(_convert_soup_node(soup.expr))


# Converters ===========================================================================

# In the first step of converting the LaTeX source into a panprob AST, the source
# text was converted to a tree of Command, Environment, and str objects. In the next
# step, we convert each of these objects into an AST object from panprob.ast. We do
# this by creating a "converter" function for each of the commands and environments
# that we want to support.

# A converter function is a function that takes two arguments:
#
#     1. A Command or Environment object to convert.
#     2. A callback function that can be used to convert the children of the
#        Command or Environment object.
#
# Command and environment names are mapped to their converter functions by the
# following dictionaries:

_ENV_CONVERTERS = {}
_CMD_CONVERTERS = {}

# To make it easier to register converters, we use the following decorators, which
# add the decorated function to the appropriate dictionary.


def _cmd_converter(name):
    """Add the converter to the _CMD_CONVERTERS dictionary."""

    def decorator(func):
        _CMD_CONVERTERS[name] = func
        return func

    return decorator


def _env_converter(name):
    """Add the converter to the _ENV_CONVERTERS dictionary."""

    def decorator(func):
        _ENV_CONVERTERS[name] = func
        return func

    return decorator


# problems and subproblems -------------------------------------------------------------


@_env_converter("prob")
def _convert_prob(env: Environment, convert):
    # in the panprob AST, subproblems are not contained in nodes representing
    # subprobsets, but are directly contained within Problems. Therefore,
    # instead of making a node for a subprobset, we "explode" the subprobset
    # into its subproblems and add them directly to the Problem node.
    def explode_subprobsets():
        """Yield all of the children of the problem, exploding subprobsets."""
        for child in env.contents:
            if isinstance(child, Environment) and child.name == "subprobset":
                for subprob in child.contents:
                    yield subprob
            else:
                yield child

    return ast.Problem(children=[convert(c) for c in explode_subprobsets()])


@_env_converter("subprob")
def _convert_subprob(env: Environment, convert):
    return ast.Subproblem(children=[convert(c) for c in env.contents])


# text formatting ----------------------------------------------------------------------


@_cmd_converter("textbf")
def _convert_textbf(cmd: Command, convert):
    return ast.Blob(children=[ast.Text(cmd.args[0].raw_contents, bold=True)])


@_cmd_converter("textit")
def _convert_textit(cmd: Command, convert):
    return ast.Blob(children=[ast.Text(cmd.args[0].raw_contents, italic=True)])


# math ---------------------------------------------------------------------------------


@_env_converter("$")
def _convert_inline_math(env: Environment, convert):
    return ast.Blob(children=[ast.InlineMath(env.raw_contents)])


@_env_converter("$$")
def _convert_double_dollar_math(env: Environment, convert):
    return ast.DisplayMath(env.raw_contents)


@_env_converter("displaymath")
def _convert_display_math(env: Environment, convert):
    return ast.DisplayMath(env.raw_contents)


# media --------------------------------------------------------------------------------


@_cmd_converter("includegraphics")
def _convert_includegraphics(cmd: Command, convert):
    return ast.ImageFile(relative_path=cmd.args[0].raw_contents)


# code ---------------------------------------------------------------------------------


@_env_converter("minted")
def _convert_minted(env: Environment, convert):
    return ast.Code(
        language=env.args[0].raw_contents, code=textwrap.dedent(env.raw_contents)
    )


@_cmd_converter("inputminted")
def _convert_inputminted(cmd: Command, convert):
    return ast.CodeFile(
        language=cmd.args[0].raw_contents, relative_path=cmd.args[1].raw_contents
    )


@_cmd_converter("mintinline")
def _convert_mintinline(cmd: Command, convert):
    return ast.Blob(
        children=[
            ast.InlineCode(
                language=cmd.args[0].raw_contents, code=cmd.args[1].raw_contents
            )
        ]
    )


# response areas and solutions ---------------------------------------------------------


@_env_converter("soln")
def _convert_soln(env: Environment, convert):
    return ast.Solution(children=[convert(c) for c in env.contents])


@_env_converter("choices")
def _convert_choices(env: Environment, convert):
    # there are three ways of writing the content of a choice:
    #
    #   1) inline, like: \choice This is a \textbf{choice}
    #   2) command-form, like:
    #
    #           \choice { This is a \textbf{choice} }
    #
    #   3) mixed, like:
    #
    #           \choice { This is a } \textbf{choice}
    #
    # The last one is odd, but it's a possibility...

    # The first type manifests as env.contents containing a list of objects, some of
    # them Choice commands and some of them representing the content of the choices:
    #
    #   [
    #       Command("\choice"),
    #       "This is a ",
    #       Command("textbf", args=[
    #           Environment(name="BraceGroup", contents=["choice"])
    #       ]),
    #       Command("\choice"),
    #       ...
    #   ]

    # The second type manifests as env.contents containing a list of Command objects
    # only, with the contents of the braces stored in the args of the command:
    #
    #   [
    #       Command("\choice", args=[
    #           Environment(name="BraceGroup", contents=[
    #               "This is a ",
    #               Command("textbf", args=[
    #                   Environment(name="BraceGroup", contents=["choice"])
    #               ])
    #           ])
    #       ]),
    #       ...
    #   ]

    # The third type manifests as env.contents containing a list of objects, some of
    # them Choice commands with args and some not:
    #
    #   [
    #       Command("\choice", args=[
    #           Environment(name="BraceGroup", contents=[
    #               "This is a ",
    #           ])
    #       ]),
    #       Command("textbf", args=[
    #           Environment(name="BraceGroup", contents=["choice"])
    #       ]),
    #       ...
    #   ]

    # The general strategy for parsing these is as follows:
    #
    #   1) group env.contents by choice nodes and non-choice nodes.
    #   2) for each choice node, start with an empty list of contents
    #       a) if the choice node has args, add them to the contents
    #       b) add all of the non-choice nodes to the contents, up until the next
    #          choice node

    is_choice = lambda n: isinstance(n, Command) and n.name in {
        "choice",
        "correctchoice",
    }
    choices = util.segment(env.contents, is_choice)

    # every segment starts with a Choice command and zero or more non-choice nodes
    # (strings, commands, environments, etc.)
    def make_choice_node(segment):
        choice_command, *rest = segment

        choice_children = []
        if choice_command.args:
            choice_children.extend(convert(c) for c in choice_command.args[0].contents)

        choice_children.extend(convert(c) for c in rest)

        correct = choice_command.name == "correctchoice"

        return ast.Choice(correct=correct, children=choice_children)

    choice_nodes = [make_choice_node(choice) for choice in choices]

    # and we finally put them all into an ast.MultipleChoice node:
    is_select_all = env.args and env.args[0].raw_contents == "rectangle"
    node_type = ast.MultipleSelect if is_select_all else ast.MultipleChoice
    return node_type(children=choice_nodes)


@_cmd_converter("Tf")
def _convert_Tf(cmd: Command, convert):
    return ast.TrueFalse(solution=True)


@_cmd_converter("tF")
def _convert_tF(cmd: Command, convert):
    return ast.TrueFalse(solution=False)


@_cmd_converter("inlineresponsebox")
def _convert_inlineresponsebox(cmd: Command, convert):
    contents = [convert(c) for c in cmd.args[-1].contents]

    # each child should be a Blob with a single child
    if not all(len(blob.children) == 1 for blob in contents):
        raise ParseError("inlineresponsebox contents must be a single paragraph")

    contents = [blob.children[0] for blob in contents]
    return ast.InlineResponseBox(children=contents)


# blobify ==============================================================================


def _blobify(s: str) -> ast.Blob:
    """Creates a :class:`Blob` from a string.

    This splits the string on double newlines, and creates a :class:`Text` node
    for each chunk, separated by :class:`ParBreak` nodes.

    Parameters
    ----------
    s : str
        The string to convert.

    Returns
    -------
    Blob
        The resulting blob.

    """
    chunks = iter(s.split("\n\n"))
    children = [ast.Text(next(chunks))]

    for chunk in chunks:
        children.append(ast.ParBreak())
        if not chunk.strip():
            continue
        children.append(ast.Text(chunk))

    return ast.Blob(children=children)


# parse() ==============================================================================


def parse(
    latex: str, command_converters=None, environment_converters=None
) -> ast.Problem:
    """Parses LaTeX source into an :class:`panprob.ast.Problem`.

    Parameters
    ----------
    latex : str
        The LaTeX source to parse.
    command_converters : dict, optional
        A dictionary mapping LaTeX command names to functions that convert them into
        panprob AST nodes. See below for the expected signature of these functions.
    environment_converters : dict, optional
        A dictionary mapping LaTeX environment names to functions that convert them
        into panprob AST nodes. See below for the expected signature of these

    Returns
    -------
    panprob.ast.Problem
        The parsed problem.

    Raises
    ------
    panprob.ParseError
        If the source cannot be parsed for some reason. For example, if it
        contains an unrecognized command or environment.

    Notes
    -----
    The default command and environment converters are defined in the
    :mod:`panprob.parsers.dsctex` module. The user can override these defaults
    (or provide their own converters) by passing in their own dictionaries of
    converters.

    Converter functions should accept two arguments: 1) the LaTeX
    :class:`Environment` or :class:`Command` node to convert, and 2) a function
    that can be used as a callback to recursively convert the children of the
    node, if necessary. The converter function should return a `panprob` AST
    node. See the documentation on extending `panprob` for examples.

    """

    command_converters = command_converters or {}
    environment_converters = environment_converters or {}

    # the first step is to parse the source text into a LaTeX AST of Command,
    # Environment, and str nodes:
    try:
        latex_ast = _parse_source_into_latex_ast(latex)
    except Exception as exc:
        raise ParseError(f"Could not parse LaTeX source. {exc}")

    # the only child of the root should be a problem environment
    try:
        [prob_node] = latex_ast.contents
    except ValueError:
        raise ParseError("The source must contain exactly one problem environment.")

    if not (isinstance(prob_node, Environment) and prob_node.name == "prob"):
        raise ParseError("The problem must be wrapped in a `prob` environment.")

    # next, we recursively convert these LaTeX nodes into panprob AST nodes.
    # default converters are defined above, but the user can override / extend them
    # by passing in their own converters:
    cmd_converters = {**_CMD_CONVERTERS, **command_converters}
    env_converters = {**_ENV_CONVERTERS, **environment_converters}

    # the convert() function recursively converts a LaTeX node into a panprob node.
    # it is passed to each converter, so that they can recursively convert their
    # children:
    def convert(latex_node: Union[Command, Environment, str]) -> ast.Node:
        if isinstance(latex_node, str):
            return _blobify(latex_node)
        elif isinstance(latex_node, Command):
            converters = cmd_converters
        elif isinstance(latex_node, Environment):
            converters = env_converters
        else:
            raise ParseError(f"Unknown type: {type(latex_node)}")

        if latex_node.name not in converters:
            msg = (
                "DSCTeX parser encountered unsupported LaTeX "
                f"{type(latex_node).__name__} '{latex_node.name}'"
            )
            raise ParseError(msg)

        # we pass this function to the converter so that it can recursively convert
        # its children:
        return converters[latex_node.name](latex_node, convert)

    tree = convert(prob_node)

    assert isinstance(tree, ast.Problem)
    tree = postprocessors.paragraphize(tree)
    assert isinstance(tree, ast.Problem)

    return tree
