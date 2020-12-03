import sublime
import sublime_plugin
from . import utils


class FormatCodeFileOnSave(sublime_plugin.EventListener):
    def on_post_save_async(self, view):
        utils.format_code_file(view, autosave=True)
