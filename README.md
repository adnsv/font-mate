# font-mate

**font-mate** is a tool for font merging and coverage analysis. This tool allows you to merge multiple font files into one, using one font as the base and the rest as fallbacks, as well as analyze font coverage for different Unicode regions.

## Installation

To install **font-mate** directly from GitHub, you need Python 3.6 or higher and `pip`:

```sh
pip install git+https://github.com/adnsv/font-mate.git
```

## Usage

**font-mate** supports two main commands: `merge` and `coverage`.

### Show Application Version

To display the current version of **font-mate**:

```sh
font-mate --version
```

### Merging Fonts

The `merge` command allows you to merge multiple font files into one. The first file in the list is used as the base font, and the rest are added as fallbacks.

Example usage:

```sh
font-mate merge FONT1.ttf FONT2.ttf FONT3.ttf -o output.ttf --keep-non-bmp
```

Options:
- `FONT` — List of font files to merge. The first file is the base font, and the rest are fallbacks.
- `-o`, `--output` — The name of the output merged font file. If not specified, a default name based on the base font will be used.
- `--ufo-dir` — Directory to save the intermediate UFO representation of the font. If not specified, the UFO font will not be saved.
- `--keep-non-bmp` — Keep characters not in the Basic Multilingual Plane (BMP) in the final merged font. By default, such characters are removed.
- `--keep-all-ranges` — Keep glyphs for rarely used codepoint ranges. By default, glyphs in these ranges are removed to reduce the font size.

### Font Coverage Analysis

The `coverage` command analyzes a font and shows which Unicode regions are supported by the font.

Example usage:

```sh
font-mate coverage FONT.ttf
```

Options:
- `font` — Path to the font file to analyze for Unicode coverage.

## Dependencies

**font-mate** requires the following libraries:
- `fonttools` — for working with TTFont.
- `ufoLib2` — for working with UFO fonts.
- `ufo2ft` — for compiling UFO fonts to TTF/OTF.
- `setuptools_scm` — for version management of the project.

## License

The project is distributed under the MIT License. See the `LICENSE` file for details.

