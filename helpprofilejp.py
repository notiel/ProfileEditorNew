# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ProfileHelpJp.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Help(object):
    def setupUi(self, Help):
        Help.setObjectName("Help")
        Help.resize(1256, 649)
        self.verticalLayout = QtWidgets.QVBoxLayout(Help)
        self.verticalLayout.setObjectName("verticalLayout")
        self.TxtHelp = QtWidgets.QTextBrowser(Help)
        self.TxtHelp.setObjectName("TxtHelp")
        self.verticalLayout.addWidget(self.TxtHelp)

        self.retranslateUi(Help)
        QtCore.QMetaObject.connectSlotsByName(Help)

    def retranslateUi(self, Help):
        _translate = QtCore.QCoreApplication.translate
        Help.setWindowTitle(_translate("Help", "プロファイルエディターヘルプ"))
        self.TxtHelp.setHtml(_translate("Help", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><img src=\":/profilejp/JapanHelp/HelpProfilesJAPAN.png\" /></p></body></html>"))

import help_rc
