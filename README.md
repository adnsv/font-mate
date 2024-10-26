# font-mate

**font-mate** is a command-line tool for merging font files and analyzing their Unicode coverage. It allows you to merge multiple font files into one, using one font as the base and others as fallbacks, as well as analyze which Unicode regions are supported by a given font.

## Features

- **Font Merging**: Combine multiple font files into a single output file, using one as the base and others as fallbacks.
- **Unicode Coverage Analysis**: Generate detailed reports on which Unicode regions are supported by a given font.

## Installation

To install **font-mate** directly from GitHub, use the following command:

```sh
pip install git+https://github.com/adnsv/font-mate.git
```

### Prerequisites

- Python 3.6 or higher
- pip (Python package manager)

### Dependencies

**font-mate** requires the following libraries:

- `fonttools` — for working with TTFont files.
- `ufoLib2` — for working with UFO fonts.
- `ufo2ft` — for compiling UFO fonts to TTF/OTF.
- `setuptools_scm` — for version management of the project.

## Usage

**font-mate** has two main commands: `merge` and `coverage`.

### Show Version

To display the current version of **font-mate**:

```sh
font-mate --version
```

### Merge Fonts

The `merge` command merges multiple font files into a single output file. The first file in the list is used as the base font, and the rest are treated as fallbacks.

**Usage**:

```sh
font-mate merge FONT [FONT ...] [-o OUTPUT] [--ufo-dir UFO_DIR] [--keep-non-bmp] [--keep-all-ranges] [--remove-empty-glyphs] [--remove-dangling-glyphs]
```

**Options**:

- `FONT [FONT ...]`: List of font files to merge. The first file is the base font, and the rest are fallbacks.
- `-o, --output`: (Optional) Output file name for the merged font. If not specified, a default name based on the base font will be used.
- `--ufo-dir`: (Optional) Directory to save the intermediate UFO font representation. If not specified, the UFO font will not be saved.
- `--keep-non-bmp`: (Optional) Keep non-BMP (Basic Multilingual Plane) codepoints in the final merged font. By default, non-BMP codepoints are removed.
- `--keep-all-ranges`: (Optional) Keep glyphs for rarely used codepoint ranges. By default, glyphs in these ranges are removed to reduce font size.
- `--remove-empty-glyphs`: (Optional) Remove empty glyphs (glyphs with no contours) from the final merged font.
- `--remove-dangling-glyphs`: (Optional) Remove dangling glyphs (glyphs that are not used or mapped to any Unicode codepoints).

### Analyze Font Coverage

The `coverage` command analyzes a font's Unicode coverage, showing which Unicode regions are supported.

**Usage**:

```sh
font-mate coverage FONT [-o OUTPUT]
```

**Options**:

- `FONT`: Path to the font file to analyze for Unicode coverage.
- `-o, --output`: (Optional) Path to save the coverage report. If not specified, the output will be printed to stdout.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

### Notice for Apache-Licensed Dependencies

This project uses dependencies under the Apache License. See the [APACHE_NOTICE](APACHE_NOTICE) file for more information.

