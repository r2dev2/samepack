import argparse
import sys
from pathlib import Path

from samepack.build import build


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("entry", help="the entry point to the program")
    parser.add_argument(
        "-o",
        "--output",
        help="output file of bundle",
        default=None
    )

    args = parser.parse_args()
    bundle = build(Path(args.entry))
    if args.output is None:
        output = sys.stdout
    else:
        output = open(args.output, "w+")
    print(bundle, file=output)
    output.close()

