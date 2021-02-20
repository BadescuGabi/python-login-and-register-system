"""
generic file path helpers
=========================

This module is pure python, does only depend on the namespace portion :mod:`ae.system`
and is providing generic file paths together with useful helper functions and classes
that are independent from the operating system.

The currently support operating systems are:

    * android OS
    * iOS
    * linux
    * MacOS
    * Windows


generic system paths
--------------------

Generic system paths are provided by the helper functions:

* :func:`app_data_path`: application data path.
* :func:`app_docs_path`: application documents path.
* :func:`user_data_path`: user data path.
* :func:`user_docs_path`: user documents path.

Additional generic paths like e.g. the current working directory as
well as file path parts (like e.g. the user or application name)
are provided by the :data:`PATH_PLACEHOLDERS` dict.


path helper functions
---------------------

The function :func:`move_paths` is moving paths (including their files and sub-folders).

With :func:`path_files` you can easily determine the files within a folder structure
that are matching the specified wildcards and path part placeholders (provided
by :data:`PATH_PLACEHOLDERS`.


file/folder collection and classification
-----------------------------------------

More specific path examinations on the files and sub-folders of a file path
can be done with the :class:`Collector` class.

The following example is collecting the files with the name `xxx.cfg` in
the current working directory, in the folder above the application data folder,
and in a folder with the name of the application underneath the user data folder::

    coll = Collector()
    coll.collect('{cwd}', '{app}/..', '{usr}/{app_name}', append='xxx.cfg')
    found_files = coll.files

For to add or overwrite the generic path parts values of the application
name (`{app_name}`) and the application data path (`{app}`) you simply
specify them in the construction of the :class:`Collector` instance::

    coll = Collector(app_name=..., app=...)

Additionally you can specify any other placeholders that will be
automatically used and replaced by the :class:`Collector` instance::

    coll = Collector(any_other_placeholder=...)

Found folders will be separately collected within the :class:`Collector` instance
attribute :attr:`~Collector.paths`.

By default only the found file(s)/folder(s) of the first combination
will be collected. For to collect all files instead, pass an empty
tuple to the :meth:`~Collector.collect' method argument
:paramref:`~Collector.collect.only_first_of`::

    coll.collect(..., only_first_of=())

Add one of the strings `'prefix'`, `'append'` or `'select'` to
the :paramref:`~Collector.collect.only_first_of` tuple argument
for to collect only the files/folders of the first combination
of the specified prefixes, append-suffixes and select-suffixes.

The following example determines all folders
underneath the current working directory with a name that contains the string
`'xxx'` or is starting with `'yyy'` or is ending with  `'zzz'`::

    coll = Collector()
    coll.collect('{cwd}', append=('*xxx*', 'yyy*', 'zzz*'))
    folders = coll.paths

By using the :paramref:`~Collector.collect.select` argument the
found files and folders will additionally be collected in
the :class:`Collector` instance attribute :attr:`~Collector.selected`.

The combinations compiled via the :paramref:`~Collector.collect.select`
argument that are not existing will be counted. The results are provided
by the attributes :attr:`~Collector.failed`, :attr:`~Collector.prefix_failed`
and :attr:`~Collector.suffix_failed`.

The :paramref:`~Collector.collect.select` argument can also be
passed together with the :paramref:`~Collector.collect.append`
argument.

Multiple calls of :meth:`~Collector.collect` are accumulating found
files and folders to the respective instance attributes::

    coll = Collector()
    coll.collect(...)
    coll.collect(...)
    ...
    files = coll.files
    folders = coll.paths
    items = coll.selected


.. hint::
    The :mod:`ae.files` namespace portion is providing helpers for to collect
    and cache any type of files.

"""
import glob
import os
import shutil
from typing import Any, Callable, Dict, Iterable, List, Tuple, Type, Union
# from mypy_extensions import KwArg

from ae.system import app_name_guess, env_str, sys_platform             # type: ignore


__version__ = '0.1.2'


def app_data_path() -> str:
    """ determine the os-specific absolute path of the directory where user app data can be stored.

    .. hint:: :func:`app_docs_path` is a more public path to the user.

    :return:    path string of the user app data folder.
    """
    return os.path.join(user_data_path(), app_name_guess())


def app_docs_path() -> str:
    """ determine the os-specific absolute path of the directory where user documents app are stored.

    .. hint:: :func:`app_data_path` is a more hidden path to the user.

    :return:    path string of the user documents app folder.
    """
    return os.path.join(user_docs_path(), app_name_guess())


def move_path(src_folder: str, dst_folder: str, overwrite: bool = False) -> List[str]:
    """ move files from src_folder into dst_folder, optionally overwriting the destination file.

    :param src_folder:      path to source folder/directory where the files get moved from. Placeholders
                            in :data:`PATH_PLACEHOLDERS` will be recognized and substituted.
    :param dst_folder:      path to destination folder/directory where the files get moved to. If
                            you pass an empty string then the user data/preferences path will be used.
                            All placeholders in :data:`PATH_PLACEHOLDERS` are recognized and will be substituted.
    :param overwrite:       pass True to overwrite existing files in the destination folder/directory.
    :return:                list of moved files, with their destination path.
    """
    if not dst_folder:
        dst_folder = user_data_path()
    else:
        dst_folder = dst_folder.format(**PATH_PLACEHOLDERS)
    src_folder = src_folder.format(**PATH_PLACEHOLDERS)

    updated = list()

    if os.path.exists(src_folder):
        for src_file in glob.glob(os.path.join(src_folder, '**'), recursive=True):
            if os.path.isfile(src_file):
                dst_file = os.path.abspath(os.path.join(dst_folder, os.path.relpath(src_file, src_folder)))
                if overwrite or not os.path.exists(dst_file):
                    dst_sub_dir = os.path.dirname(dst_file)
                    if not os.path.exists(dst_sub_dir):
                        os.makedirs(dst_sub_dir)
                    updated.append(shutil.move(src_file, dst_file))

    return updated


def path_files(file_mask: str, recursive: bool = True,
               # file_class: Union[Type[Any], Callable[[str, KwArg()], Any]] = str, **file_kwargs) -> List[Any]:
               file_class: Union[Type[Any], Callable] = str, **file_kwargs) -> List[Any]:
    """ determine existing file(s) underneath the folder specified by :paramref:`~path_files.path`.

    :param file_mask:           glob file mask (with optional glob wildcards and :data:`PATH_PLACEHOLDERS`)
                                specifying the files to collect (by default including the sub-folders).
    :param recursive:           pass False to only collect the given folder (ignoring sub-folders).
    :param file_class:          factory used for the returned list items (see :paramref:`path_items.creator`).
    :param file_kwargs:         additional/optional kwargs apart from file name passed onto the used item_class.
    :return:                    list of files of the class specified by :paramref:`path_files.item_class`.
    """
    return path_items(file_mask, recursive=recursive, selector=os.path.isfile, creator=file_class, **file_kwargs)


def path_folders(folder_mask: str, recursive: bool = True,
                 # folder_class: Union[Type[Any], Callable[[str, KwArg()], Any]] = str, **folder_kwargs) -> List[Any]:
                 folder_class: Union[Type[Any], Callable] = str, **folder_kwargs) -> List[Any]:
    """ determine existing folder(s) underneath the folder specified by :paramref:`~path_folders.path`.

    :param folder_mask:         glob folder mask (with optional glob wildcards and :data:`PATH_PLACEHOLDERS`)
                                specifying the folders to collect (by default including the sub-folders).
    :param recursive:           pass False to only collect the given folder (ignoring sub-folders).
    :param folder_class:        class or factory used for the returned list items (see :paramref:`path_items.creator`).
    :param folder_kwargs:       additional/optional kwargs apart from file name passed onto the used item_class.
    :return:                    list of folders of the class specified by :paramref:`path_folders.item_class`.
    """
    return path_items(folder_mask, recursive=recursive, selector=os.path.isdir, creator=folder_class, **folder_kwargs)


def path_items(item_mask: str, recursive: bool = True, selector: Callable[[str], bool] = os.path.exists,
               # creator: Union[Type[Any], Callable[[str, KwArg()], Any]] = str, **creator_kwargs) -> List[Any]:
               creator: Union[Type[Any], Callable] = str, **creator_kwargs) -> List[Any]:
    """ determine existing file/folder item(s) underneath the folder specified by :paramref:`~path_items.path`.

    :param item_mask:           file path mask (with optional glob wildcards and :data:`PATH_PLACEHOLDERS`)
                                specifying the files/folders to collect (by default including the sub-folders).
    :param recursive:           pass False to only collect within the specified folder (ignoring sub-folders).
    :param selector:            called with each found file/folder name for to check if it has to be added
                                to the returned list.
    :param creator:             each found file/folder will be passed as argument to this class/callable and the
                                instance/return-value will be appended as an item to the returned item list.
                                If not passed then the `str` class will be used, which means that the items
                                of the returned list will be strings of the file/folder path and name.
                                If a class, like e.g. :class:`ae.files.CachedFile`, :class:`ae.files.CachedFile`
                                or :class:`pathlib.Path`, get passed then the items will be instances of this class.
                                Alternatively you can pass a callable which will be called on each found file/folder.
                                In this case the return value of the callable will be inserted in the related
                                item of the returned list.
    :param creator_kwargs:      additional/optional kwargs passed onto the used item_class apart from the item name.
    :return:                    list of found and selected items of the item class (:paramref:`path_items.item_class`).
    """
    if '{' in item_mask and '}' in item_mask:
        item_mask = item_mask.format(**PATH_PLACEHOLDERS)
    # if recursive and '*' not in item_mask and '?' not in item_mask:
    #    item_mask = os.path.join(item_mask, '**')

    items = list()
    for part in glob.glob(item_mask, recursive=recursive):
        if selector(part):
            items.append(creator(part, **creator_kwargs))

    return items


def user_data_path() -> str:
    """ determine the os-specific absolute path of the directory where user data can be stored.

    .. hint:: :func:`user_docs_path` is a more public path to the user.

    :return:    path string of the user data folder.
    """
    platform = sys_platform()
    if platform == 'android':               # pragma: no cover
        from jnius import autoclass, cast   # type: ignore  # pylint: disable=no-name-in-module, import-outside-toplevel
        # noinspection PyPep8Naming
        PythonActivity = autoclass('org.kivy.android.PythonActivity')   # pylint: disable=invalid-name
        context = cast('android.content.Context', PythonActivity.mActivity)
        file_p = cast('java.io.File', context.getFilesDir())
        data_path = file_p.getAbsolutePath()

    elif platform in ('win32', 'cygwin'):
        data_path = env_str('APPDATA')

    else:
        if platform == 'ios':
            data_path = 'Documents'
        elif platform == 'darwin':
            data_path = os.path.join('Library', 'Application Support')
        else:                                       # platform == 'linux' or 'freebsd' or anything else
            data_path = env_str('XDG_CONFIG_HOME') or '.config'

        if not os.path.isabs(data_path):
            data_path = os.path.expanduser(os.path.join('~', data_path))

    return data_path


def user_docs_path() -> str:
    """ determine the os-specific absolute path of the directory where the user is storing the personal documents.

    .. hint:: use :func:`user_data_path` instead for to store more hidden user data.

    :return:    path string of the user documents folder.
    """
    platform = sys_platform()
    if platform == 'android':           # pragma: no cover
        from jnius import autoclass     # type: ignore  # pylint: disable=no-name-in-module, import-outside-toplevel
        # noinspection PyPep8Naming
        Environment = autoclass('android.os.Environment')  # pylint: disable=invalid-name
        docs_path = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOCUMENTS).getAbsolutePath()

    elif platform in ('win32', 'cygwin'):
        docs_path = os.path.join(env_str('USERPROFILE'), 'Documents')

    else:
        docs_path = os.path.expanduser(os.path.join('~', 'Documents'))

    return docs_path


PATH_PLACEHOLDERS = dict()   #: placeholders of user-, os- and app-specific system paths and file name parts

PATH_PLACEHOLDERS['app_name'] = app_name_guess()

PATH_PLACEHOLDERS['app'] = app_data_path()
PATH_PLACEHOLDERS['ado'] = app_docs_path()
PATH_PLACEHOLDERS['cwd'] = os.getcwd()
PATH_PLACEHOLDERS['doc'] = user_docs_path()
PATH_PLACEHOLDERS['log'] = 'logs'
PATH_PLACEHOLDERS['usr'] = PATH_PLACEHOLDERS['eme'] = user_data_path()
PATH_PLACEHOLDERS['eme'] += "/{app_name}/{log}/ae"


class Collector:
    """ file/folder collector """
    def __init__(self, path_scanner: Callable[[str], Iterable] = path_files, **placeholders):
        """ create new file/folder/item collector instance with individual (extended or overriding) placeholders.

        :param path_scanner:        callable for to determine the item type to collect. The default is the
                                    :func:`path_files` function. Pass e.g. :func:`path_folders` for to collect
                                    only folders or :func:`path_items` to collect both (files and folders).
        :param placeholders:        `format` kwargs where keys are the placeholders and the values the replacements.
                                    The placeholders provided by :data:`PATH_PLACEHOLDERS` are available too (but
                                    will be overwritten by these arguments).
        """
        self._path_scanner = path_scanner

        self.paths: List[str] = list()                  #: list of found/collected folder names
        self.files: List[str] = list()                  #: list of found/collected file names
        self.selected: List[str] = list()               #: list of found/collected file/folder item names
        self.failed = 0                                 #: number of not found select-combinations
        self.prefix_failed: Dict[str, int] = dict()     #: number of not found select-combinations for each prefix
        self.suffix_failed: Dict[str, int] = dict()     #: number of not found select-combinations for each suffix

        self.placeholders = PATH_PLACEHOLDERS.copy()    #: path part placeholders of this Collector instance
        self.placeholders.update(placeholders)

    def check_add(self, name: str, select: bool = False) -> bool:
        """ check if name file or folder and if yes append accordingly to instance lists else do nothing.

        :param name:            file/folder name, optionally including wildcards in the glob.glob format.
        :param select:          pass True for to add found files/folders into :attr:`~Collector.selected`.
        :return:                True if at least one file/folder got found/added, else False.
        """
        added_any = False
        for file_path in self._path_scanner(name) if '*' in name or '?' in name else (name,):
            found = True
            if os.path.isdir(file_path):
                self.paths.append(file_path)
                added_any = True
            elif os.path.isfile(file_path):
                self.files.append(file_path)
                added_any = True
            else:
                found = False
            if select and found:
                self.selected.append(file_path)
        return added_any

    def _collect_appends(self, prefix: str, appends: Tuple[str, ...], only_first_of: Tuple[str, ...]):
        for suffix in appends:
            name = os.path.join(prefix, suffix).format(**self.placeholders)
            if self.check_add(name) and 'append' in only_first_of:
                return

    def _collect_selects(self, prefix: str, selects: Tuple[str, ...], only_first_of: Tuple[str, ...]):
        if prefix not in self.prefix_failed:
            self.prefix_failed[prefix] = 0
        for suffix in selects:
            name = os.path.join(prefix, suffix).format(**self.placeholders)
            if not self.check_add(name, select=True):
                self.failed += 1
                self.prefix_failed[prefix] += 1
                if suffix not in self.suffix_failed:
                    self.suffix_failed[suffix] = 0
                self.suffix_failed[suffix] += 1
            elif 'select' in only_first_of:
                return

    def collect(self, *prefixes: str,
                append: Union[str, Tuple[str, ...]] = (), select: Union[str, Tuple[str, ...]] = (),
                only_first_of: Union[str, Tuple[str, ...]] = ('append', 'prefix', 'select', )):
        """ collect additional files/folders by combining the given prefixes with all the given append/select suffixes.

        :param prefixes:        tuple of file/folder paths to be used as prefix.
        :param append:          tuple of file/folder names to be used as suffix.
        :param select:          tuple of file/folder names to be used as suffix.
        :param only_first_of:   tuple with the strings `'prefix'`, `'append'` or `'select'`.
                                If it contains the string `'prefix'` then only the files/folders
                                of the first combination will be collected. If it contains
                                `'append'` then only the files/folders of the first combination
                                done with the suffixes passed into the :paramref:`~collect.append`
                                argument will be collected. If it contains
                                `'select'` then only the files/folders of the first combination
                                done with the suffixes passed into the :paramref:`~collect.select`
                                argument will be collected.

        Each of the passed :paramref:`~collect.prefixes` will be combined with the suffixes
        specified in :paramref:`~collect.append` and in :paramref:`~collect.select`. The
        resulting file/folder paths that are exist, will then be added to the appropriate instance attribute,
        either :attr:`~Collector.files` for a file or :attr:`~Collector.paths` for a folder.

        Additionally the existing file/folder paths from the combinations of
        :paramref:`~collect.prefixes` and :paramref:`~collect.select` will be added
        in the :attr:`~Collector.selected` list attribute.

        All arguments of this method can either be passed either as tuples or as a single string value.

        .. hint:: more details and some examples are available in the doc string of this :mod:`module <ae.paths>`.
        """

        if not append and not select:
            select = ("", )
        else:
            if isinstance(append, str):
                append = (append, )
            if isinstance(select, str):
                select = (select, )
        if isinstance(only_first_of, str):
            only_first_of = (only_first_of, )

        for prefix in prefixes:
            prefix_count = len(self.paths) + len(self.files)
            self._collect_appends(prefix, append, only_first_of)    # type: ignore  # mypy is sometimes so silly?!?!?
            self._collect_selects(prefix, select, only_first_of)
            if 'prefix' in only_first_of and len(self.paths) + len(self.files) > prefix_count:
                break
