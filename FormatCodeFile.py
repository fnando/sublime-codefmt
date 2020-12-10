import sublime_plugin
from . import utils


class FormatCodeFileCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    utils.format_code_file(self.view, autosave=False)
