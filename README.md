# Code Formatter for Sublime Text

A plugin that allows applying code formatting with minimum configuration.

Includes support for running the following formatters:

- [RuboCop](https://rubocop.org)
- [ESLint](https://eslint.org)
- [Prettier](https://prettier.io)
- [Golang's gofmt](https://pkg.go.dev/cmd/gofmt)
- [Golang's goimports](https://pkg.go.dev/golang.org/x/tools/cmd/goimports)

## Installation

### Setup Package Control Repository

1. Follow the instructions from https://sublime.fnando.com.
2. Open the command pallete, run “Package Control: Install Package“, then search
   for “Code Formatter“.

### Git Clone

Clone this repository into the Sublime Text “Packages” directory, which is
located where ever the “Preferences” -> “Browse Packages” option in sublime
takes you.

## Usage

By default, Code Formatter is ran whenever you save a supported code file (i.e.
a formatter is configured and enabled). You can disable this behaviour by
changing the settings under “Sublime Text -> Preferences -> Package Settings ->
Code Formatter -> Settings” or by using the command palette (`super+shift+p`)
and searching for “Code Formatter: Settings”.

You can also trigger commands using the command pallete by searching for “Code
Formatter: Format File”. Additionally, you could set up a keyboard shortcut by
adding a keybinding like the following:

```json
[{ "keys": ["super+k", "super+f"], "command": "format_code_file" }]
```

### Add new formatters

If you want to add a new formatter, you can do it so by adding adding a new key
that identifiers the formatter to `formatters`, and the related confirmation
using the same key. So, let’s say you want add a formatter called `txtfmt`. The
user configuration file could be something like this:

```json5
{
  txtfmt: {
    // The command that will be executed for format files.
    command: ["txtfmt", "--fix", "--config", "$config"],

    // The scopes that will be considered when formatting
    scopes: ["text.plain"],

    // Additional flags when running in debug mode.
    // If the formatter doesn't have a debug mode, you may set this to an empty
    // array.
    debug: ["--debug"],

    // When no custom config file exists, use a default config file.
    default_config: null,

    // Config files that will be looked up on the root of the project.
    // If the formatter doesn't require a config file (or is automatically
    // inferred by the formatter), you may want to set this to an empty array.
    config_files: ["txtfmt.config.json"],
  },

  formatters: ["gofmt", "rubocop", "prettier", "eslint", "txtfmt"],
}
```

## License

Copyright (c) 2020 Nando Vieira

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
