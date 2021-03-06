from PyQt4.QtCore import *
from PyQt4.QtGui import *

from settings_dialog import ChainparamsComboBox, LayoutChanger


class ToolBar(QToolBar):
    """Toolbar for Hashmal's main window."""
    def __init__(self, main_window, title, parent=None):
        super(ToolBar, self).__init__(title, parent)
        self.gui = main_window
        self.config = main_window.config
        self.setObjectName('Toolbar')


        self.whats_this_button = whats_this_button = QPushButton('&?')
        whats_this_button.setMaximumWidth(20)
        whats_this_button.setWhatsThis('This button activates What\'s This? mode.\n\nIn What\'s This? mode, you can click something you are not familiar with and a description of it will be shown if one exists.')
        whats_this_button.clicked.connect(lambda: QWhatsThis.enterWhatsThisMode())
        self.addWidget(whats_this_button)
        self.addSeparator()

        self.params_selector = ParamsSelector(self)
        self.addWidget(self.params_selector)
        self.addSeparator()

        self.layout_selector = LayoutSelector(self)
        self.addWidget(self.layout_selector)
        self.addSeparator()

        self.favorites_selector = FavoritesSelector(self)
        self.addWidget(self.favorites_selector)

class LayoutSelector(QWidget):
    """Selector for window layouts."""
    def __init__(self, toolbar, parent=None):
        super(LayoutSelector, self).__init__(parent)
        self.gui = toolbar.gui

        self.layout_changer = layout_changer = LayoutChanger(self.gui)
        layout_changer.setWhatsThis('Use this to load or save layouts. Layouts allow you to quickly access the tools you need for a given purpose.')
        layout_changer.layout_combo.setMinimumWidth(120)
        for i in [layout_changer.load_button, layout_changer.save_button, layout_changer.delete_button]:
            i.setMaximumWidth(50)
            i.setMaximumHeight(23)
        layout_form = QFormLayout()
        layout_form.setContentsMargins(0, 0, 0, 0)
        layout_form.addRow('Layout:', layout_changer)
        self.setLayout(layout_form)
        self.setToolTip('Load or save a layout')

class ParamsSelector(QWidget):
    """Selector for chainparams presets."""
    def __init__(self, toolbar, parent=None):
        super(ParamsSelector, self).__init__(parent)
        self.config = toolbar.config
        self.params_combo = params_combo = ChainparamsComboBox(toolbar.gui)
        params_combo.setWhatsThis('Use this to change the chainparams preset. Chainparams presets are described in the settings dialog.')
        params_combo.setMinimumWidth(120)
        params_form = QFormLayout()
        params_form.setContentsMargins(0, 0, 0, 0)
        params_form.addRow('Chainparams:', params_combo)
        self.setLayout(params_form)
        self.setToolTip('Change chainparams preset')

class FavoritesSelector(QWidget):
    """Selector for favorite plugins."""
    def __init__(self, toolbar, parent=None):
        super(FavoritesSelector, self).__init__(parent)
        self.gui = toolbar.gui
        self.config = toolbar.config
        self.favorites = []

        self.combo = QComboBox()
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.addRow('Favorites:', self.combo)
        self.setLayout(form)
        self.setToolTip('Activate favorite plugins')
        self.setWhatsThis('Use this to quickly access your favorite plugins.')

        self.refresh_favorites()
        self.config.optionChanged.connect(self.on_option_changed)
        self.combo.currentIndexChanged.connect(self.on_index_changed)

    def refresh_favorites(self):
        self.favorites = sorted(self.config.get_option('favorite_plugins', []))
        self.combo.clear()
        self.combo.addItem('Select...')
        self.combo.addItems(self.favorites)

        # Disable or enable combobox.
        enabled = len(self.favorites) > 0
        self.combo.setEnabled(enabled)

    def on_index_changed(self):
        idx = self.combo.currentIndex()
        if idx < 1:
            return
        name = str(self.combo.currentText())
        plugin = self.gui.plugin_handler.get_plugin(name)
        if plugin and plugin.has_gui:
            self.gui.plugin_handler.bring_to_front(plugin.ui)
        self.combo.setCurrentIndex(0)

    def on_option_changed(self, key):
        if key == 'favorite_plugins':
            self.refresh_favorites()
