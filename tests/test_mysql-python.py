from __future__ import absolute_import

import logging
import os

import MySQLdb
from nose.tools import assert_equals

from instana import internal_tracer as tracer
from instana.util import to_json

logger = logging.getLogger(__name__)


if 'MYSQL_HOST' in os.environ:
    mysql_host = os.environ['MYSQL_HOST']
elif 'TRAVIS_MYSQL_HOST' in os.environ:
    mysql_host = os.environ['TRAVIS_MYSQL_HOST']
else:
    mysql_host = '127.0.0.1'

if 'MYSQL_PORT' in os.environ:
    mysql_port = int(os.environ['MYSQL_PORT'])
else:
    mysql_port = 3306

if 'MYSQL_DB' in os.environ:
    mysql_db = os.environ['MYSQL_DB']
else:
    mysql_db = "travis_ci_test"

if 'MYSQL_USER' in os.environ:
    mysql_user = os.environ['MYSQL_USER']
else:
    mysql_user = "root"

if 'MYSQL_PW' in os.environ:
    mysql_pw = os.environ['MYSQL_PW']
elif 'TRAVIS_MYSQL_PASS' in os.environ:
    mysql_pw = os.environ['TRAVIS_MYSQL_PASS']
else:
    mysql_pw = None

create_table_query = 'CREATE TABLE IF NOT EXISTS users(id serial primary key, \
                      name varchar(40) NOT NULL, email varchar(40) NOT NULL)'

db = MySQLdb.connect(host=mysql_host, port=mysql_port,
                     user=mysql_user, passwd=mysql_pw,
                     db=mysql_db)
db.cursor().execute(create_table_query)
db.close()


class TestMySQLPython:
    def setUp(self):
        logger.warn("MySQL connecting: %s:<pass>@%s:3306/%s", mysql_user, mysql_host, mysql_db)
        self.db = MySQLdb.connect(host=mysql_host, port=mysql_port,
                                  user=mysql_user, passwd=mysql_pw,
                                  db=mysql_db)
        self.cursor = self.db.cursor()
        self.recorder = tracer.recorder
        self.recorder.clear_spans()
        tracer.cur_ctx = None

    def tearDown(self):
        """ Do nothing for now """
        # after each test, tracer context should be None (not tracing)
        # assert_equals(None, tracer.current_context())
        return None

    def test_vanilla_query(self):
        self.cursor.execute("""SELECT 1""")
        result = self.cursor.fetchone()
        assert_equals((1L,), result)

    def test_basic_query(self):
        span = tracer.start_span('test')
        result = self.cursor.execute("""SELECT * from users""")
        rows = self.cursor.fetchone()
        span.finish()

        # import ipdb; ipdb.set_trace()

        assert(result >= 0)

        spans = self.recorder.queued_spans()
        assert_equals(2, len(spans))

        db_span = spans[0]
        test_span = spans[1]

        assert_equals("test", test_span.data.sdk.name)
        assert_equals(test_span.t, db_span.t)
        assert_equals(db_span.p, test_span.s)

        assert_equals(None, db_span.error)
        assert_equals(0, db_span.ec)

        assert_equals(db_span.data.sdk.name, "MySQLdb")
        assert_equals(db_span.data.sdk.custom.tags['db.instance'], 'nodedb')
        assert_equals(db_span.data.sdk.custom.tags['db.type'], 'mysql')
        assert_equals(db_span.data.sdk.custom.tags['db.user'], 'root')
        assert_equals(db_span.data.sdk.custom.tags['db.statement'], 'SELECT * from users')
        assert_equals(db_span.data.sdk.custom.tags['peer.address'], 'mysql://mazzo:3306')
        assert_equals(db_span.data.sdk.custom.tags['span.kind'], 'exit')

    def test_basic_insert(self):
        span = tracer.start_span('test')
        result = self.cursor.execute(
                    """INSERT INTO users(name, email) VALUES(%s, %s)""",
                    ('beaker', 'beaker@muppets.com'))

        span.finish()

        assert_equals(1L, result)

        spans = self.recorder.queued_spans()
        assert_equals(2, len(spans))

        db_span = spans[0]
        test_span = spans[1]

        assert_equals("test", test_span.data.sdk.name)
        assert_equals(test_span.t, db_span.t)
        assert_equals(db_span.p, test_span.s)

        assert_equals(None, db_span.error)
        assert_equals(0, db_span.ec)

        assert_equals(db_span.data.sdk.name, "MySQLdb")
        assert_equals(db_span.data.sdk.custom.tags['db.instance'], 'nodedb')
        assert_equals(db_span.data.sdk.custom.tags['db.type'], 'mysql')
        assert_equals(db_span.data.sdk.custom.tags['db.user'], 'root')
        assert_equals(db_span.data.sdk.custom.tags['db.statement'], 'INSERT INTO users(name, email) VALUES(%s, %s)')
        assert_equals(db_span.data.sdk.custom.tags['peer.address'], 'mysql://mazzo:3306')
        assert_equals(db_span.data.sdk.custom.tags['span.kind'], 'exit')