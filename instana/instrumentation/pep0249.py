# This is a wrapper for PEP-0249: Python Database API Specification v2.0
import opentracing.ext.tags as ext
import wrapt

from .. import internal_tracer


class CursorWrapper(wrapt.ObjectProxy):
    __slots__ = ('_module_name', '_connect_params', '_cursor_params')

    def __init__(self, cursor, module_name,
                 connect_params=None, cursor_params=None):
        super(CursorWrapper, self).__init__(wrapped=cursor)
        self._module_name = module_name
        self._connect_params = connect_params
        self._cursor_params = cursor_params

    def execute(self, sql, params=None):
        context = internal_tracer.current_context()

        # If we're not tracing, just return
        if context is None:
            return self.__wrapped__.execute(sql, params)

        # import ipdb; ipdb.set_trace()
        span = internal_tracer.start_span(self._module_name, child_of=context)
        span.set_tag(ext.SPAN_KIND, 'exit')
        span.set_tag(ext.DATABASE_INSTANCE, self._connect_params[1]['db'])
        span.set_tag(ext.DATABASE_STATEMENT, sql)
        span.set_tag(ext.DATABASE_TYPE, 'mysql')
        span.set_tag(ext.DATABASE_USER, self._connect_params[1]['user'])
        span.set_tag(ext.PEER_ADDRESS, "mysql://%s:%s" %
                                        (self._connect_params[1]['host'],
                                         self._connect_params[1]['port']))
        result = self.__wrapped__.execute(sql, params)
        span.finish()
        return result

    def executemany(self, sql, seq_of_parameters):
        return self.__wrapped__.executemany(sql, seq_of_parameters)

    def callproc(self, proc_name, params):
        return self.__wrapped__.callproc(proc_name, params)


class ConnectionWrapper(wrapt.ObjectProxy):
    __slots__ = ('_module_name', '_connect_params')

    def __init__(self, connection, module_name, connect_params):
        super(ConnectionWrapper, self).__init__(wrapped=connection)
        self._module_name = module_name
        self._connect_params = connect_params

    def cursor(self, *args, **kwargs):
        return CursorWrapper(
            cursor=self.__wrapped__.cursor(*args, **kwargs),
            module_name=self._module_name,
            connect_params=self._connect_params,
            cursor_params=(args, kwargs) if args or kwargs else None)

    def begin(self):
        return self.__wrapped__.begin()

    def commit(self):
        return self.__wrapped__.commit()

    def rollback(self):
        return self.__wrapped__.rollback()


class ConnectionFactory(object):
    def __init__(self, connect_func, module_name):
        self._connect_func = connect_func
        self._module_name = module_name
        self._wrapper_ctor = ConnectionWrapper

    def __call__(self, *args, **kwargs):
        connect_params = (args, kwargs) if args or kwargs else None

        return self._wrapper_ctor(
            connection=self._connect_func(*args, **kwargs),
            module_name=self._module_name,
            connect_params=connect_params)