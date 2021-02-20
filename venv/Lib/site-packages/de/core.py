"""
develop and setup helper functions
==================================

This core portion of the 'de' namespace is
providing helper functions for the development and
the setup of namespace portions.


optional dependencies
---------------------

.. note::
    This portion has two optional dependencies that
    are only needed for special cases, like setup
    hooks or template processing.

The :mod:`ae.literal` portion of the 'ae' namespace
is optionally needed for
:func:`de.core.replace_with_file_content_or_default`
(which is currently used only used by the 'ae'
namespace root package for to patch the .gitlab-ci.yml
file for the portions ae.db_pg, ae.gui_app
and ae.kivy_app).

The :mod:`ae.inspector` portion of the 'ae' namespace
is optionally needed as fallback for
:func:`de.core.replace_with_file_content_or_default`
and for :func:`de.core.nev_update_hook`
(which is currently not used by any ae portion).

Therefore if your namespace portion or app is using
one of these two helper functions than the containing
repository project has to include :mod:`ae.inspector`
respective :mod:`ae.literal` explicitly in their
requirements.txt respective test_requirements.txt files.
"""
import glob
import os
import re
from typing import Callable, Dict, List, Optional, Tuple, Union


__version__ = '0.0.18'       # ALSO CHANGE IN setup.py


NevVarType = Union[str, List[str]]
NevType = Dict[str, NevVarType]


NAMESPACE_EXTEND_ENTRY_POINT = "setup_hooks:extend_namespace_env_vars"  #: default extend nev hook

PORTIONS_COMMON_DIR = 'portions_common_root'            #: default folder in root package for portions common files

_PT_PKG: str = 'sub-package'                            #: sub-package portion type
_PT_MOD: str = 'module'                                 #: module portion type

PY_EXT = '.py'                                          #: default file extension for portions and hooks

REQ_FILE_NAME = 'requirements.txt'                      #: default file name for all/dev requirements
REQ_TEST_FILE_NAME = 'test_requirements.txt'            #: default file name for test requirements

TEMPLATE_FILE_NAME_PREFIX = 'de_tpl_'                   #: template file name prefix
TEMPLATE_PLACEHOLDER_ID_PREFIX = "# "                   #: template id prefix marker
TEMPLATE_PLACEHOLDER_ID_SUFFIX = "#("                   #: template id suffix marker
TEMPLATE_PLACEHOLDER_ARGS_SUFFIX = ")#"                 #: template args suffix marker
TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID = "IncludeFile"    #: placeholder id (func:`replace_with_file_content_or_default`)

VERSION_PATCH_PARSER = re.compile(r"(^__version__ = ['\"]\d*[.])(\d*)([.]\d+[a-z]*['\"])", re.MULTILINE)
""" pre-compiled regular expression for to detect and bump the namespace/package version numbers of version string """


def bump_namespace_version_number(file_name: str) -> str:
    """ read code file version and then increment the patch number by one and write the code file back.

    :param file_name:   code file name to be patched.
    :return:            empty string on success, else error string.
    """
    msg = f"bump_namespace_version_number({file_name}) expects "
    if not os.path.exists(file_name):
        return msg + f"existing code file in folder {os.getcwd()}"
    content = file_content(file_name)
    if not content:
        return msg + f"non-empty code file in {os.getcwd()}"
    content, replaced = VERSION_PATCH_PARSER.subn(lambda m: m.group(1) + str(int(m.group(2)) + 1) + m.group(3), content)
    if replaced != 1:
        return msg + f"single occurrence of module variable __version__, but found {replaced} times"
    with open(file_name, 'w') as file_handle:
        file_handle.write(content)
    return ""


def code_file_version(file_name: str) -> str:
    """ read version of Python code file - from __version__ module variable initialization.

    :param file_name:   file name to read the version number from.
    :return:            version number string.
    """
    content = file_content(file_name)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M)
    if not version_match:
        raise FileNotFoundError(f"Unable to find version string within {file_name}")
    return version_match.group(1)


def file_content(file_name: str) -> str:
    """ returning content of the file specified by file_name arg as string.

    :param file_name:   file name to load into a string.
    :return:            file content string.
    """
    with open(file_name) as file_handle:
        return file_handle.read()


def load_requirements(namespace_name: str, nev: NevType, path: str) -> List[str]:
    """ load requirements from *requirements.txt and return list of portions package names.

    :param namespace_name:  name space name/id.
    :param nev:             dict of namespace environment variables.
    :param path:            folder from where to load the *requirements.txt files.
    :return:                portion package names.
    """
    dev_require: List[str] = list()
    requirements_file = os.path.join(path, nev_str(nev, 'REQ_FILE_NAME'))
    if os.path.exists(requirements_file):
        dev_require.extend(
            _ for _ in file_content(requirements_file).strip().split('\n') if not _.startswith('#'))
    if 'de_core' not in dev_require:
        dev_require.append('de_core')
    nev['docs_require'] = [_ for _ in dev_require if _.startswith('sphinx_')]
    nev['install_require'] = [_ for _ in dev_require if not _.startswith('sphinx_')]
    # if a namespace portion is needed for the setup process then use hyphen/dash instead of underscore
    # e.g. ae-literal instead of ae_literal (then ae.literal will be included in setup_require)
    nev['setup_require'] = [_ for _ in nev['install_require'] if not _.startswith(f'{namespace_name}_')]
    nev['portions_package_names'] = portions_package_names = [_ for _ in dev_require
                                                              if _.startswith(f'{namespace_name}_')]

    tests_require: List[str] = list()
    requirements_file = os.path.join(path, nev_str(nev, 'REQ_TEST_FILE_NAME'))
    if os.path.exists(requirements_file):
        tests_require.extend(_ for _ in file_content(requirements_file).strip().split('\n') if not _.startswith('#'))
    nev['tests_require'] = tests_require

    return portions_package_names


def namespace_env_vars(namespace_name: str, pkg_root_path: str = "", old_nev: Optional[NevType] = None) -> NevType:
    """ update variables, names and file paths of the currently executed/installed namespace development environment.

    :param namespace_name:  root name of this namespace.
    :param pkg_root_path:   optional rel/abs path to package root (def=current working directory).
    :param old_nev          optional current namespace environment variables to be updated.
    :return:                dict with namespace environment variables/info.
    """
    nev: NevType = old_nev if isinstance(old_nev, dict) else dict()
    nev['namespace_name'] = namespace_name

    # add string globals like PORTIONS_COMMON_DIR if not already added
    for var_name, var_val in globals().items():
        if not var_name.startswith('_') and var_name not in nev and isinstance(var_val, str):
            nev[var_name] = var_val

    if not pkg_root_path:
        pkg_root_path = os.getcwd()
    elif not os.path.isabs(pkg_root_path):
        pkg_root_path = os.path.join(os.getcwd(), pkg_root_path)
    nev['package_root_path'] = pkg_root_path

    if os.path.exists(os.path.join(pkg_root_path, 'conf.py')):  # called by RTDocs build
        setup_path = os.path.join(pkg_root_path, '..')
    else:
        setup_path = pkg_root_path
    nev['setup_path'] = setup_path
    setup_file = os.path.join(setup_path, 'setup.py')
    if os.path.exists(setup_file):
        nev['setup_file'] = setup_file

    portion_root_path = os.path.join(setup_path, namespace_name)
    portion_type, portion_name, _ = portion_type_name_modules(portion_root_path)
    nev['portion_type'] = portion_type
    nev['portion_name'] = portion_name
    nev['portion_license'] = "OSI Approved :: GNU General Public License v3 or later (GPLv3+)"

    nev['portion_file_name'] = portion_file_name = \
        portion_name + (os.path.sep + '__init__.py' if portion_type == _PT_PKG else nev_str(nev, 'PY_EXT'))
    nev['portion_file_path'] = portion_file_path = \
        os.path.abspath(os.path.join(portion_root_path, portion_file_name))
    nev['package_name'] = f"{namespace_name}_{portion_name}"
    nev['pip_name'] = f"{namespace_name}-{portion_name.replace('_', '-')}"
    nev['import_name'] = f"{namespace_name}.{portion_name}"
    if portion_type:    # is either portion module or package
        nev['package_version'] = code_file_version(portion_file_path)
    elif 'setup_file' in nev:
        nev['root_version'] = code_file_version(setup_file)
    nev['repo_root'] = f"https://gitlab.com/{namespace_name}-group"
    nev['repo_pages'] = f"https://{namespace_name}-group.gitlab.io"
    nev['pypi_root'] = "https://pypi.org/project"
    nev['portion_pypi_root'] = f"{nev['pypi_root']}/{nev['pip_name']}"

    # extend nev with all requirement-types, read from all *requirements.txt files
    portions_package_names = load_requirements(namespace_name, nev, setup_path)

    if portion_type:    # additional package info exclusively by portions (modules or sub-packages)
        nev['find_packages_include'] = [namespace_name + (".*" if portion_type == _PT_PKG else "")]
    else:               # provide additional package info exclusively used by the root package templates
        namespace_len = len(namespace_name)
        pypi_refs = list()
        idx_names = list()
        for p_name in portions_package_names:
            pypi_refs.append(f'* [{p_name}]({nev["pypi_root"]}/{p_name} "{namespace_name} namespace portion {p_name}")')
            dot_name = p_name[:namespace_len] + '.' + p_name[namespace_len + 1:]
            idx_names.append(dot_name)
            _pt, _pn, extra_modules = portion_type_name_modules(os.path.join(setup_path, '..', p_name, namespace_name))
            for e_mod in extra_modules:
                idx_names.append(dot_name + '.' + e_mod)
        nev['portions_pypi_refs_md'] = "\n".join(pypi_refs)                 # used in root README.md.tpl
        nev['portions_import_names'] = ("\n" + " " * 4).join(idx_names)     # used in docs/index.rst.tpl

    # finally check if optional hook exists and if yes then run it for to change the nev values accordingly
    if nev_update_hook(nev, pkg_root_path) and old_nev is None:
        # run this function one time recursively for to update nev with extended env var values
        nev = namespace_env_vars(namespace_name, pkg_root_path=pkg_root_path, old_nev=nev)

    return nev


def nev_update_hook(nev: NevType, path: str = "") -> bool:
    """ check if optional NAMESPACE_EXTEND_ENTRY_POINT hook file exists and if yes then run it for to change nev values.

    :param nev:         namespace environment variables.
    :param path:        optional path where the hook file is situated (only needed if path is not is sys.path).
    :return:            True if nev got updated, else False.
    """
    try:
        from ae.inspector import module_callable, try_call      # type: ignore   # mypy
    except ImportError:                                         # pragma: no cover
        return False

    entry_point = nev_str(nev, 'NAMESPACE_EXTEND_ENTRY_POINT')
    module, callee = module_callable(entry_point, module_path=path)
    if module and callee:
        try_call(callee, nev)
        if nev_str(nev, 'NAMESPACE_EXTEND_ENTRY_POINT') != entry_point:
            # run the redirected hook recursively, now with a new hook file or function name
            nev_update_hook(nev, path=path)
        return True
    return False


def nev_str(nev: NevType, var_name: str) -> str:
    """ determine string value of namespace environment variable from passed nev or use default.

    AssertionError will be raised if the specified variable value is not of type str. Use :func:`nev_val` instead.

    :param nev:         namespace environment variables.
    :param var_name:    name of variable.
    :return:            variable value - if not exists in nev then the constant/default value of this module or "".
    """
    val = nev_val(nev, var_name)
    assert isinstance(val, str), f"nev_str() can only return environment variables of type string, got {type(val)}"
    return val


def nev_val(nev: NevType, var_name: str) -> NevVarType:
    """ determine value of namespace environment variable from passed nev or use default.

    :param nev:         namespace environment variables.
    :param var_name:    name of variable.
    :return:            variable value - if not exists in nev then the constant/default value of this module or "".
    """
    return nev.get(var_name, globals().get(var_name, ""))


def patch_string(string: str, placeholder: str, replacer: Callable[[str], str], nev: Optional[NevType] = None) -> str:
    """ load file content, then replace patch_name placeholders and return patched/extended file content.

    :param string:      file name to patch (mostly a template).
    :param placeholder: name/id of the placeholder.
    :param replacer:    callable for to convert placeholder args into replacement string.
    :param nev:         optional namespace environment vars used (only needed if TEMPLATE_* constants got patched).
    :return:            file content extended with include snippets found in the same directory.
    """
    if nev is None:
        nev = dict()

    beg = 0
    pre = nev_str(nev, 'TEMPLATE_PLACEHOLDER_ID_PREFIX') + placeholder + nev_str(nev, 'TEMPLATE_PLACEHOLDER_ID_SUFFIX')
    len_pre = len(pre)
    suf = nev_str(nev, 'TEMPLATE_PLACEHOLDER_ARGS_SUFFIX')
    len_suf = len(suf)

    while True:
        beg = string.find(pre, beg)
        if beg == -1:
            break
        end = string.find(suf, beg)
        assert end != -1, f"patch_string() is missing args suffix marker ({suf})"
        string = string[:beg] + replacer(string[beg + len_pre: end]) + string[end + len_suf:]

    return string


def patch_templates(nev: NevType, *exclude_folders: str, **replacer: Callable[[str], str]) -> List[str]:
    """ convert ae namespace package templates found in the cwd or underneath (except excluded) to the final files.

    :param nev:             dict namespace environment variables (determined by namespace_env_vars()).
    :param exclude_folders: directory name prefixes that will be excluded from templates search.
    :param replacer:        optional dict of replacer with key=placeholder-id and value=callable.
                            If not passed then only the replacer with id TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID and its
                            callable/func :func:`replace_with_file_content_or_default` will be executed.
    :return:                list of patched template file names.
    """
    patched = list()
    fn_prefix = nev_str(nev, 'TEMPLATE_FILE_NAME_PREFIX')
    if len(replacer) == 0:
        replacer[nev_str(nev, 'TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID')] = replace_with_file_content_or_default
    for file_path in glob.glob(f"**/{fn_prefix}*.*", recursive=True):
        for folder_prefix in exclude_folders:
            if file_path.startswith(folder_prefix):
                break
        else:
            content = file_content(file_path)
            content = content.format(**nev)
            for key, func in replacer.items():
                content = patch_string(content, key, func)
            path, file = os.path.split(file_path)
            with open(os.path.join(path, file[len(fn_prefix):]), 'w') as file_handle:
                file_handle.write(content)
            patched.append(file_path)
    return patched


def portion_type_name_modules(portion_root_path: str) -> Tuple[str, str, tuple]:
    """ determine portion type, name and optional portion modules (if portion is a sub-package).

    :param portion_root_path:   file path of the root of the namespace portions.
    :return:                    the type, the name and a tuple of additional portion package module names.
    """
    if not os.path.exists(portion_root_path):
        # return placeholders if not run/imported by portion repository (e.g. imported by namespace root repo)
        return "", "{portion-name}", ()

    # first search for single module portion
    files = glob.glob(os.path.join(portion_root_path, '*' + PY_EXT))
    if len(files) == 1:
        return _PT_MOD, os.path.basename(files[0])[:-len(PY_EXT)], ()
    if len(files) > 1:
        raise RuntimeError(f"More than one portion module found: {files}")

    # must be a sub-package (with optional extra modules)
    files = glob.glob(os.path.join(portion_root_path, '*', '*' + PY_EXT))
    if len(files) == 0:
        raise RuntimeError(f"Neither {_PT_MOD} nor {_PT_PKG} found in package path {portion_root_path}")
    extra_modules = list()
    name = ""
    for file_path in files:
        path, mod = os.path.split(file_path)
        if mod == '__init__' + PY_EXT:
            name = os.path.basename(path)
        else:
            extra_modules.append(mod)
    return _PT_PKG, name, tuple(extra_mod[:-len(PY_EXT)] for extra_mod in extra_modules)


def replace_with_file_content_or_default(args_str: str) -> str:
    """ return file content if file name specified in first string arg exists, else return empty string or 2nd arg str.

    :param args_str:    pass either file name or file name and default string separated by a comma character.
    :return:            file content or default string or empty string (if file not exists and no default string given).
    """
    file_name, *default = args_str.split(",", maxsplit=1)
    file_name = file_name.strip()
    if os.path.exists(file_name):
        ret = file_content(file_name)
    elif default:
        try:
            # noinspection PyUnresolvedReferences
            from ae.literal import Literal              # type: ignore  # mypy
            ret = Literal(default[0]).value
        except ImportError:                             # pragma: no cover
            try:
                # noinspection PyUnresolvedReferences
                from ae.inspector import try_eval       # type: ignore  # mypy
                ret = try_eval(default[0], ignored_exceptions=(Exception, ))
                if ret is None:
                    ret = default[0]
            except ImportError:
                ret = default[0]
    else:
        ret = ""
    return ret
