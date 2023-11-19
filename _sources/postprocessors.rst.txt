Postprocessors
==============

These "postprocessors" take an AST as input and (typically) modify it in some
way. They can be useful for making changes to the AST after parsing, or for
writing parsers themselves.

Subsume Code
------------

Sometimes it is useful to replace all :class:`panprob.ast.CodeFile` nodes
(which are simply references to a code file) with the contents of the code
file. This can be done with the following function:

.. autofunction:: panprob.postprocessors.subsume_code

Copy Images
-----------

A common use case for `panprob` is to convert all of the problems in one
directory, placing the output in another directory. If the problems contain
images, then the images will need to be copied to the output directory as well.
This can be done with the following function (which doesn't actually modify the
AST):

.. autofunction:: panprob.postprocessors.copy_images

Paragraphize
------------

A postprocessor that is most useful for writing simpler parsers.

:class:`Text` and inline content, such as :class:`InlineMath`,
:class:`InlineCode`, and :class:`InlineResponseBox`, cannot appear directly
under, e.g., a :class:`Problem` in an AST; they must instead be contained
within a :class:`Paragraph`. However, it can be difficult for the parser to
know where a paragraph should be created during parse time. Rather, it is
often easier to infer this *post hoc*, after the full AST has been built.

The :class:`Blob` special node type exists to enable such a *post hoc*
approach to creating paragraphs. Instead of placing text directly into a
:class:`Paragraph` during parsing, the parser puts one or more pieces of
text into a :class:`Blob`. Then, after the AST has been created, a
post-processing step is run that converts all :class:`Blob` nodes into
:class:`Paragraph` nodes by merging or splitting them as necessary. This
post-processing step is implemented in the
:func:`panprob.postprocessors.paragraphize` function:

.. autofunction:: panprob.postprocessors.paragraphize
