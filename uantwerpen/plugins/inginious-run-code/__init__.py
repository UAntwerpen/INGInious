# Plugin for extra-test

import os

from flask import send_from_directory

from inginious.common.tasks_problems import CodeProblem
from inginious.frontend.task_problems import DisplayableCodeProblem
from inginious.frontend.parsable_text import ParsableText
from inginious.frontend.pages.utils import INGIniousPage

PATH_TO_PLUGIN = os.path.abspath(os.path.dirname(__file__))

class RunCodeProblem(CodeProblem):
    """Add a different test set, using code from another problem"""

    @classmethod
    def get_type(cls):
        return "run_code"


class DisplayableRunCodeProblem(RunCodeProblem, DisplayableCodeProblem):
    """ A displayable match problem """

    # def __init__(self, problemid, content, translations, taskfs):
    #     super(DisplayableRunCodeProblem, self).__init__(problemid, content, translations, taskfs)

    @classmethod
    def get_type_name(cls, language):
        return _("run_code")

    # def adapt_input_for_backend(self, input_data):
    #     return input_data
    #
    # def show_input(self, template_helper, language, seed):
    #     """ Show BasicCodeProblem and derivatives """
    #     header = ParsableText(self.gettext(language,self._header), "rst",
    #                           translation=self.get_translation_obj(language))
    #     return template_helper.render("tasks/code.html", inputId=self.get_id(), header=header,
    #                                   lines=8, maxChars=0, language=self._language, optional=self._optional,
    #                                   default=self._default)
    #
    # @classmethod
    # def show_editbox(cls, template_helper, key, language):
    #     return template_helper.render("course_admin/subproblems/code.html", key=key, multiline=True)
    #
    # @classmethod
    # def show_editbox_templates(cls, template_helper, key, language):
    #     return ""


class StaticMockPage(INGIniousPage):
    # TODO: Replace by shared static middleware and let webserver serve the files
    def GET(self, path):
        return send_from_directory(os.path.join(PATH_TO_PLUGIN, "static"), path)

    def POST(self, path):
        return self.GET(path)


def init(plugin_manager, client, plugin_config):
    plugin_manager.add_page('/plugins/run_code/static/<path:path>', StaticMockPage.as_view("runcodepage"))
    plugin_manager.add_hook("javascript_header", lambda: "/plugins/run_code/static/run_code.js")
    # course_factory.get_task_factory().add_problem_type(DisplayableRunCodeProblem)
