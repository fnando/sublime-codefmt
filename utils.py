import sublime
import os
import subprocess
from pathlib import Path
from platform import python_version
import io
from contextlib import redirect_stdout


def settings(key):
    return sublime.load_settings("Codefmt.sublime-settings").get(key)


def find_root_dir_for_file(folders, file_name):
    if len(folders) == 0:
        return os.path.dirname(file_name)

    for folder in folders:
        if folder + "/" in file_name:
            return folder


def is_debug():
    return settings("debug")


def debug(*args):
    if not is_debug():
        return

    print("[codefmt]", *args)


def expand_formatter_variables(formatter, context):
    if "variables" not in formatter:
        return context

    for variable, rules in formatter["variables"].items():
        for rule in rules:
            if "endswith" in rule and True in [
                    context["file"].endswith(input)
                    for input in rule["endswith"]
            ]:
                context[variable] = rule["value"]
                break

    return context


def format_code_file(view, autosave):
    debug("\n\n=================================================\n")
    debug("python version:", python_version())

    if autosave and not settings("format_on_save"):
        debug("autoformat on save is disabled, skipping.")
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
    (row, col) = view.rowcol(view.sel()[0].begin())
    filename = view.file_name()
    formatter_name = formatter["name"]
    window = view.window()
    folders = window.folders()
    root_dir = find_root_dir_for_file(folders, filename)

    debug("using root dir as", root_dir)
    window.status_message("%s: formatting…" % formatter_name)

    command = formatter["command"]

    if is_debug() and formatter["debug"]:
        command += formatter["debug"]

    config_file = find_config_file(formatter, root_dir)
    context = expand_formatter_variables(formatter, {
        "file": filename,
        "config": config_file
    })

    try:
        if not config_file:
            del context["config"]
            index = command.index("$config")
            command.pop(index)
            command.pop(index - 1)
    except ValueError:
        debug("command doesn't expect a config file")

    debug("raw command:", command)

    command = [sublime.expand_variables(arg, context) for arg in command]

    debug("using command:", command)

    os.chdir(root_dir)

    debug("cwd is:", os.getcwd())

    with subprocess.Popen(command,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          cwd=root_dir,
                          universal_newlines=True) as result:
        result.wait()

        if is_debug():
            debug("== Command output ==")
            debug("-- stdout ---")

            for line in result.stdout:
                debug("=>", line.rstrip())

            debug("-- stderr ---")

            for line in result.stderr:
                debug("=>", line.rstrip())

            debug("== End of Command output ==")

    return_code = result.returncode
    debug("%s command finished with exit(%d)" % (formatter_name, return_code))

    if return_code != 0:
        debug(
            "some commands exit with nonzero status to indicate that there are issues that couldn't be automatically fixed."
        )

    window.status_message("%s: done." % formatter_name if return_code ==
                          0 else "%s: error." % formatter_name)


def find_matching_formatters(view):
    enabled_formatters = settings("formatters")
    debug("enabled formatters:", enabled_formatters)

    formatters = []
    overrides = settings("overrides")

    for name in enabled_formatters:
        formatter = settings(name)

        if formatter is None:
            debug(name, "settings is missing")
            next

        matched = True in [
            view.match_selector(0, scope) for scope in formatter["scopes"]
        ]

        if matched:
            override = {}

            if name in overrides:
                override = overrides[name]

            debug(name, "override:", override)

            formatter = formatter.copy()
            formatter.update(override)
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
        os.path.join(sublime.packages_path(), "..",
                     formatter["default_config"]))

    debug("default config file path:", default_config)

    if Path(default_config).is_file():
        return default_config
    else:
        debug("default config file not found:", default_config)
