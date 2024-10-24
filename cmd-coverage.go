package main

import (
	"fmt"
	"io"
	"path/filepath"
	"strings"

	"github.com/alecthomas/kong"
)

type CoverageCmd struct {
	FontPath string `arg:"" required:"" name:"fontfile" help:"Path to the font file." type:"existingfile"`
	Output   string `short:"o" help:"Output file path. If not specified, output will be printed to stdout."`
}

func (cmd *CoverageCmd) Run(ctx *kong.Context) error {
	font, err := loadFont(cmd.FontPath)
	if err != nil {
		return fmt.Errorf("failed to load font: %v", err)
	}

	numGlyphs := font.NumGlyphs()
	coverage := CollectCoverage(font)

	coverageStats := CalculateCoverageStats(coverage)

	// Open output writer
	writer, err := getWriter(cmd.Output)
	if err != nil {
		return err
	}
	defer closeWriter(writer)

	PrintCoverageReport(writer, cmd.FontPath, numGlyphs, coverageStats)

	return nil
}

// RangeCoverage holds statistics for each Unicode range.
type RangeCoverage struct {
	Range           Range
	TotalGlyphs     int
	CoveredGlyphs   int
	CoveragePercent float64
}

// CalculateCoverageStats computes statistics for each Unicode range.
func CalculateCoverageStats(coverage map[rune]struct{}) []RangeCoverage {
	var coverageStats []RangeCoverage

	for _, r := range Ranges {
		total := int(r.Hi - r.Lo + 1)
		covered := 0

		for cp := r.Lo; cp <= r.Hi; cp++ {
			if _, exists := coverage[cp]; exists {
				covered++
			}
		}

		percent := float64(covered) / float64(total) * 100
		coverageStats = append(coverageStats, RangeCoverage{
			Range:           r,
			TotalGlyphs:     total,
			CoveredGlyphs:   covered,
			CoveragePercent: percent,
		})
	}

	return coverageStats // Keep the original order of ranges.
}

// PrintCoverageReport prints the coverage report for a single font to the specified writer.
func PrintCoverageReport(writer io.Writer, fontPath string, numGlyphs int, coverageStats []RangeCoverage) {
	fontName := filepath.Base(fontPath)

	fmt.Fprintf(writer, "Coverage Report for %s\n", fontName)
	fmt.Fprintf(writer, "Total glyphs in font: %d\n\n", numGlyphs)

	fmt.Fprintf(writer, "%-40s %-20s %-10s %-10s %-10s\n", "Range", "Codepoint Range", "Total", "Covered", "Percent")
	fmt.Fprintf(writer, "%s\n", strings.Repeat("-", 100))

	for _, stat := range coverageStats {
		if stat.CoveredGlyphs > 0 {
			codepointRange := fmt.Sprintf("U+%04X - U+%04X", stat.Range.Lo, stat.Range.Hi)
			fmt.Fprintf(writer, "%-40s %-20s %-10d %-10d %6.2f%%\n",
				stat.Range.Name,
				codepointRange,
				stat.TotalGlyphs,
				stat.CoveredGlyphs,
				stat.CoveragePercent)
		}
	}

	// Print summary statistics
	var totalCodepoints, totalCovered int
	for _, stat := range coverageStats {
		totalCodepoints += stat.TotalGlyphs
		totalCovered += stat.CoveredGlyphs
	}

	fmt.Fprintf(writer, "\nSummary:\n")
	fmt.Fprintf(writer, "Total Unicode codepoints in ranges: %d\n", totalCodepoints)
	fmt.Fprintf(writer, "Total codepoints covered: %d\n", totalCovered)
	fmt.Fprintf(writer, "Overall coverage: %.2f%%\n", float64(totalCovered)/float64(totalCodepoints)*100)
}
