from functools import wraps

from PyQt4.QtGui import QDockWidget, QWidget, QVBoxLayout
from PyQt4 import QtCore

from hashmal_lib import config

class Category(object):
    """Plugin category.

    Use one of the below class attributes for a dock's category attribute
    e.g. 'category = Category.Script'.
    """
    General = ('General', 'Misc. plugin.')
    Script = ('Scripts', 'Plugin that involves scripts.')
    Key = ('Keys', 'Plugin that involves keys.')
    Tx = ('Transactions', 'Plugin that involves transactions.')

known_augmenters = []

def augmenter(func):
    """Decorator for augmenters.

    Augmenters allow plugins to augment one another.
    """
    func_name = func.__name__
    if func_name not in known_augmenters:
        known_augmenters.append(func_name)

    @wraps(func)
    def func_wrapper(*args):
        return func(*args)
    return func_wrapper


class Plugin(object):
    """A plugin.

    A module's make_plugin() function should return
    an instance of this class.
    """
    def __init__(self, dock_widget):
        self.dock_class = dock_widget
        self.dock = None
        # name is set when the entry point is loaded.
        self.name = ''

    def instantiate_dock(self, plugin_handler):
        instance = self.dock_class(plugin_handler)
        self.dock = instance


class BaseDock(QDockWidget):
    """Base class for docks."""
    needsFocus = QtCore.pyqtSignal()
    needsUpdate = QtCore.pyqtSignal()
    statusMessage = QtCore.pyqtSignal(str, bool, name='statusMessage')

    tool_name = ''
    description = ''
    # If True, dock will be placed on the bottom by default.
    # Otherwise, dock will be placed on the right.
    is_large = False
    category = Category.General

    def __init__(self, handler):
        super(BaseDock, self).__init__('', handler)
        self.handler = handler
        self.config = config.get_config()
        self.advertised_actions = {}
        self.is_enabled = True

        self.init_data()
        self.init_actions()
        my_layout = self.create_layout()
        self.main_widget = QWidget()
        self.main_widget.setLayout(my_layout)
        self.needsUpdate.connect(self.refresh_data)
        self.setWidget(self.main_widget)

        self.config.optionChanged.connect(self.on_option_changed)

        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea | QtCore.Qt.BottomDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.setObjectName(self.tool_name)
        self.setWindowTitle(self.tool_name)
        self.setWhatsThis(self.description)

        self.augmenters = []
        for name in dir(self):
            if name in known_augmenters:
                self.augmenters.append(name)

    def init_data(self):
        """Initialize attributes such as data containers."""
        pass

    def init_actions(self):
        """Initialize advertised actions.

        Subclasses with actions to advertise should create a list of tuples for
        each category they advertise in their 'advertised_actions' attribute.

        Tuples are in the form (action_name, action)

        Example:
            If a subclass can deserialize a raw transaction via the method 'deserialize_tx',
            it would do the following:

            deserialize_raw_tx = ('Deserialize', self.deserialize_tx)
            self.advertised_actions['raw_transaction'] = [deserialize_raw_tx]
        """
        pass

    def create_layout(self):
        """Returns the main layout for our widget.

        Subclasses should override this to return their layout.
        """
        return QVBoxLayout()

    def refresh_data(self):
        """Synchronize. Called when needsUpdate is emitted."""
        pass

    def on_option_changed(self, key):
        """Called when a config option changes."""
        pass

    def get_actions(self, category):
        """Get the advertised actions for category.

        category can be one of:
            - raw_transaction

        """
        if self.advertised_actions.get(category):
            return self.advertised_actions.get(category)

    def status_message(self, msg, error=False):
        """Show a message on the status bar.

        Args:
            msg (str): Message to be displayed.
            error (bool): Whether to display msg as an error.
        """
        msg = ''.join([ '[%s] --> %s' % (self.tool_name, msg) ])
        self.statusMessage.emit(msg, error)

    def augment(self, target, data, callback=None):
        """Ask other plugins if they have anything to contribute.

        Allows plugins to enhance other plugins.
        """
        return self.handler.do_augment_hook(self.__class__.__name__, target, data, callback)