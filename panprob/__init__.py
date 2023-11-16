from . import ast, parsers, renderers, exceptions


_PARSERS = {
    "gsmd": parsers.gsmd.parse,
    "dsctex": parsers.dsctex.parse,
}

_RENDERERS = {
    "gsmd": renderers.gsmd.render,
    "dsctex": renderers.dsctex.render,
    "html": renderers.html.render,
}


def convert(source: str, parser: str, renderer: str) -> str:
    r"""Converts between problem formats.

    Arguments
    ---------
    source : str
        The source string to convert.
    parser : str
        The name of the parser to use. Can be one of: {"gsmd", "dsctex"}.
    renderer : str
        The name of the renderer to use. Can be one of: {"gsmd", "dsctex", "html"}.

    Returns
    -------
    str
        The converted string.

    For more control over the parsers and renderers, see the corresponding
    parts of the documentation.

    Example
    -------

    Choose a parser (`gsmd` for Gradescope Markdown or `dsctex` for
    `DSCTeX <https://eldridgejm.github.io/dsctex>`_)
    and a renderer (`gsmd` for Gradescope Markdown, `dsctex` for DSCTeX, or `html` for HTML)
    and pass them along with the problem source to `panprob.convert`:

    .. code:: python

        In [1]: import panprob

        In [2]: source = '''
           ...: This problem was originally written in Gradescope Markdown.
           ...:
           ...: (x) True
           ...: ( ) False
           ...: '''

        In [3]: panprob.convert(source, parser="gsmd", renderer="dsctex")

    The result is the LaTeX below:

    .. code:: tex

        \begin{prob}

            This problem was originally written in Gradescope Markdown.

            \begin{choices}
                \correctchoice {
                    True
                }
                \choice {
                    False
                }
            \end{choices}

        \end{prob}


    """
    if parser not in _PARSERS:
        raise ValueError(f"Unknown parser: {parser}. Choose from: {list(_PARSERS)}")

    if renderer not in _RENDERERS:
        raise ValueError(
            f"Unknown renderer: {renderer}. Choose from: {list(_RENDERERS)}"
        )

    tree = _PARSERS[parser](source)
    tree = ast.postprocessors.paragraphize(tree)
    return _RENDERERS[renderer](tree)
