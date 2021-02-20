"""
main app base class with context help for flow and app state changes
====================================================================

The class :class:`HelpAppBase` provided by this namespace portion
is extending your application with a context-sensitive help
functionality.

The data-driven approach is providing a help system to your app
which allows to add, edit and remove help texts without the need
to change a single line of code. This gets achieved by overriding the
:meth:`~ae.gui_app.MainAppBase.change_flow` method.

For help support on any functionality that is changing an
app state variable you only need to replace the call of the
:meth:`~ae.gui_app.MainAppBase.change_app_state` in your app
code with the method :meth:`~HelpAppBase.help_app_state_change`.

Finally you only need to add/provide the help texts, which is
done via an separate i18n translation message file for each
of the supported languages.


help layout implementation example
----------------------------------

:class:`HelpAppBase` inherits from :class:`~ae.gui_app.MainAppBase`
while still being independent from the used GUI framework/library.

.. note::
    The user interface for this help system has to be provided
    externally on top of this module. It can either be implemented
    directly in your app project or in a separate module.

Use :class:`HelpAppBase` as base class of the GUI framework
specific main application class and implement the
abstract methods :meth:`~ae.gui_app.MainAppBase.init_app` and
:meth:`~HelpAppBase.ensure_top_most_z_index`::

    from ae.gui_help import HelpAppBase

    class MyMainApp(HelpAppBase):
        def init_app(self, framework_app_class=None):
            self.framework_app = framework_app_class()
            ...
            return self.framework_app.run, self.framework_app.stop

        def ensure_top_most_z_index(self, widget):
            framework_method_to_push_widget_to_top_most(widget)
            ...

For to activate the help mode the widget
for to display the help texts have to be assigned to
the attribute :attr:`~HelpAppBase.ae_help_layout`::

    main_app.ae_help_layout = HelpScreenContainerOrWindow()

So :attr:`~HelpAppBase.ae_help_layout is also used as a flag
of the help mode activity. By assigning `None` to this
attribute the help mode will be deactivated::

    main_app.ae_help_layout = None

Optionally you can use the attribute
:attr:`~HelpAppBase.ae_help_activator` for
to store a widget that allows the user
to toggle the help mode activation. The
:meth:`~HelpAppBase.help_display` is using
it as fallback widget if no help target
widget got found.

.. hint::
    An example implementation of an de-/activation
    method is :meth:`~ae.kivy_app.KivyMainApp.help_activation_toggle`
    situated in the :mod:`ae.kivy_app` namespace portion.

    This more complete example is also demonstrating
    the implementation and usage of the help activator
    and layout widgets (in the classes
    :class:`~ae.kivy_app.HelpToggler` and
    :class:`~ae.kivy_app.HelpLayout`).


additional helper functions
---------------------------

The helper functions :func:`anchor_points`, :func:`layout_ps_hints`,
:func:`layout_x` and :func:`layout_y`, provided
by this module, are covering the framework-independent calculation
of the position and size of the help layout and the anchor.


flow change context message id
------------------------------

The message id for to identify the help texts for each flow
button is composed by the :meth:`~HelpAppBase.help_flow_id`,
using the prefix marker string `'help_flow#'` followed by
the flow id of the flow widget.

.. hint::
    More information regarding the flow id you find in
    the doc string of the module :mod:`ae.gui_app` in the
    section :ref:`application flow`.

For example the message id for a flow button with the
flow action `'open'`, the object `'item'` and the (optional)
flow key `'123456'` is resulting in the following help text
message id::

    `'help_flow#open_item:123456'`

If there is no need for a detailed message id that is taking
the flow key into account, then simply create a help text
message id without the flow key. The method
:meth:`~HelpAppBase.help_display` does first search for
a message id including the flow key in the available
help text files and if not found it will automatically
fallback to use a message id without the flow key::

    `'help_flow#open_item'`


application state change context message id
-------------------------------------------

The message ids for app state change help texts are using
the prefix marker string `'help_app_state#'` followed by
the name of the app state and are composed via the
:meth:`~HelpAppBase.help_app_state_id`.


pluralize-able help texts
-------------------------

Each message id can optionally have several different
help texts for their pluralization. For to support
them simply pass an `count` argument to either
:meth:`~HelpAppBase.change_flow`
:paramref:`~HelpAppBase.change_flow.event_kwargs`
argument or to the
:paramref:`~HelpAppBase.help_app_state_change.count`
argument of the method
:meth:`~HelpAppBase.help_app_state_change`.

With that you can define a help text for the
following count cases in your message text file
like this::

    {
        'message_id': {
                       'zero':      "help text if {count} == 0",    # {count} will be replaced with `'0'`
                       'one':       "help text if count == 1",
                       'many':      "help text if count > 1",
                       'negative':  "help text if count < 0",
                       '':          "fallback help text if count is None",
                       },
       ...
    }


pre- and post-change help texts
-------------------------------

For to display a different help message before and
after the change of the flow id or the app state
define a message dict with the keys `''` (an empty
string) and `'after'` like shown in the following
example::

    {
        'message_id': {
                       '':      "help text displayed before the flow/app-state change.",
                       'after': "help text displayed after the flow/app-state change",
                       },
       ...
    }


i18n help texts
---------------

The displayed help messages related to the message id
will automatically get translated into the default
language of the current system/environment.

The declaration and association of message ids and
their related help messages is done with the help of
the namespace portion :mod:`ae.i18n`.


further examples
----------------

More details on these and other features of this
help system, e.g. the usage of
f-strings in the help texts, is documented in the
doc string of the :mod:`ae.i18n` module.

A more complex example app demonstrating the features
of this context help system can be found in the
repository of the
`kivy lisz demo app <https://gitlab.com/ae-group/kivy_lisz>`_.

"""
from abc import abstractmethod, ABC
from typing import Any, Dict, Optional, Sequence, Tuple, Union

from ae.inspector import stack_vars, try_eval                                   # type: ignore
from ae.i18n import default_language, get_f_string, translation                 # type: ignore
from ae.gui_app import FLOW_KEY_SEP, id_of_flow, MainAppBase                    # type: ignore


__version__ = '0.1.6'


HELP_ID_FLOW_PREFIX = 'help_flow#'
IGNORED_HELP_FLOWS = (id_of_flow('close', 'flow_popup'), )  #: tuple of flow ids never search/show help text for


def anchor_points(radius: float, anchor_x: float, anchor_y: float, anchor_dir: str) -> Tuple[float, ...]:
    """ recalculate points of the anchor triangle drawing.

    :param radius:          radius of anchor triangle.
    :param anchor_x:        anchor x coordinate in window.
    :param anchor_y:        anchor y coordinate in window.
    :param anchor_dir:      anchor direction: 'r'=right, 'i'=increase-y, 'l'=left, 'd'=decrease-y

                            .. note:
                                the direction in the y axis got named increase for higher y values
                                and `decrease` for lower y values for to support different coordinate
                                systems of the GUI frameworks.

                                For example in `kivy` the zero value of the y axis is at the bottom
                                of the app window, whereas in enaml/qt it is at the top.

    :return:                tuple of the x and y coordinates of the anchor triangle edges.
    """
    return (anchor_x - (radius if anchor_dir in 'id' else 0),
            anchor_y - (radius if anchor_dir in 'lr' else 0),
            anchor_x + (0 if anchor_dir in 'id' else radius * (-1 if anchor_dir == 'r' else 1)),
            anchor_y + (0 if anchor_dir in 'lr' else radius * (-1 if anchor_dir == 'i' else 1)),
            anchor_x + (radius if anchor_dir in 'id' else 0),
            anchor_y + (radius if anchor_dir in 'lr' else 0),
            )


def layout_ps_hints(wid_x: float, wid_y, wid_width, wid_height, win_width, win_height) -> Dict[str, Union[str, float]]:
    """ recalculate anchor and max width/height on change of widget pos/size or window size.

    :param wid_x:           x coordinate in app window of help target flow widget.
    :param wid_y:           y coordinate in app window of help target flow widget.
    :param wid_width:       width of help target flow widget.
    :param wid_height:      height of help target flow widget.
    :param win_width:       app window width.
    :param win_height:      app window height.
    :return:                dict with position and size hints, like e.g.:

                            * anchor_dir:       direction of the anchor triangle (pointing from help layout
                                                to the help target widget):
                                                'r'=right, 'i'=increase-y, 'l'=left, 'd'=decrease-y(kivy:bottom/qt:top).
                            * anchor_x:         x coordinate of the anchor center.
                            * anchor_y:         y coordinate of the anchor center.
                            * max_width:        maximum width of the layout.
                            * max_height:       maximum height of the layout.

    """
    max_width = win_width - wid_x - wid_width
    if max_width < wid_x:
        max_width = wid_x
        anchor_dir_x = 'l'
    else:
        anchor_dir_x = 'r'
    max_height = win_height - wid_y - wid_height
    if max_height < wid_y:
        max_height = wid_y
        anchor_dir_y = 'd'
    else:
        anchor_dir_y = 'i'
    if max_width > max_height:
        anchor_dir = anchor_dir_x
        anchor_x = wid_x + (0 if anchor_dir_x == 'l' else wid_width)
        anchor_y = wid_y + wid_height / 2
        max_height = win_height
    else:
        anchor_dir = anchor_dir_y
        anchor_x = wid_x + wid_width / 2
        anchor_y = wid_y + (0 if anchor_dir_y == 'd' else wid_height)
        max_width = win_width

    return locals()


def layout_x(anchor_x: float, anchor_dir: str, width: float, win_width: float) -> float:
    """ recalculate help layout x position.

    :param anchor_x:        anchor x coordinate in window.
    :param anchor_dir:      anchor direction: 'r'=right, 'i'=increase-y, 'l'=left, 'd'=decrease-y (kivy:bottom, qt:top).
    :param width:           help layout width.
    :param win_width:       app window width.
    :return:                x coordinate of help layout within the app window.
    """
    if anchor_dir == 'l':
        return anchor_x - width
    if anchor_dir == 'r':
        return anchor_x
    return min(max(0.0, anchor_x - width / 2), win_width - width)


def layout_y(anchor_y: float, anchor_dir: str, height: float, win_height: float) -> float:
    """ recalculate help layout y position.

    :param anchor_y:        anchor y coordinate in window.
    :param anchor_dir:      anchor direction: 'r'=right, 'i'=increase-y, 'l'=left, 'd'=decrease-y (kivy:bottom, qt:top).
    :param height:          help layout height.
    :param win_height:      app window height.
    :return:                y coordinate of help layout in the app window.
    """
    if anchor_dir == 'i':
        return anchor_y
    if anchor_dir == 'd':
        return anchor_y - height
    return min(max(0.0, anchor_y - height / 2), win_height - height)


class HelpAppBase(MainAppBase, ABC):
    """ main app help base class. """

    # additional instance attributes
    ae_help_activator: Any = None           #: help flow mode de-/activator button widget
    ae_help_id: str = ''                    #: message id of the currently explained/focused target widget in help mode
    ae_help_layout: Optional[Any] = None    #: container/popup/dropdown/window widget in active help flow mode else None

    @abstractmethod
    def ensure_top_most_z_index(self, widget: Any):
        """ ensure visibility of the passed widget to be the top most in the z index/order.

        :param widget:          the popup/dropdown/container widget to be moved to the top.
        """

    def change_flow(self, new_flow_id: str, popups_to_close: Sequence = (), **event_kwargs) -> bool:
        """ change/switch flow id - overriding :meth:`~ae.gui_app.MainAppBase.change_flow`.

        :param new_flow_id:     new flow id (maybe overwritten by event handlers in event_kwargs['flow_id']).
        :param popups_to_close: optional sequence of widgets to be closed on confirmed flow change.
        :param event_kwargs:    optional args to pass additional data or info onto and from the event handler
                                and to the help text renderer.

                                info pass onto event handler:
                                    * `popup_kwargs`: optional dict passed to the Popup `__init__` method,
                                      like e.g. dict(parent=parent_widget_of_popup, data=...).

                                info passed from the event handler:
                                    * `flow_id`: process :attr:`~ae.gui_app.MainAppBase.flow_path` as specified by the
                                      :paramref:`~change_flow.new_flow_id` argument, but then overwrite this flow id
                                      with this event arg value for to set :attr:`~ae.gui_app.MainAppBase.flow_id`.

                                passed to the help text renderer:
                                    * `count`: optional number used for to render a pluralized help text
                                      for this flow change.

        :return:                True if flow changed and got confirmed by a declared custom event handler
                                (either event method or Popup class) of the app
                                AND if the help mode is *not* active or the calling widget is selected
                                in active help mode, else False.
                                Some flow actions are handled internally independent from the
                                return value of a found/declared
                                custom event handler, like e.g. `'enter'` or `'leave'` will always
                                extend/reduce the flow path and the action `'focus'` will give the
                                indexed widget the input focus (these exceptions are configurable via
                                the list :data:`ACTIONS_CHANGING_FLOW_WITHOUT_CONFIRMATION`).
        """
        count = event_kwargs.pop('count', None)
        help_args = locals()
        if not self.help_flow_display(help_args, count=count):
            if super().change_flow(new_flow_id, popups_to_close=popups_to_close, **event_kwargs):
                return self.help_flow_display(help_args, changed=True, count=count)
        return False

    def help_app_state_change(self, state_name: str, new_value: Any,
                              send_event: bool = True, count: Optional[int] = None):
        """ change app state via :meth:`~ae.gui_app.MainAppBase.change_app_state`, show help text in active help mode.

        :param state_name:      name of the app state to change.
        :param new_value:       new value of the app state to change.
        :param send_event:      pass False to prevent to send/call the on_<state_name> event to the main app instance.
        :param count:           optional item count for pluralized help texts.
        """
        help_vars = locals()
        if not self.help_app_state_display(help_vars, count=count):
            self.change_app_state(state_name, new_value, send_event=send_event)
            self.help_app_state_display(help_vars, changed=True, count=count)

    def help_app_state_display(self, help_vars: Dict[str, Any], changed: bool = False, count: Optional[int] = None
                               ) -> bool:
        """ actualize the help layout if active, before and after the change of the app state.

        :param help_vars:       locals (args/kwargs) of overwritten :meth:`~ae.gui_app.MainAppBase.change_flow` method.
        :param changed:         False before change to new flow, pass True if flow got changed already.
        :param count:           item count for pluralized help texts.
        :return:                return value for caller (:meth:`~ae.gui_app.MainAppBase.change_flow`) which is
                                True if help layout is active and got updated, else False.
        """
        hlw = self.ae_help_layout
        if hlw is None:
            return changed              # inactive help layout

        widget = None
        state_name = help_vars['state_name']
        help_id = self.help_app_state_id(state_name)
        if help_id == self.ae_help_id:
            if not changed:
                return False            # allow to execute app state change
        else:
            widget = self.help_widget('ae_state_name', state_name, help_vars)

        key_suffix = 'after' if changed else ''
        self.help_display(help_id, help_vars, widget, count=count, key_suffix=key_suffix, must_have=not changed)

        return True

    @staticmethod
    def help_app_state_id(state_name: str) -> str:
        """ compose help id for app state changes.

        :param state_name:      name of the app state variable.
        :return:                help id for the specified app state.
        """
        return f'help_app_state#{state_name}'

    def help_display(self, help_id: str, help_vars: Dict[str, Any], widget: Optional[Any] = None,
                     count: Optional[int] = None, key_suffix: str = '', must_have: bool = False):
        """ display help text to the user in activated help flow mode.

        :param help_id:         help id to show help text for.
        :param help_vars:       variables used in the conversion of the f-string expression to a string.
        :param widget:          target widget for to show help text for.
        :param count:           pass if the translated text changes on pluralization (see :func:`get_text`).
                                If passed then the value of this argument will be provided/overwritten in the
                                globals as a variable with the name `count`.
        :param key_suffix:      suffix to the key used if the translation is a dict.
        :param must_have:       pass True for to display error help text and console output if no help text exists.
        """
        hlw: Any = self.ae_help_layout
        hlw.widget = widget or self.ae_help_activator

        self.change_observable('ae_help_id', help_id)

        has_trans = translation(help_id)
        if not has_trans and FLOW_KEY_SEP in help_id:
            help_id = help_id[:help_id.index(FLOW_KEY_SEP)]  # remove detail (e.g. flow key or app state value)
            has_trans = translation(help_id)

        if must_have and not has_trans:
            if self.debug:
                hlw.help_text = f"help id [b]'{help_id}'[/b] has no\ntranslated help text in '{default_language()}'"
            else:
                help_id = ''        # show at least initial help text as fallback
                has_trans = True
            self.play_beep()

        if has_trans:
            help_vars['app'] = self.framework_app
            help_vars['main_app'] = self
            hlw.help_text = get_f_string(help_id, count=count, key_suffix=key_suffix,
                                         glo_vars=try_eval('globals()'), loc_vars=help_vars)

        self.ensure_top_most_z_index(hlw)

    def help_flow_display(self, help_vars: Dict[str, Any], changed: bool = False, count: Optional[int] = None) -> bool:
        """ actualize the help layout if active, exclusively called by :meth:`~ae.gui_app.MainAppBase.change_flow`.

        :param help_vars:       locals (args/kwargs) of overwritten :meth:`~ae.gui_app.MainAppBase.change_flow` method.
        :param changed:         False before change to new flow, pass True if flow got changed already.
        :param count:           item count for pluralized help texts.
        :return:                return value for caller (:meth:`~ae.gui_app.MainAppBase.change_flow`) which is
                                True if help layout is active and got updated, else False.
        """
        hlw = self.ae_help_layout
        if hlw is None:
            return changed              # inactive help layout

        nfi = help_vars['new_flow_id']
        if nfi in IGNORED_HELP_FLOWS:
            if not changed:     # check help target widget is still visible and if not then show initial help text
                wid = self.widget_by_flow_id(self.help_id_flow())
                if wid is None or not getattr(wid, 'visible', True):
                    self.help_display('', dict())
            return changed

        help_id = self.help_flow_id(nfi)
        if help_id == self.ae_help_id:
            if not changed:
                return False            # allow to execute flow change of currently explained flow button
            widget = hlw.widget
            self.help_widget('ae_flow_id', nfi, help_vars)  # extend help_vars also for 'changed/after' help text
        else:
            widget = self.help_widget('ae_flow_id', nfi, help_vars)

        key_suffix = 'after' if changed else ''
        self.help_display(help_id, help_vars, widget, count=count, key_suffix=key_suffix, must_have=not changed)

        return True

    @staticmethod
    def help_flow_id(flow_id: str) -> str:
        """ compose help id for flow changes.

        :param flow_id:         flow id to show help text for.
        :return:                help id for the specified flow id and suffix.
        """
        return f'{HELP_ID_FLOW_PREFIX}{flow_id}'

    def help_id_flow(self) -> str:
        """ determine flow id of the current help id. """
        hid = self.ae_help_id
        if hid.startswith(HELP_ID_FLOW_PREFIX):
            return hid[len(HELP_ID_FLOW_PREFIX):]
        return ''

    def help_widget(self, attr_name: str, attr_value: str, help_vars: Dict[str, Any]) -> Optional[Any]:
        """ get help target widget via variable name/value and extend :paramref:`~help_widget.help_vars` locals.

        :param attr_name:       widget attribute name for to detect widget and declaration locals.
        :param attr_value:      widget attribute value for to detect widget and declaration locals
        :param help_vars:       help flow variables, to be extended with event activation stack frame locals.
        :return:                found help target widget or None if not found.
        """
        depth = 3
        while depth <= 12:
            # look for FlowButton widget in kv/enaml rule call stack frame for translation text context
            _gfv, lfv, _deep = stack_vars('do not skip ae_gui_app', min_depth=depth, max_depth=depth)
            widget = lfv.get('self')
            if getattr(widget, attr_name, None) == attr_value:
                help_vars.update(lfv)
                return widget
            depth += 1

        self.dpo(f"help_widget(): {attr_name} value '{attr_value}' not found up to the {depth - 5}th stack level")

        return None
