import platform
osname = platform.system()
from .binstateimage import BinStateImage
from .jsoncodeinput import JsonCodeInput
from .inputext import FloatInput,IntegerInput,StrInput,SelectInput, BoolInput, AmountInput
from .scrollwidget import ScrollWidget
from .messager import Messager
__all__ = [
BinStateImage,
JsonCodeInput,
FloatInput,
AmountInput,
BoolInput,
IntegerInput,
StrInput,
SelectInput,
ScrollWidget,
Messager,
]

if osname == 'android':
	print('***********************************8')
	from .phonebutton import PhoneButton
	from .androidwebview import AWebView
	__all__ = __all__ + [PhoneButton, AWebView]
