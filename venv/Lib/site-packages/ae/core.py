"""
application core constants, helper functions and base classes
=============================================================

This module declares practical constants, base classes as well as tiny helper functions
making the code of your application (and other modules of this package) much cleaner.

core constants
--------------

For to set the debug level of your application run-time you can use one of
the constants :data:`DEBUG_LEVEL_DISABLED`, :data:`DEBUG_LEVEL_ENABLED`
or :data:`DEBUG_LEVEL_VERBOSE`. The debug level of your application can be either
set in your code or optionally data-driven externally (using the :ref:`config-files`
or :ref:`config-options` of the module :mod:`.console`).

Short names for all debug level constants are provided by the dict :data:`DEBUG_LEVELS`.

For to use the :mod:`python logging module <logging>` in conjunction with this module
the constant :data:`LOGGING_LEVELS` is providing a mapping between the debug levels
and the python logging levels.

The encoding of strings into byte-strings (for to output them to the console/stdout or
to file contents) can be tricky sometimes. For to not lose any logging output because
of invalid characters this module will automatically handle any :exc:`UnicodeEncodeError`
exception for you. Invalid characters will in case of this error be converted
to the default encoding (specified by :data:`DEF_ENCODING`) with the default error
handling method specified by :data:`DEF_ENCODE_ERRORS`.


core helper functions
---------------------

For to encode unicode strings to other codecs the functions :func:`force_encoding` and
:func:`to_ascii` can be used. The :func:`print_out` function, which is fully compatible to pythons
:func:`print`, is using these encode helpers for to auto-correct invalid characters.

:func:`hide_dup_line_prefix` is very practical if you want to remove or hide redundant
line prefixes in your log files, to make them better readable.

The :func:`round_traditional` function get provided by this module for traditional rounding of
float values. The function signature is fully compatible to Python's :func:`round` function.


application base classes
------------------------

The classes :class:`AppBase` and :class:`SubApp` are applying logging and debugging features
to your application. Create in your application one instance of :class:`AppBase` for to represent
the main application task. If your application needs a separate logging/debugging configuration for
sub-threads or sub-tasks then create an :class:`SubApp` instance for each of these sub-apps.

Sub-apps are not tied to any fix use-case. They can be created for example for each sub-task or
application thread. You could also create a :class:`SubApp` instance for each of your external systems,
like a database server or for to connect your application onto different test environments
or to your live an your production system (e.g. for system comparison and maintenance).

Both application classes are automatically catching and handling any exceptions and run-time
errors: only if any critical exception/error cannot be handled then the :meth:`~AppBase.shutdown`
method will make sure that all sub-apps and threads get terminated and joined.
Additionally all print-out buffers will be flushed for to include all the info
of the critical error (the last debug and error messages) into the
standard error/output and into any activated log files.


basic usage of an application base class
........................................

At the top of your python application main file/module create an instance of the class :class:`AppBase`::

    \"\"\"  docstring at the top of the main module of your application  \"\"\"
    from ae.core import AppBase

    __version__ = '1.2.3'

    ca = AppBase()

In the above example the :class:`AppBase` instance will automatically use the docstring of the
module as application title and the string in the module variable __version___ as application version.
To overwrite these defaults pass your application title and version string via the
arguments :paramref:`~AppBase.app_title` and :paramref:`~AppBase.app_version`
to the instantiation of :class:`AppBase`::

    ca = AppBase("title of this app instance", app_version='3.2.1')

Other automatically initialized instance attributes of :class:`AppBase` are documented underneath
in the :class:`class docstring <AppBase>`. They include e.g.
the :attr:`date and time when the instance got created <AppBase.startup_beg>`,
the :attr:`name/id of this application instance <AppBase.app_name>` or
the :attr:`startup folder or application path <AppBase.app_path>`.


application class hierarchy
...........................

For most use cases you will not instantiate from :class:`AppBase` directly - instead you will
instantiate one of the extended application classes that are inherited from this base class.

The class :class:`~ae.console.ConsoleApp` e.g. inherits from :class:`AppBase` and is adding
configuration options and variables to it. So in your console application it is recommended to directly
use instances of :class:`~ae.console.ConsoleApp` instead of :class:`AppBase`.

For applications with an GUI use instead one of the classes :class:`~ae.kivy_app.KivyApp`,
:class:`~ae.enaml_app.EnamlApp` or :class:`~ae.dabo_app.DaboApp`.


application logging
-------------------

Print-outs are an essential tool for the debugging and logging of your application at run-time. In python
the print-outs are done with the :func:`print` function or with the python :mod:`logging` module. These
print-outs get per default send to the standard output and error streams of your OS and so displayed on
your system console/shell. The :func:`print_out` function and the :meth:`~AppBase.print_out` method of
this :mod:`.core` module are adding two more sophisticated ways for print-outs to the console/log-files.

Using :class:`AppBase` is making the logging much easier and also ensures that print-outs of any
imported library or package will be included within your log files. This is done by redirecting the
standard output and error streams to your log files with the help of the :class:`_PrintingReplicator`
class.

Head-less server applications like web servers are mostly not allowed to use the standard output streams.
For some these applications you could redirect the standard output and error streams to a log file by
using the OS redirection character (>)::

    python your_application.py >log_std_out.log 2>log_std_err.log

But because most web servers doesn't allow you to use this redirection, you can alternatively specify
the :paramref:`~AppBase.suppress_stdout` parameter as True in the instantiation of an :class:`AppBase`
instance. Additionally you can call the :meth:`~AppBase.init_logging` method for to activate a log file.
After that all print-outs of your application and libraries will only appear in your log file.

Also in complex applications, where huge print-outs to the console can get lost easily, you want to use
a log file instead. But even a single log file can get messy to read, especially for multi-threaded
server applications. For that :class:`SubApp` is allowing you to create for each thread a separate
sub-app instance with its own log file.

Using this module ensures that any crashes or freezes happening in your application will be fully logged.
Apart from the gracefully handling of :exc:`UnicodeEncodeError` exceptions, the
:mod:`Python faulthandler <faulthandler>` will be enabled automatically for to also catch
system errors and to dump a traceback of them to the console and any activated log file.


activate ae log file
....................

.. _ae-log-file:

Ae Log Files are text files using by default the encoding of your OS console/shell. To activate the
redirection of your applications print-outs into a ae log file for a :class:`AppBase` instance you
simply specify the file name of the log file in the :meth:`~AppBase.init_logging` method call::

    app = AppBase()
    app.init_logging(log_file_name='my_log_file.log')


activate ae logging features
............................

For multi-threaded applications you can include the thread-id of the printing thread automatically
into your log files. For that you have to pass a True value to the
:paramref:`~AppBase.multi_threading` argument. For to additionally also suppress any print-outs
to the standard output/error streams pass True to the :paramref:`~AppBase.suppress_stdout` argument::

    app = AppBase(multi_threading=True, suppress_stdout=True)
    app.init_logging(log_file_name='my_log_file.log')

The ae log files provided by this module are automatically rotating if the size of an log file
succeeds the value in MBytes defined in the :data:`LOG_FILE_MAX_SIZE`. For to adapt this value
to your needs you can specify the maximum log file size in MBytes with the argument
:paramref:`~AppBase.init_logging.log_file_size_max` in your call of :meth:`~AppBase.init_logging`::

    app.init_logging(log_file_name='my_log_file.log', log_file_size_max=9.)

By using the :class:`~ae.console.ConsoleApp` class instead of :class:`AppBase` you can
alternatively store the logging configuration of your application within a
:ref:`configuration variable <config-variables>` or a
:ref:`configuration option <config-options>`.
The order of precedence for to find the appropriate logging configuration of each
app instance is documented :meth:`here <ae.console.ConsoleApp._init_logging>` .


using python logging module
...........................

If you prefer to use instead the python logging module for the print-outs of your application,
then pass a :mod:`python logging configuration dictionary <logging.config>` with the individual
configuration of your logging handlers, files and loggers to the
:paramref:`~AppBase.init_logging.py_logging_params` argument of the
:meth:`~AppBase.init_logging` method::

    app.init_logging(py_logging_params=my_py_logging_config_dict)

Passing the python logging configuration dictionary to one of the :class:`AppBase`
instances created by your application will automatically disable the ae log file of this
instance.


application debugging
---------------------

For to use the debug features of :mod:`~.core` you simple have to import the needed
:ref:`debug level constant <debug-level-constants>` for to pass it at instantiation of
your :class:`AppBase` or :class:`SubApp` class to the :paramref:`~AppBase.debug_level` argument:

    app = AppBase(..., debug_level= :data:`DEBUG_LEVEL_ENABLED`)     # same for :class:`SubApp`

By passing :data:`DEBUG_LEVEL_ENABLED` the print-outs (and log file contents) will be more detailed,
and even more verbose if you use instead the debug level :data:`DEBUG_LEVEL_VERBOSE`.

The debug level can be changed at any time in your application code by directly assigning
the new debug level to the :attr:`~AppBase.debug_level` property. If you prefer to change
the (here hard-coded) debug levels dynamically, then use the :class:`~.console.ConsoleApp` instead
of :class:`AppBase`, because :class:`~.console.ConsoleApp` provides this property as a
:ref:`configuration file variable <config-variables>`
and :ref:`commend line option <config-options>`. This way you can
specify :ref:`the actual debug level <pre-defined-config-options>` without the need
to change (and re-build) your application code.
"""
import datetime
import faulthandler
import logging
import logging.config
import os
import sys
import threading
import unicodedata
import weakref

from io import StringIO
from typing import Any, AnyStr, Dict, List, Optional, TextIO, Tuple, Union, cast

from ae.system import DATE_TIME_ISO                                         # type: ignore
from ae.paths import app_name_guess, PATH_PLACEHOLDERS                      # type: ignore


__version__ = '0.1.42'                          #: actual version of this portion/package/module


DEF_ENCODE_ERRORS: str = 'backslashreplace'     #: default encode error handling for UnicodeEncodeErrors
DEF_ENCODING: str = 'ascii'
""" core encoding that will always work independent from destination (console, file system, XMLParser, ...).

.. _debug-level-constants:

"""
# DON'T RE-ORDER: using DEF_ENCODING doc-string as _debug-level-constants sphinx hyperlink to following DEBUG_ constants
DEBUG_LEVEL_DISABLED: int = 0       #: lowest debug level - only display logging levels ERROR/CRITICAL.
DEBUG_LEVEL_ENABLED: int = 1        #: minimum debugging info - display logging levels WARNING or higher.
DEBUG_LEVEL_VERBOSE: int = 2        #: verbose debug info - display logging levels INFO/DEBUG or higher.

DEBUG_LEVELS: Dict[int, str] = {DEBUG_LEVEL_DISABLED: 'disabled', DEBUG_LEVEL_ENABLED: 'enabled',
                                DEBUG_LEVEL_VERBOSE: 'verbose'}
""" numeric ids and names of all supported debug levels. """

LOGGING_LEVELS: Dict[int, int] = {DEBUG_LEVEL_DISABLED: logging.WARNING, DEBUG_LEVEL_ENABLED: logging.INFO,
                                  DEBUG_LEVEL_VERBOSE: logging.DEBUG}
""" association between ae debug levels and python logging levels. """

HIDDEN_CREDENTIALS = ('password', 'token')      #: credential keys that are hidden in print/repr output (not if verbose)


def force_encoding(text: AnyStr, encoding: str = DEF_ENCODING, errors: str = DEF_ENCODE_ERRORS) -> str:
    """ force/ensure the encoding of text (str or bytes) without any UnicodeDecodeError/UnicodeEncodeError.

    :param text:        text as str/bytes.
    :param encoding:    encoding (def= :data:`DEF_ENCODING`).
    :param errors:      encode error handling (def= :data:`DEF_ENCODE_ERRORS`).

    :return:            text as str (with all characters checked/converted/replaced for to be encode-able).
    """
    enc_str: bytes = cast(str, text).encode(encoding=encoding, errors=errors) if isinstance(text, str) else text
    return enc_str.decode(encoding=encoding)


def hide_dup_line_prefix(last_line: str, current_line: str) -> str:
    """ replace duplicate characters at the begin of two strings with spaces.

    :param last_line:       last line string (e.g. the last line of text/log file).
    :param current_line:    current line string.
    :return:                current line string but duplicate characters at the begin are replaced by space characters.
    """
    idx = 0
    min_len = min(len(last_line), len(current_line))
    while idx < min_len and last_line[idx] == current_line[idx]:
        idx += 1
    return " " * idx + current_line[idx:]


def round_traditional(num_value: float, num_digits: int = 0) -> float:
    """ round numeric value traditional.

    Needed because python round() is working differently, e.g. round(0.075, 2) == 0.07 instead of 0.08
    inspired by https://stackoverflow.com/questions/31818050/python-2-7-round-number-to-nearest-integer.

    :param num_value:   float value to be round.
    :param num_digits:  number of digits to be round (def=0 - rounds to an integer value).

    :return:        rounded value.
    """
    return round(num_value + 10 ** (-len(str(num_value)) - 1), num_digits)


def to_ascii(unicode_str: str) -> str:
    """ converts unicode string into ascii representation.

    Useful for fuzzy string compare; inspired by MiniQuark's answer
    in: https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string

    :param unicode_str:     string to convert.
    :return:                converted string (replaced accents, diacritics, ... into normal ascii characters).
    """
    nfkd_form = unicodedata.normalize('NFKD', unicode_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


MAX_NUM_LOG_FILES: int = 69                         #: maximum number of :ref:`ae log files <ae-log-file>`
LOG_FILE_MAX_SIZE: int = 15                         #: max. size in MB of rotating :ref:`ae log files <ae-log-file>`
LOG_FILE_IDX_WIDTH: int = len(str(MAX_NUM_LOG_FILES)) + 3
""" width of rotating log file index within log file name; adding +3 to ensure index range up to factor 10^3. """

ori_std_out: TextIO = sys.stdout                    #: original sys.stdout on app startup
ori_std_err: TextIO = sys.stderr                    #: original sys.stderr on app startup

log_file_lock: threading.RLock = threading.RLock()  #: log file rotation multi-threading lock


_logger = None       #: python logger for this module gets lazy/late initialized and only if requested by caller


def logger_late_init():
    """ check if logging modules got initialized already and if not then do it now. """
    global _logger
    if not _logger:
        _logger = logging.getLogger(__name__)


_multi_threading_activated: bool = False            #: flag if threading is used in your application


def activate_multi_threading():
    """ activate multi-threading for all app instances (normally done at main app startup). """
    global _multi_threading_activated
    _multi_threading_activated = True


def _deactivate_multi_threading():
    """ disable multi threading (needed for to reset app environment in unit testing). """
    global _multi_threading_activated
    _multi_threading_activated = False


def print_out(*objects, sep: str = " ", end: str = "\n", file: Optional[TextIO] = None, flush: bool = False,
              encode_errors_def: str = DEF_ENCODE_ERRORS, logger: Optional['logging.Logger'] = None,
              app: Optional['AppBase'] = None, **kwargs):
    """ universal/unbreakable print function - replacement for the :func:`built-in python function print() <print>`.

    :param objects:             tuple of objects to be printed. If the first object is a string that
                                starts with a \\\\r character then the print-out will be only sent
                                to the standard output (and will not be added to any active log files -
                                see also :paramref:`~print_out.end` argument).
    :param sep:                 separator character between each printed object/string (def=" ").
    :param end:                 finalizing character added to the end of this print-out (def="\\\\n").
                                Pass \\\\r for to suppress the print-out into :ref:`ae log file <ae-log-file>`
                                or to any activated python logger
                                - useful for console/shell processing animation (see :meth:`.tcp.TcpServer.run`).
    :param file:                output stream object to be printed to (def=None which will use standard output streams).
                                If given then the redirection to all active log files and python logging loggers
                                will be disabled (even if the :paramref:`~print_out.logger` argument is specified).
    :param flush:               flush stream after printing (def=False).
    :param encode_errors_def:   default error handling for to encode (def=:data:`DEF_ENCODE_ERRORS`).
    :param logger:              used logger for to output `objects` (def=None). Ignored if the
                                :paramref:`print_out.file` argument gets specified/passed.
    :param app:                 the app instance from where this print-out got initiated.
    :param kwargs:              catch unsupported kwargs for debugging (all items will be printed to all
                                the activated logging/output streams).

    This function is silently handling and auto-correcting string encode errors for output/log streams which are
    not supporting unicode. Any instance of :class:`AppBase` is providing this function as a method with the
    :func:`same name <AppBase.print_out>`). It is recommended to call/use this instance method instead of this function.

    In multi-threaded applications this function prevents dismembered/fluttered print-outs from different threads.

    This function has an alias named :func:`.po`.
    """
    processing = end == "\r" or (objects and str(objects[0]).startswith('\r'))  # True if called by Progress.next()
    enc = getattr(file or ori_std_out if processing else sys.stdout, 'encoding', 'utf-8')
    use_py_logger = False

    main_app = main_app_instance()
    if main_app:
        file = main_app.log_file_check(file)    # check if late init of logging system is needed
    if app and app != main_app:
        file = app.log_file_check(file)         # check sub-app suppress_stdout/log file status and rotation
    else:
        app = main_app

    if processing:
        file = ori_std_out
    elif logger is not None and file is None and (
            app and app.py_log_params and main_app != app or main_app and main_app.py_log_params):
        use_py_logger = True
        logger_late_init()

    if kwargs:
        objects += (f"\n   *  EXTRA KWARGS={kwargs}", )

    retries = 2
    while retries:
        try:
            print_strings = tuple(map(lambda _: str(_).encode(enc, errors=encode_errors_def).decode(enc), objects))
            if use_py_logger or _multi_threading_activated:
                # concatenating objects also prevents fluttered log file content in multi-threading apps
                # .. see https://stackoverflow.com/questions/3029816/how-do-i-get-a-thread-safe-print-in-python-2-6
                # .. and https://stackoverflow.com/questions/50551637/end-key-in-print-not-thread-safe
                print_one_str = sep.join(print_strings)
                sep = ""
                if end and (not use_py_logger or end != '\n'):
                    print_one_str += end
                    end = ""
                print_strings = (print_one_str, )

            if use_py_logger:
                debug_level = app.debug_level if app else DEBUG_LEVEL_VERBOSE
                if logger:      # mypy insists to have this extra check, although use_py_logger is including logger
                    logger.log(level=LOGGING_LEVELS[debug_level], msg=print_strings[0])
            else:
                print(*print_strings, sep=sep, end=end, file=file, flush=flush)
            break
        except UnicodeEncodeError:
            fixed_objects = list()
            for obj in objects:
                if not isinstance(obj, str) and not isinstance(obj, bytes):
                    obj = str(obj)
                if retries == 2:
                    obj = force_encoding(obj, encoding=enc)
                else:
                    obj = to_ascii(obj)
                fixed_objects.append(obj)
            objects = tuple(fixed_objects)
            retries -= 1


po = print_out              #: alias of function :func:`.print_out`


APP_KEY_SEP: str = '@'      #: separator character used in :attr:`~AppBase.app_key` of :class:`AppBase` instance

# Had to use type comment because the following line is throwing an error in the Sphinx docs make:
# _app_instances: weakref.WeakValueDictionary[str, "AppBase"] = weakref.WeakValueDictionary()
_app_instances = weakref.WeakValueDictionary()   # type: weakref.WeakValueDictionary[str, AppBase]
""" dict that is weakly holding references to all :class:`AppBase` instances created at run time.

Gets automatically initialized in :meth:`AppBase.__init__` for to allow log file split/rotation
and debug_level access at application thread or module level.

The first created :class:`AppBase` instance is called the main app instance. :data:`_main_app_inst_key`
stores the dict key of the main instance.
"""
_main_app_inst_key: str = ''    #: key in :data:`_app_instances` of main :class:`AppBase` instance

app_inst_lock: threading.RLock = threading.RLock()  #: app instantiation multi-threading lock


def main_app_instance() -> Optional['AppBase']:
    """ determine the main instance of the :class:`AppBase` in the current running application.

    :return:    main/first-instantiated :class:`AppBase` instance or None (if app is not fully initialized yet).
    """
    with app_inst_lock:
        return _app_instances.get(_main_app_inst_key)


def _register_app_instance(app: 'AppBase'):
    """ register new :class:`AppBase` instance in :data:`_app_instances`.

    :param app:         :class:`AppBase` instance to register
    """
    with app_inst_lock:
        global _app_instances, _main_app_inst_key
        msg = f"register_app_instance({app}) expects "
        assert app not in _app_instances.values(), msg + "new instance - this app got already registered"

        key = app.app_key
        assert key and key not in _app_instances, \
            msg + f"non-empty, unique app key (app_name+sys_env_id=={key} keys={list(_app_instances.keys())})"

        cnt = len(_app_instances)
        if _main_app_inst_key:
            assert cnt > 0, f"No app instances registered but main app key is set to {_main_app_inst_key}"
        else:
            assert cnt == 0, f"{cnt} sub-apps {list(_app_instances.keys())} found after main app remove"
            _main_app_inst_key = key
        _app_instances[key] = app


def _unregister_app_instance(app_key: str) -> Optional['AppBase']:
    """ unregister/remove :class:`AppBase` instance from within :data:`_app_instances`.

    :param app_key:     app key of the instance to remove.
    :return:            removed :class:`AppBase` instance.
    """
    with app_inst_lock:
        global _app_instances, _main_app_inst_key
        app = _app_instances.pop(app_key, None)
        cnt = len(_app_instances)
        if app_key == _main_app_inst_key:
            _main_app_inst_key = ''
            assert cnt == 0, f"{cnt} sub-apps {list(_app_instances.keys())} found after main app {app_key}{app} remove"
        elif _main_app_inst_key:
            assert cnt > 0, f"Unregistered last app {app_key}/{app} but was not the main app {_main_app_inst_key}"
        return app


def _shut_down_sub_app_instances(timeout: Optional[float] = None):
    """ shut down all :class:`SubApp` instances.

    :param timeout:     timeout float value in seconds used for the :class:`SubApp` shutdowns and for the acquisition
                        of the threading locks of :data:`the ae log file <log_file_lock>` and the :data:`app instances
                        <app_inst_lock>`.
    """
    aqc_kwargs: Dict[str, Any] = (dict(blocking=False) if timeout is None else dict(timeout=timeout))
    blocked = app_inst_lock.acquire(**aqc_kwargs)
    main_app = main_app_instance()
    for app in list(_app_instances.values()):   # list is needed because weak ref dict get changed in loop
        if app is not main_app:
            app.shutdown(timeout=timeout)
    if blocked:
        app_inst_lock.release()


class _PrintingReplicator:
    """ replacement of standard/error stream replicating print-outs to all active logging streams (log files/buffers).
    """
    def __init__(self, sys_out_obj: TextIO = ori_std_out) -> None:
        """ initialise a new T-stream-object

        :param sys_out_obj:     standard output/error stream to be replicated (def=sys.stdout)
        """
        self.sys_out_obj = sys_out_obj

    def write(self, any_str: AnyStr) -> None:
        """ write string to ae logging and standard output streams.

        Automatically suppressing UnicodeEncodeErrors if console/shell or log file has different encoding
        by forcing re-encoding with DEF_ENCODE_ERRORS.

        :param any_str:     string to output.
        """
        message = cast(bytes, any_str).decode() if isinstance(any_str, bytes) else any_str
        app_streams: List[Tuple[Optional[AppBase], TextIO]] = list()
        with log_file_lock, app_inst_lock:
            for app in list(_app_instances.values()):
                stream = app.log_file_check(app.active_log_stream)  # check if log rotation or buf-to-file-switch needed
                if stream:
                    app_streams.append((app, stream))
            if not self.sys_out_obj.closed:
                app_streams.append((main_app_instance(), self.sys_out_obj))

            if message and message[0] != '\n' and message[-1] == '\n':
                message = '\n' + message[:-1]
            log_lines = message.split('\n')
            for app_or_none, stream in app_streams:
                line_prefix = '\n' + (app_or_none.log_line_prefix() if app_or_none else '')
                app_msg = line_prefix.join(log_lines)
                try:
                    stream.write(app_msg)
                except UnicodeEncodeError:
                    stream.write(force_encoding(app_msg, encoding=stream.encoding))

    def __getattr__(self, attr: str) -> Any:
        """ get attribute value from standard output stream.

        :param attr:    name of the attribute to retrieve/return.
        :return:        value of the attribute.
        """
        return getattr(self.sys_out_obj, attr)


_app_threads = weakref.WeakValueDictionary()   # type: weakref.WeakValueDictionary[int, threading.Thread]
""" weak dict for to keep the references of all application threads. Added for to prevent
the joining of unit testing threads in the test teardown (resetting app environment). """


def _register_app_thread():
    """ add new app thread to _app_threads if not already added. """
    global _app_threads
    tid = threading.get_ident()
    if tid not in _app_threads:
        _app_threads[tid] = threading.current_thread()


def _join_app_threads(timeout: Optional[float] = None):
    """ join/finish all app threads and finally deactivate multi-threading.

    :param timeout:     timeout float value in seconds for thread joining (def=None - block/no-timeout).

    .. note::
       This function has to be called by the main app instance only.
    """
    global _app_threads
    main_thread = threading.current_thread()
    for app_thread in list(_app_threads.values()):     # threading.enumerate() also includes PyCharm/pytest threads
        if app_thread is not main_thread:
            po(f"  **  joining thread id <{app_thread.ident: >6}> name={app_thread.getName()}", logger=_logger)
            app_thread.join(timeout)
            if app_thread.ident is not None:     # mypy needs it because ident is Optional
                _app_threads.pop(app_thread.ident)
    _deactivate_multi_threading()


class AppBase:
    """ provides easy logging and debugging for your application.

    Most applications only need a single instance of this class; apps with threads could create separate instances
    for each thread.

    Instance Attributes (ordered alphabetically - ignoring underscore characters):

    * :attr:`app_key`               id/key of this application instance.
    * :attr:`app_name`              basename (without the file name extension) of the executable.
    * :attr:`app_path`              file path of executable.
    * :attr:`app_title`             application title/description.
    * :attr:`app_version`           application version (set via the :paramref:`AppBase.app_version` argument).
    * :attr:`debug_level`           debug level of this instance.
    * :attr:`_last_log_line_prefix` last ae log file line prefix that got print-out to the log of this app instance.
    * :attr:`_log_buf_stream`       ae log file buffer stream.
    * :attr:`_log_file_index`       index of the current rotation ae log file backup.
    * :attr:`_log_file_name`        path and file name of the ae log file.
    * :attr:`_log_file_size_max`    maximum size in MBytes of a ae log file.
    * :attr:`_log_file_stream`      ae log file TextIO output stream.
    * :attr:`_log_with_timestamp`   log timestamp line prefix if True or a non-empty strftime compatible format string.
    * :attr:`py_log_params`         python logging config dictionary.
    * :attr:`_nul_std_out`          null stream used for to prevent print-outs to :attr:`standard output <sys.stdout>`.
    * :attr:`_shut_down`            flag set to True if this application instance got already shutdown.
    * :attr:`startup_beg`           datetime of begin of the instantiation/startup of this app instance.
    * :attr:`startup_end`           datetime of end of the instantiation/startup of this application instance.
    * :attr:`suppress_stdout`       flag set to True if this application does not print to stdout/console.
    * :attr:`sys_env_id`            system environment id of this application instance.
    """
    def __init__(self, app_title: str = '', app_name: str = '', app_version: str = '', sys_env_id: str = '',
                 debug_level: int = DEBUG_LEVEL_DISABLED, multi_threading: bool = False, suppress_stdout: bool = False):
        """ initialize a new :class:`AppBase` instance.

        :param app_title:               application title/description for to set the instance attribute
                                        :attr:`~ae.core.AppBase.app_title`.

                                        If not specified then the docstring of your app's main module will
                                        be used (see :ref:`example <app-title>`).

        :param app_name:                application instance name for to set the instance attribute
                                        :attr:`~ae.core.AppBase.app_name`.

                                        If not specified then base name of the main module file name will be used.

        :param app_version:             application version string for to set the instance attribute
                                        :attr:`~ae.core.AppBase.app_version`.

                                        If not specified then value of a global variable with the name
                                        `__version__` will be used (if declared in the actual call stack).

        :param sys_env_id:              system environment id for to set the instance attribute
                                        :attr:`~ae.core.AppBase.sys_env_id`.

                                        The default value of this argument is an empty string.

        :param debug_level:             default debug level for to set the instance attribute
                                        :attr:`~ae.core.AppBase.debug_level`.

                                        The default value of this argument is :data:`~ae.core.DEBUG_LEVEL_DISABLED`.

        :param multi_threading:         pass True if instance is used in multi-threading app.

        :param suppress_stdout:         pass True (for wsgi apps) for to prevent any python print outputs to stdout.
        """
        try:
            from ae.inspector import stack_var      # type: ignore
        except ImportError:                         # pragma: no cover
            def stack_var(key: str) -> str:
                """ get default value for app title and version (if ae.inspector is not provided/available). """
                return f"AppBase.__init__(): stack_var() not imported for to determine {key} value"

        self.startup_beg: datetime.datetime = datetime.datetime.now()   #: begin of app startup datetime
        self.app_path: str = os.path.dirname(sys.argv[0])               #: path to folder of your main app code file
        PATH_PLACEHOLDERS['app'] = self.app_path

        if not app_title:
            doc_str = stack_var('__doc__')
            app_title = doc_str.split('\n')[0] if doc_str else ""
        if app_name:
            PATH_PLACEHOLDERS['app_name'] = app_name
        else:
            app_name = app_name_guess()
        if not app_version:
            app_version = stack_var('__version__') or ""

        self.app_title: str = app_title                         #: title/description of this app instance
        self.app_name: str = app_name                           #: name of this app instance
        self.app_version: str = app_version                     #: version of this app instance
        self._debug_level: int = debug_level                    #: debug level of this app instance
        self.sys_env_id: str = sys_env_id                       #: system environment id of this app instance
        if multi_threading:
            activate_multi_threading()
        self.suppress_stdout: bool = suppress_stdout            #: flag to suppress prints to stdout

        with log_file_lock:
            self._last_log_line_prefix: str = ""                #: prefix of the last printed log line
            self._log_buf_stream: Optional[StringIO] = None     #: log file buffer stream instance
            self._log_file_stream: Optional[TextIO] = None      #: log file stream instance
            self._log_file_index: int = 0                       #: log file index (for rotating logs)
            self._log_file_size_max: float = LOG_FILE_MAX_SIZE  #: maximum log file size in MBytes (rotating log files)
            self._log_file_name: str = ""                       #: log file name
            self._log_with_timestamp: Union[bool, str] = False  #: True of strftime format string to enable timestamp
            self._nul_std_out: Optional[TextIO] = None          #: logging null stream
            self.py_log_params: Dict[str, Any] = dict()         #: dict of config parameters for py logging

        self._shut_down: bool = False                           #: True if this app instance got shut down already
        self.startup_end: Optional[datetime.datetime] = None    #: end datetime of the application startup

        _register_app_thread()
        _register_app_instance(self)

    def __del__(self):
        """ deallocate this app instance by calling :func:`AppBase.shutdown`.
        """
        self.shutdown(exit_code=None)

    @property
    def active_log_stream(self) -> Optional[Union[StringIO, TextIO]]:
        """ check if ae logging is active and if yes then return the currently used log stream (read-only property).

        :return:        log file or buf stream if logging is activated, else None.
        """
        with log_file_lock:
            return self._log_file_stream or self._log_buf_stream

    @property
    def app_key(self) -> str:
        """ determine the key of this application class instance (read-only property).

        :return:        application key string.
        """
        return self.app_name + APP_KEY_SEP + self.sys_env_id

    @property
    def debug_level(self) -> int:
        """ debug level property:

        :getter:    return the current debug level of this app instance.
        :setter:    change the debug level of this app instance.
        """
        return self._debug_level

    @debug_level.setter
    def debug_level(self, debug_level: int):
        """ debug level setter (added for easier overwrite in inheriting classes). """
        self._debug_level = debug_level

    @property
    def debug(self) -> bool:
        """ True if app is in debug mode. """
        return self._debug_level >= DEBUG_LEVEL_ENABLED

    @property
    def verbose(self) -> bool:
        """ True if app is in verbose debug mode. """
        return self._debug_level >= DEBUG_LEVEL_VERBOSE

    def init_logging(self, py_logging_params: Optional[Dict[str, Any]] = None, log_file_name: str = "",
                     log_file_size_max: float = LOG_FILE_MAX_SIZE, log_with_timestamp: Union[bool, str] = False,
                     disable_buffering: bool = False):
        """ initialize logging system.

        :param py_logging_params:       config dict for python logging configuration.
                                        If this dict is not empty then python logging is configured with the
                                        given options in this dict and all the other kwargs are ignored.
        :param log_file_name:           default log file name for ae logging (def='' - ae logging disabled).
        :param log_file_size_max:       max. size in MB of ae log file (def=LOG_FILE_MAX_SIZE).
        :param log_with_timestamp:      add timestamp prefix to each log line if True or a non-empty strftime
                                        compatible format string.
        :param disable_buffering:       pass True to disable ae log buffering at app startup.

        Log files and config values will be initialized as late as possible in :meth:`~AppBase.log_file_check`
        e.g. indirectly triggered by a request to a config variable via :meth:`~AppBase._parse_args` (like `logFile`).
        """
        with log_file_lock:
            if py_logging_params:                   # init python logging - app is using python logging module
                logger_late_init()
                # logging.basicConfig(level=logging.DEBUG, style='{')
                logging.config.dictConfig(py_logging_params)     # re-configure py logging module
                self.py_log_params = py_logging_params
            else:                                   # (re-)init ae logging
                if self._log_file_stream:
                    self._close_log_file()
                    self._std_out_err_redirection(False)
                self._log_file_name = log_file_name
                self._log_file_size_max = log_file_size_max
                self._log_with_timestamp = log_with_timestamp
                if not disable_buffering:
                    self._log_buf_stream = StringIO(initial_value="####  Log Buffer\n" if self.debug else "")

    def log_line_prefix(self) -> str:
        """ compile prefix of log print-out line for this :class:`AppBase` instance.

        The line prefix consists of (depending on the individual values of either a module variable or of an
        attribute this app instance):

        * :data:`_multi_threading_activated`: if True then the thread id gets printed surrounded with
          angle brackets (< and >), right aligned and space padded to minimal 6 characters.
        * :attr:`sys_env_id`: if not empty then printed surrounded with curly brackets ({ and }), left aligned
          and space padded to minimal 4 characters.
        * :attr:`_log_with_timestamp`: if (a) True or (b) an non-empty string then the system time
          (determined with :meth:`~datetime.datetime.now`) gets printed in the format specified either by the
          (a) the :data:`~ae.system.DATE_TIME_ISO` constant or (b) by the string in this attribute.

        This method is using the instance attribute :attr:`_last_log_line_prefix` for to keep a copy of
        the last printed log line prefix for to prevent the printout of duplicate characters in consecutive
        log lines.

        :return: log file line prefix string including one space as separator character at the end.
        """
        parts = list()
        if _multi_threading_activated:
            parts.append(f"<{threading.get_ident(): >6}>")
        if self.app_key[-1] != APP_KEY_SEP:
            parts.append(f"{{{self.app_key: <6}}}")
        if self._log_with_timestamp:
            format_string = DATE_TIME_ISO if isinstance(self._log_with_timestamp, bool) else self._log_with_timestamp
            parts.append(datetime.datetime.now().strftime(format_string))
        if self.debug:
            parts.append(f"[{DEBUG_LEVELS[self.debug_level][0]}]")

        prefix = "".join(parts)
        with log_file_lock:
            last_pre = self._last_log_line_prefix
            self._last_log_line_prefix = prefix

        return hide_dup_line_prefix(last_pre, prefix) + " "

    def log_file_check(self, curr_stream: Optional[TextIO] = None) -> Optional[TextIO]:
        """ check and possibly correct log file status and the passed currently used stream.

        :param curr_stream:     currently used stream.
        :return:                stream passed into :paramref:`~log_file_check.curr_stream` or
                                new/redirected stream of :paramref:`~log_file_check.curr_stream` or
                                None if :paramref:`~log_file_check.curr_stream` is None.

        For already opened log files check if the ae log file is big enough and if yes then do a file rotation.
        If log file is not opened but log file name got already set, then check if log startup buffer is active
        and if yes then create log file, pass log buffer content to log file and close the log buffer.
        """
        old_stream = new_stream = None
        with log_file_lock:
            if self._log_file_stream:
                old_stream = self._log_file_stream
                self._log_file_stream.seek(0, 2)  # due to non-posix-compliant Windows feature
                if self._log_file_stream.tell() >= self._log_file_size_max * 1024 * 1024:
                    self._close_log_file()
                    self._rename_log_file()
                    self._open_log_file()
                    new_stream = self._log_file_stream
            elif self._log_file_name:
                old_stream = self._log_buf_stream
                self._open_log_file()
                self._std_out_err_redirection(True)
                self._flush_and_close_log_buf()
                new_stream = self._log_file_stream
            elif self.suppress_stdout and not self._nul_std_out:    # pragma: no cover/_std_out_err_redirection does it
                old_stream = sys.stdout
                sys.stdout = self._nul_std_out = new_stream = open(os.devnull, 'w')

        if curr_stream == old_stream and new_stream:
            return new_stream
        return curr_stream

    def print_out(self, *objects, file: Optional[TextIO] = None, **kwargs):
        """ app-instance-specific print-outs.

        :param objects:     objects to be printed out.
        :param file:        output stream object to be printed to (def=None). Passing None on a main app instance
                            will print the objects to the standard output and any active log files, but on a
                            :class:`SubApp` instance with an active log file the print-out will get redirected
                            exclusively/only to log file of this :class:`SubApp` instance.
        :param kwargs:      All the other supported kwargs of this method are documented
                            :func:`at the print_out() function of this module <print_out>`.

        This method has an alias named :meth:`.po`
        """
        if file is None and main_app_instance() is not self:
            with log_file_lock:
                file = self._log_buf_stream or self._log_file_stream
        if file:
            kwargs['file'] = file
        if 'app' not in kwargs:
            kwargs['app'] = self
        print_out(*objects, **kwargs)

    po = print_out          #: alias of method :meth:`.print_out`

    def debug_out(self, *objects, minimum_debug_level: int = DEBUG_LEVEL_ENABLED, **kwargs):
        """ special debug version of :func:`builtin print() function <print>`.

        This method will print-out the passed objects only if the :attr:`current debug level
        <.core.AppBase.debug_level>` of this app instance is higher than the value passed into the
        :paramref:`~debug_out.minimum_debug_level` argument. In this case the print-out will be
        delegated onto the :meth:`~.print_out`.

        :param objects:                 objects to be printed out.
        :param minimum_debug_level:     minimum debug level for to print the passed objects.
        :param kwargs:                  All the supported kwargs of this method
                                        are documented at the :func:`print_out() function <~.core.print_out>`
                                        of the :mod:`~.core` module (including the
                                        :paramref:`~.print_out.file` argument).

        This method has an alias named :meth:`.dpo`.
        """
        if self.debug_level >= minimum_debug_level:
            self.po(*objects, **kwargs)

    dpo = debug_out         #: alias of method :meth:`.debug_out`

    def verbose_out(self, *objects, **kwargs):
        """ special verbose debug version of :func:`builtin print() function <print>`.

        :param objects:                 objects to be printed out.
        :param kwargs:                  The :paramref:`~.core.AppBase.print_out.file` argument is documented
                                        at the :meth:`~.core.AppBase.print_out` method of the
                                        :class:`~.core.AppBase` class. All other supported kwargs of this method
                                        are documented at the :func:`print_out() function <~.core.print_out>`
                                        of the :mod:`~.core` module.

        This method has an alias named :meth:`.vpo`.
        """
        if self.debug_level >= DEBUG_LEVEL_VERBOSE:
            self.po(*objects, **kwargs)

    vpo = verbose_out         #: alias of method :meth:`.verbose_out`

    def shutdown(self, exit_code: Optional[int] = 0, timeout: Optional[float] = None):
        """ shutdown this app instance and if it is the main app instance then also any created sub-app-instances.

        :param exit_code:   set application OS exit code - ignored if this is NOT the main app instance (def=0).
                            Pass None for to prevent call of sys.exit(exit_code).
        :param timeout:     timeout float value in seconds used for the thread termination/joining, for the
                            :class:`SubApp` shutdowns and for the acquisition of the
                            threading locks of :data:`the ae log file <log_file_lock>` and the :data:`app instances
                            <app_inst_lock>`.
        """
        if self._shut_down:
            return
        aqc_kwargs: Dict[str, Any] = dict(blocking=False) if timeout is None else dict(timeout=timeout)
        is_main_app_instance = main_app_instance() is self
        force = is_main_app_instance and exit_code      # prevent deadlock on app error exit/shutdown

        if exit_code is not None:
            self.po(f"####  Shutdown............  {exit_code if force else ''} {timeout}", logger=_logger)

        a_blocked = (False if force else app_inst_lock.acquire(**aqc_kwargs))
        if is_main_app_instance:
            _shut_down_sub_app_instances(timeout=timeout)
            if _multi_threading_activated:
                _join_app_threads(timeout=timeout)

        l_blocked = (False if force else log_file_lock.acquire(**aqc_kwargs))

        self._flush_and_close_log_buf()
        self._close_log_file()
        if self._log_file_index:
            self._rename_log_file()

        if self._nul_std_out:
            if not self._nul_std_out.closed:
                self._append_eof_and_flush_file(self._nul_std_out, "NUL stdout")
                self._nul_std_out.close()
            self._nul_std_out = None

        if self.py_log_params:
            logging.shutdown()

        self._std_out_err_redirection(False)

        if l_blocked:
            log_file_lock.release()

        _unregister_app_instance(self.app_key)
        if a_blocked:
            app_inst_lock.release()
        self._shut_down = True
        if is_main_app_instance and exit_code is not None:
            sys.exit(exit_code)             # pragma: no cover (would break/cancel test run)

    def _std_out_err_redirection(self, redirect: bool):
        """ enable/disable the redirection of the standard output/error TextIO streams if needed.

        :param redirect:    pass True to enable or False to disable the redirection.
        """
        is_main_app_instance = main_app_instance() is self
        if redirect:
            if not isinstance(sys.stdout, _PrintingReplicator):  # sys.stdout==ori_std_out not works with pytest/capsys
                if not self.suppress_stdout:
                    std_out = ori_std_out
                elif self._nul_std_out and not self._nul_std_out.closed:
                    std_out = self._nul_std_out     # pragma: no cover - should never happen
                else:
                    std_out = self._nul_std_out = open(os.devnull, 'w')
                sys.stdout = cast(TextIO, _PrintingReplicator(sys_out_obj=std_out))
                sys.stderr = cast(TextIO, _PrintingReplicator(sys_out_obj=ori_std_err))
        else:
            if is_main_app_instance:
                sys.stderr = ori_std_err
                sys.stdout = ori_std_out

        if is_main_app_instance:
            if redirect:
                faulthandler.enable(file=sys.stdout)
            elif faulthandler.is_enabled():
                faulthandler.disable()  # pragma: no cover (badly testable - would cancel/break test runs)

    def _append_eof_and_flush_file(self, stream_file: TextIO, stream_name: str):
        """ add special end-of-file marker and flush the internal buffers to the file stream.

        :param stream_file:     file stream.
        :param stream_name:     name of the file stream (only used for debugging/error messages).
        """
        try:
            try:
                # cannot use print_out() here because of recursions on log file rotation, so use built-in print()
                print(file=stream_file)
                if self.debug:
                    print('EoF', file=stream_file)
            except Exception as ex:     # pragma: no cover - pylint: disable=broad-except
                self.po(f"Ignorable {stream_name} end-of-file marker exception={ex}", logger=_logger)

            stream_file.flush()

        except Exception as ex:         # pylint: disable=broad-except
            self.po(f"Ignorable {stream_name} flush exception={ex}", logger=_logger)

    def _flush_and_close_log_buf(self):
        """ flush and close ae log buffer and pass content to log stream if opened.
        """
        stream = self._log_buf_stream
        if stream:
            if self._log_file_stream:
                self._append_eof_and_flush_file(stream, "ae log buf")
                buf = stream.getvalue() + ("\n####  End Of Log Buffer" if self.debug else "")
                self._log_file_stream.write(buf)
            self._log_buf_stream = None
            stream.close()

    def _open_log_file(self):
        """ open the ae log file with path and file name specified by :attr:`_log_file_name`.

        Tries to create a log sub-folder - if specified in :attr:`_log_file_name` and
        the folder does not exists (folder creation is limited to one folder level).

        .. note::
           A already existing file with the same file name will be overwritten (file contents get lost!).
        """
        log_dir = os.path.dirname(self._log_file_name)
        if log_dir and not os.path.exists(log_dir):
            os.mkdir(log_dir)
        self._log_file_stream = open(self._log_file_name, "w", errors=DEF_ENCODE_ERRORS)

    def _close_log_file(self):
        """ close the ae log file.
        """
        if self._log_file_stream:
            stream = self._log_file_stream
            self._append_eof_and_flush_file(stream, "ae log file")
            self._log_file_stream = None
            stream.close()

    def _rename_log_file(self):
        """ rename rotating log file while keeping first/startup log and log file count below :data:`MAX_NUM_LOG_FILE`.
        """
        file_base, file_ext = os.path.splitext(self._log_file_name)
        dfn = f"{file_base}-{self._log_file_index:0>{LOG_FILE_IDX_WIDTH}}{file_ext}"
        if os.path.exists(dfn):
            os.remove(dfn)                              # remove old log file from previous app run
        if os.path.exists(self._log_file_name):         # prevent errors after log file error or unit test cleanup
            os.rename(self._log_file_name, dfn)

        self._log_file_index += 1
        if self._log_file_index > MAX_NUM_LOG_FILES:    # use > instead of >= for to always keep first/startup log file
            first_idx = self._log_file_index - MAX_NUM_LOG_FILES
            dfn = f"{file_base}-{first_idx:0>{LOG_FILE_IDX_WIDTH}}{file_ext}"
            if os.path.exists(dfn):
                os.remove(dfn)


class SubApp(AppBase):
    """ separate/additional sub-app/thread/task with own/individual logging/debug configuration.

    Create an instance of this class for every extra thread and task where your application needs separate
    logging and/or debug configuration - additional to the main app instance.

    All members of this class are documented at the :class:`AppBase` class.
    """
