import sys
from fontTools.ttLib import TTFont
import ufoLib2
from ufoLib2.objects.component import Component


def print_progress_bar(current: int, total: int, bar_length: int = 30):
    """Prints a live progress bar with stars on the same line."""
    progress = current / total
    stars = int(progress * bar_length)
    spaces = bar_length - stars
    bar = f"[{'*' * stars}{' ' * spaces}] {current}/{total}"

    sys.stdout.write(f"\r{bar}")
    sys.stdout.flush()


def convert_ttfont_to_ufo(tt_font: TTFont) -> ufoLib2.Font:
    # Create a new UFO font
    ufo_font = ufoLib2.Font()

    # Extract metadata from the TTF font
    tt_name_table = tt_font['name']
    tt_head_table = tt_font['head']
    tt_hhea_table = tt_font['hhea']
    ufo_font.info.familyName = tt_name_table.getName(1, 3, 1).toUnicode()
    ufo_font.info.styleName = tt_name_table.getName(2, 3, 1).toUnicode()
    ufo_font.info.unitsPerEm = tt_head_table.unitsPerEm
    ufo_font.info.ascender = tt_hhea_table.ascent
    ufo_font.info.descender = tt_hhea_table.descent

    # Extract the cmap to get Unicode mappings
    cmap = tt_font.getBestCmap()

    # Get the glyph set from the TTF font
    glyph_set = tt_font.getGlyphSet()
    tt_glyf_table = tt_font['glyf']

    total_glyphs = len(glyph_set)
    print(f"Converting {total_glyphs} glyphs to UFO format...")

    # Reverse the cmap to map glyph names to Unicode values
    glyph_to_unicodes = {}
    for unicode_val, glyph_name in cmap.items():
        if glyph_name not in glyph_to_unicodes:
            glyph_to_unicodes[glyph_name] = []
        glyph_to_unicodes[glyph_name].append(unicode_val)

    # Iterate over glyphs and handle both simple and composite glyphs
    for i, glyph_name in enumerate(glyph_set.keys(), start=1):
        tt_glyph = tt_glyf_table[glyph_name]

        glyph = ufo_font.newGlyph(glyph_name)

        # Set glyph width and Unicode value, if available
        glyph.width = glyph_set[glyph_name].width
        glyph.unicodes = glyph_to_unicodes.get(glyph_name, [])

        # Check if the glyph is composite
        if 'glyf' in tt_font and tt_glyph.isComposite():
            for component in tt_glyph.components:
                glyphName, transform = component.getComponentInfo()

                c = Component(baseGlyph=glyphName, transformation=transform)

                # Create a UFO component with reference to the base glyph
                glyph.components.append(c)

        else:
            # Handle simple glyphs by drawing the outline
            pen = glyph.getPen()
            glyph_set[glyph_name].draw(pen)

        # Print progress every 10 glyphs or at the end
        if i % 100 == 0 or i == total_glyphs:
            print_progress_bar(i, total_glyphs)

    print()  # Ensure the next output starts on a new line

    return ufo_font
