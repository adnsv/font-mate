package main

import "golang.org/x/image/font/sfnt"

// CollectCoverage gathers the glyph coverage from the font.
func CollectCoverage(font *sfnt.Font) map[rune]struct{} {
	coverage := make(map[rune]struct{})
	b := &sfnt.Buffer{} // Buffer for sfnt operations

	for cp := rune(0x0020); cp <= 0x10FFFF; cp++ {
		glyphIndex, err := font.GlyphIndex(b, cp)
		if err != nil {
			// Skip errors, as some codepoints may be invalid
			continue
		}

		if glyphIndex != 0 {
			coverage[cp] = struct{}{} // Add codepoint to the set
		}
	}
	return coverage
}
