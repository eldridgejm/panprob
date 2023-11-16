Parsers
=======

`panprob` converts problems by first *parsing* them into an intermediate format (an
abstract syntax tree, or AST) and then *rendering* that tree into the desired output
format. The parsers provided by `panprob` are documented below.

Note that most use cases do not require instantiating a parsers directly. Instead,
you should use the :func:`panprob.convert` function, which does parsing and rendering
in one step.

DSCTeX
------

.. currentmodule:: panprob.parsers.dsctex

.. automodule:: panprob.parsers.dsctex

The main functionality of the module is provided by the :func:`parse` function:

.. autofunction:: parse

The environments understood by the parser are:

- :code:`$` and :code:`$$` for inline and display math, respectively.
- :code:`\\begin{prob}` .. :code:`\\end{prob}` environments for problems.
- :code:`\\begin{subprob}` .. :code:`\\end{subprob}` environments for subproblems.
- :code:`\\begin{minted}` .. :code:`\\end{minted}` environments for code.
- :code:`\\begin{soln}` .. :code:`\\end{soln}` environments for solutions.
- :code:`\\begin{choices}` .. :code:`\\end{choices}` environments for multiple-choice questions.
- :code:`\\begin{choices}[rectangle]` .. :code:`\\end{choices}` environments for select-all-that-apply questions.

The commands understood by the parser are:

- :code:`\\textbf` for bold text.
- :code:`\\textit` for italic text.
- :code:`\\includegraphics` for images.
- :code:`\\inputminted` for code.
- :code:`\\mintinline` for inline code.
- :code:`\\Tf` for true/false questions (whose answer is True).
- :code:`\\tF` for true/false questions (whose answer is False).

The default command and environment converters are defined in the
:mod:`panprob.parsers.dsctex.converters` module.


Custom Commands and Environments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because it is common when writing LaTeX to define custom commands and
environments, this parser is designed to be easily extensible. Before extending
it, though, it's useful to understand a little about how the parser works.

The first step taken by the parser is to convert the LaTeX source into a tree
of :class:`Command`, :class:`Environment`, and `str` objects. These objects
represent pieces of the LaTeX document, and are documented below:

.. autoclass:: Command
.. autoclass:: Environment

Once this tree representing the LaTeX document has been constructed, the parser
then walks through it, looking for commands and environments that it knows how
to "convert" to :class:`panprob.ast` nodes. This module defines numerous
"converter" functions for this purpose, but you can define your own, overriding
or extending the defaults.

In short, a "converter" is a function that takes two arguments:

1. a :class:`Command` or :class:`Environment` object.
2. a callback function that can be used to convert the children of the node

It should return a node type from :class:`panprob.ast`.

Example - :code:`\\python` command
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Suppose your LaTeX source uses a custom command called :code:`\\python` to
represent inline Python code. This is not one of the default converters, but
you can define a converter function to convert this command to a
:class:`panprob.ast.InlineCode` node and pass it to :func:`parse`:

.. code-block:: python

    from panprob.ast import InlineCode

    def convert_python(node, children):
        return ast.InlineCode("python", "this")

    latex = r"\python{x = 3 + 4}"

    tree = parse(latex, command_converters={"python": convert_python})

Gradescope Markdown
-------------------

.. currentmodule:: panprob.parsers.gsmd

.. automodule:: panprob.parsers.gsmd

The main functionality of the module is provided by the :func:`parse` function:

.. autofunction:: parse
