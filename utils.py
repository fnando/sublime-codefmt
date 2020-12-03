import sublime, os, subprocess
from pathlib import Path

settings = None

def plugin_loaded():
  global settings
  settings = sublime.load_settings("Code Formatter.sublime-settings")

def is_debug():
  global settings
  return settings.get("debug")

def debug(*args):
  global settings

  if is_debug():
    print("[Code Formatter]", *args)

def format_code_file(view, autosave):
  global settings

  if autosave and not settings.get("format_on_save"):
    debug("autoformat is disabled, skipping.")
    return

  debug("file scopes:", view.scope_name(0).strip().split(" "))
  formatters = find_matching_formatters(view)

  if len(formatters) == 0:
    debug("no formatters found: skipping.")
    return

  debug("formatters to apply:", formatters)

  for formatter in formatters:
    run_formatter(view, formatter)

def run_formatter(view, formatter):
  global settings

  (row, col) = view.rowcol(view.sel()[0].begin())
  filename = view.file_name()
  formatter_name = formatter["name"]
  window = view.window()
  folders = window.folders()

  if len(folders) == 1:
    root_dir = folders[0]
  else:
    root_dir = os.path.dirname(filename)

  debug("using root dir as", root_dir)
  window.status_message("%s: formatting…" % formatter_name)

  command = formatter["command"]

  if is_debug() and formatter["debug"]:
    command += formatter["debug"]

  config_file = find_config_file(formatter, root_dir)

  try:
    index = command.index("$config")

    if config_file:
      command[index] = config_file
    else:
      command.pop(index)
      command.pop(index - 1)
  except ValueError:
    debug("command doesn't expect a config file")

  command.append(filename)

  debug("using command", command)

  with subprocess.Popen(command, stdout=subprocess.PIPE, cwd=root_dir, universal_newlines=True) as result:
    if is_debug():
      debug("== Command output ==")

      for line in result.stdout:
        debug("=>", line.rstrip())

      debug("== End of Command output ==")

  return_code = result.returncode
  debug("%s command finished with exit(%d)" % (formatter_name, return_code))

  if return_code != 0:
    debug("some commands exit with nonzero status to indicate that there are issues that couldn't be automatically fixed.")

  window.status_message("%s: done." % formatter_name if return_code == 0 else "%s: error." % formatter_name)
  view.sel().add(sublime.Region(view.text_point(row, col)))

def find_matching_formatters(view):
  global settings

  enabled_formatters = settings.get("formatters")
  debug("enabled formatters:", enabled_formatters)

  formatters = []

  for name in enabled_formatters:
    formatter = settings.get(name)

    if formatter is None:
      debug(formatter, "settings is missing")
      next

    matched = True in [view.match_selector(0, scope) for scope in formatter["scopes"]]

    if matched:
      formatter = formatter.copy()
      formatter.update({"name": name})
      formatters.append(formatter)

  return formatters

def find_config_file(formatter, root_dir):
  for file_name in formatter["config_files"]:
    config_file = os.path.join(root_dir, file_name)

    if Path(config_file).is_file():
      return config_file

  debug("no config file found:", formatter["config_files"])

  if "default_config" not in formatter:
    debug("no default config file set")
    return

  if not formatter["default_config"]:
    debug("no default config file set")
    return

  default_config = os.path.realpath(
    os.path.join(
      sublime.packages_path(),
      "..",
      formatter["default_config"]
    )
  )

  if Path(default_config).is_file():
    return default_config
  else:
    debug("default config file not found:", default_config)
