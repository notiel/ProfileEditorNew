from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtWidgets, QtCore
import os
from typing import Optional
from help import Ui_Help
from profileshelp import  Ui_Help as Profile_Help
from auxhelp import Ui_Help as Aux_Help
from helpauxjp import Ui_Help as Aux_Help_Jp
from helpprofilejp import  Ui_Help as Profile_Help_Jp
from helpcommonjp import Ui_Help as Common_Help_Jp
from helpcommonru import Ui_Help as Common_Help_Ru
from helpprofileru import  Ui_Help as Profile_Help_Ru
from helpauxru import Ui_Help as Aux_Help_Ru
from localtable import local_table

about_text = """Settings Editor 1.1 for lightsabers.
By Warsabers.ru"""


class CommonHelp(QtWidgets.QDialog, Ui_Help):

    def __init__(self):
        super().__init__()
        self.setupUi(self)


class ProfileHelp(QtWidgets.QDialog, Profile_Help):

    def __init__(self):
        super().__init__()
        self.setupUi(self)


class AuxHelp(QtWidgets.QDialog, Aux_Help):

    def __init__(self):
        super().__init__()
        self.setupUi(self)


class CommonHelpRu(QtWidgets.QDialog, Common_Help_Ru):

    def __init__(self):
        super().__init__()
        self.setupUi(self)


class ProfileHelpRu(QtWidgets.QDialog, Profile_Help_Ru):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

class AuxHelpRu(QtWidgets.QDialog, Aux_Help_Ru):

    def __init__(self):
        super().__init__()
        self.setupUi(self)


class CommonHelpJp(QtWidgets.QDialog, Common_Help_Jp):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

class ProfileHelpJp(QtWidgets.QDialog, Profile_Help_Jp):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

class AuxHelpJp(QtWidgets.QDialog, Aux_Help_Jp):

    def __init__(self):
        super().__init__()
        self.setupUi(self)


def about_help(lang: str):
    """
    shows help window with about text
    :return:
    """
    editor_help(about_text, lang)


def common_help(lang: str):
    """
    show help window with text for common
    :param lang: language pf program
    :return:
    """
    if lang == 'en':
        help_window = CommonHelp()
        help_window.exec()
    if lang == 'ru':
        help_window = CommonHelpRu()
        help_window.exec()
    if lang == 'jp':
        help_window = CommonHelpJp()
        help_window.exec()


def auxleds_help(lang: str):
    """
    show help window with text for auxleds
    :param lang: language pf program
    :return:
    """
    if lang == 'en':
        help_window = AuxHelp()
        help_window.exec()
    if lang == 'ru':
        help_window = AuxHelpRu()
        help_window.exec()
    if lang == 'jp':
        help_window = AuxHelpJp()
        help_window.exec()


def profile_help(lang: str):
    """
    show help window with text for common
    :param lang: language pf program
    :return:
    """
    if lang == 'en':
        help_window = ProfileHelp()
        help_window.exec()
    if lang == 'ru':
        help_window = ProfileHelpRu()
        help_window.exec()
    if lang == 'jp':
        help_window = ProfileHelpJp()
        help_window.exec()

def editor_help(text, lang):
    """
    functions for showing help window
    :param text:
    :return:
    """
    help = QMessageBox()
    help.setIcon(QMessageBox.Information)
    help.setText(text)
    help.setWindowTitle(local_table['About'][lang])
    help.setStandardButtons(QMessageBox.Ok)
    help.exec_()


def find_file(filename: str, path: str = ".") -> Optional[str]:
    """
    case insensitive search for file in current directory
    :param filename: filename
    :param path: directory for search
    :return: real filename
    """
    for file in os.listdir(path):
        if filename.lower() == file.lower():
            return file
    return None