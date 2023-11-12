"""Postprocessor that inserts Paragraph nodes into the AST."""

from typing import Sequence, List, Union
import itertools
import copy

from .._types import Text, InlineMath, InlineCode, Paragraph, InternalNode


TextLikeNode = Union[Text, InlineMath, InlineCode]


def _create_paragraphs_from_textlike_nodes(
    nodes: Sequence[TextLikeNode],
) -> List[Paragraph]:
    """Creates paragraphs out of a sequence of nodes that can be in paragraphs.

    Given a sequence of "text-like" nodes that can be in paragraphs, we need to merge
    some of them into the same paragraph, while splitting others into multiple
    paragraphs.

    For example, if we have a sequence of nodes like:

        - Text("This is a ")
        - Text("bold", bold=True)
        - Text(" paragraph with math: ")
        - InlineMath("x^2 + y^2 = z^2")

    We need to combine these four nodes under one paragraph. But in the following sequence
    we must split the text node into two paragraphs:

        - Text("This is a paragraph.\n\nAnd this is another.")

    Returns
    -------
    List[Paragraph]
        A list of paragraph objects.

    """
    # our first step is to "split" text nodes containing multiple paragraphs into multiple
    # nodes. We'll keep track of where the split was made by using a sentinel object,
    # `parbreak`:
    parbreak = object()

    # first, we create a helper function to split a single node into a list of nodes
    # and parbreaks:
    def _insert_parbreaks(node: Text) -> List[Union[Text, object]]:
        """Takes a text node and looks for paragraph breaks.

        Returns a list of text nodes interspersed with `parbreak` objects
        representing paragraph breaks. If there are no paragraph breaks, the
        list will contain a single text node.

        """
        paragraphs = node.text.split("\n\n")
        if len(paragraphs) == 1:
            return [node]

        nodes = []
        for paragraph in paragraphs:
            nodes.append(Text(paragraph))
            nodes.append(parbreak)
        nodes.pop()  # remove the last break

        return nodes

    # now we do the splitting. the result of this will be an expanded list of
    # nodes with `parbreak` objects interspersed.
    nodes_after_splitting = []
    for node in nodes:
        # only text nodes can be split (inline math and code nodes can't)
        if isinstance(node, Text):
            for split_node in _insert_parbreaks(node):
                nodes_after_splitting.append(split_node)
        else:
            nodes_after_splitting.append(node)

    # now we have a list of the form [Text, InlineCode, parbreak, Text, ...]
    # we group this by splitting on the parbreaks:
    groups = itertools.groupby(nodes_after_splitting, lambda n: n is parbreak)

    # each group where the key is False is a group of nodes that should be merged
    # into a single paragraph.
    paragraphs = []
    for is_break, nodes in groups:
        if not is_break:
            paragraphs.append(Paragraph(children=list(nodes)))

    return paragraphs


def paragraphize(node: InternalNode) -> InternalNode:
    r"""Creates a new AST with :class:`Paragraph` nodes inserted where appropriate.


    Parameters
    ----------
    node : InternalNode
        The root node of the AST.

    Returns
    -------
    InternalNode
        A new AST with Paragraph nodes inserted.

    Notes
    -----

    In some input formats, like LaTeX, paragraphs are not explicitly marked.
    This makes it difficult for parsers to know where paragraphs begin and end,
    and thus where to insert Paragraph nodes into the AST. This postprocessor
    attempts to do that post hoc.

    For example, a Problem node could have the children:

    - `Text("This is the first ")`
    - `Text("problem", bold=True)`
    - `Text(" in the assignment.\\n\\n")`
    - `Text("It is worth 10 points.")`
    - `Solution(...)`

    We want to merge the first three nodes into a single paragraph node. The last
    Text node is in a separate paragraph (due to the "\\n\\n"), so we'll create
    a second paragraph node for that. So the result will be

    .. code:: text

        - Paragraph(
                children=[
                    Text("This is the first "),
                    Text("problem", bold=True),
                    Text(" in the assignment."),
                    ]
                )
        - Paragraph(
                children=[
                    Text("It is worth 10 points."),
                    ]
                )
        - Solution(...)

    This function performs the fix recursively on the tree, producing a new
    tree with the same general structure but with paragraph nodes added.

    """

    # first, we look through the children of this internal node for nodes which
    # can be contained in a paragraph (these are Text, InlineMath, and
    # InlineCode). Paragraph nodes will be created for each contiguous group of
    # such nodes. But we only need to do this if the node isn't already contained
    # in a paragraph.
    def should_go_in_paragraph(child):
        return not isinstance(node, Paragraph) and isinstance(
            child, Paragraph.allowed_child_types
        )

    groups = itertools.groupby(node.children, should_go_in_paragraph)

    # the children that will be in the new node. we'll populate this as we go.
    new_children = []

    for is_allowed_in_paragraph, children in groups:
        if is_allowed_in_paragraph:
            new_children.extend(_create_paragraphs_from_textlike_nodes(children))
        else:
            for child in children:
                # we only recuriively call paragraphize on internal nodes.
                # we know at this point that `child` is not allowed in a paragraph,
                # but it could be a leaf node, so we check for that here.
                if isinstance(child, InternalNode):
                    child = paragraphize(child)
                new_children.append(child)

    result = copy.copy(node)
    result.children = tuple(new_children)
    return result
