from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtWidgets
import os
from typing import Optional
from help import Ui_Help
from profileshelp import Ui_Help as Profile_Help
from auxhelp import Ui_Help as Aux_Help
from helpauxjp import Ui_Help as Aux_Help_Jp
from helpprofilejp import Ui_Help as Profile_Help_Jp
from helpcommonjp import Ui_Help as Common_Help_Jp
from helpcommonru import Ui_Help as Common_Help_Ru
from helpprofileru import Ui_Help as Profile_Help_Ru
from helpauxru import Ui_Help as Aux_Help_Ru
from localtable import local_table

about_text = """Settings Editor 2.0 for lightsabers.
By Warsabers.com"""


ffmpeg_text_rus = """Пожалуйста, скачайте сперва файл ffmpeg.exe с нашего сайта. 
Данный файл необходимо поместить в ту же директорию,
где находится SettingsEditor. Запускать файл не нужно. 
Он используется программой автоматически для успешной оптимизации. 
Скачать его можно по ссылке: """

ffmpeg_text_en = """Please first download ffmpeg.exe converter file 
and put it in same folder with SettingsEditor. 
No need to execute it. This file required for successful optimizing. 
File can be downloaded from our site:  
"""

ffmpeg_text_jp = """
請首先下載ffmpeg.exe轉換器文件，
並將其與SettingsEditor放在同一文件夾中。 
無需運行它。 成功優化需要此文件。 可以從我們的網站下載文件
"""


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
    :param text: text for help
    :param lang: language for use
    :return:
    """
    help_popup = QMessageBox()
    help_popup.setIcon(QMessageBox.Information)
    help_popup.setText(text)
    help_popup.setWindowTitle(local_table['About'][lang])
    help_popup.setStandardButtons(QMessageBox.Ok)
    help_popup.exec_()


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


def ffmpeg_missing(language: str):
    if language == 'ru':
        error_message(ffmpeg_text_rus + 'https://warsabers.com/en/downloads/', 'ru')
    elif language == 'jp':
        error_message(ffmpeg_text_jp + 'https://warsabers.com/en/downloads/', 'jp')
    else:
        error_message(ffmpeg_text_en + 'https://warsabers.com/en/downloads/', 'en')


def error_message(text: str, language: str):
    error = QMessageBox()
    error.setIcon(QMessageBox.Critical)
    error.setText(text)
    error.setWindowTitle(local_table['Error'][language])
    error.setStandardButtons(QMessageBox.Ok)
    error.exec_()
