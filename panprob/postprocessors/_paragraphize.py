"""Postprocessor that inserts Paragraph nodes into the AST."""

import itertools
import copy
import typing

from ..ast import Text, Paragraph, Node, InternalNode, Blob, ParBreak

# The algorithm in this module is best explained by an abstract example.
# Suppose we're given an InternalNode with the following children:
#
#     [Blob(I, PB, I), I, NI, I]
#
# where I is a node that's allowed in paragraphs, NI is a node that's not allowed in
# paragraphs, and PB is a ParBreak node. The algorithm is as follows:
#
# 1. "Explode" the blobs into their children. This gives us:
#
#     [I, PB, I, I, NI, I]
#
# 2. Find contiguous groups of nodes that are and aren't allowed in
#    paragraphs. This gives us:
#
#     [[I], [PB] [I, I], [NI], [I]]
#
# 3. Create a new list of children by iterating over the groups. If the group is
#    allowed in paragraphs, create a new paragraph node and add it to the list of
#    children. Otherwise, if the group is not allowed in paragraphs, add each node
#    in the group to the list of children, one-by-one (except for ParBreak nodes).
#    This gives us:
#
#     [Paragraph([I]), Paragraph([I, I]), NI, Paragraph([I])]
#
# 4. Recursively paragraphize each child that is an InternalNode.


def _fixup_paragraph_spacing(paragraph: Paragraph) -> Paragraph:
    """Removes spaces at the beginning and end of paragraphs."""
    paragraph = copy.copy(paragraph)
    paragraph.children = tuple(copy.copy(child) for child in paragraph.children)

    if isinstance(paragraph.children[0], Text):
        paragraph.children[0].text = paragraph.children[0].text.lstrip()

    if isinstance(paragraph.children[-1], Text):
        paragraph.children[-1].text = paragraph.children[-1].text.rstrip()

    return paragraph


def paragraphize(node: InternalNode) -> InternalNode:
    """Recursively creates :class:`Paragraph` nodes from :class:`Blob` nodes.

    :class:`Blob` nodes may contain :class:`ParBreak` nodes, representing
    forced paragraph breaks.

    As a side effect, this removes leading and trailing spaces from the paragraph.

    Arguments
    ---------
    node: panprob.ast.InternalNode
        The node to paragraphize.

    Returns
    -------
    panprob.ast.InternalNode
        The paragraphized node. The original node is not modified.

    Example
    -------

    Suppose we have the following tree:

    .. code-block:: python

        Problem(children=[
            Blob(children=[
                Text("This is a paragraph."),
                ParBreak(),
                Text("This is another paragraph with ")
            ]),
            Blob(children=[
                Text("two", bold=True),
            ]),
            Blob(children=[
                Text(" sentences."),
            ])
        ])

    Though this tree has three :class:`Blob` nodes, it represents two paragraphs.

    When we run :func:`paragraphize` on this tree, we get the result below:

    .. code-block:: python

        Problem(children=[
            Paragraph(children=[
                Text("This is a paragraph."),
            ]),
            Paragraph(children=[
                Text("This is another paragraph with "),
                Text("two", bold=True),
                Text(" sentences."),
            ])
        )

    """

    # STEP 1: explode blobs into their children
    def explode_blobs(children: typing.Sequence[Node]):
        for node in children:
            if isinstance(node, Blob):
                yield from node.children
            else:
                yield node

    children = explode_blobs(node.children)

    # STEP 2: find contiguous groups of nodes that are and aren't allowed in paragraphs
    def should_go_in_paragraph(child):
        return (
            # if this node can't contain paragraphs, then we shouldn't paragraphize it
            # though we should still paragraphize its children
            Paragraph in node.allowed_child_types
            and isinstance(child, Paragraph.allowed_child_types)
        )

    groups = itertools.groupby(children, should_go_in_paragraph)

    # STEP 3: create paragraphs
    new_children = []
    for is_allowed_in_paragraph, children in groups:
        if is_allowed_in_paragraph:
            paragraph = _fixup_paragraph_spacing(Paragraph(children=children))
            new_children.append(paragraph)
        else:
            new_children.extend(c for c in children if not isinstance(c, ParBreak))

    # STEP 4: recursively paragraphize each child that is an InternalNode
    for i, child in enumerate(new_children):
        if isinstance(child, InternalNode):
            new_children[i] = paragraphize(child)

    new_node = copy.copy(node)
    new_node.children = tuple(new_children)
    return new_node
