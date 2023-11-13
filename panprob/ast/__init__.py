"""Types for representing a problem as an Abstract Syntax Tree.

Abstractly, a problem is made up of "components" such as images, paragraphs of
text, response areas, and so forth. Representing a problem as an AST of Python
objects does three things:

    1) It defines a canonical problem format, and consequently determines the
    common set of components that any problem format should support.

    2) It allows us to more easily manipulate problems programmatically.

    3) It saves us work when converting between one problem format to another.
    Instead of writing a separate "transformer" for every combination of source
    format and output format, we only need to write a parser for each input
    format and a renderer for each output format.

Each node in the AST represents a component of a problem, such as an image, a
response area, a paragraph of text, and so forth. This module provides Python
types for every component that can be part of a problem: types such as
`Problem`, `Subproblem`, `Paragraph`, `Image`, `MultipleChoices`, and so forth.

Some problem components, like problems, paragraphs, etc., can contain other
problem components. The nodes representing these components in the AST are
therefore "internal nodes", and they can have children. Other problem
components, like images, inline code, etc., cannot contain other problem
components. The nodes representing these components in the AST are therefore
"leaf nodes", and they cannot have children.

Problem components that act as containers for other components cannot
necessarily contain every other type of component. For example, an option in
a multiple choice problem cannot contain a subproblem. To enforce this, each
internal node type has a list of the types of nodes that it can contain. When
the AST is constructed, the parser checks to make sure that child nodes are
valid for their parent nodes -- if not, an exception is raised.

"""
from ._types import *
from . import  postprocessors
