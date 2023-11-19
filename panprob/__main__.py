"""CLI for converting between problem types."""

import argparse
import pathlib
import sys

from . import parsers, renderers, ast, exceptions


def cli():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("input", help="The input file to parse.", type=pathlib.Path)
    argparser.add_argument(
        "output", help="The output file to write to.", type=pathlib.Path
    )
    return argparser.parse_args()


EXT_TO_PARSER = {".tex": parsers.dsctex.parse, ".md": parsers.gsmd.parse}
EXT_TO_RENDERER = {
    ".html": renderers.html.render,
    ".tex": renderers.dsctex.render,
    ".md": renderers.gsmd.render,
}


def main():
    args = cli()

    parse = EXT_TO_PARSER[args.input.suffix]
    render = EXT_TO_RENDERER[args.output.suffix]

    with args.input.open() as f:
        contents = f.read()

    try:
        tree = parse(contents)
        out = render(tree)
    except exceptions.Error as exc:
        print("Error:", exc)
        sys.exit(1)
    except Exception as exc:
        print("There was an unexpected error:", exc)
        raise

    with args.output.open("w") as f:
        f.write(out)


if __name__ == "__main__":
    main()
