from fontTools.ttLib import TTFont
import sys

UNICODE_RANGES = [
    (0x20, 0x7f, "BasicLatin"),
    (0x80, 0xff, "Latin1Supplement"),
    (0x100, 0x17f, "LatinExtendedA"),
    (0x180, 0x24f, "LatinExtendedB"),
    (0x250, 0x2af, "IPAExtensions"),
    (0x2b0, 0x2ff, "SpacingModifierLetters"),
    (0x300, 0x36f, "CombiningDiacriticalMarks"),
    (0x370, 0x3ff, "GreekandCoptic"),
    (0x400, 0x4ff, "Cyrillic"),
    (0x500, 0x52f, "CyrillicSupplement"),
    (0x530, 0x58f, "Armenian"),
    (0x590, 0x5ff, "Hebrew"),
    (0x600, 0x6ff, "Arabic"),
    (0x700, 0x74f, "Syriac"),
    (0x750, 0x77f, "ArabicSupplement"),
    (0x780, 0x7bf, "Thaana"),
    (0x7c0, 0x7ff, "NKo"),
    (0x800, 0x83f, "Samaritan"),
    (0x840, 0x85f, "Mandaic"),
    (0x860, 0x86f, "SyriacSupplement"),
    (0x870, 0x89f, "ArabicExtendedB"),
    (0x8a0, 0x8ff, "ArabicExtendedA"),
    (0x900, 0x97f, "Devanagari"),
    (0x980, 0x9ff, "Bengali"),
    (0xa00, 0xa7f, "Gurmukhi"),
    (0xa80, 0xaff, "Gujarati"),
    (0xb00, 0xb7f, "Oriya"),
    (0xb80, 0xbff, "Tamil"),
    (0xc00, 0xc7f, "Telugu"),
    (0xc80, 0xcff, "Kannada"),
    (0xd00, 0xd7f, "Malayalam"),
    (0xd80, 0xdff, "Sinhala"),
    (0xe00, 0xe7f, "Thai"),
    (0xe80, 0xeff, "Lao"),
    (0xf00, 0xfff, "Tibetan"),
    (0x1000, 0x109f, "Myanmar"),
    (0x10a0, 0x10ff, "Georgian"),
    (0x1100, 0x11ff, "HangulJamo"),
    (0x1200, 0x137f, "Ethiopic"),
    (0x1380, 0x139f, "EthiopicSupplement"),
    (0x13a0, 0x13ff, "Cherokee"),
    (0x1400, 0x167f, "UnifiedCanadianAboriginalSyllabics"),
    (0x1680, 0x169f, "Ogham"),
    (0x16a0, 0x16ff, "Runic"),
    (0x1700, 0x171f, "Tagalog"),
    (0x1720, 0x173f, "Hanunoo"),
    (0x1740, 0x175f, "Buhid"),
    (0x1760, 0x177f, "Tagbanwa"),
    (0x1780, 0x17ff, "Khmer"),
    (0x1800, 0x18af, "Mongolian"),
    (0x18b0, 0x18ff, "UnifiedCanadianAboriginalSyllabicsExtended"),
    (0x1900, 0x194f, "Limbu"),
    (0x1950, 0x197f, "TaiLe"),
    (0x1980, 0x19df, "NewTaiLue"),
    (0x19e0, 0x19ff, "KhmerSymbols"),
    (0x1a00, 0x1a1f, "Buginese"),
    (0x1a20, 0x1aaf, "TaiTham"),
    (0x1ab0, 0x1aff, "CombiningDiacriticalMarksExtended"),
    (0x1b00, 0x1b7f, "Balinese"),
    (0x1b80, 0x1bbf, "Sundanese"),
    (0x1bc0, 0x1bff, "Batak"),
    (0x1c00, 0x1c4f, "Lepcha"),
    (0x1c50, 0x1c7f, "OlChiki"),
    (0x1c80, 0x1c8f, "CyrillicExtendedC"),
    (0x1c90, 0x1cbf, "GeorgianExtended"),
    (0x1cc0, 0x1ccf, "SundaneseSupplement"),
    (0x1cd0, 0x1cff, "VedicExtensions"),
    (0x1d00, 0x1d7f, "PhoneticExtensions"),
    (0x1d80, 0x1dbf, "PhoneticExtensionsSupplement"),
    (0x1dc0, 0x1dff, "CombiningDiacriticalMarksSupplement"),
    (0x1e00, 0x1eff, "LatinExtendedAdditional"),
    (0x1f00, 0x1fff, "GreekExtended"),
    (0x2000, 0x206f, "GeneralPunctuation"),
    (0x2070, 0x209f, "SuperscriptsandSubscripts"),
    (0x20a0, 0x20cf, "CurrencySymbols"),
    (0x20d0, 0x20ff, "CombiningDiacriticalMarksforSymbols"),
    (0x2100, 0x214f, "LetterlikeSymbols"),
    (0x2150, 0x218f, "NumberForms"),
    (0x2190, 0x21ff, "Arrows"),
    (0x2200, 0x22ff, "MathematicalOperators"),
    (0x2300, 0x23ff, "MiscellaneousTechnical"),
    (0x2400, 0x243f, "ControlPictures"),
    (0x2440, 0x245f, "OpticalCharacterRecognition"),
    (0x2460, 0x24ff, "EnclosedAlphanumerics"),
    (0x2500, 0x257f, "BoxDrawing"),
    (0x2580, 0x259f, "BlockElements"),
    (0x25a0, 0x25ff, "GeometricShapes"),
    (0x2600, 0x26ff, "MiscellaneousSymbols"),
    (0x2700, 0x27bf, "Dingbats"),
    (0x27c0, 0x27ef, "MiscellaneousMathematicalSymbolsA"),
    (0x27f0, 0x27ff, "SupplementalArrowsA"),
    (0x2800, 0x28ff, "BraillePatterns"),
    (0x2900, 0x297f, "SupplementalArrowsB"),
    (0x2980, 0x29ff, "MiscellaneousMathematicalSymbolsB"),
    (0x2a00, 0x2aff, "SupplementalMathematicalOperators"),
    (0x2b00, 0x2bff, "MiscellaneousSymbolsandArrows"),
    (0x2c00, 0x2c5f, "Glagolitic"),
    (0x2c60, 0x2c7f, "LatinExtendedC"),
    (0x2c80, 0x2cff, "Coptic"),
    (0x2d00, 0x2d2f, "GeorgianSupplement"),
    (0x2d30, 0x2d7f, "Tifinagh"),
    (0x2d80, 0x2ddf, "EthiopicExtended"),
    (0x2de0, 0x2dff, "CyrillicExtendedA"),
    (0x2e00, 0x2e7f, "SupplementalPunctuation"),
    (0x2e80, 0x2eff, "CJKRadicalsSupplement"),
    (0x2f00, 0x2fdf, "KangxiRadicals"),
    (0x2ff0, 0x2fff, "IdeographicDescriptionCharacters"),
    (0x3000, 0x303f, "CJKSymbolsandPunctuation"),
    (0x3040, 0x309f, "Hiragana"),
    (0x30a0, 0x30ff, "Katakana"),
    (0x3100, 0x312f, "Bopomofo"),
    (0x3130, 0x318f, "HangulCompatibilityJamo"),
    (0x3190, 0x319f, "Kanbun"),
    (0x31a0, 0x31bf, "BopomofoExtended"),
    (0x31c0, 0x31ef, "CJKStrokes"),
    (0x31f0, 0x31ff, "KatakanaPhoneticExtensions"),
    (0x3200, 0x32ff, "EnclosedCJKLettersandMonths"),
    (0x3300, 0x33ff, "CJKCompatibility"),
    (0x3400, 0x4dbf, "CJKUnifiedIdeographsExtensionA"),
    (0x4dc0, 0x4dff, "YijingHexagramSymbols"),
    (0x4e00, 0x9fff, "CJKUnifiedIdeographs"),
    (0xa000, 0xa48f, "YiSyllables"),
    (0xa490, 0xa4cf, "YiRadicals"),
    (0xa4d0, 0xa4ff, "Lisu"),
    (0xa500, 0xa63f, "Vai"),
    (0xa640, 0xa69f, "CyrillicExtendedB"),
    (0xa6a0, 0xa6ff, "Bamum"),
    (0xa700, 0xa71f, "ModifierToneLetters"),
    (0xa720, 0xa7ff, "LatinExtendedD"),
    (0xa800, 0xa82f, "SylotiNagri"),
    (0xa830, 0xa83f, "CommonIndicNumberForms"),
    (0xa840, 0xa87f, "Phagspa"),
    (0xa880, 0xa8df, "Saurashtra"),
    (0xa8e0, 0xa8ff, "DevanagariExtended"),
    (0xa900, 0xa92f, "KayahLi"),
    (0xa930, 0xa95f, "Rejang"),
    (0xa960, 0xa97f, "HangulJamoExtendedA"),
    (0xa980, 0xa9df, "Javanese"),
    (0xa9e0, 0xa9ff, "MyanmarExtendedB"),
    (0xaa00, 0xaa5f, "Cham"),
    (0xaa60, 0xaa7f, "MyanmarExtendedA"),
    (0xaa80, 0xaadf, "TaiViet"),
    (0xaae0, 0xaaff, "MeeteiMayekExtensions"),
    (0xab00, 0xab2f, "EthiopicExtendedA"),
    (0xab30, 0xab6f, "LatinExtendedE"),
    (0xab70, 0xabbf, "CherokeeSupplement"),
    (0xabc0, 0xabff, "MeeteiMayek"),
    (0xac00, 0xd7af, "HangulSyllables"),
    (0xd7b0, 0xd7ff, "HangulJamoExtendedB"),
    (0xd800, 0xdb7f, "HighSurrogates"),
    (0xdb80, 0xdbff, "HighPrivateUseSurrogates"),
    (0xdc00, 0xdfff, "LowSurrogates"),
    (0xe000, 0xf8ff, "PrivateUseArea"),
    (0xf900, 0xfaff, "CJKCompatibilityIdeographs"),
    (0xfb00, 0xfb4f, "AlphabeticPresentationForms"),
    (0xfb50, 0xfdff, "ArabicPresentationFormsA"),
    (0xfe00, 0xfe0f, "VariationSelectors"),
    (0xfe10, 0xfe1f, "VerticalForms"),
    (0xfe20, 0xfe2f, "CombiningHalfMarks"),
    (0xfe30, 0xfe4f, "CJKCompatibilityForms"),
    (0xfe50, 0xfe6f, "SmallFormVariants"),
    (0xfe70, 0xfeff, "ArabicPresentationFormsB"),
    (0xff00, 0xffef, "HalfwidthandFullwidthForms"),
    (0xfff0, 0xffff, "Specials"),
    (0x10000, 0x10FFF, "LinearBSyllabary"),
    (0x11000, 0x11FFF, "BrahmiAndOtherIndicScripts"),
    (0x1B000, 0x1B0FF, "KanaSupplement"),
    (0x1D000, 0x1D0FF, "MusicalSymbols"),
    (0x1D100, 0x1D1FF, "AncientGreekMusicalNotation"),
    (0x1F000, 0x1F02F, "MahjongTiles"),
    (0x1F030, 0x1F09F, "DominoTiles"),
    (0x1F300, 0x1F5FF, "MiscellaneousSymbolsAndPictographs"),
    (0x1F600, 0x1F64F, "Emoticons"),
    (0x1F680, 0x1F6FF, "TransportAndMapSymbols"),
    (0x1F700, 0x1F77F, "AlchemicalSymbols"),
    (0x20000, 0x2A6DF, "CJKUnifiedIdeographsExtensionB"),
    (0x2A700, 0x2B73F, "CJKUnifiedIdeographsExtensionC"),
    (0x2B740, 0x2B81F, "CJKUnifiedIdeographsExtensionD"),
    (0x2B820, 0x2CEAF, "CJKUnifiedIdeographsExtensionE"),
    (0x2CEB0, 0x2EBEF, "CJKUnifiedIdeographsExtensionF"),
    (0x2F800, 0x2FA1F, "CJKCompatibilityIdeographsSupplement"),
    (0xE0000, 0xE007F, "Tags"),
    (0xE0100, 0xE01EF, "VariationSelectorsSupplement"),
    (0xF0000, 0xFFFFF, "PrivateUseAreaPlane15"),
    (0x100000, 0x10FFFF, "PrivateUseAreaPlane16"),
]

# Create a mapping from codepoint range to region for faster lookup
UNICODE_RANGE_MAPPING = {
    (start, end): region for start, end, region in UNICODE_RANGES
}


def coverage_analysis(font_path: str, output_file=None):
    try:
        font = TTFont(font_path)
    except FileNotFoundError:
        print(f"Error: The file '{font_path}' was not found.")
        return
    except Exception as e:
        print(f"Error: Failed to load the font file '{font_path}'. Reason: {e}")
        return

    output_stream = open(output_file, 'w') if output_file else None

    def write_output(message):
        if output_stream:
            output_stream.write(message + "\n")
        else:
            print(message)


# Collect global font info
    write_output("\nFont Information:")
    write_output(f"File: {font_path}")
    if 'name' in font:
        for record in font['name'].names:
            if record.nameID == 1:  # Font Family name
                write_output(f"Font Family: {record.toUnicode()}")
            elif record.nameID == 4:  # Full font name
                write_output(f"Full Font Name: {record.toUnicode()}")
            elif record.nameID == 6:  # PostScript name
                write_output(f"PostScript Name: {record.toUnicode()}")
                break

    write_output(f"Number of glyphs: {font['maxp'].numGlyphs}")

    num_empty_glyphs = 0
    num_regular_glyphs = 0
    num_composite_glyphs = 0
    num_directly_addressable_glyphs = 0
    used_glyphs = set()

    for glyph_name in font.getGlyphOrder():
        glyph = font['glyf'][glyph_name]
        if glyph.isComposite():
            num_composite_glyphs += 1
            for component in glyph.components:
                used_glyphs.add(component.glyphName)
        elif glyph.numberOfContours == 0:
            num_empty_glyphs += 1
        else:
            num_regular_glyphs += 1

    try:
        cmap = font['cmap'].getBestCmap()
    except AttributeError:
        write_output("Error: The font does not contain a valid cmap table.")
        sys.exit(1)

    num_directly_addressable_glyphs = len(cmap)
    directly_addressable_glyphs = set(cmap.values())
    all_glyphs = set(font.getGlyphOrder())
    dangling_glyphs = all_glyphs - directly_addressable_glyphs - used_glyphs
    num_dangling_glyphs = len(dangling_glyphs)

    write_output(f"Number of empty glyphs: {num_empty_glyphs}")
    write_output(f"Number of regular glyphs: {num_regular_glyphs}")
    write_output(f"Number of composite glyphs: {num_composite_glyphs}")
    write_output(f"Number of glyphs directly addressable by codepoint: {num_directly_addressable_glyphs}")
    write_output(f"Number of dangling glyphs: {num_dangling_glyphs}")

    glyph_coverage = {region: 0 for _, _, region in UNICODE_RANGES}

    for codepoint in cmap.keys():
        for (start, end), region in UNICODE_RANGE_MAPPING.items():
            if start <= codepoint <= end:
                glyph_coverage[region] += 1
                break

    write_output("\nGlyph Coverage by Unicode Region:\n")
    write_output(f"{'Region':<35}{'Codepoints':<20}{'Coverage':<15}{'Percentage':<10}")
    write_output("=" * 85)
    for start, end, region in UNICODE_RANGES:
        count = glyph_coverage[region]
        total = end - start + 1
        if count > 0:
            percentage = (count / total) * 100
            codepoints_str = f"U+{start:04X}-U+{end:04X}"
            coverage_str = f"{count}/{total}"
            write_output(f"{region:<35}{codepoints_str:<20}{coverage_str:<15} {percentage:6.1f}%")

    if output_stream:
        output_stream.close()
