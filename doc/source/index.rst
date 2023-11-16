.. panprob documentation master file, created by
   sphinx-quickstart on Sat Nov 11 18:09:02 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to panprob's documentation!
===================================

`panprob` is a Python package for converting between different problem formats.
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
   ast.rst



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
