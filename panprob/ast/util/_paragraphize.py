_TextLikeNode = typing.Union[
    ast.NormalText,
    ast.BoldText,
    ast.ItalicText,
    ast.InlineMath,
    ast.InlineCode,
]


def _paragraphize_textlike_nodes(
    nodes: typing.Sequence[_TextLikeNode],
) -> typing.List[ast.Paragraph]:
    """Creates paragraphs out of a sequence of nodes that can be in paragraphs.

    Given a sequence of "text-like" nodes that can be in paragraphs, we need to merge
    some of them into the same paragraph, while splitting others into multiple
    paragraphs.

    For example, if we have a sequence of nodes like:

        - NormalText("This is a ")
        - BoldText("bold")
        - NormalText(" paragraph with math: ")
        - InlineMath("x^2 + y^2 = z^2")

    We need to combine these four nodes under one paragraph. But in the following sequence
    we must split the text node into two paragraphs:

        - NormalText("This is a paragraph.\n\nAnd this is another.")

    This is necessary because TexSoup does not split different paragraphs into
    different nodes. Instead, it puts them all into one node, separated by two
    newlines. We need to split this node into two separate nodes.

    Returns
    -------
    List[ast.Paragraph]
        A list of paragraph objects.

    """
    # our first step is to "split" text nodes containing multiple paragraphs into multiple
    # nodes. We'll keep track of where the split was made by using a sentinel object,
    # `parbreak`:
    parbreak = object()

    # first, we create a helper function to split a single node into a list of nodes
    # and parbreaks:
    def _split_text_node_into_paragraphs(node):
        """Takes a text node and looks for paragraph breaks.

        Returns a list of text nodes. The list will contain `parbreak` objects to
        represent paragraph breaks. If there are no paragraph breaks, the list
        will contain a single text node.

        """
        paragraphs = node.text.split("\n\n")
        if len(paragraphs) == 1:
            return [node]

        nodes = []
        for paragraph in paragraphs:
            nodes.append(type(node)(paragraph))
            nodes.append(parbreak)
        nodes.pop()  # remove the last break

        return nodes

    # now we do the splitting. the result of this will be an expanded list of
    # nodes with `parbreak` objects interspersed.
    nodes_after_splitting = []
    for node in nodes:
        # only text nodes can be split (inline math and code nodes can't)
        if isinstance(node, ast._TextNode):
            for split_node in _split_text_node_into_paragraphs(node):
                nodes_after_splitting.append(split_node)
        else:
            nodes_after_splitting.append(node)

    # now we have a list of the form [NormalText, BoldText, parbreak, NormalText, ...]
    # we group this by splitting on the parbreaks:
    groups = itertools.groupby(nodes_after_splitting, lambda n: n is parbreak)

    # each group where the key is False is a group of nodes that should be merged
    # into a single paragraph.
    paragraphs = []
    for is_break, nodes in groups:
        if not is_break:
            paragraphs.append(ast.Paragraph(children=list(nodes)))
    return paragraphs


def _paragraphize(node: ast.InternalNode):
    """Creates paragraph nodes, where appropriate.

    TexSoup does not have the concept of paragraphs. Therefore, after constructing
    the tree, we need to do some post-processing to create paragraph nodes out of
    text nodes that should be split or merged.

    For example, a Prob node could have children:

        - NormalText("This is the first ")
        - BoldText("problem")
        - NormalText(" in the assignment.\n\n")
        - NormalText("It is worth 10 points.")
        - Solution(...)

    We want to merge the first three nodes into a single paragraph node. The last
    NormalText node is in a separate paragraph (due to the "\n\n"), so we'll create
    a second paragraph node for that. So the result will be

        - Paragraph(
                children=[
                    NormalText("This is the first "),
                    BoldText("problem"),
                    NormalText(" in the assignment."),
                    ]
                )
        - Paragraph(
                children=[
                    NormalText("It is worth 10 points."),
                    ]
                )
        - Solution(...)

    This function performs the fix recursively on the tree, producing a new
    tree with the same general structure but with paragraph nodes added.

    """

    node_with_paragraphs = copy.copy(node)
    node_with_paragraphs.children = []

    # some of the children will be text-like (NormalText, InlineMath, etc.), and need
    # to be grouped into paragraphs. Others, like Solution, should not be grouped.
    groups = itertools.groupby(
        node.children, lambda n: isinstance(n, ast.Paragraph.allowed_child_types)
    )

    # each group where the key is True is a group of nodes that could be merged
    # into a single paragraph; we do this with _paragraphize_textlike_nodes
    # each group where the key is False is a group of nodes that should not be
    # merged into a paragraph and can simply be inserted into the tree as-is. These
    # are the nodes that can be recursively processed with _paragraphize.
    for is_allowed_in_paragraph, nodes in groups:
        if is_allowed_in_paragraph:
            for paragraph in _paragraphize_textlike_nodes(nodes):
                node_with_paragraphs.add_child(paragraph)
        else:
            for node in nodes:
                # `node` could still be a leaf node at this point; if so, we don't need
                # to paragraphize it
                if isinstance(node, ast.InternalNode):
                    node = _paragraphize(node)
                node_with_paragraphs.add_child(node)

    return node_with_paragraphs
