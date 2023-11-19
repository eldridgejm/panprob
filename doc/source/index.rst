panprob
=======

`panprob` is a Python package for converting between different problem formats.
Currently, `panprob` can read problems written in `Gradescope-flavored markdown
<https://help.gradescope.com/article/gm5cmcz19k-instructor-assignment-online>`_
and `DSCTeX LaTeX <https://eldridgejm.github.io/dsctex>`_, and can render problems in
Gradescope-flavored markdown, DSCTeX, and HTML.

See the source code on `GitHub <https://github.com/eldridgejm/panprob>`_.



Usage
-----

From Python
^^^^^^^^^^^

For simply converting back and forth between formats, use the :func:`convert`
function:

.. autofunction:: panprob.convert

For more sophisticated use cases, see below.


Command Line
^^^^^^^^^^^^

You can also directly convert between problems from the command line:

.. code:: bash

   python -m panprob <input-file> <output-file>

The input and output formats will be inferred from the extensions.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   parsers.rst
   renderers.rst
   postprocessors.rst
   exceptions.rst
   ast.rst



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
