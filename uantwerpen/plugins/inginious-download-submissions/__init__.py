# Plugin for extra-test
import io
import os
import logging
import pymongo
import tempfile
import tarfile
import zipfile
# import mosspy

from flask import send_from_directory, request, Response, redirect

from inginious.common.tasks_problems import Problem
from inginious.frontend.pages.course_admin.utils import INGIniousSubmissionsAdminPage
from inginious.frontend.task_problems import DisplayableProblem
from inginious.frontend.parsable_text import ParsableText
from inginious.frontend.pages.utils import INGIniousPage

PATH_TO_PLUGIN = os.path.abspath(os.path.dirname(__file__))
PATH_TO_TEMPLATES = os.path.join(PATH_TO_PLUGIN, "templates")


def add_admin_menu(course):  # pylint: disable=unused-argument
    """ Add a menu for jplag analyze in the administration """
    return 'downloadpage', '<i class="fa fa-download"></i>&nbsp; Download Submissions'



class DownloadPage(INGIniousSubmissionsAdminPage):
    def GET_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ GET request """
        course = self.course_factory.get_course(courseid)

        user_input = request.form.copy()
        user_input["users"] = request.form.getlist("users")
        user_input["audiences"] = request.form.getlist("audiences")
        user_input["tasks"] = request.form.getlist("tasks")
        user_input["org_tags"] = request.form.getlist("org_tags")

        params = self.get_input_params(user_input, course, 500)
        return self.show_page(course, params)

    def POST_AUTH(self, courseid):
        """POST REQUEST - Allows display of the diagram"""
        self._logger = logging.getLogger("inginious.webapp.plugins.download")

        self._logger.info("Database: %s" % str(self.database))

        course = self.course_factory.get_course(courseid)
        tasks = course.get_tasks()

        x = request.form.copy()
        x["tasks"] = request.form.getlist("tasks")
        x["users"] = request.form.getlist("users")

        self._logger.info("Selected Tasks: " + str(x["tasks"]))
        self._logger.info("Selected Users:" + str(x["users"]))

        files_added = []

        submissions = self.get_selected_submissions(course, only_tasks=x["tasks"], only_users=x["users"], keep_only_evaluation_submissions=True)

        # Initialize tmp directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir = tmp_dir + "/submissions"
            if not os.path.exists(tmp_dir):
                os.mkdir(tmp_dir)
            for task in x["tasks"]:
                if not os.path.exists(tmp_dir + "/" + task):
                    os.mkdir(tmp_dir + "/" + task)

            archive = tempfile.TemporaryFile()
            tar = tarfile.open(fileobj=archive, mode='w:gz')

            scores = {}

            for sub in submissions:
                user_inputs = self.submission_manager.get_input_from_submission(sub)["input"]
                # Get userid and taskid
                user_id = sub["username"][0]
                task_id = sub["taskid"]
                user_score = sub["grade"] / 10

                # Get expected tasks
                task = course.get_task(task_id)
                sub_dir = task_id + "/" + user_id

                if task_id not in scores:
                    scores[task_id] = []
                scores[task_id].append(str(user_id + "\t" + str(user_score)))

                extension = ""
                if "python" in task.get_environment_id():
                    extension = ".py"
                else: # For now only python and cpp files are allowed
                    extension = ".cpp"

                for pid, problem in user_inputs.items():
                    if pid in task.get_problems_dict().keys():
                        # Set filename
                        task_file = sub_dir + "/" + pid + extension
                        task_input = user_inputs[pid]


                        if isinstance(task_input, dict) and "filename" in task_input:
                            if task_input["filename"].endswith(".zip"):
                                subfile = io.BytesIO(task_input["value"])

                                z_file = zipfile.ZipFile(subfile, "r")
                                for info in z_file.infolist():
                                    if not info.filename.startswith("_") and (info.filename.endswith(".cpp") or
                                                                              info.filename.endswith(".h") or
                                                                              info.filename.endswith(".py")):
                                        b_file = io.BytesIO(z_file.open(info.filename).read())

                                        task_file = sub_dir + "/" + pid + "/"
                                        info = tarfile.TarInfo(name=task_file + info.filename)
                                        info.size = b_file.getbuffer().nbytes
                                        tar.addfile(info, fileobj=b_file)

                                z_file.close()
                            else:
                                subfile = io.BytesIO(task_input['value'])

                                info = tarfile.TarInfo(name=task_file)
                                info.size = subfile.getbuffer().nbytes
                                tar.addfile(info, fileobj=subfile)
                        elif isinstance(task_input, dict):
                            pass
                        elif task_input is not None:
                            task_io = io.BytesIO(task_input.encode('utf-8'))

                            # Add file in tar archive
                            info = tarfile.TarInfo(name=task_file)
                            info.size = task_io.getbuffer().nbytes
                            tar.addfile(info, fileobj=task_io)

                # print("Check for input")
                # for pid, problem in user_inputs.items():
                #     if isinstance(problem, dict) and "filename" in problem:
                #         # Process uploaded file
                #         print("INPUT FILE FOUND")

            # Save results in tar file
            for task_id in scores:
                score = "\n".join(scores[task_id])

                results = io.BytesIO(score.encode('utf-8'))

                info = tarfile.TarInfo(name=task_id + "/results.txt")
                info.size = results.getbuffer().nbytes
                tar.addfile(info, fileobj=results)

            tar.close()
            archive.seek(0)

            # if 'run_plagiarism' in x:
            #     # TODO: Make id as config and language selection as parameter
            #     moss = mosspy.Moss(703078888, "python")
            #     moss.setDirectoryMode(1)
            #
            #     tar = tarfile.open(fileobj=archive, mode='r:gz')
            #
            #     tar_members = tar.getmembers()
            #     with tempfile.TemporaryDirectory() as tmp_dir:
            #         tar.extractall(tmp_dir)
            #
            #         for tar_member in tar_members:
            #             if tar_member.size > 0:
            #                 moss.addFile(tmp_dir + "/" + tar_member.name)
            #
            #         url = moss.send(lambda file_path, display_name: print('*', end='', flush=True))
            #         return redirect(url)
            #
            #     tar.close()
            #     archive.seek(0)

            response = Response(response=archive, content_type='application/x-gzip')
            response.headers['Content-Disposition'] = 'attachment; filename="submissions.tgz"'
            return response




    def get_selected_submissions(self, course,
                                 only_tasks=None, only_tasks_with_categories=None,
                                 only_users=None, only_audiences=None,
                                 with_tags=None,
                                 grade_between=None, submit_time_between=None,
                                 keep_only_evaluation_submissions=False,
                                 keep_only_crashes=False,
                                 sort_by=("submitted_on", True),
                                 limit=None, skip=None):
        """
        All the parameters (excluding course, sort_by and keep_only_evaluation_submissions) can be None.
        If that is the case, they are ignored.

        :param course: the course
        :param only_tasks: a list of task ids. Only submissions on these tasks will be loaded.
        :param only_tasks_with_categories: keep only tasks that have a least one category in common with this list
        :param only_users: a list of usernames. Only submissions from these users will be loaded.
        :param only_audiences: a list of audience ids. Only submissions from users in these will be loaded
        :param with_tags: a list of tags in the form [(tagid, present)], where present is a boolean indicating
               whether the tag MUST be present or MUST NOT be present. If you don't mind if a tag is present or not,
               just do not put it in the list.
        :param grade_between: a tuple of two floating point number or None ([0.0, None], [None, 0.0] or [None, None])
               that indicates bounds on the grade of the retrieved submissions
        :param submit_time_between: a tuple of two dates or None ([datetime, None], [None, datetime] or [None, None])
               that indicates bounds on the submission time of the submission. Format: "%Y-%m-%d %H:%M:%S"
        :param keep_only_evaluation_submissions: True to keep only submissions that are counting for the evaluation
        :param keep_only_crashes: True to keep only submissions that timed out or crashed
        :param sort_by: a tuple (sort_column, ascending) where sort_column is in ["submitted_on", "username", "grade", "taskid"]
               and ascending is either True or False.
        :param limit: an integer representing the maximum number of submission to list.
        :return: a list of submission filling the criterias above.
        """

        filter, best_submissions_list = self.get_submissions_filter(course, only_tasks=only_tasks,
                                                                    only_tasks_with_categories=only_tasks_with_categories,
                                                                    only_users=only_users,
                                                                    only_audiences=only_audiences, with_tags=with_tags,
                                                                    grade_between=grade_between,
                                                                    submit_time_between=submit_time_between,
                                                                    keep_only_evaluation_submissions=keep_only_evaluation_submissions,
                                                                    keep_only_crashes=keep_only_crashes)

        submissions = self.database.submissions.find(filter)
        submissions_count = self.database.submissions.count_documents(filter)

        if sort_by[0] not in ["submitted_on", "username", "grade", "taskid"]:
            sort_by[0] = "submitted_on"
        submissions = submissions.sort(sort_by[0], pymongo.ASCENDING if sort_by[1] else pymongo.DESCENDING)

        if skip is not None and skip < submissions_count:
            submissions.skip(skip)

        if limit is not None:
            submissions.limit(limit)

        out = list(submissions)

        for d in out:
            d["best"] = d["_id"] in best_submissions_list  # mark best submissions

        if limit is not None:
            number_of_pages = submissions_count // limit + (submissions_count % limit > 0)
            return out, submissions_count, number_of_pages
        else:
            return out



    def show_page(self, course, user_input, msg="", error=False):
        # Load task list
        # tasks, user_data, aggregations, tutored_aggregations, \
        # tutored_users, checked_tasks, checked_users, show_aggregations = self.show_page_params(course, user_input)
        users, tutored_users, audiences, tutored_audiences, tasks, limit = self.get_course_params(course,
                                                                                                  user_input)
        print(PATH_TO_PLUGIN + "/templates")
        return self.template_helper.render("download_index.html", template_folder=PATH_TO_TEMPLATES,
                                           course=course, tasks=tasks, users=users, audiences=audiences,
                                           tutored_audiences=tutored_audiences, tutored_users=tutored_users,
                                           old_params=user_input, msg=msg, error=error)


class StaticMockPage(INGIniousPage):
    # TODO: Replace by shared static middleware and let webserver serve the files
    def GET(self, path):
        return send_from_directory(os.path.join(PATH_TO_PLUGIN, "static"), path)

    def POST(self, path):
        return self.GET(path)

def init(plugin_manager, client, plugin_config):
    plugin_manager.add_page('/plugins/download/static/<path:path>', StaticMockPage.as_view("downloadstaticpage"))

    plugin_manager.add_page("/admin/<courseid>/download", DownloadPage.as_view("downloadpage"))

    plugin_manager.add_hook("css", lambda: "/plugins/inginious-download-submissions/static/download_submissions.css")
    plugin_manager.add_hook('course_admin_menu', add_admin_menu)
