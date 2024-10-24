package main

import (
	"fmt"
	"io"
	"path/filepath"
	"sort"
	"strings"

	"github.com/alecthomas/kong"
)

type CompareCmd struct {
	Fonts  []string `arg:"" required:"" name:"fontfiles" help:"Paths to font files." type:"existingfile"`
	Output string   `short:"o" help:"Output file path. If not specified, output will be printed to stdout."`
}

func (c *CompareCmd) Run(ctx *kong.Context) error {
	// Load fonts and collect coverage
	fontCoverages := make(map[string]map[rune]struct{})
	fontNames := make([]string, len(c.Fonts))

	for i, fontPath := range c.Fonts {
		font, err := loadFont(fontPath)
		if err != nil {
			return fmt.Errorf("failed to load font %s: %v", fontPath, err)
		}

		coverage := CollectCoverage(font)
		fontName := filepath.Base(fontPath)
		fontCoverages[fontName] = coverage
		fontNames[i] = fontName
	}

	// Open output writer
	writer, err := getWriter(c.Output)
	if err != nil {
		return err
	}
	defer closeWriter(writer)

	// Generate report
	printMultiComparisonReport(writer, fontNames, fontCoverages, 65536)

	return nil
}

type RangeCoverageInfo struct {
	Lo             rune
	Hi             rune
	Fonts          string
	CodepointCount int
}

// printMultiComparisonReport prints the comparison report for multiple fonts.
func printMultiComparisonReport(writer io.Writer, fontNames []string, fontCoverages map[string]map[rune]struct{}, maxGap int) {
	// Define the struct for holding range information
	type RangeCoverageInfo struct {
		Lo             rune
		Hi             rune
		Fonts          string
		CodepointCount int
	}

	// Map to hold coverage keys and their display strings
	type CoverageKey string
	coverageKeyMap := make(map[CoverageKey]string)

	// Map each codepoint to its coverage key
	codepointCoverage := make(map[rune]CoverageKey)

	// Collect codepoints and their coverage keys
	for cp := rune(0x0000); cp <= 0x10FFFF; cp++ {
		var fonts []string
		for fontName, coverage := range fontCoverages {
			if _, exists := coverage[cp]; exists {
				fonts = append(fonts, fontName)
			}
		}
		if len(fonts) > 0 {
			sort.Strings(fonts)
			key := CoverageKey(strings.Join(fonts, ", "))
			codepointCoverage[cp] = key
			coverageKeyMap[key] = strings.Join(fonts, ", ")
		}
	}

	// Sort codepoints
	var codepoints []rune
	for cp := range codepointCoverage {
		codepoints = append(codepoints, cp)
	}
	sort.Slice(codepoints, func(i, j int) bool { return codepoints[i] < codepoints[j] })

	// Create non-overlapping ranges, allowing gaps up to maxGap
	var ranges []RangeCoverageInfo
	if len(codepoints) > 0 {
		startCP := codepoints[0]
		prevCP := codepoints[0]
		currentKey := codepointCoverage[startCP]

		for i := 1; i < len(codepoints); i++ {
			cp := codepoints[i]
			key := codepointCoverage[cp]
			if int(cp-prevCP) <= maxGap+1 && key == currentKey {
				// Continue the current range
				prevCP = cp
			} else {
				// Finish the current range and start a new one
				ranges = append(ranges, RangeCoverageInfo{
					Lo:             startCP,
					Hi:             prevCP,
					Fonts:          coverageKeyMap[currentKey],
					CodepointCount: int(prevCP - startCP + 1),
				})
				startCP = cp
				prevCP = cp
				currentKey = key
			}
		}
		// Add the last range
		ranges = append(ranges, RangeCoverageInfo{
			Lo:             startCP,
			Hi:             prevCP,
			Fonts:          coverageKeyMap[currentKey],
			CodepointCount: int(prevCP - startCP + 1),
		})
	}

	// Print the report
	fmt.Fprintf(writer, "Comparison Report for Fonts:\n")
	for _, fontName := range fontNames {
		fmt.Fprintf(writer, "- %s\n", fontName)
	}
	fmt.Fprintf(writer, "\n")

	fmt.Fprintf(writer, "%-20s %-40s %-10s\n", "Codepoint Range", "Fonts", "Codepoints")
	fmt.Fprintf(writer, "%s\n", strings.Repeat("-", 80))

	for _, rc := range ranges {
		codepointRange := fmt.Sprintf("U+%04X - U+%04X", rc.Lo, rc.Hi)
		fmt.Fprintf(writer, "%-20s %-40s %d\n", codepointRange, rc.Fonts, rc.CodepointCount)
	}
}
