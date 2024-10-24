package main

import (
	"fmt"
	"io"
	"os"

	"golang.org/x/image/font/sfnt"
)

// loadFont reads and parses a font file.
func loadFont(fontPath string) (*sfnt.Font, error) {
	fontData, err := os.ReadFile(fontPath)
	if err != nil {
		return nil, fmt.Errorf("failed to read font file: %v", err)
	}

	font, err := sfnt.Parse(fontData)
	if err != nil {
		return nil, fmt.Errorf("failed to parse font: %v", err)
	}

	return font, nil
}

// getWriter returns an io.Writer based on the outputPath.
// If outputPath is empty, it returns os.Stdout.
func getWriter(outputPath string) (io.Writer, error) {
	if outputPath == "" {
		return os.Stdout, nil
	}

	file, err := os.Create(outputPath)
	if err != nil {
		return nil, fmt.Errorf("failed to create output file: %v", err)
	}
	return file, nil
}

// closeWriter closes the writer if it's a file.
// If the writer is os.Stdout, it does nothing.
func closeWriter(writer io.Writer) {
	if writer == os.Stdout {
		return
	}
	if closer, ok := writer.(io.Closer); ok {
		closer.Close()
	}
}

// groupCodepointsIntoRanges groups codepoints into continuous ranges.
func groupCodepointsIntoRanges(codepoints []rune, maxGap int) []Range {
	if len(codepoints) == 0 {
		return nil
	}

	var ranges []Range
	start := codepoints[0]
	prev := codepoints[0]

	for i := 1; i < len(codepoints); i++ {
		cp := codepoints[i]
		if int(cp-prev) <= maxGap+1 {
			// Extend the current range, including the gap
			prev = cp
		} else {
			// End the current range and start a new one
			ranges = append(ranges, Range{
				Lo: start,
				Hi: prev,
			})
			start = cp
			prev = cp
		}
	}
	// Add the final range
	ranges = append(ranges, Range{
		Lo: start,
		Hi: prev,
	})

	return ranges
}
