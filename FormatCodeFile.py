import sublime_plugin
from . import utils


class FormatCodeFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.run_command("save", {"async": False})
        utils.format_code_file(self.view, autosave=False)
