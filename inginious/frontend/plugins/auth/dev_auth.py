# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Developer login plugin.

    DO NOT enable in production.

    When this module is listed in the ``plugins`` section of the configuration
    file *and* the ``INGINIOUS_DEV_LOGIN`` environment variable is set, it
    exposes ``/dev-login``, which opens a session for a fixed local user
    (creating the account on first use) without going through any external
    authentication provider.

    Configuration entry::

        plugins:
          - plugin_module: inginious.frontend.plugins.auth.dev_auth
            username: tapers          # optional, defaults to "tapers"
            realname: "Tim Apers"     # optional
            email: tapers@dev.local   # optional
"""

import logging
import os

from flask import redirect
from werkzeug.exceptions import Forbidden

from inginious.frontend.models import User
from inginious.frontend.pages.utils import INGIniousPage

_logger = logging.getLogger("inginious.webapp.plugin.dev_auth")

_settings = {"username": "tapers", "realname": "Developer (tapers)", "email": "tapers@dev.local"}


class DevLoginPage(INGIniousPage):
    """ Logs the configured developer user in, bypassing external auth. """

    def GET(self):
        if not os.environ.get("INGINIOUS_DEV_LOGIN"):
            raise Forbidden(description=_("Developer login is disabled."))

        user = User.objects(username=_settings["username"]).first()
        if user is None:
            user = User(username=_settings["username"], realname=_settings["realname"],
                        email=_settings["email"], language="en", tos_accepted=True).save()

        self.user_manager.connect_user(user)
        _logger.warning("Developer login used for user '%s'", _settings["username"])
        return redirect("/")


def init(plugin_manager, _client, conf):
    username = conf.get("username", _settings["username"])
    _settings["username"] = username
    _settings["realname"] = conf.get("realname", "Developer (%s)" % username)
    _settings["email"] = conf.get("email", "%s@dev.local" % username)
    plugin_manager.add_page("/dev-login", DevLoginPage.as_view("devloginpage"))
