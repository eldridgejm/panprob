Renderers
=========

As described in the previous section, `panprob` converts problems by first
*parsing* them into an intermediate format (an abstract syntax tree, or AST)
and then *rendering* that tree into the desired output format. The renderers
provided by `panprob` are described below.

.. currentmodule:: panprob.renderers

HTML
----

.. automodule:: panprob.renderers.html

.. autofunction:: render

DSCTeX
------

.. automodule:: panprob.renderers.dsctex

.. autofunction:: render

Gradescope Markdown
-------------------

.. automodule:: panprob.renderers.gsmd

.. autofunction:: render
