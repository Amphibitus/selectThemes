# -*- coding: utf-8 -*-
"""
/***************************************************************************
 selectThemes
                                 A QGIS plugin
                               -------------------
        begin                : 2021-05-03
        git sha              : $Format:%H$
        copyright            : (C) 2021 by gerd 3er geoplaning GmbH
        email                : kontakt@geoplaning.de

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication,QUrl
from qgis.PyQt.QtGui import QIcon,QDesktopServices
from qgis.PyQt.QtWidgets import QAction, QApplication, QLabel, QComboBox

from qgis.core import *
from qgis.gui import *

# Initialize Qt resources from file resources.py
from .resources import *

import os.path


class selectThemes:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        self.locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'selectThemes_{}.qm'.format(self.locale))

        if os.path.exists(locale_path) and self.locale!='pt':
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.separators=[]
        self.menu = '&Select Themes'

        # add an Own Toolbar        
        self.toolbar = self.iface.addToolBar(self.tr(u'selectThemes'))
        self.toolbar.setObjectName(self.tr(u'selectThemes'))
   

        self.pluginIsActive = False
        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('selectThemes', message)


    def add_action(
        self,
        icon_path,
        text,
        callback=None,
        enabled_flag=True,
        add_to_menu=False,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
        separator=False):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        if not separator:
            action.triggered.connect(callback)

        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)
       
        if add_to_menu:
            if separator:
                menuSep=self.toolbar
                self.separator=menuSep.addSeparator()
                self.separators.append(self.separator)
                self.iface.addPluginToMenu(
                    self.menu,
                    self.separator)
            else:
                self.iface.addPluginToMenu(
                    self.menu,
                    action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        ### Add Icon
        icon_path = ':/plugins/selectThemes/icon.png'
        self.add_action(
            icon_path,
            add_to_menu=True,
            add_to_toolbar=True,
            text=self.tr(u'selectThemes'),
            callback=self.projComboThemesLoad,
            parent=self.iface.mainWindow())


       # icon_path = ':/plugins/selectThemes/help.png'
       # self.add_action(
       #     icon_path,
       #     add_to_menu=True,
       #     add_to_toolbar=True,
       #     text=self.tr(u'Help'),
       #     callback=self.CallSite,
       #     parent=self.iface.mainWindow())

        ###Styles Combobox Label
        #cmbLabel = QLabel(self.iface.mainWindow())
        #cmbLabel.setText(self.tr('Theme:'))
        #cmbLabel.setStyleSheet('color: rgb(255, 170, 0)') #font: 87 8pt "Arial Black";  #color: rgb(255, 218, 68);
        #cmbLabelAction = self.toolbar.addWidget(cmbLabel)

        ###Styles Combobox
        self.projComboThemes = QComboBox(self.iface.mainWindow())
        self.projComboThemes.setStyleSheet("background-color: rgb(194, 255, 194);color: rgb(58, 48, 255);")
        
        self.projComboThemes.activated.connect(self.projComboThemesChange) #currentIndexChanged
        self.projComboThemes.setToolTip('Change Layer Theme')
        self.projComboThemes.addItem('No Theme exist')
        
        projComboThemesAction = self.toolbar.addWidget(self.projComboThemes)
        
        self.projComboThemesLoad()


        QgsProject.instance().cleared.connect(self.projComboThemesLoad)

        
        QgsProject.instance().readProject.connect(self.projComboThemesLoad)

        #Insere separador
        icon_path = ''
        self.add_action(
            icon_path,
            add_to_menu=True,
            add_to_toolbar=False,
            text='',
            parent=self.iface.mainWindow(),
            separator=True)


        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        # remove Separators
        for sep in self.separators:
            self.iface.removePluginMenu(
                self.tr('&QEsg'),
                sep)        
        del self.toolbar

    def run(self):
        """Run method that performs all the real work"""
        
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started

        if self.first_start == True:
            self.first_start = False
            


        settings = QSettings("MicroResources", "selectThemes")
        self.projComboThemesLoad()



    def projComboThemesLoad(self):
        """Load diffrent Themes"""
        self.projComboThemes.clear()
        themecount = QgsProject.instance().mapThemeCollection().mapThemes()
        for setting in themecount:
            self.projComboThemes.addItem(setting)



    def projComboThemesChange(self, Int):
        """Select Themes"""
        theme = self.projComboThemes.currentText()
        root = QgsProject.instance().layerTreeRoot()
        model = self.iface.layerTreeView().layerTreeModel()
        QgsProject.instance().mapThemeCollection().applyTheme(
            theme, root, model
        )

    def CallSite(self):
        if self.locale!='pt':
            link='https://github.com/Amphibitus/selectThemes/blob/main/README.md'
        else:
            link='https://github.com/Amphibitus/selectThemes/blob/main/README_en.md'
        QDesktopServices.openUrl(QUrl(link))