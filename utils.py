import sublime
import os
from subprocess import Popen, PIPE
from pathlib import Path
from platform import python_version
import io
import threading
import json


def settings(key):
    return sublime.load_settings("Codefmt.sublime-settings").get(key)


def find_root_dir_for_file(folders, file_name):
    debug("finding root dir for file:", {
        "folders": folders,
        "file_name": file_name
    })

    if folders is None:
        folders = []

    if len(folders) == 0:
        return os.path.dirname(file_name)

    for folder in folders:
        if folder + "/" in file_name:
            return folder

    if len(folders) > 0:
        return folders[0]

    return os.path.dirname(file_name)


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


def run_command(cmd, root_dir, stdout):
    try:
        result = Popen(cmd,
                       stdout=PIPE,
                       stderr=PIPE,
                       cwd=root_dir,
                       universal_newlines=True)
        result.wait()
        stdout.write(
            json.dumps({
                "stdout": str(result.stdout.read()),
                "stderr": str(result.stderr.read()),
                "returncode": result.returncode
            }))
    except Exception as error:
        stdout.write(
            json.dumps({
                "stdout": "",
                "stderr": "%s: %s" % (error.__class__.__name__, error),
                "returncode": 1
            }))


def run_formatter(view, formatter):
    (row, col) = view.rowcol(view.sel()[0].begin())
    file_name = view.file_name()

    if file_name is None:
        debug("ERROR: view didn't return a file name for some reason")
        return

    formatter_name = formatter["name"]
    window = view.window()
    folders = window.folders()
    root_dir = find_root_dir_for_file(folders, file_name)

    debug("using root dir as", root_dir)
    window.status_message("%s: formatting…" % formatter_name)

    cmd = formatter["command"]

    if is_debug() and formatter["debug"]:
        cmd += formatter["debug"]

    config_file = find_config_file(formatter, root_dir)
    context = expand_formatter_variables(formatter, {
        "file": file_name,
        "config": config_file
    })

    try:
        if not config_file:
            del context["config"]
            index = cmd.index("$config")
            cmd.pop(index)
            cmd.pop(index - 1)
    except ValueError:
        debug("command doesn't expect a config file")

    debug("raw command:", cmd)

    cmd = [sublime.expand_variables(arg, context) for arg in cmd]

    debug("using command:", cmd)

    os.chdir(root_dir)

    debug("cwd is:", os.getcwd())

    stdout = io.StringIO()

    thread = threading.Thread(target=run_command,
                              args=(cmd, root_dir, stdout),
                              name=formatter_name)
    thread.start()
    thread.join(settings("timeout"))

    if thread.is_alive():
        debug("thread was killed, which means command took to long to finish")
        result = {"returncode": -1, "stdout": "", "stderr": ""}
    else:
        output = stdout.getvalue()
        result = json.loads(output)
        debug("command exited with status", result["returncode"])

    success = result["returncode"] == 0

    if is_debug():
        debug("== Command output ==")
        debug("-- stdout ---")
        debug(result["stdout"])

        debug("-- stderr ---")
        debug(result["stderr"])

        debug("== End of Command output ==")

    debug("%s command finished" % (formatter_name))

    if not success:
        debug(
            "some commands exit with nonzero status to indicate that there are issues that couldn't be automatically fixed."
        )

    window.status_message("%s: done." %
                          formatter_name if success else "%s: error." %
                          formatter_name)


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
