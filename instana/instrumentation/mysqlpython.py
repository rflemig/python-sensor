from __future__ import absolute_import

from .. import internal_tracer
from ..log import logger
from .pep0249 import ConnectionFactory

try:
    import MySQLdb # noqa

    cf = ConnectionFactory(connect_func=MySQLdb.connect, module_name='MySQLdb')

    setattr(MySQLdb, 'connect', cf)
    if hasattr(MySQLdb, 'Connect'):
        setattr(MySQLdb, 'Connect', cf)

    logger.debug("Instrumenting mysql-python")
except ImportError:
    pass
