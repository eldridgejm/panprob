from panprob import convert

from textwrap import dedent


def test_convert():
    latex = dedent(
        r"""
        \begin{prob}
            This problem was originally written in LaTeX.
        \end{prob}
        """
    ).strip()

    md = convert(latex, parser="dsctex", renderer="gsmd")

    assert (
        md
        == dedent(
            r"""
        This problem was originally written in LaTeX.
        """
        ).strip()
    )
