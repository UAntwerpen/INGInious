# Plugin for run-code

import os

from flask import send_from_directory

from gettext import gettext as _

from inginious.common.tasks_problems import CodeProblem
from inginious.frontend.task_problems import DisplayableCodeProblem
from inginious.frontend.pages.utils import INGIniousPage

PATH_TO_PLUGIN = os.path.abspath(os.path.dirname(__file__))

class RunCodeProblem(CodeProblem):
    """Add a different test set, using code from another problem"""

    @classmethod
    def get_type(cls):
        return "run_code"


class DisplayableRunCodeProblem(RunCodeProblem, DisplayableCodeProblem):
    """ A displayable match problem """

    @classmethod
    def get_type_name(cls, language):
        return _("run_code")


class StaticMockPage(INGIniousPage):
    # TODO: Replace by shared static middleware and let webserver serve the files
    def GET(self, path):
        return send_from_directory(os.path.join(PATH_TO_PLUGIN, "static"), path)

    def POST(self, path):
        return self.GET(path)


def init(plugin_manager, client, plugin_config):
    plugin_manager.add_page('/plugins/run_code/static/<path:path>', StaticMockPage.as_view("runcodepage"))
    plugin_manager.add_hook("javascript_header", lambda: "/plugins/run_code/static/run_code.js")
    # Problem types are auto-discovered from DisplayableProblem subclasses.
