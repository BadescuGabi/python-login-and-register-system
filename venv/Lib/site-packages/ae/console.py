"""
console application environment
===============================

The :class:`ConsoleApp` allows your application the easy declaration of
command line arguments and options.

:class:`ConsoleApp` inherits from the :class:`~ae.core.AppBase`
application base class. :class:`~ae.core.AppBase` will extend your
application with dynamically configurable logging and debugging
features. The attributes and methods of :class:`~ae.core.AppBase`
are documented in the :mod:`docstrings of the core module <ae.core>`.


.. _app-title:
.. _app-version:

basic usage of console application class
----------------------------------------

At the top of your python application main file/module create an instance of the class :class:`ConsoleApp`::

    \"\"\" module docstring \"\"\"
    from ae.console import ConsoleApp

    __version__ = '1.2.3'

    ca = ConsoleApp()

    assert ca.app_title == "module docstring"
    assert ca.app_version == '1.2.3'

In the above example the :class:`ConsoleApp` instance will automatically collect the docstring of the
module as application title and the string in the module variable __version___ as application version.
Alternatively you can specify your application title and version string by passing them (into the
arguments :paramref:`~ConsoleApp.app_title` and :paramref:`~ConsoleApp.app_version`)
to the instantiation call of :class:`ConsoleApp`.

.. _app-name:

:class:`ConsoleApp` also determines automatically the name/id of your application from the file base name
of your application main/startup module (e.g. <app_name>.py or main.py). Also other application environment
vars/options (like e.g. the application startup folder path and the current working directory path) will be
automatically initialized for your application.


define command line arguments and options
-----------------------------------------

With the methods :meth:`~ConsoleApp.add_argument` and :meth:`~ConsoleApp.add_option` of your just created
:class:`ConsoleApp` instance you can then define the command line arguments and
the :ref:`config options <config-options>` of your application::

    ca.add_argument('argument_name_or_id', help="Help text for this command line argument")
    ca.add_option('option_name_or_id', "help text for this command line option", "default_value")
    ...
    ca.run_app()

After all arguments and config options of your application are defined, you have to call
the :meth:`~ConsoleApp.run_app` method of the :class:`ConsoleApp` instance for to parse
the command line arguments.

After the commend line argument parsing your application can gather their values with the methods
:meth:`~ConsoleApp.get_argument` and :meth:`~ConsoleApp.get_option` of your :class:`ConsoleApp` instance.

Additional configuration values of your application can be provided by :ref:`INI/CFG files <config-files>`
and gathered with the :class:`ConsoleApp` method :meth:`~ConsoleApp.get_variable`.


configuration files, sections, variables and options
----------------------------------------------------

.. _config-files:

config files
^^^^^^^^^^^^

You can create and use separate config files for each of your applications, used system environments and data domains.
A config file consists of config sections, each section provides config variables and config options
for to parametrize your application at run-time.

While the config file names and extensions for data domains can be freely chosen (like any_name.txt), there
are also some hard-coded file names that are recognized:

+----------------------------+---------------------------------------------------+
|  config file               |  used for .... config variables and options       |
+============================+===================================================+
| <any_path_name_and_ext>    |  application/domain specific                      |
+----------------------------+---------------------------------------------------+
| <app_name>.ini             |  application specific (read-/write-able)          |
+----------------------------+---------------------------------------------------+
| <app_name>.cfg             |  application specific (read-only)                 |
+----------------------------+---------------------------------------------------+
| .app_env.cfg               |  application/suite specific (read-only)           |
+----------------------------+---------------------------------------------------+
| .sys_env.cfg               |  general system (read-only)                       |
+----------------------------+---------------------------------------------------+
| .sys_env<SYS_ENV_ID>.cfg   |  the system with SYS_ID (read-only)               |
+----------------------------+---------------------------------------------------+

The config files in the above table are ordered by their preference, so domain specific
config variables/options will always precede/overwrite any application and system
specific config values. Additionally only domain-specific config files can have any
file extension and can be placed into any accessible folder. In contrary all
non-domain-specific config files get only loaded if they are either in the application
installation folder, in the current working directory or up to two levels above
the current working.

Each config file get first searched in the current working directory, then in the user
data directory (see :func:`ae.paths.user_data_path`) and finally in the application
installation directory.


.. _config-sections:

config sections
^^^^^^^^^^^^^^^

This module is supporting the `config file format <https://en.wikipedia.org/wiki/INI_file>`_ of
Pythons built-in :class:`~configparser.ConfigParser` class, and also extends it with
:ref:`complex config value types <config-value-types>`.

The following examples shows a config file with two config sections containing one config option (named
`log_file`) and two config variables (`configVar1` and `configVar2`)::

    [aeOptions]
    log_file = './logs/your_log_file.log'

    [YourSectionName]
    configVar1 = ['list-element1', ('list-element2-1', 'list-element2-2', ), dict()]
    configVar2 = {'key1': 'value 1', 'key2': 2222, 'key3': datetime.datetime.now()}

.. _config-main-section:

The ae modules are using the main config section `aeOptions` (defined by :data:`MAIN_SECTION_NAME`)
for to store the values of any pre-defined :ref:`config option <config-options>` and
:ref:`config variables <config-variables>`.

.. _config-variables:

config variables
^^^^^^^^^^^^^^^^

Config variables can be defined in any config section and can hold any data type. In the example
config file above the config variable `configVar1` has a list with 3 elements: the first element
is a string the second element is a tuple and the third element is an empty dict.

The complex data type support of this module allows to specify a config value as a string that can be
evaluated with the built-in :func:`eval` function. The value of the evaluated string is taken as the
resulting config value of this config variable.

From within your application simply call the :meth:`~ConsoleApp.get_variable` method with the
name and section names of the config variable for to fetch their config value.

The default value of a config variable can also be set/changed directly from within your application
by calling the :meth:`~ConsoleApp.set_variable` method.

The following pre-defined config variables in the :ref:`main config section <config-main-section>` are recognized
by :mod:`this module <.console>` as well as by :mod:`.core`.

* ``logging_params`` : general logging configuration parameters (py and ae logging)
  - :meth:`documented here <.core.AppBase.init_logging>`.
* ``py_logging_params`` : configuration parameters for to activate python logging
  - `documented in the Python docs
  <https://docs.python.org/3.6/library/logging.config.html#logging.config.dictConfig>`_.
* ``log_file`` : log file name for ae logging (this is also a config option - set-able as command line arg).

.. note::
  The value of a config variable can be overwritten by defining an OS environment variable with a name
  that is equal to the :func:`snake+upper-case converted names <ae.system.env_str>` of the config-section
  and -variable.
  E.g. declare an OS environment variable with the name `AE_OPTIONS_DEBUG_LEVEL` for to overwrite the value
  of the :ref:`pre-defined config option/variable <pre-defined-config-options>` `debug_level`.


.. _config-options:

config options
^^^^^^^^^^^^^^

Config options are config variables that are defined exclusively in the hard-coded section
:data:`aeOptions <MAIN_SECTION_NAME>`. The value of a config option can optionally be given/overwritten
on the command line by adding the option name or id with two leading hyphen characters, followed by an equal
character and the option value)::

    $ your_application --log_file='your_new_log_file.log'

If a command line option is not specified on the command line then :class:`ConsoleApp` is searching if a default value
for this config option got specified either in a config file or in the call of :meth:`~ConsoleApp.add_option`.
The order of this default value search is documented :meth:`here <ConsoleApp.get_option>`.

For to query the resulting value of a config option, simply call the :meth:`~ConsoleApp.get_option` method
of your :class:`ConsoleApp` instance::

    option_value = c.get_option('option_id')

For to read the default value of a config option or variable directly from the available configuration files use the
:meth:`~ConsoleApp.get_variable` method instead. The default value of a config option or variable can also be
set/changed directly from within your application by calling the :meth:`~ConsoleApp.set_variable` method.

Use the :meth:`~ConsoleApp.set_option` if you want to change the value of a configuration option at run-time.


.. _config-value-types:

config value types
^^^^^^^^^^^^^^^^^^

A configuration options can be of any type. With the :paramref:`~ConsoleApp.add_option.value` argument and
:attr:`special encapsulated strings <.literal.Literal.value>` you're able to specify any type
for your config options and variables (like dict/list/tuple/datetime/... or any other object type).


pre-defined configuration options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _pre-defined-config-options:

For a more verbose output you can specify on the command line or in one of your configuration files
the pre-defined config option `debug_level` (or as short option -D) with a value of 2 (for verbose).
The supported config option values are documented :data:`here <.core.DEBUG_LEVELS>`.

The value of the second pre-defined config option `log_file` specifies the log file path/file_name, which can
be abbreviated on the command line with the short option -L.


console helper functions
------------------------

The function :func:`instantiate_config_parser` ensures that the :class:`~configparser.ConfigParser` instance
is correctly configured, e.g. to support case-sensitive config variable names and to use
:class:`ExtendedInterpolation` for the interpolation argument.

"""
import os
import datetime
import threading

from typing import Any, Callable, Dict, Iterable, Optional, Type, Tuple
from configparser import ConfigParser, ExtendedInterpolation, NoSectionError
from argparse import ArgumentParser, ArgumentError, HelpFormatter, Namespace

from ae.system import DATE_TIME_ISO, DATE_ISO, env_str, sys_env_text    # type: ignore
from ae.paths import Collector                                          # type: ignore
# noinspection PyProtectedMember
from ae.core import (                                                   # type: ignore  # for mypy
    DEBUG_LEVEL_DISABLED, DEBUG_LEVEL_ENABLED, DEBUG_LEVELS,
    main_app_instance, ori_std_out, _logger,
    AppBase)
from ae.literal import Literal                                          # type: ignore


__version__ = '0.1.36'


INI_EXT: str = '.ini'                           #: INI file extension
MAIN_SECTION_NAME: str = 'aeOptions'            #: default name of main config section

# Lock for to prevent errors in config var value changes and reloads/reads
config_lock = threading.RLock()


def instantiate_config_parser() -> ConfigParser:
    """ instantiate and prepare config file parser. """
    cfg_parser = ConfigParser(interpolation=ExtendedInterpolation())
    # set optionxform to have case sensitive var names (or use 'lambda option: option')
    # mypy V 0.740 bug - see mypy issue #5062: adding pragma "type: ignore" breaks PyCharm (showing
    # .. inspection warning "Non-self attribute could not be type-hinted"), but
    # .. also cast(Callable[[Arg(str, 'option')], str], str) and # type: ... is not working
    # .. (because Arg is not available in plain mypy, only in the extra mypy_extensions package)
    setattr(cfg_parser, 'optionxform', str)
    return cfg_parser


class ConsoleApp(AppBase):
    """ provides command line arguments and options, config options, logging and debugging for your application.

    Most applications only need a single instance of this class. Each instance is encapsulating a ConfigParser and
    a ArgumentParser instance. So only apps with threads and different sets of config options for each
    thread could create a separate instance of this class.

    Instance Attributes (ordered alphabetically - ignoring underscore characters):

    * :attr:`_arg_parser`           ArgumentParser instance.
    * :attr:`cfg_opt_choices`       valid choices for pre-/user-defined options.
    * :attr:`cfg_opt_eval_vars`     additional dynamic variable values that are getting set via
      the :paramref:`~.ConsoleApp.cfg_opt_eval_vars` argument of the method :meth:`ConsoleApp.__init__`
      and get then used in the evaluation of :ref:`evaluable config option values <evaluable-literal-formats>`.
    * :attr:`_cfg_files`            iterable of config file names that are getting loaded and parsed (specify
      additional configuration/INI files via the :paramref:`~ConsoleApp.additional_cfg_files` argument).
    * :attr:`cfg_options`           pre-/user-defined options (dict of :class:`~.literal.Literal` instances defined
      via :meth:`~ConsoleApp.add_option`).
    * :attr:`_cfg_parser`           ConfigParser instance.
    * :attr:`_main_cfg_fnam`        main config file name.
    * :attr:`_main_cfg_mod_time`    last modification datetime of main config file.
    * :attr:`_cfg_opt_val_stripper` callable to strip option values.
    * :attr:`_parsed_arguments`     ArgumentParser.parse_args() return.
    """
    def __init__(self, app_title: str = '', app_name: str = '', app_version: str = '', sys_env_id: str = '',
                 debug_level: int = DEBUG_LEVEL_DISABLED, multi_threading: bool = False, suppress_stdout: bool = False,
                 cfg_opt_eval_vars: Optional[dict] = None, additional_cfg_files: Iterable = (),
                 cfg_opt_val_stripper: Optional[Callable] = None,
                 formatter_class: Optional[Any] = None, epilog: str = "",
                 **logging_params):
        """ initialize a new :class:`ConsoleApp` instance.

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

                                        This value is also used as file name suffix for to load all
                                        the system config variables in sys_env<suffix>.cfg. Pass e.g. 'LIVE'
                                        for to init this ConsoleApp instance with config values from sys_envLIVE.cfg.

                                        The default value of this argument is an empty string.

                                        .. note::
                                          If the argument value results as empty string then the value of the
                                          optionally defined OS environment variable `AE_OPTIONS_SYS_ENV_ID`
                                          will be used as default.

        :param debug_level:             default debug level for to set the instance attribute
                                        :attr:`~ae.core.AppBase.debug_level`.

                                        The default value of this argument is :data:`~ae.core.DEBUG_LEVEL_DISABLED`.

        :param multi_threading:         pass True if instance is used in multi-threading app.

        :param suppress_stdout:         pass True (for wsgi apps) for to prevent any python print outputs to stdout.

        :param cfg_opt_eval_vars:       dict of additional application specific data values that are used in eval
                                        expressions (e.g. AcuSihotMonitor.ini).

        :param additional_cfg_files:    iterable of additional CFG/INI file names (opt. incl. abs/rel. path).

        :param cfg_opt_val_stripper:    callable for to strip/reformat/normalize the option choices values.

        :param formatter_class:         alternative formatter class passed onto ArgumentParser instantiation.

        :param epilog:                  optional epilog text for command line arguments/options help text (passed
                                        onto ArgumentParser instantiation).

        :param logging_params:          all other kwargs are interpreted as logging configuration values - the
                                        supported kwargs are all the method kwargs of
                                        :meth:`~.core.AppBase.init_logging`.
        """
        if not sys_env_id:
            sys_env_id = env_str(MAIN_SECTION_NAME + '_sys_env_id', convert_name=True) or ''

        super().__init__(app_title=app_title, app_name=app_name, app_version=app_version, sys_env_id=sys_env_id,
                         debug_level=debug_level, multi_threading=multi_threading, suppress_stdout=suppress_stdout)

        with config_lock:
            self._cfg_parser = instantiate_config_parser()                  #: ConfigParser instance
            self.cfg_options: Dict[str, Literal] = dict()                   #: all config options
            self.cfg_opt_choices: Dict[str, Iterable] = dict()              #: all valid config option choices
            self.cfg_opt_eval_vars: dict = cfg_opt_eval_vars or dict()      #: app-specific vars for init of cfg options

            # prepare config files, including default config file (last existing INI/CFG file) for
            # to write to. If there is no INI file at all then create on demand a <app_name>.INI file in the cwd.
            # Note: the main INI file default file path will possibly be overwritten by load_cfg_files.
            self._cfg_files: list = list()                                  #: list of all found INI/CFG files
            self._main_cfg_fnam: str = os.path.join(os.getcwd(), self.app_name + INI_EXT)  #: def main config file name
            self._main_cfg_mod_time: float = 0.0                            #: main config file modification datetime
            self.add_cfg_files(*additional_cfg_files)
            self._cfg_opt_val_stripper: Optional[Callable] = cfg_opt_val_stripper
            #: callable to strip or normalize config option choice values

            self._parsed_arguments: Optional[Namespace] = None
            """ storing returned namespace of ArgumentParser.parse_args() call, used for to retrieve command line args
            """
        self.load_cfg_files()

        log_file_name = self._init_logging(logging_params)

        self.po(self.app_name, " V", app_version, " Startup", self.startup_beg, self.app_title, logger=_logger)
        self.po("####  Initialization......  ####", logger=_logger)

        # prepare argument parser
        if not formatter_class:
            formatter_class = HelpFormatter
        self._arg_parser: ArgumentParser = ArgumentParser(
            description=self.app_title, epilog=epilog, formatter_class=formatter_class)   #: ArgumentParser instance
        # changed for to pass mypy checks (current workarounds are use setattr or add type: ignore:
        # self.add_argument = self._arg_parser.add_argument       #: redirect this method to our ArgumentParser instance
        setattr(self, 'add_argument', self._arg_parser.add_argument)

        # create pre-defined config options
        self.add_opt('debug_level', "Verbosity of debug messages send to console and log files", debug_level, 'D',
                     choices=DEBUG_LEVELS.keys())
        if log_file_name is not None:
            self.add_opt('log_file', "Log file path", log_file_name, 'L')

    def _init_logging(self, logging_params: Dict[str, Any]) -> Optional[str]:
        """ determine and init logging config.

        :param logging_params:      logging config dict passed as args by user that will be amended with cfg values.
        :return:                    None if py logging is active, log file name if ae logging is set in cfg or args
                                    or empty string if no logging got configured in cfg/args.

        The logging configuration can be specified in several alternative places. The precedence
        on various existing configurations is (highest precedence first):

        * :ref:`log_file  <pre-defined-config-options>` :ref:`configuration option <config-options>` specifies
          the name of the used ae log file (will be read after initialisation of this app instance)
        * `logging_params` :ref:`configuration variable <config-variables>` dict with a `py_logging_params` key
          for to activate python logging
        * `logging_params` :ref:`configuration variable <config-variables>` dict with the ae log file name
          in the key `log_file_name`
        * `py_logging_params` :ref:`configuration variable <config-variables>` for to use the python logging module
        * `log_file` :ref:`configuration variable <config-variables>` specifying ae log file
        * :paramref:`~_init_logging.logging_params` dict passing the python logging configuration in the
          key `py_logging_params` to this method
        * :paramref:`~_init_logging.logging_params` dict passing the ae log file in the logging
          key `log_file_name` to this method

        """
        log_file_name = ""
        cfg_logging_params = self.get_var('logging_params')
        if cfg_logging_params:
            logging_params = cfg_logging_params
            if 'py_logging_params' not in logging_params:                       # .. there then cfg py_logging params
                log_file_name = logging_params.get('log_file_name', '')         # .. then cfg logging_params log file
        if 'py_logging_params' not in logging_params and not log_file_name:
            lcd = self.get_var('py_logging_params')
            if lcd:
                logging_params['py_logging_params'] = lcd                       # .. then cfg py_logging params directly
            else:
                log_file_name = self.get_var('log_file', default_value=logging_params.get('log_file_name'))
                logging_params['log_file_name'] = log_file_name                 # .. finally cfg log_file / log file arg
        super().init_logging(**logging_params)

        return None if 'py_logging_params' in logging_params else log_file_name

    def __del__(self):
        """ deallocate this app instance by calling :func:`AppBase.shutdown`. """
        self.shutdown(exit_code=None)

    @AppBase.debug_level.setter
    def debug_level(self, debug_level):
        """ overwriting AppBase setter for to update also the `debug_level` config option. """
        # Seems there is no way to set the value without referencing self._debug_level:
        # .. using following statement ..
        #   AppBase.debug_level.fset(self, debug_level)
        # .. PyCharm complains: Unexpected argument
        # .. and pylint with E1101: Function 'debug_level' has no 'fset' member (no-member)
        # and for the two next alternative statements getting the same pylint error and PyCharm complains:
        # .. Unresolved attribute reference 'fset' for class 'int'
        #   super(ConsoleApp, self.__class__).debug_level.fset(self, debug_level)
        #   super(ConsoleApp, type(self)).debug_level.fset(self, debug_level)
        # additionally PyCharm is showing this setter not as a property but as an attribute (f icon)
        self._debug_level = debug_level
        if self.get_opt('debug_level') != debug_level:
            self.set_opt('debug_level', debug_level)

    def add_argument(self, *args, **kwargs):
        """ define new command line argument.

        Original/underlying args/kwargs of :class:`argparse.ArgumentParser` are used - please see the
        description/definition of :meth:`~argparse.ArgumentParser.add_argument`.

        This method has an alias named :meth:`add_arg`.
        """
        # ### THIS METHOD DEF GOT CODED HERE ONLY FOR SPHINX DOCUMENTATION BUILD PURPOSES ###
        # .. this method get never called because gets overwritten with self._arg_parser.add_argument in __init__().
        self._arg_parser.add_argument(*args, **kwargs)  # pragma: no cover - will never be executed

    add_arg = add_argument      #: alias of method :meth:`.add_argument`

    def get_argument(self, name: str) -> Any:
        """ determine the command line parameter value.

        :param name:    Argument id of the parameter.
        :return:        Value of the parameter.

        This method has an alias named :meth:`get_arg`.
        """
        if not self._parsed_arguments:
            self.parse_arguments()
            self.vpo("ConsoleApp.get_argument call before explicit command line args parsing (run_app call missing)")
        return getattr(self._parsed_arguments, name)

    get_arg = get_argument      #: alias of method :meth:`.get_argument`

    def add_option(self, name: str, desc: str, value: Any,
                   short_opt: str = None, choices: Optional[Iterable] = None, multiple: bool = False):
        """ defining and adding a new config option for this app.

        :param name:        string specifying the option id and short description of this new option.
                            The name value will also be available as long command line argument option (case-sens.).
        :param desc:        description and command line help string of this new option.
        :param value:       default value and the type of the option. This value will be used only if the config values
                            are not specified in any config file. The command line argument option value
                            will always overwrite this value (and any value in any config file).
        :param short_opt:   short option character. If not passed or passed as '' then the first character of the name
                            will be used. Please note that the short options 'D' and 'L' are already used internally
                            by :class:`ConsoleApp` (recommending using lower-case options for your application).
        :param choices:     list of valid option values (optional, default=allow all values).
        :param multiple:    True if option can be added multiple times to command line (optional, default=False).

        The value of a config option can be of any type and gets represented by an instance of the
        :class:`~.literal.Literal` class. Supported value types and literals are documented
        :attr:`here <.literal.Literal.value>`.

        This method has an alias named :meth:`add_opt`.
        """
        if self._parsed_arguments:
            self._parsed_arguments = None        # request (re-)parsing of command line args
            self.vpo("ConsoleApp.add_option call after parse of command line args parsing (re-parse requested)")
        if short_opt == '':
            short_opt = name[0]

        args = list()
        if short_opt and len(short_opt) == 1:
            args.append('-' + short_opt)
        args.append('--' + name)

        # determine config value for to use as default for command line arg
        option = Literal(literal_or_value=value, name=name)
        cfg_val = self._get_cfg_parser_val(name, default_value=value)
        option.value = cfg_val
        kwargs = dict(help=desc, default=cfg_val, type=option.convert_value, choices=choices, metavar=name)
        if multiple:
            kwargs['type'] = option.append_value
            if choices:
                kwargs['choices'] = None    # for multiple options this instance need to check the choices
                self.cfg_opt_choices[name] = choices

        self._arg_parser.add_argument(*args, **kwargs)

        self.cfg_options[name] = option

    add_opt = add_option    #: alias of method :meth:`.add_option`

    def _change_option(self, name: str, value: Any):
        """ change config option and any references to it. """
        self.cfg_options[name].value = value
        if name == 'debug_level' and self.debug_level != value:
            self.debug_level = value

    def get_option(self, name: str, default_value: Optional[Any] = None) -> Any:
        """ get the value of a config option specified by it's name (option id).

        The returned value has the same type as the value specified in the :meth:`add_option` call and
        gets taken either from the command line, the default section (:data:`MAIN_SECTION_NAME`) of any found
        config variable file (with file extension INI or CFG) or from the default values specified in your python code.

        Underneath you find the order of the value search - the first specified/found value will be returned:

        #. command line arguments option value
        #. :ref:`config files <config-files>` added in your app code via the method
           :meth:`add_cfg_files`. These files will be searched for the config option value in reversed order - so the
           last added :ref:`config file <config-files>` will be the first one where the config option will be searched.
        #. :ref:`config files <config-files>` added via :paramref:`~ConsoleApp.additional_cfg_files` argument of
           :meth:`ConsoleApp.__init__` (searched in the reversed order)
        #. <app_name>.INI file in the <cwd>
        #. <app_name>.CFG file in the <cwd>
        #. <app_name>.INI file in the <app_dir>
        #. <app_name>.CFG file in the <app_dir>
        #. .sys_env.cfg in the <cwd>
        #. .sys_env<sys_env_id>.cfg in the <cwd>
        #. .app_env.cfg in the <cwd>
        #. .sys_env.cfg in the parent folder of the <cwd>
        #. .sys_env<sys_env_id>.cfg in the parent folder of the <cwd>
        #. .app_env.cfg in the parent folder of the <cwd>
        #. .sys_env.cfg in the <app_dir>
        #. .sys_env<sys_env_id>.cfg in the <app_dir>
        #. .app_env.cfg in the <app_dir>
        #. .sys_env.cfg in the parent folder of the parent folder of the <cwd>
        #. .sys_env<sys_env_id>.cfg in the parent folder of the parent folder of the <cwd>
        #. .app_env.cfg in the parent folder of the parent folder of the <cwd>
        #. value argument passed into the add_opt() method call (defining the option)
        #. default_value argument passed into this method (only if :class:`~ConsoleApp.add_option` didn't get called)

        **Placeholders in the above search order lists are**:

        * *<cwd>* is the current working directory of your application (determined with :func:`os.getcwd`)
        * *<app_name>* is the base name without extension of your main python code file.
        * *<app_dir>* is the application directory (where your <app_name>.py or the exe file of your app is situated)
        * *<sys_env_id>* is specified as argument of :meth:`ConsoleApp.__init__`

        :param name:            id of the config option.
        :param default_value:   default value of the option (if not defined with :class:`~ConsoleApp.add_option`).

        :return:                first found value of the option identified by :paramref:`~ConsoleApp.get_option.name`.

        This method has an alias named :meth:`get_opt`.
        """
        if not self._parsed_arguments:
            self.parse_arguments()
            self.vpo("ConsoleApp.get_option call before explicit command line args parsing (run_app call missing)")
        return self.cfg_options[name].value if name in self.cfg_options else default_value

    get_opt = get_option    #: alias of method :meth:`.get_option`

    def run_app(self):
        """ prepare app run. call after definition of command line arguments/options and before run of app code. """
        self.parse_arguments()

    def show_help(self):
        """ show help message on console output/stream.

        Original/underlying args/kwargs are used - please see description/definition of
        :meth:`~argparse.ArgumentParser.print_help` of :class:`~argparse.ArgumentParser`.
        """
        self._arg_parser.print_help(file=ori_std_out)

    def parse_arguments(self):
        """ parse all command line args.

        This method get normally only called once and after all the options have been added with :meth:`add_option`.
        :meth:`add_option` will then set the determined config file value as the default value and then the
        following call of this method will overwrite it with command line argument value, if given.
        """
        self._parsed_arguments = self._arg_parser.parse_args()

        for name, cfg_opt in self.cfg_options.items():
            cfg_opt.value = getattr(self._parsed_arguments, name)
            if name in self.cfg_opt_choices:
                for given_value in cfg_opt.value:
                    if self._cfg_opt_val_stripper:
                        given_value = self._cfg_opt_val_stripper(given_value)
                    allowed_values = self.cfg_opt_choices[name]
                    if given_value not in allowed_values:
                        raise ArgumentError(None,
                                            f"Wrong {name} option value {given_value}; allowed are {allowed_values}")

        is_main_app = main_app_instance() is self
        if is_main_app and not self.py_log_params and 'log_file' in self.cfg_options:
            self._log_file_name = self.cfg_options['log_file'].value
            if self._log_file_name:
                self.log_file_check()

        # finished argument parsing - now print chosen option values to the console
        self.debug_level = self.cfg_options['debug_level'].value
        if self.debug_level >= DEBUG_LEVEL_ENABLED:
            self.po("  ##  Debug Level(" + ", ".join([str(k) + "=" + v for k, v in DEBUG_LEVELS.items()]) + "):",
                    self.debug_level, logger=_logger)
            # print sys env - s.a. pyinstaller docs (http://pythonhosted.org/PyInstaller/runtime-information.html)
            if self.sys_env_id or not is_main_app:
                self.po(" ###  Initialized ConsoleApp instance for system env id", self.sys_env_id, logger=_logger)
            self.po("  ##  System Environment:", logger=_logger)
            self.po(sys_env_text(extra_sys_env_dict={'main cfg': self._main_cfg_fnam}), logger=_logger)

        self.startup_end = datetime.datetime.now()
        self.po(self.app_name, " V", self.app_version, "  Args  parsed", self.startup_end, logger=_logger)
        if not is_main_app and not self.sys_env_id:
            self.po("  **  Additional instance of ConsoleApp requested with empty system environment ID",
                    logger=_logger)
        self.po("####  Startup finished....  ####", logger=_logger)

    def set_option(self, name: str, value: Any, cfg_fnam: Optional[str] = None, save_to_config: bool = True) -> str:
        """ set or change the value of a config option.

        :param name:            id of the config option to set.
        :param value:           value to assign to the option, identified by :paramref:`~set_option.name`.
        :param cfg_fnam:        config file name to save new option value. If not specified then the
                                default file name of :meth:`~ConsoleApp.set_variable` will be used.
        :param save_to_config:  pass False to prevent to save the new option value also to a config file.
                                The value of the config option will be changed in any case.
        :return:                ''/empty string on success else error message text.

        This method has an alias named :meth:`set_opt`.
        """
        self._change_option(name, value)
        return self.set_var(name, value, cfg_fnam) if save_to_config else ''

    set_opt = set_option    #: alias of method :meth:`.set_option`

    def add_cfg_files(self, *additional_cfg_files: str) -> str:
        """ extend list of found config files (in :attr:`~ConsoleApp.config_files`).

        :param additional_cfg_files:    additional/user-defined config file names (searched in cwd and .
        :return:                        ""/empty string on success else line-separated list of error message text.
        """
        coll = Collector(app=self.app_path, app_name=self.app_name)
        coll.collect('{cwd}/../..', '{app}', '{usr}', '{usr}/{app_name}', '{cwd}/..', '{cwd}',
                     append=('.app_env.cfg', '.sys_env.cfg', '.sys_env' + (self.sys_env_id or 'TEST') + '.cfg',),
                     only_first_of=())
        coll.collect('{app}', '{usr}', '{usr}/{app_name}', '{cwd}',
                     append=('{app_name}.cfg', '{app_name}.ini'), only_first_of=())
        if additional_cfg_files:
            coll.collect('{cwd}', '{app}', select=additional_cfg_files, only_first_of=())

        self._cfg_files.extend(coll.files)

        return "\n".join(f"Additional config file {cfg_fnam} not found!"
                         for cfg_fnam, count in coll.suffix_failed.items() if count == 2)

    def cfg_section_variable_names(self, section: str, cfg_parser: Optional[ConfigParser] = None) -> Tuple[str, ...]:
        """ determine current config variable names/keys of the passed config file section.

        :param section:         config file section name.
        :param cfg_parser:      ConfigParser instance to use (def=self._cfg_parser).
        :return:                tuple of all config variable names.
        """
        try:                                # quicker than asking before with: if cfg_parser.has_section(section):
            with config_lock:
                return tuple((cfg_parser or self._cfg_parser).options(section))
        except NoSectionError:
            self.dpo(f"ConsoleApp.cfg_section_variable_names: ignoring missing config file section {section}")
            return tuple()

    def _get_cfg_parser_val(self, name: str, section: Optional[str] = None, default_value: Optional[Any] = None,
                            cfg_parser: Optional[ConfigParser] = None) -> Any:
        """ determine thread-safe the value of a config variable from the config file.

        :param name:            name/option_id of the config variable.
        :param section:         name of the config section (def= :data:`MAIN_SECTION_NAME` also if passed as None/'')
        :param default_value:   default value to return if config value is not specified in any config file.
        :param cfg_parser:      ConfigParser instance to use (def=self._cfg_parser).
        """
        with config_lock:
            cfg_parser = cfg_parser or self._cfg_parser
            val = cfg_parser.get(section or MAIN_SECTION_NAME, name, fallback=default_value)
        return val

    def load_cfg_files(self, config_modified: bool = True):
        """  load and parse all config files.

        :param config_modified:     pass False to prevent the refresh/overwrite the initial config file modified date.
        """
        with config_lock:
            for cfg_fnam in reversed(self._cfg_files):
                if cfg_fnam.endswith(INI_EXT) and os.path.isfile(cfg_fnam):
                    self._main_cfg_fnam = cfg_fnam
                    if config_modified:
                        self._main_cfg_mod_time = os.path.getmtime(self._main_cfg_fnam)
                    break

            self._cfg_parser = instantiate_config_parser()      # new instance needed in case of renamed config var
            self._cfg_parser.read(self._cfg_files, encoding='utf-8')

    def is_main_cfg_file_modified(self) -> bool:
        """ determine if main config file got modified.

        :return:    True if the content of the main config file got modified/changed.
        """
        with config_lock:
            return os.path.getmtime(self._main_cfg_fnam) > self._main_cfg_mod_time \
                if self._main_cfg_fnam and self._main_cfg_mod_time else False

    def get_variable(self, name: str, section: Optional[str] = None, default_value: Optional[Any] = None,
                     cfg_parser: Optional[ConfigParser] = None, value_type: Optional[Type] = None) -> Any:
        """ determine value of a :ref:`config option <config-options>` or a :ref:`config variable <config-variables>`.

        :param name:            id/name of a :ref:`config option <config-options>` or the name of a existing/declared
                                :ref:`config variable <config-variables>`.
        :param section:         name of the :ref:`config section <config-sections>` (def= :data:`MAIN_SECTION_NAME`).
        :param default_value:   default value to return if config value is not specified in any config file.
        :param cfg_parser:      optional ConfigParser instance to use (def= :attr:`~ConsoleApp._cfg_parser`).
        :param value_type:      optional type of the config value. Only used for :ref:`config-variables` and
                                ignored for :ref:`config-options`.
        :return:                variable value which will be searched in the OS environment, the :ref:`config-options`
                                and in the :ref:`config-variables` in the following order and manner:

                                * **OS environment variable** with a matching snake+upper-cased name, compiled from
                                  the :paramref:`~get_variable.section` and :paramref:`~get_variable.name` arguments.
                                * **config option** with an id equal to the :paramref:`~get_variable.name` argument
                                  and with a passed :paramref:`~get_variable.section` value that is either empty,
                                  None or equal to the value of :data:`MAIN_SECTION_NAME`.
                                * **config variable** with a name and section equal to the values passed into
                                  the :paramref:`~get_variable.name` and :paramref:`~get_variable.section` arguments.

                                If no variable could be found then a None value will be returned.

        This method has an alias named :meth:`get_var`.
        """
        val = env_str((section or MAIN_SECTION_NAME) + '_' + name, convert_name=True)
        if val is None:
            if name in self.cfg_options and section in (MAIN_SECTION_NAME, '', None):
                val = self.cfg_options[name].value
            else:
                lit = Literal(literal_or_value=default_value, value_type=value_type, name=name)  # used for convert/eval
                lit.value = self._get_cfg_parser_val(name, section=section, default_value=lit.value,
                                                     cfg_parser=cfg_parser)
                val = lit.value
        return val

    get_var = get_variable      #: alias of method :meth:`.get_variable`

    def set_variable(self, name: str, value: Any, cfg_fnam: Optional[str] = None, section: Optional[str] = None,
                     old_name: str = '') -> str:
        """ set/change the value of a :ref:`config variable <config-variables>` and if exists the related config option.

        If the passed string in :paramref:`~set_variable.name` is the id of a defined
        :ref:`config option <config-options>` and :paramref:`~set_variable.section` is either empty or
        equal to the value of :data:`MAIN_SECTION_NAME` then the value of this
        config option will be changed too.

        If the section does not exist it will be created (in contrary to Pythons ConfigParser).

        :param name:            name/option_id of the config value to set.
        :param value:           value to assign to the config value, specified by the
                                :paramref:`~set_variable.name` argument.
        :param cfg_fnam:        file name (def= :attr:`~ConsoleApp._main_cfg_fnam`) to save the new option value to.
        :param section:         name of the config section (def= :data:`MAIN_SECTION_NAME`).
        :param old_name:        old name/option_id that has to be removed (used for to rename config option name/key).
        :return:                ''/empty string on success else error message text.

        This method has an alias named :meth:`set_var`.
        """
        msg = f"****  ConsoleApp.set_var({name!r}, {value!r}) "
        if not cfg_fnam:
            cfg_fnam = self._main_cfg_fnam
        if not section:
            section = MAIN_SECTION_NAME

        if name in self.cfg_options and section in (MAIN_SECTION_NAME, '', None):
            self._change_option(name, value)

        if not cfg_fnam or not os.path.isfile(cfg_fnam):
            return msg + f"INI/CFG file {cfg_fnam} not found." \
                         f" Please set the ini/cfg variable {section}/{name} manually to the value {value!r}"

        err_msg = ''
        with config_lock:
            try:
                cfg_parser = instantiate_config_parser()
                cfg_parser.read(cfg_fnam)
                if isinstance(value, datetime.datetime):
                    str_val = value.strftime(DATE_TIME_ISO)
                elif isinstance(value, datetime.date):
                    str_val = value.strftime(DATE_ISO)
                else:
                    str_val = repr(value)
                str_val = str_val.replace('%', '%%')

                if not cfg_parser.has_section(section):
                    cfg_parser.add_section(section)
                cfg_parser.set(section, name, str_val)
                if old_name:
                    cfg_parser.remove_option(section, old_name)
                with open(cfg_fnam, 'w') as configfile:
                    cfg_parser.write(configfile)

                # refresh self._config_parser cache in case the written var is in one of our already loaded config files
                # .. while keeping the initial modified date untouched
                self.load_cfg_files(config_modified=False)

            except Exception as ex:
                err_msg = msg + f"exception: {ex}"

        return err_msg

    set_var = set_variable  #: alias of method :meth:`.set_variable`
