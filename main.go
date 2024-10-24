package main

import "github.com/alecthomas/kong"

var cli struct {
	Coverage CoverageCmd      `cmd:"" help:"Collect coverage stats for a font."`
	Compare  CompareCmd       `cmd:"" help:"Compare codepoint coverages of multiple fonts."`
	Version  kong.VersionFlag `short:"v" help:"Print version information and quit."`
}

func main() {
	ctx := kong.Parse(&cli,
		kong.Name("font-mate"),
		kong.Description("Font utilities."),
		kong.UsageOnError(),
		kong.Vars{"version": app_version()},
	)
	err := ctx.Run()
	ctx.FatalIfErrorf(err)
}
