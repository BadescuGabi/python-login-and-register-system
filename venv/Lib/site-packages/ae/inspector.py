"""
inspection and debugging helper functions
=========================================

The function :func:`module_callable` allows you
to dynamically determine a pointer to any
callable object (function, class, ...) in
a Python module.

The functions :func:`module_name`,
:func:`stack_frames` and :func:`stack_variable`
are very helpful for to inspect the call stack.
With them you can easily access the stack frames
and read e.g. variable values of the callers
of your functions/methods.

.. hint::
    The class :class:`AppBase` is optionally using
    them e.g. for to determine the
    :attr:`version <AppBase.app_version>`
    and :attr:`title <AppBase.app_title>` of
    your application, if these values are
    not specified in the constructor.

Another useful helper function provided by
this portion, which eases the inspection and
debugging of your application is
:func:`full_stack_trace`.


dynamic execution of code blocks and expressions
------------------------------------------------

For the dynamic execution of functions and
code blocks the helper functions :func:`try_call`,
:func:`try_exec` and :func:`exec_with_return` are
provided. Additionally :func:`try_eval` is making
the evaluation of dynamic Python expressions
much easier.

.. note::
    Before the call of one of these functions
    make sure the code block or expression
    string is secure for to prevent injections
    of malware.

.. hint::
    These functions are e.g. used by the
    :class:`~.literal.Literal` class for
    the implementation of dynamically
    determined literal values.

"""
import ast
import datetime
import importlib.abc
import importlib.util
from inspect import getinnerframes, getouterframes
import logging
import logging.config as logging_config
import os
import sys
from string import ascii_letters, digits
import threading
from types import ModuleType
from typing import Any, Callable, Dict, Generator, Optional, Tuple, Type
import unicodedata
import weakref

from ae.system import DATE_ISO, DATE_TIME_ISO                                       # type: ignore


__version__ = '0.1.3'


# suppress unused import err (needed e.g. for unpickling of dates via try_eval() and for include them into base_globals)
_d = (DATE_ISO, DATE_TIME_ISO,
      ascii_letters, digits, datetime, logging, logging_config, threading, unicodedata, weakref)

SKIPPED_MODULES = ('ae.system', 'ae.paths', 'ae.inspector', 'ae.core', 'ae.console', 'ae.gui_app',
                   'ae.gui_help', 'ae.kivy_app', 'ae.enaml_app', 'ae.lisz_app_data',
                   'ae.beeware_app', 'ae.pyglet_app', 'ae.pygobject_app', 'ae.dabo_app',
                   'ae.qpython_app', 'ae.appjar_app')
""" skipped modules used as default by :func:`module_name` and :func:`stack_variable` """


def exec_with_return(code_block: str, ignored_exceptions: Tuple[Type[Exception], ...] = (),
                     glo_vars: Optional[Dict[str, Any]] = None, loc_vars: Optional[Dict[str, Any]] = None
                     ) -> Optional[Any]:
    """ execute python code block and return the resulting value of its last code line.

    Inspired by this SO answer
    https://stackoverflow.com/questions/33409207/how-to-return-value-from-exec-in-function/52361938#52361938.

    :param code_block:          python code block to execute.
    :param ignored_exceptions:  tuple of ignored exceptions.
    :param glo_vars:            optional globals() available in the code execution.
    :param loc_vars:            optional locals() available in the code execution.
    :return:                    value of the expression at the last code line
                                or None if either code block is empty, only contains comment lines, or one of
                                the ignorable exceptions raised or if last code line is no expression.
    """
    if glo_vars is None:
        glo_vars = base_globals
    elif '_add_base_globals' in glo_vars:
        glo_vars.update(base_globals)

    try:
        code_ast = ast.parse(code_block)    # raises SyntaxError if code block is invalid
        nodes = code_ast.body
        if nodes:
            if isinstance(nodes[-1], ast.Expr):
                last_node = nodes.pop()
                if len(nodes) > 0:
                    # noinspection BuiltinExec
                    exec(compile(code_ast, "<ast>", 'exec'), glo_vars, loc_vars)
                # mypy needs getattr() instead of last_node.value
                return eval(compile(ast.Expression(getattr(last_node, 'value')), "<ast>", 'eval'), glo_vars, loc_vars)
            # noinspection BuiltinExec
            exec(compile(code_ast, "<ast>", 'exec'), glo_vars, loc_vars)
    except ignored_exceptions:
        pass                            # RETURN None if one of the ignorable exceptions raised in compiling
    return None                         # mypy needs explicit return statement and value


def full_stack_trace(ex: Exception) -> str:
    """ get full stack trace from an exception.

    :param ex:  exception instance.
    :return:    str with stack trace info.
    """
    ret = f"Exception {ex!r}. Traceback:\n"
    trace_back = sys.exc_info()[2]
    if trace_back:
        def ext_ret(item):
            """ process traceback frame and add as str to ret """
            nonlocal ret
            ret += f'File "{item[1]}", line {item[2]}, in {item[3]}\n'
            lines = item[4]  # mypy does not detect item[]
            if lines:
                for line in lines:
                    ret += ' ' * 4 + line.lstrip()

        for frame in reversed(getouterframes(trace_back.tb_frame)[1:]):
            ext_ret(frame)
        for frame in getinnerframes(trace_back):
            ext_ret(frame)
    return ret


def module_callable(entry_point: str, module_path: str = "") -> Tuple[Optional[ModuleType], Optional[Callable]]:
    """ determine dynamically the pointers to a module and to a callable declared within the module.

    :param entry_point:         entry point of a callable in the form <module_name>:<callable_name>.
                                If the module folder is not available in sys.path then you also have to
                                pass the module folder path into the :paramref:`module_path` argument.
    :param module_path:         optional path where the module is situated (only needed if path is not is sys.path).
    :return:                    tuple of module object and callable object ore None if module/callable doesn't exist.
    """
    module = func = None
    mod_name, func_name = entry_point.split(':')
    module_path = os.path.join(module_path, mod_name + '.py')

    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location(mod_name, module_path)
        module = importlib.util.module_from_spec(spec)

        # mypy: had to add import (from importlib.abc import Loader) and assert and then also noinspection for PyCharm
        assert isinstance(spec.loader, importlib.abc.Loader)
        # noinspection PyUnresolvedReferences
        spec.loader.exec_module(module)

    elif mod_name in sys.modules:
        module = sys.modules[mod_name]

    if module:
        func = getattr(module, func_name, None)

    return module, func


def module_name(*skip_modules: str, depth: int = 1) -> Optional[str]:
    """ find the first module in the call stack that is *not* in :paramref:`module_name.skip_modules`.

    :param skip_modules:    module names to skip (def=this ae.core module).
    :param depth:           the calling level from which on to search (def=1 which refers the next deeper frame).
                            Pass 2 or a even higher value if you want to get the module name from a deeper level
                            in the call stack.
    :return:                The module name of the call stack level specified in the :paramref:`~module_name.depth`
                            argument.
    """
    if not skip_modules:
        skip_modules = SKIPPED_MODULES
    return stack_var('__name__', *skip_modules, depth=depth)


def stack_frames(depth: int = 2) -> Generator:  # Generator[frame, None, None]
    """ generator returning the call stack frame from the level given in :paramref:`~stack_frames.depth`.

    :param depth:           the calling level from which on to start (def=2 which refers the next deeper stack frame
                            of the caller of this function).
                            Pass 3 or a higher value if you want to start with an even deeper frame in the call stack.
    :return:                The stack frame of a deeper level within the call stack.
    """
    try:
        while True:
            # noinspection PyProtectedMember,PyUnresolvedReferences
            yield sys._getframe(depth)          # pylint: disable=protected-access
            depth += 1
    except (TypeError, AttributeError, ValueError):
        pass


def stack_variable(name: str, *skip_modules: str, depth: int = 1, locals_only: bool = False) -> Optional[Any]:
    """ determine variable value in calling stack/frames.

    :param name:            variable name.
    :param skip_modules:    module names to skip (def=see :data:`SKIPPED_MODULES` module constant).
    :param depth:           the calling level from which on to search (def=1 which refers the next deeper stack frame).
                            Pass 2 or a even higher value if you want to get the variable value from a deeper level
                            in the call stack.
    :param locals_only:     pass True to only check for local variables (ignoring globals).
    :return:                The variable value of a deeper level within the call stack.

    This function has an alias named :func:`.stack_var`.
    """
    global_vars, local_vars, deep = stack_vars(*skip_modules, find_name=name, min_depth=depth + 1)  # +1 -> stack_vars()
    if locals_only:
        if name in global_vars:
            while global_vars and name not in local_vars:
                global_vars, local_vars, deep = stack_vars(*skip_modules, find_name=name, min_depth=deep + 1)
        variables = local_vars
    else:
        variables = global_vars
    return variables.get(name)


stack_var = stack_variable          #: alias of function :func:`.stack_variable`


def stack_variables(*skip_modules: str, find_name: str = '', max_depth: int = 0, min_depth: int = 3
                    ) -> Tuple[Dict[str, Any], Dict[str, Any], int]:
    """ determine global and local variables in calling stack/frames.

    :param skip_modules:    module names to skip (def=see :data:`SKIPPED_MODULES` module constant).
    :param find_name:       if passed then the returned stack frame must contain a variable with the passed name.
    :param max_depth:       the maximum depth in the call stack from which to return the variables.
                            If the specified argument is not zero and no :paramref:`~stack_variables.skip_modules`
                            are specified then the first deeper stack frame that is not within the default
                            :data:`SKIPPED_MODULES` will be returned.
                            If this argument and :paramref:`~stack_variable.find_name` get not passed then
                            the variables of the top stack frame will be returned.
    :param min_depth:       the calling level from which on to search (def=3 which refers the next deeper stack frame
                            of the caller of this function).
                            Pass 4 or a higher value if you want to get the variable value from a deeper level
                            in the call stack.
    :return:                tuple of the global and local variable dicts and the depth in the call stack.

    This function has an alias named :func:`.stack_vars`.
    """
    if not skip_modules:
        skip_modules = SKIPPED_MODULES
    glo = loc = dict()
    depth = min_depth
    for frame in stack_frames(depth=min_depth):
        depth += 1
        glo, loc = frame.f_globals, frame.f_locals

        if glo.get('__name__') in skip_modules:
            continue
        if find_name and (find_name in glo or find_name in loc):
            break
        if max_depth and depth > max_depth:
            break
    # experienced strange overwrites of locals (e.g. self) when returning f_locals directly (adding .copy() fixed it)
    return glo.copy(), loc.copy(), depth - 1


stack_vars = stack_variables        #: alias of function :func:`.stack_variables`


def try_call(callee: Callable, *args, ignored_exceptions: Tuple[Type[Exception], ...] = (), **kwargs) -> Any:
    """ execute callable while ignoring specified exceptions and return callable return value.

    :param callee:              pointer to callable (either function pointer, lambda expression, a class, ...).
    :param args:                function arguments tuple.
    :param ignored_exceptions:  tuple of ignored exceptions.
    :param kwargs:              function keyword arguments dict.
    :return:                    function return value or None if a ignored exception got thrown.
    """
    ret = None
    try:  # catch type conversion errors, e.g. for datetime.date(None) while bool(None) works (->False)
        ret = callee(*args, **kwargs)
    except ignored_exceptions:
        pass
    return ret


def try_eval(expr: str, ignored_exceptions: Tuple[Type[Exception], ...] = (),
             glo_vars: Optional[Dict[str, Any]] = None, loc_vars: Optional[Dict[str, Any]] = None) -> Any:
    """ evaluate expression string ignoring specified exceptions and return evaluated value.

    :param expr:                expression to evaluate.
    :param ignored_exceptions:  tuple of ignored exceptions.
    :param glo_vars:            optional globals() available in the expression evaluation.
    :param loc_vars:            optional locals() available in the expression evaluation.
    :return:                    function return value or None if a ignored exception got thrown.
    """
    ret = None

    if glo_vars is None:
        glo_vars = base_globals
    elif '_add_base_globals' in glo_vars:
        glo_vars.update(base_globals)

    try:  # catch type conversion errors, e.g. for datetime.date(None) while bool(None) works (->False)
        ret = eval(expr, glo_vars, loc_vars)
    except ignored_exceptions:
        pass
    return ret


def try_exec(code_block: str, ignored_exceptions: Tuple[Type[Exception], ...] = (),
             glo_vars: Optional[Dict[str, Any]] = None, loc_vars: Optional[Dict[str, Any]] = None) -> Any:
    """ execute python code block string ignoring specified exceptions and return value of last code line in block.

    :param code_block:          python code block to be executed.
    :param ignored_exceptions:  tuple of ignored exceptions.
    :param glo_vars:            optional globals() available in the code execution.
    :param loc_vars:            optional locals() available in the code execution.
    :return:                    function return value or None if a ignored exception got thrown.
    """
    ret = None
    try:
        ret = exec_with_return(code_block, glo_vars=glo_vars, loc_vars=loc_vars)
    except ignored_exceptions:
        pass
    return ret


base_globals = globals()        #: default if no global variables get passed in dynamic code/expression evaluations
