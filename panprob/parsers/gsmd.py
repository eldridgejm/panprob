"""Parses problems written in Gradescope-flavored Markdown.

Gradescope-flavored Markdown is an extension of Markdown used by Gradescope for
writing online quizzes. It provides support for LaTeX math, code blocks, and
various response area types, such as multiple choices, multiple selects, and
short answer boxes.

For details about this format, see the `Gradescope documentation
<https://help.gradescope.com/article/gm5cmcz19k-instructor-assignment-online>`_.

"""

from .. import ast, exceptions, postprocessors

import typing

import marko

# Parsing the markdown source into a tree of :mod:`panprob.ast` objects is a two-step
# process. First, we use the `marko <https://marko-py.readthedocs.io/en/latest/>`_
# library to parse the markdown source into an AST of marko nodes. Then, we convert
# this AST into an AST of :mod:`panprob.ast` nodes.

# In the :mod:`panprob.parsers.dsctex` module, we also adopted a two-step process, and
# we exposed the intermediate LaTeX AST to the user. We did this because users often
# implement custom LaTeX macros, and they need to be able to extend the LaTeX parser
# to support these macros. However, Gradescope-flavored Markdown does not support
# custom macros, so we don't need to expose the marko AST to the user. As such, it
# is a private implementation detail in this module.

# marko parser extensions ==============================================================

# We need to extend the marko parser to support non-standard Markdown features,
# such as LaTeX math and the Gradescope response area syntax. We do this by
# subclassing the :class:`marko.inline.InlineElement` and
# :class:`marko.block.BlockElement` classes and registering them with the marko
# parser.

# Extending marko is (lightly) documented here:
#
#   https://marko-py.readthedocs.io/en/latest/extend.html
#
# Inline extensions are straightforward, but it is less obvious how to
# implement a block extension. It is clear that each block extension needs to
# implement a ``match`` class method and a ``parse`` class method. The ``match``
# method is used to determine whether the block extension should be applied to
# the current line. The ``parse`` method is used to parse the block extension
# into a marko element.

# Both methods are passed an instance of a ``Source`` object, which is used to
# access the current line and consume lines from the source. As best I can
# tell, a ``Source`` object is a wrapper around a list of lines, and it acts
# like a "cursor", keeping track of where we are in the parsing of the source.
# A block element should "consume" lines from the source, effectively moving
# the cursor forward.


class _InlineMath(marko.inline.InlineElement):
    """A marko element for inline math, like $$f(x) = 42$$.

    Attributes
    ----------
    latex : str
        The LaTeX code to typeset.

    """

    pattern = r"\$\$(.+?)\$\$"  # don't be greedy!
    parse_children = False
    priority = 5

    def __init__(self, match):
        self.latex = match.group(1)


class _Solution(marko.block.BlockElement):
    """A marko element for a Gradescope explanation / solution.

    The Gradescope markdown syntax for a solution is:

        [[This is the solution]]

    It should be contained on a single line in the source.

    The contents of the solution are parsed recursively.

    Attributes
    ----------
    children : list of marko elements

    """

    def __init__(self, *args):
        self.children = []

    @classmethod
    def match(cls, source):
        return source.expect_re(r"\[\[(.+)\]\]")

    @classmethod
    def parse(cls, source):
        element = cls()
        match = source.match
        # the result of _MARKO_PARSER.parse should be a list with a single
        # element: a marko.block.Document object. Its children are the actual
        # contents of the solution:
        element.children = _MARKO_PARSER.parse(match.group(1)).children
        source.consume()
        return element


class _MultipleChoice(marko.block.BlockElement):
    """A marko element for a Gradescope multiple choice question.

    The Gradescope markdown syntax for a multiple choice question is:

        ( ) This is a choice
        ( ) This is another choice
        (x) This is the correct choice

    The choices should be contained on consecutive lines in the source.

    Attributes
    ----------
    choices : list of (marko element, bool) tuples
        Each tuple contains a marko element for the contents of the choice and
        a boolean indicating whether the choice is correct.

    """

    def __init__(self, choices):
        self.choices = choices

    @classmethod
    def match(cls, source):
        # when we see any line that starts with "( )" or "(x)", we assume it is
        # the start of a multiple choice question:
        next_line = source.next_line()
        return next_line.startswith("( )") or next_line.startswith("(x)")

    @classmethod
    def parse(cls, source):
        # consume all consecutive lines that start with "( )" or "(x)"
        choices = []
        while cls.match(source):
            choices.append(source.next_line())
            source.consume()

        def _make_choice(choice):
            # we parse the text of each choice using the marko parser. the
            # result of _MARKO_PARSER.parse should be a list with a single
            # element: a marko.block.Document object. Its children are the
            # actual contents of the choice:
            is_correct = choice.startswith("(x)")
            return (_MARKO_PARSER.parse(choice[3:]).children[0], is_correct)

        return cls(choices=[_make_choice(choice) for choice in choices])


class _MultipleSelect(marko.block.BlockElement):
    """A marko element for a Gradescope multiple select question.

    The Gradescope markdown syntax for a multiple select question is:

        [ ] This is a choice
        [x] This is a correct choice
        [x] This is another correct choice

    The choices should be contained on consecutive lines in the source.

    Attributes
    ----------
    choices : list of (marko element, bool) tuples
        Each tuple contains a marko element for the contents of the choice and
        a boolean indicating whether the choice is correct.

    """

    def __init__(self, choices):
        self.choices = choices

    @classmethod
    def match(cls, source):
        # when we see any line that starts with "[ ]" or "[x]", we assume it is
        # the start of a multiple select question:
        next_line = source.next_line()
        return next_line.startswith("[ ]") or next_line.startswith("[x]")

    @classmethod
    def parse(cls, source):
        # consume all consecutive lines that start with "[ ]" or "[x]"
        choices = []
        while cls.match(source):
            choices.append(source.next_line())
            source.consume()

        def _make_choice(choice):
            # we parse the text of each choice using the marko parser. the
            # result of _MARKO_PARSER.parse should be a list with a single
            # element: a marko.block.Document object. Its children are the
            # actual contents of the choice:
            is_correct = choice.startswith("[x]")
            return (_MARKO_PARSER.parse(choice[3:]).children[0], is_correct)

        return cls(choices=[_make_choice(choice) for choice in choices])


class _InlineResponseBox(marko.block.BlockElement):
    """A marko element for an inline response box.

    The Gradescope markdown syntax for an inline response box is:

        [____](This is the answer)

    The answer contents are parsed recursively.

    Attributes
    ----------
    answer : list of marko elements
        The parsed contents of the answer.

    """

    def __init__(self, answer):
        self.answer = answer

    @classmethod
    def match(cls, source):
        return source.expect_re(r"\[____\]\((.*)\)")

    @classmethod
    def parse(cls, source):
        answer = source.match.group(1)
        # the result of _MARKO_PARSER.parse should be a list with a single
        # element: a marko.block.Document object. Its only child should be a
        # marko Paragraph object, and its children are the actual contents of
        # the answer:
        try:
            children = _MARKO_PARSER.parse(answer).children[0].children
        except IndexError:
            raise exceptions.ParseError(
                "Inline response box does not contain an answer."
            )

        source.consume()
        return cls(children)


class _BlockImage(marko.block.BlockElement):
    """A marko element for a block image.

    The panprob AST does not support inline images. Therefore, we detect block
    images and handle them as expected, but we will later raise an error if we
    see an inline image.

    Attributes
    ----------
    relative_path : str
        The relative path to the image file.

    """

    def __init__(self, relative_path):
        self.relative_path = relative_path

    @classmethod
    def match(cls, source):
        return source.expect_re(r"\!\[(.*)\]\((.*)\)")

    @classmethod
    def parse(cls, source):
        match = source.match
        source.consume()
        return cls(match.group(2))


# parser setup -------------------------------------------------------------------------

_MARKO_PARSER = marko.parser.Parser()

_MARKO_PARSER.add_element(_InlineMath)
_MARKO_PARSER.add_element(_Solution)
_MARKO_PARSER.add_element(_MultipleChoice)
_MARKO_PARSER.add_element(_MultipleSelect)
_MARKO_PARSER.add_element(_InlineResponseBox)
_MARKO_PARSER.add_element(_BlockImage)

# converters ===========================================================================

# In the second step of the parsing process, we convert the marko elements into
# :mod:`panprob.ast` nodes. The converters are registered in a dictionary keyed
# by the marko element type:

_CONVERTERS = {}


def _converter(marko_element_type):
    """Decorator for registering a converter for a Marko node type."""

    def _decorator(func):
        _CONVERTERS[marko_element_type] = func
        return func

    return _decorator


# The key abstraction in this step is the "converter" function. A converter is
# a function that takes two arguments: a marko element and a function for
# recursively converting general marko elements into :mod:`panprob.ast` nodes.
# It should return a :mod:`panprob.ast` node.

# problems -----------------------------------------------------------------------------


@_converter(marko.block.Document)
def _convert_document(marko_element, convert):
    return ast.Problem(children=[convert(child) for child in marko_element.children])


# text ---------------------------------------------------------------------------------


@_converter(marko.block.BlankLine)
def _convert_blank_line(marko_element, convert):
    return ast.Blob(children=[])


@_converter(marko.inline.LineBreak)
def _convert_line_break(marko_element, convert):
    return ast.Blob(children=[])


@_converter(marko.block.Paragraph)
def _convert_paragraph(marko_element, convert):
    return ast.Paragraph(children=[convert(child) for child in marko_element.children])


@_converter(marko.inline.RawText)
def _convert_raw_text(marko_element, convert):
    child = ast.Text(marko_element.children)
    return ast.Blob(children=[child])


@_converter(marko.inline.Emphasis)
def _convert_emphasis(marko_element, convert):
    child = ast.Text(marko_element.children[0].children, italic=True)
    return ast.Blob(children=[child])


@_converter(marko.inline.StrongEmphasis)
def _convert_strong_emphasis(marko_element, convert):
    child = ast.Text(marko_element.children[0].children, bold=True)
    return ast.Blob(children=[child])


# code ---------------------------------------------------------------------------------


@_converter(marko.inline.CodeSpan)
def _convert_code_span(marko_element, convert):
    child = ast.InlineCode("text", marko_element.children)
    return ast.Blob(children=[child])


@_converter(marko.block.FencedCode)
def _convert_fenced_code(marko_element, convert):
    return ast.Code(marko_element.lang, marko_element.children[0].children)


# math ---------------------------------------------------------------------------------


@_converter(_InlineMath)
def _convert_inline_math(marko_element, convert):
    child = ast.InlineMath(marko_element.latex)
    return ast.Blob(children=[child])


# media --------------------------------------------------------------------------------


@_converter(_BlockImage)
def _convert_image(marko_element, convert):
    return ast.ImageFile(marko_element.relative_path)


@_converter(marko.inline.Image)
def _convert_inline_image(marko_element, convert):
    raise exceptions.ParseError("Inline images are not supported")


# response areas and solutions ---------------------------------------------------------


@_converter(_Solution)
def _convert_solution(marko_element, convert):
    return ast.Solution(children=[convert(child) for child in marko_element.children])


@_converter(_MultipleChoice)
def _convert_multiple_choices(marko_element, convert):
    def _make_choice(choice: typing.Tuple[marko.block.BlockElement, bool]):
        element, correct = choice
        return ast.Choice(
            children=[convert(child) for child in element.children], correct=correct
        )

    return ast.MultipleChoice(
        children=[_make_choice(choice) for choice in marko_element.choices]
    )


@_converter(_MultipleSelect)
def _convert_multiple_select(marko_element, convert):
    def _make_choice(choice: typing.Tuple[marko.block.BlockElement, bool]):
        element, correct = choice
        return ast.Choice(
            children=[convert(child) for child in element.children], correct=correct
        )

    choices = [_make_choice(choice) for choice in marko_element.choices]
    return ast.MultipleSelect(children=choices)


@_converter(_InlineResponseBox)
def _convert_inline_response_box(marko_element, convert):
    answer = [convert(child) for child in marko_element.answer]

    # the answer will be a list of blobs, each should have a single child
    if not all(len(blob.children) == 1 for blob in answer):
        raise exceptions.ParseError(
            "Inline response box answer should be a single paragraph"
        )

    answer = [blob.children[0] for blob in answer]

    def is_empty_text(node):
        return isinstance(node, ast.Text) and node.text.strip() == ""

    answer = [node for node in answer if not is_empty_text(node)]

    return ast.InlineResponseBox(children=answer)


# parser ===============================================================================


def parse(md: str) -> ast.Problem:
    """Parses Gradescope Markdown into a :class:`panprob.ast.Problem`.

    Arguments
    ---------
    md : str
        The Gradescope Markdown to parse.

    Returns
    -------
    ast.Problem
        The parsed problem.

    Raises
    ------
    panprob.exceptions.ParseError
        If the source cannot be parsed for some known reason.

    Notes
    -----

    This parser does not support inline images, such as:

    .. code-block:: markdown

        This is an image: ![alt text](path/to/image.png)

    Images should instead be placed on their own line. If an inline image is
    encountered, a :class:`panprob.exceptions.ParseError` will be raised.

    """
    marko_tree = _MARKO_PARSER.parse(md)

    def _convert_marko_element(marko_element):
        """Recursively convert a Marko node to an AST node."""
        if type(marko_element) not in _CONVERTERS:
            raise exceptions.ParseError(
                f"Gradescope markdown parser found unsupported node {marko_element}"
            )

        converter = _CONVERTERS[type(marko_element)]
        return converter(marko_element, _convert_marko_element)

    tree = _convert_marko_element(marko_tree)

    tree = postprocessors.paragraphize(tree)
    assert isinstance(tree, ast.Problem)
    return tree
