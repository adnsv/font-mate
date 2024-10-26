import argparse
from importlib.metadata import version, PackageNotFoundError

from impl import merge_fonts, coverage_analysis

# Get version dynamically from setuptools_scm
try:
    VERSION = version("font-mate")
except PackageNotFoundError:
    VERSION = "0.0.0"


def main():
    parser = argparse.ArgumentParser(
        description="font-mate: A tool for font merging and coverage analysis."
    )
    parser.add_argument(
        '--version', '-v',
        action='version',
        version=f'font-mate {VERSION}',
        help='Show the version number of the font-mate tool and exit.'
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands:")

    # Merge subcommand
    merge_parser = subparsers.add_parser(
        "merge",
        help="Merge multiple font files into a single font, with the first font as the base and others as fallbacks."
    )
    merge_parser.add_argument(
        "fonts",
        metavar="FONT",
        type=str,
        nargs="+",
        help="List of font files to merge. The first file is the base font, and the rest are fallbacks."
    )
    merge_parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file name for the merged font. If not specified, a default name will be used based on the base font name."
    )
    merge_parser.add_argument(
        "--ufo-dir",
        type=str,
        help="Directory to save the intermediate UFO font representation. If not specified, the UFO font will not be saved."
    )
    merge_parser.add_argument(
        "--keep-non-bmp",
        action="store_true",
        help="Keep non-BMP (Basic Multilingual Plane) codepoints in the final merged font. By default, non-BMP codepoints are removed."
    )
    merge_parser.add_argument(
        "--keep-all-ranges",
        action="store_true",
        help="Keep glyphs for rarely used codepoint ranges. By default, glyphs in these ranges are removed to reduce font size."
    )

    # Coverage subcommand
    coverage_parser = subparsers.add_parser(
        "coverage",
        help="Analyze the coverage of a font, detailing which Unicode regions are supported."
    )
    coverage_parser.add_argument(
        "font",
        type=str,
        help="Path to the font file to analyze for Unicode coverage."
    )
    coverage_parser.add_argument(
      "-o", "--output",
      type=str,
      help="Path to save the coverage report. If not specified, the output will be printed to stdout."
    )

    args = parser.parse_args()

    if args.command == "merge":
        merge_fonts(
            font_paths=args.fonts,
            output=args.output,
            ufo_dir=args.ufo_dir,
            keep_non_bmp=args.keep_non_bmp,
            keep_all_ranges=args.keep_all_ranges
        )
    elif args.command == "coverage":
        coverage_analysis(args.font, output_file=args.output)


if __name__ == "__main__":
    main()
