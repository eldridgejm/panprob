Extending `panprob`
===================

You can extend `panprob` by writing your own problem parser and/or renderer.
This section describes how to do that, starting with a description of the
abstract syntax tree (AST) that `panprob` uses to represent problems
internally. Your parser should take a problem in some format and convert it
into an AST, and your renderer should take an AST and convert it to text.

.. currentmodule:: panprob.ast

.. module:: panprob.ast

Abstract Syntax Trees
---------------------

Abstractly, a problem is made up of "components" such as images, paragraphs of
text, response areas, and so forth. Representing a problem as an AST of Python
objects does three things:

    1. It defines a canonical problem format, and consequently determines the
       common set of components that any problem format should support.
    2. It allows us to more easily manipulate problems programmatically.
    3. It saves us work when converting between one problem format to another.
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

Abstract Base Classes
^^^^^^^^^^^^^^^^^^^^^

Every node in the tree is a derivative of the :class:`Node` base class, which provides
some simple functionality that all nodes have in common: checking for equality, and
printing a human-readable representation.

.. autoclass:: Node
   :members: __eq__, __repr__, prettify

Internal nodes derive from :class:`InternalNode`:

.. autoclass:: InternalNode
   :members:

Leaf nodes derive from :class:`LeafNode`:

.. autoclass:: LeafNode
   :members:

Concrete Node Types
^^^^^^^^^^^^^^^^^^^

These node types represent problem components, such as paragraphs, response
areas, images, and so forth.

Problems
~~~~~~~~
.. autoclass:: Problem
.. autoclass:: Subproblem

Text
~~~~
.. autoclass:: Paragraph
.. autoclass:: Text
.. autoclass:: Blob
.. autoclass:: ParBreak

Math
~~~~
.. autoclass:: DisplayMath
.. autoclass:: InlineMath

Code
~~~~
.. autoclass:: Code
.. autoclass:: InlineCode
.. autoclass:: CodeFile

Media
~~~~~
.. autoclass:: ImageFile

Response Areas
~~~~~~~~~~~~~~
.. autoclass:: MultipleChoice
.. autoclass:: MultipleSelect
.. autoclass:: Choice
.. autoclass:: InlineResponseBox
.. autoclass:: Solution


Example
^^^^^^^

The below shows an example of creating an AST by hand:

.. code:: python

    ast.Problem(children=[
        ast.Paragraph(children=[
            ast.Text("Is 'hello world' a common test phrase?"),
        ]),
        ast.TrueFalse(True),
        ast.Solution(children=[
            ast.Paragraph(children=[
                ast.Text("Yes, it is. In fact, it is "),
                ast.Text("very", bold=True),
                ast.Text(" common."),
            ]),
        ]),
    ])

Writing a New Parser or Renderer
--------------------------------

If you have a new problem format that you want to convert to HTML or one of the
other formats that `panprob` supports, you can write a parser for it. A parser
is simply a function that takes a string as input and returns a
:class:`Problem` object as output. You can take a look at the source of the
existing parsers on `GitHub
<https://github.com/eldridgejm/panprob/tree/main/panprob/parsers>`_ for inspiration.

If the format you're writing a parser for is based on a standard markup (such
as LaTeX or Markdown), you can probably use an off-the-shelf parser for that
markup and then convert the resulting AST into a `panprob` AST. For example,
the Gradescope markdown parser uses the `marko` library to parse markdown, and
then converts the resulting AST into a `panprob` AST.

On the other hand, if you'd like to write a renderer for a new format, you can
do that too. A renderer is simply a function that takes a :class:`Problem`
object as input and returns a string as output. You can take a look at the
source of the existing renderers on `GitHub
<https://github.com/eldridgejm/panprob/tree/main/panprob/renderers>`_.
