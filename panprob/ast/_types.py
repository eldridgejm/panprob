from abc import ABC
import typing
import re
from textwrap import dedent, indent

from ..exceptions import IllegalChild, Error

# abstract base classes ================================================================


class Node(ABC):
    """ABC for a node in the AST."""

    @property
    def _attrs(self):
        """Return a dictionary of the node's public attributes.

        More formally, a "public attribute" is an entry in the instance
        dictionary whose key does not start with an underscore and whose value
        is not callable.

        """

        def is_public_attribute(k, v):
            return not k.startswith("_") and not callable(v)

        attrs = {k: v for k, v in self.__dict__.items() if is_public_attribute(k, v)}

        return attrs

    def __eq__(self, other):
        raise NotImplementedError

    def prettify(self) -> str:
        """Return a pretty-printed string representation of the node."""
        raise NotImplementedError


class InternalNode(Node):
    """ABC for an internal node in the AST.

    Attributes
    ----------
    allowed_child_types : tuple of type
        The types of nodes that this node can contain.

    """

    allowed_child_types = tuple()

    def __init__(self, *, children: typing.Optional[typing.Iterable[Node]] = None):
        if children is None:
            self.children = tuple()
        else:
            self.children = tuple(self._check_child_type(child) for child in children)

    def _check_child_type(self, child: Node):
        """Check if the child node is a valid type."""
        if not isinstance(child, self.allowed_child_types):
            raise IllegalChild(self, child)
        return child

    @property
    def children(self) -> typing.Tuple[Node]:
        """The children of this node.

        This attribute can be set in the usual way:

        .. code-block:: python

            node.children = (child1, child2, ...)

        When it is set, each child is checked to ensure that it is a valid type for this
        node. If it is not, an :class:`panprob.exceptions.IllegalChild`
        exception is raised.

        """
        return self._children

    @children.setter
    def children(self, children: typing.Sequence[Node]):
        """Set the children of this node.

        Performs error checking to ensure that each child is a valid type for this node.

        """
        self._children = tuple(self._check_child_type(child) for child in children)

    def __eq__(self, other) -> bool:
        """Determine if this node is equal to the other."""
        if not isinstance(self, type(other)):
            return False

        return self._attrs == other._attrs and self.children == other.children

    def __repr__(self):
        """Human-readable representation of this node."""
        return f"{type(self).__name__}(children={self.children!r})"

    def prettify(self) -> str:
        """Return a pretty string representation of the node."""
        children = ", \n".join(child.prettify() for child in self.children)
        children = indent(children, "    " * 2)
        typename = type(self).__name__
        return (
            dedent(
                """
            {typename}(children=[
            {children}
                ]
            )
            """.strip(
                    "\n"
                )
            )
            .format(children=children, typename=typename)
            .strip()
        )


class LeafNode(Node):
    """ABC for a leaf node in the AST."""

    def __repr__(self):
        """Human-readable representation of this node."""
        kwargs = ", ".join(f"{k}={v!r}" for k, v in self._attrs.items())
        return f"{type(self).__name__}({kwargs})"

    def __eq__(self, other):
        """Determine if this node is equal to the other."""
        if not isinstance(self, type(other)):
            return False

        return self._attrs == other._attrs

    def prettify(self):
        """Return a pretty string representation of the node."""
        kwargs = ", ".join(f"{k}={v!r}" for k, v in self._attrs.items())
        return f"{type(self).__name__}({kwargs})"


# AST node types =======================================================================

# problems and subproblems -------------------------------------------------------------


class Problem(InternalNode):
    """A problem.

    Can contain the following node types:

    - :class:`Subproblem`
    - :class:`Paragraph`
    - :class:`Blob`
    - :class:`DisplayMath`
    - :class:`Code`
    - :class:`ImageFile`
    - :class:`Solution`
    - :class:`MultipleChoice`
    - :class:`MultipleSelect`
    - :class:`TrueFalse`

    """


class Subproblem(InternalNode):
    """A subproblem within a problem.

    Allowed to contain everything that a :class:`Problem` is allowed to
    contain, except for other subproblems.

    """


# text ---------------------------------------------------------------------------------


class Paragraph(InternalNode):
    """A paragraph of text.

    Can contain the following node types:

    - :class:`Blob`
    - :class:`Text`
    - :class:`InlineMath`
    - :class:`InlineCode`
    - :class:`InlineResponseBox`

    It can be difficult for the parser to know where a paragraph should be
    created during parse time. Rather, it is often easier to infer this *post
    hoc*, after the full AST has been built. This can be done by placing text into
    :class:`Blob` nodes at parse time, and then converting them into
    :class:`Paragraph` nodes with the :func:`panprob.postprocessors.paragraphize`
    function; see their documentation for more details.

    """


class Blob(InternalNode):
    r"""
    A special node type that is used to hold inline content that should be
    placed into a :class:`Paragraph` after the AST has been built. Parsers
    should remove all :class:`Blob` nodes from the AST after parsing and before
    returning the AST to the caller. Renderers should not expect to encounter
    any :class:`Blob` nodes in the AST.

    :class:`Text` and inline content, such as :class:`InlineMath`,
    :class:`InlineCode`, and :class:`InlineResponseBox`, cannot appear directly
    under, e.g., a :class:`Problem` in an AST; they must instead be contained
    within a :class:`Paragraph`. However, it can be difficult for the parser to
    know where a paragraph should be created during parse time. Rather, it is
    often easier to infer this *post hoc*, after the full AST has been built.

    The :class:`Blob` special node type exists to enable such a *post hoc*
    approach to creating paragraphs. Instead of placing text directly into a
    :class:`Paragraph` during parsing, the parser puts one or more pieces of
    text into a :class:`Blob`. Then, after the AST has been created, a
    post-processing step is run that converts all :class:`Blob` nodes into
    :class:`Paragraph` nodes by merging or splitting them as necessary. This
    post-processing step is implemented in the
    :func:`panprob.postprocessors.paragraphize` function.

    A :class:`Blob` node can have one or more children. A forced paragraph
    break is indicated by a :class:`ParBreak` node. For example, the string

    .. code:: latex

        This is a single paragraph.

        And this is another.

    Can be represented in a :class:`Blob` as:

    .. code:: python

        Blob(children=[
            Text("This is a single paragraph."),
            ParBreak(),
            Text("And this is another.")
        ])

    A :class:`Blob` can contain the following node types:

    - :class:`Text`
    - :class:`InlineMath`
    - :class:`InlineCode`
    - :class:`InlineResponseBox`
    - :class:`ParBreak`

    Example
    -------

    For an example of where one might use a :class:`Blob`, consider the LaTeX
    string:

    .. code:: latex

        This is a \textbf{single} paragraph.

        And this is another.

    A LaTeX parser may parse this in three pieces: 1) a string containing the
    text :code:`"This is a "`, 2) an inline node containing the
    :code:`\\textbf{single}` command, and 3) a string containing the rest:
    :code:`"paragraph\\n\\nAnd this is another."`. In the final AST, we want these three pieces
    to be in *two* paragraphs: the first containing three :class:`Text`
    nodes for :code:`"This is a"`, :code:`"single"` (in bold), and :code:`"paragraph."`,
    and the second paragraph consisting of a single :class:`Text` node for
    :code:`"And this is another."`.

    Instead of inferring these two paragraphs during parsing, the parser
    instead might create three :class:`Blob` nodes: one for each piece of text
    produced by the parser. During postprocessing, the blobs will be "exploded"
    into their consituents which are then re-formed into paragraphs as necessary.

    When placing text into a :class:`Blob`, the parser should break the text
    into pieces at paragraph breaks. In this example, the first blob will
    contain a single child node: a :class:`Text` node containing the text
    :code:`"This is a "`. The second blob will contain a single child node: a
    :class:`Text` node containing the text :code:`"single"` (in bold). The
    third blob will contain two child nodes: a :class:`Text` node containing
    the text :code:`"paragraph."` and a :class:`Text` node containing the text
    :code:`"And this is another."`.

    """


class ParBreak(LeafNode):
    """A paragraph break.

    This special node is meant to only be used in :class:`Blob` nodes. It
    is not meant to be used in the final AST that is returned to the caller.

    """


class Text(LeafNode):
    """Text, optionally bold and/or italic.

    Upon passing the text to the constructor, all newlines are replaced with
    spaces. All repeated whitespace is replaced with a single space.

    The text cannot be empty, and it cannot only be whitespace. If either of
    these conditions are violated, an :class:`Error` will be raised.

    A :class:`Text` node is a leaf node.

    Attributes
    ----------
    text : str
        The text.
    bold : bool
        If the text should be bold.
    italic : bool
        If the text should be italic.

    """

    def __init__(self, text, bold=False, italic=False):
        super().__init__()

        if not text:
            raise Error("Text cannot be empty.")

        # replace all repeated whitespace with a single space.
        # this also has the effect of replacing all newlines with spaces.
        text = re.sub(r"\s+", " ", text)

        if not text.strip():
            raise Error("Text cannot contain only whitespace.")

        self.text = text
        self.bold = bold
        self.italic = italic


# math ---------------------------------------------------------------------------------


class DisplayMath(LeafNode):
    """A block of text that should be typeset as display math.

    A leaf node.

    Attributes
    ----------
    latex : str
        The LaTeX code to typeset.

    """

    def __init__(self, latex: str):
        super().__init__()
        self.latex = latex


class InlineMath(LeafNode):
    """A block of text that should be typeset as inline math.

    A leaf node.

    Attributes
    ----------
    latex : str
        The LaTeX code to typeset.

    """

    def __init__(self, latex: str):
        super().__init__()
        self.latex = latex


class AlignMath(LeafNode):
    """A block of aligned equations using the align environment.

    A leaf node.

    Attributes
    ----------
    latex : str
        The LaTeX code to typeset (contents of the align environment).
    starred : bool
        If True, uses align* (unnumbered). If False, uses align (numbered).

    """

    def __init__(self, latex: str, starred: bool = False):
        super().__init__()
        self.latex = latex
        self.starred = starred


# code ---------------------------------------------------------------------------------


class Code(LeafNode):
    """A block of code.

    A leaf node.

    Attributes
    ----------
    language : str
        The language of the code. This is used to determine the syntax
        highlighting.
    code : str
        The code.

    """

    def __init__(self, language: str, code: str):
        super().__init__()
        self.language = language
        self.code = code


class InlineCode(LeafNode):
    """A block of code, displayed inline.

    A leaf node.

    Attributes
    ----------
    language : str
        The language of the code. This is used to determine the syntax
        highlighting.
    code : str
        The code.

    """

    def __init__(self, language: str, code: str):
        super().__init__()
        self.language = language
        self.code = code


class CodeFile(LeafNode):
    """A reference to an external code file.

    A leaf node.

    Attributes
    ----------
    language : str
        The language of the code. This is used to determine the syntax
        highlighting.
    relative_path : str
        The relative path to the code file.

    """

    def __init__(self, language: str, relative_path: str):
        super().__init__()
        self.language = language
        self.relative_path = relative_path


class ImageFile(LeafNode):
    """A reference to an image file.

    A leaf node.

    Attributes
    ----------
    relative_path : str
        The relative path to the image.

    """

    def __init__(self, relative_path: str):
        super().__init__()
        self.relative_path = relative_path


# response areas and solutions ---------------------------------------------------------


class MultipleChoice(InternalNode):
    """A multiple choice area.

    Can contain :class:`Choice` nodes.

    """


class MultipleSelect(InternalNode):
    """A select-all-that-apply area in a question.

    Can contain :class:`Choice` nodes.

    """


class Choice(InternalNode):
    """A choice within a multiple choice question.

    Can contain the following node types:

    - :class:`Paragraph`
    - :class:`Blob`
    - :class:`ImageFile`
    - :class:`Code`
    - :class:`CodeFile`
    - :class:`DisplayMath`

    Attributes
    ----------
    correct : bool
        Whether or not this choice is correct.

    """

    def __init__(self, *, correct=False, children=None):
        super().__init__(children=children)
        self.correct = correct


class TrueFalse(LeafNode):
    """A true/false question.

    A leaf node.

    Attributes
    ----------
    solution : bool
        The solution to the question.

    """

    def __init__(self, solution: bool):
        super().__init__()
        self.solution = solution


class InlineResponseBox(InternalNode):
    """An inline response box.

    Can contain the following node types:

    - :class:`Text`
    - :class:`InlineMath`
    - :class:`InlineCode`

    """


class Solution(InternalNode):
    """A solution to a problem.

    Can contain all of the same types as a :class:`Solution` node.

    - :class:`Blob`
    - :class:`Paragraph`
    - :class:`Code`
    - :class:`CodeFile`
    - :class:`DisplayMath`
    - :class:`ImageFile`

    """


# allowed child types ==================================================================

Problem.allowed_child_types = (
    Subproblem,
    Blob,
    Paragraph,
    Code,
    CodeFile,
    DisplayMath,
    AlignMath,
    ImageFile,
    MultipleChoice,
    MultipleSelect,
    TrueFalse,
    InlineResponseBox,
    Solution,
)

Paragraph.allowed_child_types = (Text, InlineMath, InlineCode, InlineResponseBox, Blob)

# do not allow subproblems to contain subproblems
Subproblem.allowed_child_types = Problem.allowed_child_types[1:]

MultipleChoice.allowed_child_types = (Choice,)

MultipleSelect.allowed_child_types = (Choice,)

Choice.allowed_child_types = (
    Blob,
    Paragraph,
    ImageFile,
    Code,
    CodeFile,
    DisplayMath,
    AlignMath,
)

Solution.allowed_child_types = (
    Blob,
    Paragraph,
    Code,
    CodeFile,
    DisplayMath,
    AlignMath,
    ImageFile,
)

InlineResponseBox.allowed_child_types = (Text, InlineMath, InlineCode)

Blob.allowed_child_types = (Text, InlineMath, InlineCode, InlineResponseBox, ParBreak)
