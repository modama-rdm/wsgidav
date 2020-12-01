# -*- coding: utf-8 -*-
# (c) 2009-2020 Martin Wendt and contributors; see WsgiDAV https://github.com/mar10/wsgidav
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
"""
Implementation of a domain controller that allows users to authenticate using
only their username. The idea is that there is sufficient firewalling
that only allows nextcloud to access this service.
"""
from __future__ import print_function
import pwd
from wsgidav import util
from wsgidav.dc.base_dc import BaseDomainController


__docformat__ = "reStructuredText"
_logger = util.get_module_logger(__name__)


class UserOnlyDomainController(BaseDomainController):
    def __init__(self, wsgidav_app, config):
        super(UserOnlyDomainController, self).__init__(wsgidav_app, config)

        # auth_conf = config["http_authenticator"]
        dc_conf = config.get("useronly_dc", {})

    def __str__(self):
        return "{}('')".format(self.__class__.__name__)

    def get_domain_realm(self, path_info, environ):
        return "UserOnly()"

    def require_authentication(self, realm, environ):
        return True

    def basic_auth_user(self, realm, user_name, password, environ):
        try:
            user_pwd = pwd.getpwnam(user_name)
            return True  # user found, allow "anonymous" access
        except KeyError as e:
            _logger.warning(
                "useronly.authenticate('{}', '***') failed: {}".format(
                    user_name, str(e)
                )
            )
            return False  # user not found, don't allow access

    def supports_http_digest_auth(self):
        # We don't have access to a plaintext password (or stored hash)
        return False

