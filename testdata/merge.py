from fontTools.ttLib import TTFont, newTable
from fontTools.merge import Merger
import os

# Unicode ranges to remove
glyph_ranges_to_remove = [
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

def is_base_plane(codepoint):
    """Check if codepoint is in the Basic Multilingual Plane (BMP, Plane 0)"""
    return 0 <= codepoint <= 0xFFFF

def should_remove_glyph(codepoint):
    """Check if the codepoint falls within any of the ranges to be removed or outside of BMP"""
    if not is_base_plane(codepoint):
        return True
    for start, end in glyph_ranges_to_remove:
        if start <= codepoint <= end:
            return True
    return False

def merge_fonts(main_font_path, fallback_paths, output_path):
    """
    Merge multiple TrueType fonts into a single file, optimizing size by removing non-essential tables.
    
    Args:
        main_font_path (str): Path to the main font file
        fallback_paths (list): List of paths to fallback font files
        output_path (str): Path where the merged font will be saved
    """
    # Load fonts
    main_font = TTFont(main_font_path)
    fallback_fonts = [TTFont(path) for path in fallback_paths]
    
    # Filter main font cmap to only include base plane codepoints
    main_cmap = main_font.getBestCmap()
    filtered_main_cmap = {cp: name for cp, name in main_cmap.items() if is_base_plane(cp) and not should_remove_glyph(cp)}
    
    # Update main font's cmap tables with filtered cmap
    for cmap in main_font['cmap'].tables:
        if cmap.platformID in [0, 3]:  # Unicode or Windows
            cmap.cmap = filtered_main_cmap
    
    # Merge cmap tables
    for fallback in fallback_fonts:
        # Get and filter fallback cmap
        fallback_cmap = fallback.getBestCmap()
        filtered_fallback_cmap = {cp: name for cp, name in fallback_cmap.items() if is_base_plane(cp) and not should_remove_glyph(cp)}
        
        if filtered_fallback_cmap:
            # Update main cmap with fallback entries
            for code, name in filtered_fallback_cmap.items():
                if code not in filtered_main_cmap:
                    if name in fallback['glyf']:
                        try:
                            # Copy the glyph
                            main_font['glyf'][name] = fallback['glyf'][name]
                            # Copy glyph metrics
                            if 'hmtx' in main_font and name in fallback['hmtx'].metrics:
                                main_font['hmtx'].metrics[name] = fallback['hmtx'].metrics[name]
                            # Update cmap
                            for cmap in main_font['cmap'].tables:
                                if cmap.platformID in [0, 3]:  # Unicode or Windows
                                    cmap.cmap[code] = name
                        except KeyError:
                            continue
    
    # Remove non-essential and hinting tables
    tables_to_remove = {
        # Hinting tables
        'fpgm',     # Font program
        'prep',     # Control value program
        'cvt ',     # Control value table
        'hdmx',     # Horizontal device metrics
        'LTSH',     # Linear threshold table
        'VDMX',     # Vertical device metrics
        'gasp',     # Grid-fitting/Scan-conversion
        
        # Kerning and layout tables
        'kern',     # Kerning
        'GPOS',     # Glyph positioning
        'GSUB',     # Glyph substitution
        'GDEF',     # Glyph definition
        
        # Other non-essential tables
        'DSIG',     # Digital signature
        'JSTF',     # Justification
        'PCLT',     # PCL5
        'VORG',     # Vertical origin
        'SVG ',     # SVG outlines
        'sbix',     # Standard bitmap graphics
        'COLR',     # Color
        'CPAL',     # Color palette
        'CBDT',     # Color bitmap data
        'CBLC',     # Color bitmap location
        'EBDT',     # Embedded bitmap data
        'EBLC',     # Embedded bitmap location
        'EBSC',     # Embedded bitmap scaling
        'BASE',     # Baseline
        'meta',     # Metadata
        'ankr',     # Anchor points
        'feat',     # Layout features
        'morx',     # Extended metamorphosis
        'prop',     # Glyph properties
        'opbd',     # Optical bounds
    }
    
    # Remove tables
    for table_tag in tables_to_remove:
        if table_tag in main_font:
            del main_font[table_tag]
    
    # Save the merged font
    main_font.save(output_path)

def main():
    main_font = "testdata/NotoSans-Regular.ttf"
    fallbacks = [
        "testdata/NotoSansJP-Regular.ttf",
        "testdata/NotoSansKR-Regular.ttf",
        "testdata/NotoSansSC-Regular.ttf",
        "testdata/NotoSansTC-Regular.ttf",
    ]
    output = "testdata/NotoSansFallback-Regular.ttf"
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    try:
        # Get original size of main font
        orig_size = os.path.getsize(main_font)
        
        merge_fonts(main_font, fallbacks, output)
        
        # Get new size
        new_size = os.path.getsize(output)
        
        # Print statistics
        merged = TTFont(output)
        merged_cmap = merged.getBestCmap()
        print(f"Merge completed successfully:")
        print(f"Total glyphs in merged font: {len(merged.getGlyphSet())}")
        print(f"Total codepoints in merged font: {len(merged_cmap)}")
        print(f"Highest codepoint in merged font: {hex(max(merged_cmap.keys()))}")
        print(f"\nRemaining tables in merged font: {sorted(merged.keys())}")
        print(f"\nFile sizes:")
        print(f"Original main font: {orig_size:,} bytes")
        print(f"Merged font: {new_size:,} bytes")
        
    except Exception as e:
        print(f"Error merging fonts: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
