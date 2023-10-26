import os
import pwd
import grp
import contextlib


from cachetools import cached, TTLCache

from wsgidav import util
from wsgidav.middleware import BaseMiddleware

DEFAULT_CACHE_TTL = 120
_logger = util.get_module_logger(__name__)


@cached(cache=TTLCache(maxsize=1024, ttl=DEFAULT_CACHE_TTL))
def get_user_pwd(user_name):
    return pwd.getpwnam(user_name)


@cached(cache=TTLCache(maxsize=1024, ttl=DEFAULT_CACHE_TTL))
def get_user_groups(user_name):
    import pysss
    user_pwd = get_user_pwd(user_name)
    user_group_names = pysss.getgrouplist(user_name)
    user_groups = [grp.getgrnam(g).gr_gid
                   for g in user_group_names]
    user_groups.insert(0, user_pwd.pw_gid)
    return user_groups


@cached(cache=TTLCache(maxsize=1024, ttl=DEFAULT_CACHE_TTL))
def get_group_by_id(gid):
    return grp.getgrgid(gid)


@contextlib.contextmanager
def setuid(user_name):
    _logger.info("changing euid to %s", user_name)
    old_groups = os.getgroups()
    user_pwd = get_user_pwd(user_name)
    user_groups = get_user_groups(user_name)
    try:
        try:
            os.setegid(user_pwd.pw_gid)
            os.setgroups(user_groups)
            os.seteuid(user_pwd.pw_uid)

            # debug output:
            gids = os.getgroups()
            gids.insert(0, os.getegid())

            gids_str = ", ".join([
                "%d(%s)" % (gid, get_group_by_id(gid).gr_name)
                for gid in gids
            ])
            _logger.info("want groups: %s", str(user_groups))
            _logger.info("have groups: %s", gids_str)
        except Exception as e:
            _logger.error("error setting gid/uid/groups: %r", str(e))
            _logger.error("groups: %r", user_groups)
            _logger.error("gid: %d, uid: %d", user_pwd.pw_gid, user_pwd.pw_uid)
            raise
        yield
    finally:
        _logger.info("changing euid back to 0")
        os.setegid(0)
        os.seteuid(0)
        os.setgroups(old_groups)


class SuidMiddleware(BaseMiddleware):
    """
    SUID middleware. Put this below the auth middleware.
    """
    def __init__(self, wsgidav_app, next_app, config):
        super().__init__(wsgidav_app, next_app, config)

    def __call__(self, environ, start_response):
        user_name = environ.get('wsgidav.auth.user_name')
        with setuid(user_name=user_name):
            yield from self.next_app(environ, start_response)
