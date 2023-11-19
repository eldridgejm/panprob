class Error(Exception):
    """Base class for exceptions in this module."""


class ParseError(Error):
    """Raised when a parser encounters an error."""


class RenderError(Error):
    """Raised when a renderer encounters an error."""


class IllegalChild(Error):
    """Raised when attempting to add a child node of a disallowed type to a parent node.

    Arguments
    ---------
    parent : ast.Node
        The parent node.
    child : ast.Node
        The child node that is being added to the parent node.

    """

    def __init__(self, parent, child):
        self.parent = parent
        self.child = child

    def __str__(self):
        return f"Cannot add child of type {type(self.child)} to {type(self.parent)}."
