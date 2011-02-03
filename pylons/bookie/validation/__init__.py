import os
import logging
import formencode as fe
from pylons import config

log = logging.getLogger(__name__)


def error_formatter(error):
    return '<span class="form errortext">%s</span>\n' % (
        fe.htmlfill.html_quote(error))


class UserFormNew(fe.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    user_name = fe.validators.Email(not_empty=True, strip=True)
