# Code Formatter for Sublime Text

A plugin that allows applying code formatting with minimum configuration.

Includes support for running the following formatters:

- [Ruby’s RuboCop](https://rubocop.org)
- [Ruby’s rubyfmt](https://github.com/penelopezone/rubyfmt)
- [ESLint](https://eslint.org)
- [Prettier](https://prettier.io)
- [Golang’s gofmt](https://pkg.go.dev/cmd/gofmt)
- [Golang’s goimports](https://pkg.go.dev/golang.org/x/tools/cmd/goimports)
- [Python’s autopep8](https://pypi.org/project/autopep8/)
- [Python’s yapf](https://pypi.org/project/yapf/)
- [PHP Code Standards Fixer](https://github.com/FriendsOfPHP/PHP-CS-Fixer)
- [Rust’s rustfmt](https://github.com/rust-lang/rustfmt)
- [SVGO](https://github.com/svg/svgo)
- [Flutter](https://flutter.dev/)
- [Dart’s dartfmt](https://dart.dev/tools/dartfmt)
- [Crystal](https://crystal-lang.org/reference/1.3/using_the_compiler/index.html#crystal-tool-format)

## Installation

### Setup Package Control Repository

1. Follow the instructions from https://sublime.fnando.com.
2. Open the command pallete, run “Package Control: Install Package“, then search
   for “Codefmt“.

### Git Clone

Clone this repository into the Sublime Text “Packages” directory, which is
located where ever the “Preferences” -> “Browse Packages” option in sublime
takes you.

## Usage

By default, Codefmt is ran whenever you save a supported code file (i.e. a
formatter is configured and enabled). You can disable this behaviour by changing
the settings under “Sublime Text -> Preferences -> Package Settings -> Codefmt
-> Settings” or by using the command palette (`super+shift+p`) and searching for
“Codefmt: Settings”.

You can also trigger commands using the command pallete by searching for “Code
Formatter: Format File”. You can add a custom shortcut by using the following
command:

```json
[{ "keys": ["super+k", "super+f"], "command": "format_code_file" }]
```

When auto saving is disabled, you can set up alternative keybindings so you can
use `super+s` to save and format the current file, and another shortcut to
bypass auto formatting. The following keybindings show how to do that for macOS:

```json
[
  {
    "keys": ["super+s"],
    "command": "run_macro_file",
    "args": {"file": "Packages/Codefmt/save_and_format_code_file.sublime-macro"}
  },
  {
    "keys": ["ctrl+s"],
    "command": "save",
    "args": { "async": true }
  }
]
```

### Add new formatters

You add new formatters or override the settings for an existing one. All you
have to do is a new key that identifiers the formatter to `formatters`, and the
related configuration using the same key. So, let’s say you want add a formatter
called `txtfmt`. The user configuration file could be something like this:

```json5
{
  overrides: {
    txtfmt: {
      // The command that will be executed for format files.
      // The special variables are:
      //
      // - `$config`: the full path to the configuration file we found.
      // - `$file`: the full path to the file that’s being formatted.
      command: ["txtfmt", "--fix", "--config", "$config", "$file"],

      // The scopes that will be considered when formatting
      scopes: ["text.plain"],

      // Additional flags when running in debug mode.
      // If the formatter doesn’t have a debug mode, you may set this to an empty
      // array.
      debug: ["--debug"],

      // When no custom config file exists, use a default config file.
      default_config: null,

      // Config files that will be looked up on the root of the project.
      // If the formatter doesn’t require a config file (or is automatically
      // inferred by the formatter), you may want to set this to an empty array.
      config_files: ["txtfmt.config.json"],
    },
  },

  formatters: ["gofmt", "rubocop", "prettier", "eslint", "txtfmt"],
}
```

> **Note**
>
> When overriding existing commands, you only need to define the keys that are
> changing; there's no need to add all options.

### Using version managers

If you use version managers like [asdf](https://asdf-vm.com), you may need to
set the command to the full path. The following example shows how to override
[RuboCop](https://rubocop.org)'s command to use the shim:

```json
{
  "overrides": {
    "rubocop": {
      "command": [
        "/Users/fnando/.asdf/shims/rubocop",
        "--auto-correct-all",
        "--config",
        "$config",
        "$file"
      ]
    }
  }
}
```

> **Note**
>
> Commands are always executed from the root directory of your project.

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
