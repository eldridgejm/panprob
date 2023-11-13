Abstract Syntax Trees
=====================

.. currentmodule:: panprob.ast

.. automodule:: panprob.ast

Abstract Base Classes
---------------------

Every node in the tree is a derivative of the :class:`Node` base class, which provides
some simple functionality that all nodes have in common: checking for equality, and
printing a human-readable representation.

.. autoclass:: Node
   :members: __eq__, __repr__

Internal nodes derive from :class:`InternalNode`:

.. autoclass:: InternalNode
   :members:

Leaf nodes derive from :class:`LeafNode`:

.. autoclass:: LeafNode
   :members:

Concrete Nodes
--------------

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
-------

The below shows an example of creating an AST by hand. This is not the
recommended way to create an AST, but it is useful for understanding how the
AST works.

.. code:: python

    prob = ast.Problem()

    # create children and add them one-by-one
    para = ast.Paragraph()
    para.add_child(ast.Text('Is "hello world" a common test phrase?'))

    prob.add_child(para)
    prob.add_child(ast.TrueFalse("True"))

    # create children and add them all at once
    prob.add_child(ast.Solution(children=[
        ast.Text("Yes, it is. In fact, it is "),
        ast.Text("very", bold=True),
        ast.Text(" common."),
    ]))

Postprocessors
--------------

These "postprocessors" take an AST as input and (typically) modify it in some
way.

.. autofunction:: panprob.ast.postprocessors.paragraphize
.. autofunction:: panprob.ast.postprocessors.copy_images
.. autofunction:: panprob.ast.postprocessors.subsume_code
