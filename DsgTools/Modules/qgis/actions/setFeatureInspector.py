from qgis import gui, core
from qgis.utils import iface
from PyQt5 import QtCore, uic, QtWidgets, QtGui


class SetFeatureInspector:
    def __init__(self):
        self.names = [
            "dsgtools: set active layer on feature inspector",
            "dsgtools: definir a camada ativa no inspetor de feições",
        ]

    def execute(self):
        for a in gui.QgsGui.shortcutsManager().listActions():
            if not (a.text().lower() in self.names):
                continue
            a.trigger()
            break
