import copy
import pathlib

from ..ast import Node, InternalNode, CodeFile, Code


def subsume_code(node: Node, root: pathlib.Path) -> Node:
    """Replaces all :class:`CodeFile` nodes in the AST with :class:`Code` nodes
    by reading the code from disk.

    Parameters
    ----------
    node : Node
        The node to transform.
    root : pathlib.Path
        The path to the root directory. All relative paths in the AST are
        assumed to be relative to this path.

    Returns
    -------
    Node
        The transformed node with the code subsumed. Does not modify the
        original node.

    """
    if isinstance(node, CodeFile):
        with (root / node.relative_path).open() as fileob:
            code = fileob.read()
        return Code(node.language, code)
    elif isinstance(node, InternalNode):
        node = copy.copy(node)
        node.children = tuple(subsume_code(child, root) for child in node.children)
        return node
    else:
        return copy.copy(node)
