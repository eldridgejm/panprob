"""CLI for converting between problem types."""

import argparse
import pathlib

from . import parsers, renderers, ast


def cli():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("input", help="The input file to parse.", type=pathlib.Path)
    argparser.add_argument(
        "output", help="The output file to write to.", type=pathlib.Path
    )
    return argparser.parse_args()


EXT_TO_PARSER = {".tex": parsers.dsctex.parse}
EXT_TO_RENDERER = {".html": renderers.html.render}


def main():
    args = cli()

    parse = EXT_TO_PARSER[args.input.suffix]
    render = EXT_TO_RENDERER[args.output.suffix]

    with args.input.open() as f:
        tree = parse(f.read())

    tree = ast.postprocessors.paragraphize(tree)

    with args.output.open("w") as f:
        f.write(render(tree))


if __name__ == "__main__":
    main()
