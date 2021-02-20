"""
context help system for your kivy apps
======================================

This namespace portion is a requirement of the :mod:`ae.kivy_app`
module and is tight coupled to it. For to keep the module size
small it got extracted into its own namespace portion.

:mod:`ae.kivy_app` is automatically importing/integrating this
module for you. For android apps built with buildozer you only need
to add it to the requirements list in your `buildozer.spec` file.

Use the widget :class:`HelpToggler` provided by this namespace
portion in your app for to toggle the help mode.

The layout widget :class:`HelpLayout` of this module is
displaying the help texts prepared by the
:meth:`~ae.gui_help.HelpAppBase.help_display` method of the
namespace portion :mod:`ae.gui_help`.
"""
from kivy.input import MotionEvent                                                  # type: ignore
from kivy.lang import Builder                                                       # type: ignore
# pylint: disable=no-name-in-module
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty         # type: ignore
from kivy.uix.image import Image                                                    # type: ignore
from kivy.uix.scrollview import ScrollView                                          # type: ignore
from kivy.uix.widget import Widget                                                  # type: ignore
from kivy.app import App                                                            # type: ignore


__version__ = '0.1.3'


Builder.load_string("""\
#: import anchor_points ae.gui_help.anchor_points
#: import layout_x ae.gui_help.layout_x
#: import layout_y ae.gui_help.layout_y
#: import layout_ps_hints ae.gui_help.layout_ps_hints


<HelpBehaviour>:
    ae_help_id:
        app.main_app.help_flow_id(self.ae_flow_id) if hasattr(self, 'ae_flow_id') else \
        app.main_app.help_app_state_id(self.ae_state_name) if hasattr(self, 'ae_state_name') else \
        ''
    # 'ae_help_layout is not None' is needed because None is not allowed for bool ae_help_lock attribute/property
    ae_help_lock: app.ae_help_layout is not None and app.ae_help_id != self.ae_help_id
    canvas.after:
        Color:
            rgba: app.font_color[:3] + (0.27 if self.ae_help_lock else 0, )
        Ellipse:
            pos: self.x + dp(3), self.y + dp(3)
            size: self.width - dp(6), self.height - dp(6)
        Color:
            rgba: app.font_color[:3] + (0.54 if self.ae_help_lock else 0, )
        Line:
            width: sp(3)
            rounded_rectangle: self.x + dp(3), self.y + dp(3), self.width - dp(6), self.height - dp(6), sp(15)


<HelpLayout>:
    size_hint: None, None
    ps_hints: layout_ps_hints(*root.widget.to_window(*root.widget.pos), *root.widget.size, Window.width, Window.height)
    width: min(help_label.width, Window.width)
    height: min(help_label.height, Window.height)
    x: layout_x(root.ps_hints['anchor_x'], root.ps_hints['anchor_dir'], root.width, Window.width)
    y: layout_y(root.ps_hints['anchor_y'], root.ps_hints['anchor_dir'], root.height, Window.height)
    ani_value: 0.99
    canvas.before:
        Color:
            rgba: Window.clearcolor[:3] + (root.ani_value, )
        RoundedRectangle:
            pos: root.pos
            size: root.size
    canvas.after:
        Color:
            rgba: app.font_color[:3] + (root.ani_value, )
        Line:
            width: dp(3)
            rounded_rectangle: root.x + dp(1), root.y + dp(1), root.width - dp(2), root.height - dp(2), dp(12)
        Triangle:
            points:
                anchor_points(app.main_app.font_size * 0.69, root.ps_hints['anchor_x'], root.ps_hints['anchor_y'], \
                root.ps_hints['anchor_dir'])
        Color:
            rgba: Window.clearcolor[:3] + (root.ani_value, )
        Line:
            width: dp(1)
            rounded_rectangle: root.x + dp(1), root.y + dp(1), root.width - dp(2), root.height - dp(2), dp(12)
    Label:
        id: help_label
        text: root.help_text
        color: app.font_color[:3] + (root.ani_value, )
        background_color: Window.clearcolor[:3] + (root.ani_value, )
        font_size: app.main_app.font_size * 0.81
        markup: True
        padding: dp(12), dp(9)
        size_hint: None, None
        size: self.texture_size


<HelpToggler>:
    ae_icon_name: 'help_icon' if app.ae_help_layout else 'app_icon'
    ani_value: 0.99
    size_hint_x: None
    width: self.height
    source: app.main_app.img_file(self.ae_icon_name, app.ae_states['font_size'], app.ae_states['light_theme'])
    canvas.after:
        Color:
            rgba: min(self.ani_value * 1.5, 1), min(self.ani_value * 1.5, 1), 1 - self.ani_value, 1 - self.ani_value / 2
        Ellipse:
            pos: self.pos
            size: self.size


""")


class HelpBehaviour(Widget):
    """ behaviour mixin class for widgets having help texts. """
    ae_help_id = StringProperty()
    ae_help_lock = BooleanProperty()


class HelpLayout(ScrollView):                                                           # pragma: no cover
    """ semi-transparent and click-through container for to display help texts. """
    widget = ObjectProperty()       #: target widget to display help text for
    ps_hints = ObjectProperty()     #: pos- and size-hints for the layout window widget
    help_text = StringProperty()    #: help text string to display

    def _update_effect_bounds(self, *args):
        """ override to prevent ScrollView recursion error/crash.

        kivy bug workaround (fixed in kivy master via https://github.com/kivy/kivy/pull/6985 on 15-Jul-2020).
        solution from https://www.gitmemory.com/issue/kivy/kivy/5638/529400808
        Unfortunately not included in Kivy 2.0.0rc3 (from 15-Jun-2020)
        """

    def on_touch_down(self, touch: MotionEvent) -> bool:
        """ check for additional events added by this class.

        :param touch:   motion/touch event data.
        :return:        True if event got processed/used.
        """
        return False        # let user click through this transparent help text widget


class HelpToggler(Image):                                                               # pragma: no cover
    """ widget for to activate and deactivate the help mode.

    For to prevent the dismiss of opened popups and dropdowns at help mode activation, this singleton instance has to
    (1) be registered in its __init__ to the :attr:`~ae.gui_app.HelpAppBase.ae_help_activator` attribute and
    (2) have a :meth:`~HelpToggler.on_touch_down` method that is eating the activation touch event (returning True) and
    (3) a :meth:`~HelpToggler.on_touch_down` method not passing a activation touch in all DropDown/Popup widgets.
    """
    def __init__(self, **kwargs):
        App.get_running_app().main_app.ae_help_activator = self
        super().__init__(**kwargs)

    def on_touch_down(self, touch: MotionEvent) -> bool:
        """ touch down event handler for to toggle help flow mode while preventing dismiss of open dropdowns/popups.

        :param touch:           touch event.
        :return:                True if touch happened on this button (and will get no further processed => eaten).
        """
        if self.collide_point(*touch.pos):
            App.get_running_app().main_app.help_activation_toggle()
            return True
        return False
