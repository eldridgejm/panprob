from abc import ABC
import typing

from ..exceptions import IllegalChild

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

        return {k: v for k, v in self.__dict__.items() if is_public_attribute(k, v)}

    def __eq__(self, other):
        """Determine if this node is equal to the other."""
        if not isinstance(other, type(self)):
            return False

        return self._attrs == other._attrs

    def __repr__(self):
        """Human-readable representation of this node."""
        return f"{type(self).__name__}({self.__dict__!r})"


class InternalNode(Node):
    """ABC for an internal node in the AST.

    Attributes
    ----------
    children : tuple of Node
        The children of this node.
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

    def add_child(self, node: Node):
        """Add a child node, checking to see if it's a valid type.

        Parameters
        ----------
        node : Node
            The node to add.

        Raises
        ------
        IllegalChild
            If the child is not a valid type for this parent.

        """
        self.children = (*self.children, self._check_child_type(node))


class LeafNode(Node):
    """ABC for a leaf node in the AST."""


# AST node types =======================================================================

# problems and subproblems -------------------------------------------------------------


class Problem(InternalNode):
    """A problem.

    Can contain the following node types:

    - Subproblem
    - Code
    - DisplayMath
    - ImageFile
    - MultipleChoice
    - MultipleSelect
    - TrueFalse
    - Solution
    - Text
    - InlineMath
    - InlineCode
    - Paragraph

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

    - Text
    - InlineMath
    - InlineCode
    - ImageFile

    """


class Text(LeafNode):
    """Text, optionally bold, and/or italic.

    A leaf node.

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

    Can contain Choice nodes.

    """


class MultipleSelect(InternalNode):
    """A select-all-that-apply area in a question.

    Can contain Choice nodes.

    """


class Choice(InternalNode):
    """A choice within a multiple choice question.

    Can contain the following node types:

    - Text
    - InlineMath
    - DisplayMath
    - Code
    - InlineCode
    - CodeFile
    - ImageFile
    - Paragraph

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

    - Text
    - InlineMath
    - InlineCode

    """


class Solution(InternalNode):
    """A solution to a problem.

    Can contain all of the same types as a :class:`Solution` node.

    """


# allowed child types ==================================================================

Problem.allowed_child_types = (
    Subproblem,
    Code,
    CodeFile,
    DisplayMath,
    ImageFile,
    MultipleChoice,
    MultipleSelect,
    TrueFalse,
    InlineResponseBox,
    Solution,
    Text,
    InlineMath,
    InlineCode,
    Paragraph,
)

Paragraph.allowed_child_types = (
    Text,
    InlineMath,
    InlineCode,
    InlineResponseBox,
    ImageFile,
)

# do not allow subproblems to contain subproblems
Subproblem.allowed_child_types = Problem.allowed_child_types[1:]

MultipleChoice.allowed_child_types = (Choice,)

MultipleSelect.allowed_child_types = (Choice,)

Choice.allowed_child_types = (
    Text,
    InlineMath,
    DisplayMath,
    Code,
    InlineCode,
    CodeFile,
    ImageFile,
    Paragraph,
)

Solution.allowed_child_types = Choice.allowed_child_types

InlineResponseBox.allowed_child_types = (Text, InlineMath, InlineCode)
