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

	// Collect all unique codepoints
	allCodepointsSet := make(map[rune]struct{})
	for _, coverage := range fontCoverages {
		for cp := range coverage {
			allCodepointsSet[cp] = struct{}{}
		}
	}

	// Convert codepoint set to slice and sort
	allCodepoints := make([]rune, 0, len(allCodepointsSet))
	for cp := range allCodepointsSet {
		allCodepoints = append(allCodepoints, cp)
	}
	sort.Slice(allCodepoints, func(i, j int) bool { return allCodepoints[i] < allCodepoints[j] })

	// For each codepoint, record which fonts cover it
	codepointCoverage := make(map[rune][]string)
	for _, cp := range allCodepoints {
		for fontName, coverage := range fontCoverages {
			if _, exists := coverage[cp]; exists {
				codepointCoverage[cp] = append(codepointCoverage[cp], fontName)
			}
		}
	}

	// Open output writer
	writer, err := getWriter(c.Output)
	if err != nil {
		return err
	}
	defer closeWriter(writer)

	// Generate report
	printMultiComparisonReport(writer, fontNames, codepointCoverage)
	return nil
}

// printMultiComparisonReport prints the comparison report for multiple fonts.
func printMultiComparisonReport(writer io.Writer, fontNames []string, codepointCoverage map[rune][]string) {
	// Create a map from coverage (list of fonts) to codepoint ranges
	type CoverageKey string
	coverageMap := make(map[CoverageKey][]rune)

	// For each codepoint, create a key representing the fonts that cover it
	for cp, fonts := range codepointCoverage {
		sort.Strings(fonts) // Ensure consistent order
		key := CoverageKey(strings.Join(fonts, ", "))
		coverageMap[key] = append(coverageMap[key], cp)
	}

	// Now, for each coverage key, group codepoints into ranges
	coverageRanges := make(map[CoverageKey][]Range)

	for key, codepoints := range coverageMap {
		sort.Slice(codepoints, func(i, j int) bool { return codepoints[i] < codepoints[j] })
		ranges := groupCodepointsIntoRanges(codepoints)
		coverageRanges[key] = ranges
	}

	// Now, print the report
	fmt.Fprintf(writer, "Comparison Report for Fonts:\n")
	for _, fontName := range fontNames {
		fmt.Fprintf(writer, "- %s\n", fontName)
	}
	fmt.Fprintf(writer, "\n")

	fmt.Fprintf(writer, "%-20s %-40s %-10s\n", "Codepoint Range", "Fonts", "Codepoints")
	fmt.Fprintf(writer, "%s\n", strings.Repeat("-", 80))

	for key, ranges := range coverageRanges {
		for _, r := range ranges {
			codepointRange := fmt.Sprintf("U+%04X - U+%04X", r.Lo, r.Hi)
			count := int(r.Hi - r.Lo + 1)
			fmt.Fprintf(writer, "%-20s %-40s %d\n", codepointRange, key, count)
		}
	}
}
