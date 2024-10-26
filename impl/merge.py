from fontTools.ttLib import TTFont
import ufoLib2
from ufo2ft import compileTTF
from pathlib import Path
import shutil
from collections import defaultdict

from .utils import (
    print_progress_bar,
    convert_ttfont_to_ufo,
)

codepoint_ranges_to_remove = [
    (0x0250, 0x02AF),  # IPA Extensions
    (0x0300, 0x036F),  # Combining Diacritical Marks
    (0x0500, 0x052F),  # Cyrillic Supplement
    (0x0900, 0x097F),  # Devanagari
    (0x10A0, 0x10FF),  # Georgian
    (0x1100, 0x11FF),  # Hangul Jamo
    (0x1AB0, 0x1AFF),  # Combining Diacritical Marks Extended
    (0x1C80, 0x1C8F),  # Cyrillic Extended C
    (0x1D00, 0x1D7F),  # Phonetic Extensions
    (0x1D80, 0x1DBF),  # Phonetic Extensions Supplement
    (0x1DC0, 0x1DFF),  # Combining Diacritical Marks Supplement
    (0x1E00, 0x1EFF),  # Latin Extended Additional
    (0x1F00, 0x1FFF),  # Greek Extended
    (0x2400, 0x243F),  # Control Pictures
    (0x2700, 0x27BF),  # Dingbats
    (0x2900, 0x297F),  # Supplemental Arrows B
    (0x2980, 0x29FF),  # Miscellaneous Mathematical Symbols B
    (0x2B00, 0x2BFF),  # Miscellaneous Symbols and Arrows
    (0x2C60, 0x2C7F),  # Latin Extended C
    (0x2DE0, 0x2DFF),  # Cyrillic Extended A
    (0x2E00, 0x2E7F),  # Supplemental Punctuation
    (0x2E80, 0x2EFF),  # CJK Radicals Supplement
    (0x2F00, 0x2FDF),  # Kangxi Radicals
    (0x2FF0, 0x2FFF),  # Ideographic Description Characters
    (0x3190, 0x319F),  # Kanbun
    (0x31A0, 0x31BF),  # Bopomofo Extended
    (0x31C0, 0x31EF),  # CJK Strokes
    (0x31F0, 0x31FF),  # Katakana Phonetic Extensions
    (0xA700, 0xA71F),  # Modifier Tone Letters
    (0xA720, 0xA7FF),  # Latin Extended D
    (0xA8E0, 0xA8FF),  # Devanagari Extended
    (0xA900, 0xA92F),  # Kayah Li
    (0xA960, 0xA97F),  # Hangul Jamo Extended A
    (0xAB30, 0xAB6F),  # Latin Extended E
    (0xD7B0, 0xD7FF),  # Hangul Jamo Extended B
    (0xFB00, 0xFB4F),  # Alphabetic Presentation Forms
    (0xFE00, 0xFE0F),  # Variation Selectors
    (0xFE10, 0xFE1F),  # Vertical Forms
    (0xFE20, 0xFE2F),  # Combining Half Marks
    (0xFE70, 0xFEFF),  # Arabic Presentation Forms B
    (0xFFF0, 0xFFFF),  # Specials
]


def merge_ufo_fonts(base_font: ufoLib2.Font, merge_font: ufoLib2.Font):
    """Merges the second UFO font into the base font, avoiding duplicates and handling composites."""
    # Track existing glyphs in the base font
    existing_glyphs = set(base_font.keys())

    referenced_unicodes = set()
    for glyph in base_font:
        referenced_unicodes.update(glyph.unicodes)

    # Get total number of glyphs for progress tracking
    total_glyphs = len(merge_font.keys())
    print(f"Merging {total_glyphs} glyphs...")

    # Add glyphs from the merge font, avoiding duplicates, with progress tracking
    for i, glyph_name in enumerate(merge_font.keys(), start=1):
        merge_glyph = merge_font[glyph_name]

        # Check for glyph name collision
        if glyph_name in existing_glyphs:
            continue

        # Check for Unicode collisions
        if any(codepoint in referenced_unicodes for codepoint in merge_glyph.unicodes):
            continue

        base_font.addGlyph(merge_glyph)
        existing_glyphs.add(glyph_name)
        referenced_unicodes.update(merge_glyph.unicodes)

        # Print progress every 10 glyphs or at the end
        if i % 100 == 0 or i == total_glyphs:
            print_progress_bar(i, total_glyphs)

    print()  # Move to a new line after progress bar completes

    # Ensure composite glyphs reference existing base glyphs
    total_composites = len(base_font.keys())
    print(f"Fixing composite glyphs ({total_composites} glyphs)...")

    for i, glyph_name in enumerate(base_font.keys(), start=1):
        glyph = base_font[glyph_name]
        for component in glyph.components:
            base_glyph_name = component.baseGlyph
            if base_glyph_name not in base_font:
                if base_glyph_name in merge_font:
                    base_font.addGlyph(merge_font[base_glyph_name])

        # Print progress every 10 glyphs or at the end
        if i % 1000 == 0 or i == total_composites:
            print_progress_bar(i, total_composites)

    print()  # Move to a new line after progress bar completes


def is_codepoint_in_ranges(codepoint: int, ranges: list[tuple[int, int]]) -> bool:
    """Check if a codepoint falls within any of the specified ranges."""
    return any(start <= codepoint <= end for start, end in ranges)


def build_component_reference_map(ufo_font: ufoLib2.Font) -> defaultdict[str, list[str]]:
    """Builds a map of glyphs referenced by composite glyphs."""
    component_references = defaultdict(list)
    for glyph_name in ufo_font.keys():
        glyph = ufo_font[glyph_name]
        for component in glyph.components:
            component_references[component.baseGlyph].append(glyph_name)
    return component_references


def remove_glyphs_in_ranges(ufo_font: ufoLib2.Font, ranges: list[tuple[int, int]]):
    # First Pass: Collect all glyphs that need to be removed based on codepoint ranges
    total_glyphs = len(ufo_font)
    glyphs_to_remove = set()

    print(f"Analyzing {total_glyphs} glyphs for removal...")
    for i, glyph_name in enumerate(list(ufo_font.keys()), start=1):
        glyph = ufo_font[glyph_name]

        # Identify codepoints in the removal ranges
        codepoints_to_remove = [cp for cp in glyph.unicodes if is_codepoint_in_ranges(cp, ranges)]

        if not codepoints_to_remove:
            print_progress_bar(i, total_glyphs)
            continue

        # Remove only the specified codepoints or mark the glyph for removal if no codepoints remain
        if len(glyph.unicodes) > len(codepoints_to_remove):
            glyph.unicodes = [cp for cp in glyph.unicodes if cp not in codepoints_to_remove]
        else:
            glyphs_to_remove.add(glyph_name)

        # Update the progress bar
        print_progress_bar(i, total_glyphs)

    print()  # Ensure the next output starts on a new line

    # Second Pass: Identify composite references and adjust glyphs to remove accordingly
    print("Resolving composite references...")
    component_references = build_component_reference_map(ufo_font)
    for glyph_name, references in component_references.items():
        if glyph_name in glyphs_to_remove:
            continue
        # If a base glyph is marked for removal, but it is referenced by a composite not marked for removal,
        # retain the base glyph
        references_to_keep = [ref for ref in references if ref not in glyphs_to_remove]
        if not references_to_keep:
            glyphs_to_remove.add(glyph_name)

    # Third Pass: Perform the actual removal of glyphs
    total_to_remove = len(glyphs_to_remove)
    print(f"Removing {total_to_remove} glyphs...")
    for i, glyph_name in enumerate(glyphs_to_remove, start=1):
        del ufo_font[glyph_name]
        # Update the progress bar
        print_progress_bar(i, total_to_remove)

    print()  # Ensure the next output starts on a new line


def clean_non_bmp_glyphs(ufo_font: ufoLib2.Font):
    """Removes non-BMP codepoints from glyphs and deletes glyphs with only non-BMP codepoints."""
    total_glyphs = len(ufo_font)
    glyphs_to_remove = []  # Collect glyphs to be removed
    print(f"Cleaning non-BMP codepoints from {total_glyphs} glyphs...")

    # Iterate over glyphs and clean unicodes
    for i, glyph_name in enumerate(list(ufo_font.keys()), start=1):  # Use list to avoid modifying while iterating
        glyph = ufo_font[glyph_name]

        # Keep only BMP codepoints
        glyph.unicodes = [cp for cp in glyph.unicodes if cp <= 0xFFFF]

        # If no BMP codepoints remain, mark the glyph for removal
        if not glyph.unicodes:
            glyphs_to_remove.append(glyph_name)

        # Update progress every 100 glyphs or at the end
        if i % 100 == 0 or i == total_glyphs:
            print_progress_bar(i, total_glyphs)

    print()  # Ensure the next output starts on a new line

    # Remove glyphs that only referenced non-BMP codepoints
    print(f"Removing {len(glyphs_to_remove)} glyphs with only non-BMP codepoints...")
    for i, glyph_name in enumerate(glyphs_to_remove, start=1):
        del ufo_font[glyph_name]

        # Update progress every 100 glyphs or at the end
        if i % 100 == 0 or i == len(glyphs_to_remove):
            print_progress_bar(i, len(glyphs_to_remove))

    print()  # Ensure the next output starts on a new line


def calculate_glyph_counts(ufo_font: ufoLib2.Font) -> tuple[int, int, int]:
    """
    Calculates the number of glyphs in the font that are addressable by codepoint,
    the number of glyphs that are only addressable by name, and the total number of glyphs.

    Returns:
        A tuple containing:
        - Number of glyphs directly addressable by codepoint
        - Number of glyphs only addressable by name
        - Total number of glyphs
    """
    glyphs_with_codepoints = 0
    glyphs_without_codepoints = 0

    for glyph_name in ufo_font.keys():
        glyph = ufo_font[glyph_name]
        if glyph.unicodes:
            glyphs_with_codepoints += 1
        else:
            glyphs_without_codepoints += 1

    total_glyphs = glyphs_with_codepoints + glyphs_without_codepoints

    return glyphs_with_codepoints, glyphs_without_codepoints, total_glyphs


def merge_fonts(font_paths, output=None, ufo_dir=None, keep_non_bmp=False, keep_all_ranges=False):
    base_font_path = font_paths[0]
    fallback_paths = font_paths[1:]

    if output is None:
        output = f"{Path(base_font_path).stem}-Fallback{Path(base_font_path).suffix}"

    print(f"Reading base font: {base_font_path}")
    ufo_main = convert_ttfont_to_ufo(TTFont(base_font_path))

    if not keep_all_ranges:
        remove_glyphs_in_ranges(ufo_main, codepoint_ranges_to_remove)
    if not keep_non_bmp:
        clean_non_bmp_glyphs(ufo_main)

    for fallback_path in fallback_paths:
        print(f"Reading fallback font: {fallback_path}")
        u = convert_ttfont_to_ufo(TTFont(fallback_path))
        if not keep_all_ranges:
            remove_glyphs_in_ranges(u, codepoint_ranges_to_remove)
        if not keep_non_bmp:
            clean_non_bmp_glyphs(u)
        merge_ufo_fonts(ufo_main, u)

    glyphs_with_codepoints, glyphs_without_codepoints, total_glyphs = calculate_glyph_counts(ufo_main)

    print(f"Number of glyphs directly addressable by codepoint: {glyphs_with_codepoints}")
    print(f"Number of glyphs only addressable by name: {glyphs_without_codepoints}")
    print(f"Total number of glyphs: {total_glyphs}")

    if ufo_dir:
        print(f"Writing UFO font to: {ufo_dir}")
        path = Path(ufo_dir)
        if path.exists() and path.is_dir():
            shutil.rmtree(path)  # Delete the existing directory
        ufo_main.save(path)

    print("Compiling TTF...")
    out_fft_font = compileTTF(ufo_main)
    print(f"Writing merged font to: {output}")
    out_fft_font.save(output)

    print("Mission Accomplished!")
