"""
Internationalization / Localization helpers
===========================================

On importing this portion it will automatically determine the default locale of
your operating system and user configuration. Additionally it will check the
current working directory for a folder with the name ``loc`` and if it exists
load the translatable message texts for the determined language accordingly.

For to determine or to change the default language and message text encoding the
functions :func:`default_language` and :func:`default_encoding` are provided
by this portion.

For to specify other locale folders you can use the function :func:`add_paths`,
which is calling :func:`init_installed_languages` for to prepare the loading
of additional translations.

In any locale folder have to exist one sub-folder with a name of the
language code (e.g. 'en' for english) for each supported language.

In each of these sub-folders there have to be at least on message translation
file with a file name ending in the string specified by the constant
:data:`MSG_FILE_SUFFIX`).

Additional languages have to be explicitly loaded with the function
:func:`load_language_texts`.


translatable message texts and f-strings
----------------------------------------

Simple message texts can be enclosed in the code of your application with the
:func:`get_text` function, which can also be imported with the underscore alias
from this module (the function :func:`_`)::

    from ae.i18n import _

    message = _("any translatable message displayed to the app user.")
    print(message)          # prints the translated message text

For more complex messages with placeholders you can use the :func:`get_f_string`
function or its short alias :func:`f_`::

    from ae.i18n import f_

    my_var = 69
    print(f_("The value of my_var is {my_var}."))

Translatable message can also be provided in various pluralization forms.
For to get a pluralized message you have to pass the :paramref:`~get_text.count`
keyword argument of :func:`get_text`::

    print(_("child", count=1))     # translated into "child" (in english) or e.g. "Kind" in german
    print(_("child", count=3))     # -> "children" (in english) or e.g. "Kinder" (in german)

For pluralized message translated by the :func:`get_f_string` function, the count value have to
be passed in the `count` item of the :paramref:`~get_f_string.loc_vars`::

    print(f_("you have {count] children", loc_vars=dict(count=1)))  # -> "you have 1 child" or e.g. "Sie haben 1 Kind"
    print(f_("you have {count] children", loc_vars={'count': 3}))   # -> "you have 3 children" or "Sie haben 3 Kinder"

You can load several languages into your app run-time. For to get the translation for a language
that is not the current default language you have to pass the :paramref:`~get_text.language` keyword argument
with the desired language code onto the call of :func:`get_text` (or :func:`get_f_string`)::

    print(_("message", language='es'))   # returns the spanish translation text of "message"
    print(_("message", language='de'))   # returns the german translation text of "message"

The helper function :func:`translation` can be used for to determine if a translation exists for
a message text.
"""
import ast
import locale
import os
from typing import Any, Dict, List, Optional, Tuple, Union

from ae.system import app_name_guess                    # type: ignore
from ae.paths import Collector                          # type: ignore
from ae.files import FilesRegister                      # type: ignore
from ae.inspector import stack_variables, try_eval      # type: ignore


__version__ = '0.1.11'


MsgType = Union[str, Dict[str, str]]                    #: type of message translations within :data:`MSG_FILE_SUFFIX`
LanguageMessages = Dict[str, MsgType]                   #: type of the data structure storing the loaded messages


MSG_FILE_SUFFIX = 'Msg.txt'                             #: file name containing translated texts of a language/locale
DEF_LANGUAGE = 'en'                                     #: language code of the messages in your app code
DEF_ENCODING = 'UTF-8'                                  #: encoding of the messages in your app code

_LANG, _ENC = locale.getdefaultlocale()
if not _LANG:
    _LANG = DEF_LANGUAGE     # pragma: no cover
elif '_' in _LANG:
    _LANG = _LANG.split('_')[0]
if not _ENC:
    _ENC = DEF_ENCODING      # pragma: no cover
default_locale: List[str] = [_LANG, _ENC]               #: language and encoding code of the current language/locale
del _LANG, _ENC

COLL_FILES: List[str] = list()                          #: file paths for to search for locale configurations/messages
INSTALLED_LANGUAGES: List[str] = list()                 #: list of all languages found in the :data:`local_paths`
LOADED_LANGUAGES: Dict[str, LanguageMessages] = dict()  #: message text translations of all loaded languages


def default_language(new_lang: str = '') -> str:
    """ get and optionally set the default language code.

    :param new_lang:    new default language code to be set. Kept unchanged if not passed.
    :return:            old default language (or current one if :paramref:`~default_language.new_lang` get not passed).
    """
    old_lang = default_locale[0]
    if new_lang:
        default_locale[0] = new_lang
        if new_lang in INSTALLED_LANGUAGES and new_lang not in LOADED_LANGUAGES:
            load_language_texts(new_lang)
    return old_lang


def default_encoding(new_enc: str = '') -> str:
    """ get and optionally set the default message text encoding.

    :param new_enc:     new default encoding to be set. Kept unchanged if not passed.
    :return:            old default encoding (current one if :paramref:`~default_encoding.new_enc` get not passed).
    """
    old_enc = default_locale[1]
    if new_enc:
        default_locale[1] = new_enc
    return old_enc


def init_installed_languages(*file_paths: str, reset: bool = True):
    """ init/add/register file paths for to search for language and region configurations.

    The list of installed translation languages will automatically be updated.

    :param file_paths:  optional tuple of additional locale folder root paths. Each folder path is containing
                        sub-folders for each supported language/locale. The name of each
                        sub is the language code of the locale (e.g. `en` for english, `es` for spanish, ...).
    :param reset:       True (==def) for to clear previously added paths and rescan the configured/supported languages.
    """
    global INSTALLED_LANGUAGES, COLL_FILES

    # faster than locale_paths[:] = [] (https://stackoverflow.com/questions/850795/different-ways-of-clearing-lists)
    if reset:
        INSTALLED_LANGUAGES *= 0
        prefixes: Tuple[str, ...] = ('{eme}/loc', '{cwd}/loc', '{usr}/loc', )
    else:
        prefixes = ()
    prefixes += file_paths
    if not prefixes:
        prefixes = ('{cwd}', )

    coll = Collector(app_name=app_name_guess())
    coll.collect(*prefixes, select="**/*" + MSG_FILE_SUFFIX, only_first_of='prefix')
    COLL_FILES = coll.files

    reg_files = FilesRegister()
    for file in COLL_FILES:
        reg_files.add_file(file)

    for main_msg_file in reg_files.get(os.path.splitext(MSG_FILE_SUFFIX)[0], ()):
        INSTALLED_LANGUAGES.append(os.path.basename(os.path.dirname(main_msg_file)))


def load_language_file(file_name: str, encoding: str, language: str):
    """ load file content encoded with the given encoding into the specified language.

    :param file_name:       file name (incl. path and extension to load.
    :param encoding:        encoding id string.
    :param language:        language id string.
    """
    with open(file_name, encoding=encoding) as file_handle:  # refactor with de.core.file_content into ae.core
        file_content = file_handle.read()
    if file_content:
        lang_messages = ast.literal_eval(file_content)
        if lang_messages:
            LOADED_LANGUAGES[language].update(lang_messages)


def load_language_texts(language: str, encoding: str = '', domain: str = '', reset: bool = False):
    """ load translatable message texts for the given language and optional domain.

    :param language:    language code to load.
    :param encoding:    encoding to use for to load message file.
    :param domain:      optional domain id, e.g. the id of an app, attached process or a user. if passed
                        then it will be used as prefix for the message file name to be loaded.
    :param reset:       pass True for to clear all previously added language/locale messages.
    """
    global LOADED_LANGUAGES
    if reset:
        LOADED_LANGUAGES.clear()
    if language not in LOADED_LANGUAGES:
        LOADED_LANGUAGES[language] = dict()
    if not encoding:
        encoding = default_locale[1]

    main_file = ""
    for file_path in COLL_FILES:
        path, file = os.path.split(file_path)
        if os.path.basename(path) == language:
            if file == domain + MSG_FILE_SUFFIX:
                main_file = file_path
            else:
                load_language_file(file_path, encoding, language)
    if main_file:
        load_language_file(main_file, encoding, language)


def get_text(text: str, count: Optional[int] = None, key_suffix: str = '', language: str = '') -> str:
    """ translate passed text string into the current language.

    :param text:        text message to be translated.
    :param count:       pass int value if the translated text has variants for their pluralization.
                        The count value will be converted into an amount/pluralize key by the
                        function :func:`plural_key`.
    :param key_suffix:  suffix to the key used if the translation is a dict.
    :param language:    language code to load (def=current language code in 1st item of :data:`default_locale`).
    :return:            translated text message or the value passed into :paramref:`~get_text.text`
                        if no translation text got found for the current language.
    """
    trans = translation(text, language=language)
    if isinstance(trans, str):
        text = trans
    elif trans is not None:
        text = trans.get(plural_key(count) + key_suffix, text)
    return text


_ = get_text         #: alias of :func:`get_text`.


def get_f_string(f_str: str, key_suffix: str = '', language: str = '',
                 glo_vars: Optional[Dict[str, Any]] = None, loc_vars: Optional[Dict[str, Any]] = None
                 ) -> str:
    """ translate passed f-string into a message string of the passed / default language.

    :param f_str:       f-string to be translated and evaluated.
    :param key_suffix:  suffix to the key used if the translation is a dict.
    :param language:    language code to load (def=current language code in 1st item of :data:`default_locale`).
    :param glo_vars:    global variables used in the conversion of the f-string expression to a string.
                        The globals() of the caller of the callee will be available too and get overwritten
                        by the items of this argument.
    :param loc_vars:    local variables used in the conversion of the f-string expression to a string.
                        The locals() of the caller of the callee will be available too and get overwritten
                        by the items of this argument.
                        Pass a numeric value in the `count` item of this dict for pluralized translated texts
                        (see also :paramref:`~get_text.count` parameter of the function :func:`get_text`).
    :return:            translated text message or the evaluated string result of the expression passed into
                        :paramref:`~get_f_string.f_str` if no translation text got found for the current language.
                        Any syntax errors and exceptions occurring in the conversion of the f-string will be
                        ignored and the original or translated f_string value will be returned in these cases.
    """
    count = loc_vars.get('count') if isinstance(loc_vars, dict) else None
    f_str = get_text(f_str, count=count, key_suffix=key_suffix, language=language)

    ret = ''
    if '{' in f_str and '}' in f_str:  # performance optimization: skip f-string evaluation if no placeholders
        g_vars, l_vars, _ = stack_variables(max_depth=3)
        if glo_vars is not None:
            g_vars.update(glo_vars)
        if loc_vars is not None:
            l_vars.update(loc_vars)

        ret = try_eval('f"""' + f_str + '"""', ignored_exceptions=(Exception, ), glo_vars=g_vars, loc_vars=l_vars)

    return ret or f_str


f_ = get_f_string       #: alias of :func:`get_f_string`.


def plural_key(count: Optional[int]) -> str:
    """ convert number in count into a dict key for to access the correct plural form.

    :param count:       number of items used in the current context or None (resulting in empty string).
    :return:            dict key (prefix) within the MsgType part of the translation data structure.
    """
    if count is None:
        key = ''
    elif count == 0:
        key = 'zero'
    elif count == 1:
        key = 'one'
    elif count > 1:
        key = 'many'
    else:
        key = 'negative'

    return key


def translation(text: str, language: str = '') -> Optional[Union[str, MsgType]]:
    """ determine translation for passed text string and language.

    :param text:        text message to be translated.
    :param language:    language code to load (def=current language code in 1st item of :data:`default_locale`).
    :return:            None if not found else translation message or dict with plural forms.
    """
    if not language:
        language = default_locale[0]

    if language in LOADED_LANGUAGES:
        translations = LOADED_LANGUAGES[language]
        if text in translations:
            return translations[text]
    return None


# load and set the system/os locale/language/encoding as the app defaults at startup (import)
init_installed_languages()
if default_locale[0] in INSTALLED_LANGUAGES:  # pragma: no cover
    load_language_texts(default_locale[0], encoding=default_locale[1])
