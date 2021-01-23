import os
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox
import design
from Auxledsdata import *
from Commondata import *
from profiledata import *
import Mediator
import assistant
import palitra
from localtable import local_table
import wav_convertion
import datetime

from loguru import logger

logger.start("logfile.log", rotation="1 week", format="{time} {level} {message}", level="DEBUG", enqueue=True)

auxleds = 'AUXLEDs'
common = 'Common'
profiletab = 'Profiles'
tabnames_global = [auxleds, common, profiletab]

tabnames = {0: 'AfterWake', 1: 'PowerOn', 2: 'WorkingMode', 3: 'PowerOff', 4: 'Flaming', 5: 'Flickering', 6: 'Blaster',
            7: 'Clash', 8: 'Stab', 9: 'Lockup'}


def initiate_exception_logging():
    # generating our hook
    # Back up the reference to the exceptionhook
    sys._excepthook = sys.excepthook

    def my_exception_hook(exctype, value, traceback):
        # Print the error and traceback
        logger.exception(f"{exctype}, {value}, {traceback}")
        # Call the normal Exception hook after
        sys._excepthook(exctype, value, traceback)

    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook


def resource_path(relative):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative)
    else:
        return os.path.join(os.path.abspath("."), relative)


class StepTreeItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, name):
        super().__init__([name])


class RepeatTreeItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, name):
        super().__init__([name])


class SequencerTreeItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, name):
        super().__init__([name])


class ProfileEditor(QtWidgets.QMainWindow, design.Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.auxdata = AuxEffects()
        self.commondata = CommonData()
        self.profiledata = Profiles()
        self.language = "en"
        self.data = [self.auxdata, self.commondata, self.profiledata]
        self.saved = [True, True, True]
        self.filename = ["", "", ""]
        self.default_names = ["Auxleds.ini", "Common.ini", "Profiles.ini"]
        self.savefunctions = [self.auxdata.save_to_file, self.commondata.save_to_file, self.profiledata.save_to_file]
        self.openfunctions = [Mediator.translate_json_to_tree_structure, Mediator.get_common_data,
                              Mediator.load_profiles]
        self.statusfields = [self.TxtAuxStatus, self.TxtCommonStatus, self.TxtProfileStatus]
        self.loadfunctions = [self.load_auxleds, self.load_common, self.load_profiles]
        self.init_aux_ui()
        self.common_ui()
        self.profile_ui()
        if self.language in ['ru', 'jp']:
            self.language_init()

        # add menu triggers
        self.actionExit.triggered.connect(self.close)
        self.actionExit.setShortcut('Ctrl+Q')
        self.actionSave.triggered.connect(self.save_pressed)
        self.actionSave.setShortcut('Ctrl+S')
        self.actionSave_As.triggered.connect(self.save_as_pressed)
        self.actionSave_As.setShortcut('Ctrl+Shift+S')
        self.actionNew.triggered.connect(self.new_pressed)
        self.actionSave_All.setShortcut('Ctrl+Alt+S')
        self.actionSave_All.triggered.connect(self.save_all_pressed)
        self.actionNew.setShortcut('Ctrl+N')
        self.actionOpen.triggered.connect(self.open_pressed)
        self.actionOpen.setShortcut('Ctrl+O')
        self.actionAuxLeds_Editor_Help.triggered.connect(self.auxled_help)
        self.actionCommon_Editor_Help.triggered.connect(self.common_help)
        self.actionProfiles_Edtor_Help.triggered.connect(self.profile_help)
        self.actionAbout.triggered.connect(self.about_help)
        self.actionOpenAll.triggered.connect(self.open_all_pressed)

        self.BtnSelectFont.clicked.connect(self.font_folder_clicked)
        self.LineFontPath.editingFinished.connect(self.get_folder_from_field)
        self.BtnOptimize.clicked.connect(self.optimize_fonts)


    # init part
    def init_aux_ui(self):
        # useful lists of items
        self.leds_combo_list = [self.CBLed1, self.CBLed2, self.CBLed3, self.CBLed4, self.CBLed5, self.CBLed6,
                                self.CBLed7, self.CBLed8]
        self.leds = dict(list(zip(Mediator.leds_list, self.leds_combo_list)))
        self.leds_cb_str = dict(list(zip(self.leds_combo_list, Mediator.leds_list)))
        self.step_leds_brightnesses = [self.SpinBrightness1, self.SpinBrightness2, self.SpinBrightness3,
                                       self.SpinBrightness4, self.SpinBrightness5, self.SpinBrightness6,
                                       self.SpinBrightness7, self.SpinBrightness8]
        self.step_channels = [self.CBChannel1, self.CBChannel2, self.CBChannel3, self.CBChannel4, self.CBChannel5,
                              self.CBChannel6, self.CBChannel7, self.CBChannel8]
        self.step_brightness_dict = dict(list(zip(Mediator.leds_list, self.step_leds_brightnesses)))
        self.step_channels_dict = dict(list(zip(Mediator.leds_list, self.step_channels)))
        # add button clicks
        self.BtnAddGroup.clicked.connect(self.add_group)
        self.BtnAddSequencer.clicked.connect(self.add_sequencer)
        self.BtnCopySeq.clicked.connect(self.copy_sequencer)
        self.BtnDeleteGroup.clicked.connect(self.delete_group)
        self.BtnAddStep.clicked.connect(self.add_step)
        self.BtnEditStep.clicked.connect(self.edit_step)
        self.BtnDeleteSeq.clicked.connect(self.delete_item)
        self.BtnDeleteStep.clicked.connect(self.delete_item)
        self.BtnAddRepeat.clicked.connect(self.add_repeat_step)
        self.BtnDeleteRepeat.clicked.connect(self.delete_item)
        self.BtnEditRepeat.clicked.connect(self.edit_repeater)
        self.BtnUpdate.clicked.connect(self.update_group)
        self.BtnChange.clicked.connect(self.change_pressed)
        self.CBGroup.currentTextChanged.connect(self.group_changed)
        self.TxtGroup.textChanged[str].connect(self.group_name_changed)

        # for led in self.step_leds_brightnesses:
        # led.valueChanged.connect(self.BrightnessChanged)
        self.LstGroup.itemPressed.connect(self.group_clicked)
        # self.TrStructure.itemPressed.connect(self.TreeItemChanged)
        self.TrStructure.currentItemChanged.connect(self.tree_item_changed)

        for CB in self.leds_combo_list:
            CB.stateChanged.connect(self.led_clicked)
        self.preload_auxes()

    def preload_auxes(self):
        """
        load Auxleds.ini file if it exists in current directory
        :return:
        """
        filename = assistant.find_file("Auxleds.ini")
        if filename:
            try:
                text = open(filename, encoding='utf-8').read()
                gui_data, error, warning = self.openfunctions[0](text)
                if error == "":
                    if warning:
                        warning = warning.replace("Data error in", local_table['wrong_data_in'][self.language])
                        warning = warning.replace("Sequencer error in", local_table['seq_error'][self.language])
                        warning = warning.replace("LED Group error in", local_table['leg_group_error'][self.language])
                        warning = warning.replace("Step error in", local_table['step_error'][self.language])
                        self.statusfields[0].setText("%s %s...\n%s" %
                                                     (local_table['try_open'][self.language], filename, warning))
                    else:
                        self.statusfields[0].setText("%s %s" % (filename, local_table['open_warnings'][self.language]))
                    self.load_auxleds(gui_data)
                    self.filename[0] = filename
                    self.change_tab_title(auxleds, 0)
                else:
                    self.error_message(error)
                    self.statusfields[0].setText("%s %s...\n" %
                                                 (local_table['file_not_loaded'][self.language], filename))
            except Exception:
                self.statusfields[0].setText("%s %s...\n" % (local_table['file_not_loaded'][self.language], filename))

    def common_ui(self):
        # list of common items
        self.blade1_controls = [self.SpinBand, self.SpinPixPerBand, self.SpinStartFlash]
        self.blade2_controls = [self.SpinBandNumber, self.SpinPixPerBand2, self.SpinStartFlash_2]
        self.volume_controls = [self.SpinCommon, self.SpinCoarseLow, self.SpinCoarseMid, self.SpinCoarseHigh]
        self.other_ccntrols = [self.SpinPowerOffTimeout, self.CBOneButton, self.CBPowerOnByStab]
        self.swing_controls = [self.SpinSwingHighW, self.SpinSwingPercent, self.SpinSwingCircle, self.SpinSwingCircleW]
        self.smooth_swing_controls = [self.SpinSmoothSwingStart, self.HiddenSpin, self.SpinSmoothSwingLength,
                                      self.SpinSmoothSwingMinHum, self.SpinSmoothSwingStrength,
                                      self.SpinSmoothSwingMinVolume]
        self.spin_controls = [self.CBSpinEnabled, self.SpinSpinCounter, self.SpinSpinW, self.SpinSpinCircle,
                              self.SpinSpinWLow]
        self.clash_controls = [self.SpinClashHighA, self.SpinClashLength, self.SpinClashHitLevel, self.SpinClashLowW]
        self.stab_controls = [self.CBStabEnabled, self.SpinStabHighA, self.SpinStabLowW, self.SpinStabHitLevel,
                              self.SpinStabLength, self.SpinStabPercent]
        self.screw_controls = [self.CBScrewEnabled, self.SpinScrewHighW, self.SpinScrewLowW]
        self.common_controls = [self.blade1_controls, self.blade2_controls, self.volume_controls, self.other_ccntrols]
        self.motion_controls = [self.swing_controls, self.smooth_swing_controls, self.spin_controls,
                                self.clash_controls, self.stab_controls, self.screw_controls]

        # common_controls_connect_maps
        self.common_dict = {}
        for i in range(len(self.common_controls)):
            keys_list = [[Mediator.main_sections[i], key] for key in Mediator.main_list[i]]
            self.common_dict.update(dict(list(zip(self.common_controls[i], keys_list))))
        self.motion_dict = {}
        for i in range(len(self.motion_controls)):
            keys_list = [[Mediator.motion_key, Mediator.motion_keys[i], key] for key in Mediator.motion_list[i]]
            self.motion_dict.update((dict(list(zip(self.motion_controls[i], keys_list)))))

        # common controls init
        for control_list in self.common_controls + self.motion_controls:
            for control in control_list:
                if control in (self.CBBlade2Enabled, self.CBSpinEnabled, self.CBStabEnabled, self.CBScrewEnabled,
                               self.CBPowerOnByStab, self.CBOneButton):
                    control.stateChanged.connect(self.cb_clicked)
                else:
                    control.valueChanged.connect(self.spin_changed)

        self.set_default_common()
        self.BtnSave.clicked.connect(self.save_pressed)
        self.BtnDefault.clicked.connect(self.set_default_common)
        self.CBBlade2Enabled.stateChanged.connect(self.blade2_clicked)
        self.preload_common()
        self.saved[1] = True
        self.change_tab_title(common, 1)

    def preload_common(self):
        """
        loaas file Commom.ini if any
        :return:
        """
        filename = assistant.find_file("Common.ini")
        try:
            if filename:
                text = open(filename, encoding='utf-8').read()
                gui_data, error, warning = self.openfunctions[1](text)
                if error == "":
                    if warning:
                        self.statusfields[1].setText("%s %s...\n%s" %
                                                     (local_table['try_open'][self.language], filename, warning))
                    else:
                        self.statusfields[1].setText("%s %s" %
                                                     (filename, local_table['open_warnings'][self.language]))
                    self.load_common(gui_data)
                    self.filename[1] = filename
                    self.change_tab_title(common, 1)
                else:
                    self.error_message(error)
                    self.statusfields[1].setText("%s %s...\n" %
                                                 (local_table['file_not_loaded'][self.language], filename))
        except Exception:
            self.statusfields[1].setText("%s %s...\n" %
                                         (local_table['file_not_loaded'][self.language], filename))

    def profile_ui(self):
        # list of controls
        self.poweron = [self.SpinBladeSpeedOn]
        self.poweroff = [self.SpinPowerOffSpeed, self.CBMoveForward]
        self.working = [self.TxtWorkingColor, self.CBFlaming, self.CBFlickering]
        self.flaming = [self.SpinFlamingSizeMin, self.SpinFlamingSizeMax, self.SpinFlamingSpeedMin,
                        self.SpinFlamingSpeedMax,
                        self.SpinFlamingDelayMin, self.SpinFlamingDelayMax]
        self.flickering = [self.SpinFlickeringTimeMin, self.SpinFlickeringTimeMax, self.SpinFlickeringBrMin,
                           self.SpinFlickeringBrMax]
        self.blaster = [self.TxtBlasterColor, self.SpinBlasterDuration, self.SpinBlasterSizePix]
        self.clash = [self.TxtClashColor, self.SpinClashDuration, self.SpinClashSizePix]
        self.stab = [self.TxtStabColor, self.SpinStabDuration, self.SpinStabSizePix]
        self.lockup = [self.TxtLockupFlickerColor, self.SpinLockupTimeMin, self.SpinLockupTimeMax,
                       self.SpinLockupBrightnessMin, self.SpinLockupBrightnessMax, self.SpinLockupPeriodMin,
                       self.SpinLockupPeriodMax, self.TxtLockupFlashesColor, self.SpinLockupDuration,
                       self.SpinLockupSizepix]
        # map of tabs and their controls
        self.control_tab_dict = {1: self.poweron, 2: self.working, 3: self.poweroff, 4: self.flaming,
                                 5: self.flickering, 6: self.blaster, 7: self.clash, 8: self.stab, 9: self.lockup}
        # map of color change data to their text field
        self.color_dict = {self.BtnBlasterColor: self.TxtBlasterColor, self.BtnClashColor: self.TxtClashColor,
                           self.BtnStabColor: self.TxtStabColor, self.BtnWorkingColor: self.TxtWorkingColor,
                           self.BtnLockupFlashesColor: self.TxtLockupFlashesColor,
                           self.BtnLockupFlickerColor: self.TxtLockupFlickerColor}
        self.selected_color_dict = {self.TxtBlasterColor: self.BlasterColor, self.TxtClashColor: self.ClashColor,
                                    self.TxtStabColor: self.StabColor, self.TxtWorkingColor: self.WorkingColor,
                                    self.TxtLockupFlashesColor: self.LockupFlashesColor,
                                    self.TxtLockupFlickerColor: self.LockupFlickerColor}
        # list of color text fields
        self.color_list = [self.TxtClashColor, self.TxtWorkingColor, self.TxtStabColor, self.TxtBlasterColor,
                           self.TxtLockupFlickerColor, self.TxtLockupFlashesColor]
        self.color_CB_dict = {self.CBWMRandom: self.TxtWorkingColor, self.CBBlasterRandom: self.TxtBlasterColor,
                              self.CBClashRandom: self.TxtClashColor, self.CBStabRandom: self.TxtStabColor,
                              self.CBFlashesRandom: self.TxtLockupFlashesColor,
                              self.CBFlickerRandom: self.TxtLockupFlickerColor}
        # map of min to max values in min max pairs
        self.min_max_dict = {self.SpinLockupTimeMin: self.SpinLockupTimeMax,
                             self.SpinLockupPeriodMin: self.SpinLockupPeriodMax,
                             self.SpinLockupBrightnessMin: self.SpinLockupBrightnessMax,
                             self.SpinFlickeringTimeMin: self.SpinFlickeringTimeMax,
                             self.SpinFlickeringBrMin: self.SpinFlickeringBrMax,
                             self.SpinFlamingSpeedMin: self.SpinFlamingSpeedMax,
                             self.SpinFlamingSizeMin: self.SpinFlamingSizeMax,
                             self.SpinFlamingDelayMin: self.SpinFlamingDelayMax}
        # lists of checkboxes
        self.CB_list = [self.CBFlickering, self.CBFlaming, self.CBMoveForward]
        self.extra_blade_CB_dict = {self.CBIndicate: Mediator.indicate_path, self.CBFlickeringAlwaysOn:
            Mediator.flickering_on_path, self.CBFlamingAlwaysOn: Mediator.flaming_on_path}
        self.CB_single_dict = {self.CBFlickering: self.CBFlaming, self.CBFlaming: self.CBFlickering,
                               self.CBFlamingAlwaysOn: self.CBFlickeringAlwaysOn,
                               self.CBFlickeringAlwaysOn: self.CBFlamingAlwaysOn}
        # reverse of min max dict - map max value to min
        self.max_min_dict = dict([(self.min_max_dict[key], key) for key in self.min_max_dict.keys()])

        # create map of controls to key path in data dictionary (path lists from Mediator file)
        self.profile_dict = {}
        for i in self.control_tab_dict.keys():
            keys_list = []
            for key in Mediator.profile_list[i - 1]:
                keys_list.append([Mediator.tab_list[i - 1]] + key)
            self.profile_dict.update(dict(list(zip(self.control_tab_dict[i], keys_list))))
        # set data change handlers
        for control in self.profile_dict.keys():
            if control in self.CB_list:
                control.stateChanged.connect(self.profile_cb_clicked)
            else:
                if control in self.color_list:
                    control.textChanged.connect(self.profile_text_changed)
                else:
                    control.valueChanged.connect(self.profile_spin_changed)

        for color_button in self.color_dict.keys():
            color_button.clicked.connect(self.color_changed)

        for CB in self.color_CB_dict.keys():
            CB.stateChanged.connect(self.color_random_clicked)

        for CB in self.extra_blade_CB_dict.keys():
            CB.clicked.connect(self.extra_blade_clicked)

        self.BtnProfile.clicked.connect(self.add_profile)
        self.BtnDeleteProfile.clicked.connect(self.delete_profile)
        self.BtnAddColor.clicked.connect(self.add_color)
        self.BtnAddRandom.clicked.connect(self.add_random_color)
        self.BtnDeleteColor.clicked.connect(self.delete_color)
        self.BtnCReateAux.clicked.connect(self.profile_add_aux)
        self.BtnAuxDelete.clicked.connect(self.delete_aux)
        self.BtnEditProfile.clicked.connect(self.profile_edit_pressed)
        self.BtnUp.clicked.connect(self.move_up)
        self.BtnDown.clicked.connect(self.move_down)

        self.TabEffects.currentChanged.connect(self.effect_tab_changed)
        self.TxtAddProfile.textChanged[str].connect(self.profile_name_changed)
        self.LstProfile.itemPressed.connect(self.profile_clicked)
        self.LstProfile.currentItemChanged.connect(self.profile_clicked)
        self.LstFlamingColor.itemPressed.connect(self.color_clocked)
        self.LstFlamingColor.currentItemChanged.connect(self.color_clocked)
        self.LstAuxProfile.itemPressed.connect(self.aux_clicked)
        self.LstAuxProfile.currentItemChanged.connect(self.aux_clicked)
        self.CBBlade.currentIndexChanged.connect(self.blade_changed)
        self.SpinDelayBeforeOn.valueChanged.connect(self.delay_changed)

        self.preload_profiles()

    def preload_profiles(self):
        """
        load Profiles.ini file if it exists in current directory
        :return:
        """
        filename = assistant.find_file("Profiles.ini")
        if filename:
            try:
                text = open(filename, encoding='utf-8').read()
                gui_data, error, warning = self.openfunctions[2](text)
                if error == "":
                    if warning:
                        self.statusfields[2].setText("%s %s...\n%s" %
                                                     (local_table['try_open'][self.language], filename, warning))
                    else:
                        self.statusfields[2].setText("%s %s" % (filename, local_table['open_warnings'][self.language]))
                    self.load_profiles(gui_data)
                    self.filename[2] = filename
                    self.change_tab_title(profiletab, 2)
                else:
                    self.error_message(error)
                    self.statusfields[2].setText("%s %s...\n" %
                                                 (local_table['file_not_loaded'][self.language], filename))
            except Exception:
                self.statusfields[2].setText("%s %s...\n" % (local_table['file_not_loaded'][self.language], filename))

    def language_init(self):
        lang = self.language
        aux_labels = [self.LblGroup, self.LblGroupName, self.LblLeds, self.LblLED1, self.LblLED2, self.LblLED3,
                      self.LblLED4, self.LblLed5, self.LblLED6, self.LblLED7, self.LblLED8,
                      self.LblSequencers, self.LblSeqName, self.LBLCopy, self.LblStepName, self.LblNewName, self.LblLED,
                      self.LblBrightness, self.LblChannel, self.LblBrightness_2, self.LblChannel_2, self.LblWait,
                      self.LblSmooth, self.LblStartFrom, self.LblCount, self.LblAuxStatus]
        aux_buttons = [self.BtnAddGroup, self.BtnUpdate, self.BtnDeleteGroup, self.BtnChange, self.BtnAddSequencer,
                       self.BtnCopySeq, self.BtnAddStep, self.BtnEditStep, self.BtnDeleteStep, self.BtnDeleteSeq,
                       self.BtnAddRepeat, self.BtnEditRepeat, self.BtnDeleteRepeat]
        aux_cb = [self.CBLed1, self.CBLed2, self.CBLed3, self.CBLed4, self.CBLed5, self.CBLed6, self.CBLed7,
                  self.CBLed8, self.CBForever]
        aux_groups = [self.GBStep, self.GBEditStep, self.GBRepeat]
        labels_without_colon = [self.LBLChange, self.LBLWith]
        common_labels = [self.LblGeneral, self.LblBandNumber, self.LblBandNumber_2, self.LblPixPerBand,
                         self.LblPixPerBand_2, self.LblCommon, self.LblCoarceLow, self.LblCoarseHigh, self.LblCOarseMid,
                         self.LblSwingHighW, self.LblSwingWPercent, self.LblCircleW, self.LBLSpinEnabled,
                         self.LBLSpinCounter, self.LblSpinWLow, self.LblSpinW, self.LblClashHighA,
                         self.LblClashHitLevel, self.LblClashLowW, self.LblEnabled, self.LblStabHighA, self.LblStabLowW,
                         self.LblStabHitLevel, self.LblStabPercent, self.LblScrewEnabled, self.LbScrewHighW,
                         self.LblScrewLowW, self.LblMotion, self.LblCommonStatus, self.LblSmoothSwingStart,
                         self.LblSmoothSwingMaxVolume, self.LbLSmoothSwingMinHum, self.LblSmoothSwingMinVolume,
                         self.LblOneButton, self.LblPowerOnByStab]
        common_labels_ms = [self.LblSwingCircle, self.LblSpinCircle, self.LblClashLength, self.LblSpinLength,
                            self.LblSmoothSwingLength]
        labels_s = [self.LblPowerOffTimeout]
        common_without_colon = [self.LblStartFlash, self.LblStartFlash_2]
        common_groups = [self.GBClash, self.GBSpin, self.GBScrew, self.GBSwing, self.GBStab, self.GBSmoothSwing,
                         self.GBCommonBlade, self.GBCommonSettings, self.GBCommonVolume, self.GBCommonBlade2]
        common_buttons = [self.BtnSave, self.BtnDefault]
        profile_labels = [self.LblProfile, self.LblProfile_2, self.LblDelayBeforeOn, self.LBLBladeSpeed,
                          self.LblWorkingColor, self.LblWorkingColorSelected, self.LblPowerOffSpeed, self.LblFlamigSize,
                          self.LblFlamingColors, self.LblFlamingSpeed, self.LblFlamingDelayMax, self.LblFlamingDelayMin,
                          self.LblFlamingSizeMin, self.LblFlamingSizeMax, self.LblFlamingSpeedMax,
                          self.LblFlamingSpeedMin, self.LblFlickeringBrigtness, self.LblFlickeringBrMax,
                          self.LblFlickeringBrMin, self.LblFlickeringTimeMax, self.LblFlickeringTimeMin,
                          self.LblBlasterColorSelected, self.LblBlasterColor, self.LblClashCOlor,
                          self.LblClashColorSelected, self.LblStabColor, self.LblStabColorSelected,
                          self.LblClashSizePix, self.LblBlasterSizePix, self.LblStabSizePix,
                          self.LblLockcupBrightnessMax, self.LblLockupBrightness, self.LblLockupBrightnessMin,
                          self.LblLockupFlashes, self.LblLockupFlicker, self.LblLockupPeriodMax,
                          self.LblLockupPeriodMin, self.LblLockupSizepix, self.LblLockupTimeMax, self.LblLockupTimeMin,
                          self.LblAddAux, self.LblAddedAuxes, self.LblCreateAux, self.LblProfileStatus]
        profile_no_colon = [self.LblShadowed]
        profile_labels_ms = [self.LblFlamingDelay, self.LblFlickeringTime, self.LblClashDuration,
                             self.LblLockupDuration, self.LblLockupPeriod, self.LblLockupTime,
                             self.LblBlasterDuration, self.LblStabDuration]
        profile_buttons = [self.BtnProfile, self.BtnEditProfile, self.BtnDeleteProfile, self.BtnDown, self.BtnUp,
                           self.BtnWorkingColor, self.BtnDeleteColor, self.BtnAddRandom, self.BtnAddColor,
                           self.BtnBlasterColor, self.BtnStabColor, self.BtnClashColor, self.BtnLockupFlickerColor,
                           self.BtnLockupFlashesColor, self.BtnAuxDelete]
        profile_cb = [self.CBWMRandom, self.CBFlaming, self.CBFlickering, self.CBMoveForward, self.CBFlickerRandom,
                      self.CBFlashesRandom, self.CBBlasterRandom, self.CBStabRandom, self.CBClashRandom,
                      self.CBIndicate]
        font_labels = [self.LblInsertPath]
        font_labels_without_colon = [self.LblFont]
        font_buttons = [self.BtnOptimize, self.BtnSelectFont]
        all_labels = aux_labels.copy()
        all_labels.extend(common_labels)
        all_labels.extend(profile_labels)
        all_labels.extend(font_labels)
        all_groups_labels = aux_groups.copy()
        all_groups_labels.extend(common_groups)
        for label in all_labels:
            current = label.text().replace(":", "")
            label.setText(local_table[current][lang] + ':')
        labels_without_colon.extend(aux_buttons)
        labels_without_colon.extend(common_without_colon)
        labels_without_colon.extend(common_buttons)
        labels_without_colon.extend(profile_no_colon)
        labels_without_colon.extend(profile_buttons)
        labels_without_colon.extend(aux_cb)
        labels_without_colon.extend(profile_cb)
        labels_without_colon.extend(font_labels_without_colon)
        labels_without_colon.extend(font_buttons)
        for label in labels_without_colon:
            current = label.text()
            label.setText(local_table[current][lang])
        for label in all_groups_labels:
            current = label.title()
            label.setTitle(local_table[current][lang])
        for CB in self.step_channels:
            CB.setItemText(0, local_table['None'][lang])
            CB.setItemText(1, local_table['CopyRed'][lang])
            CB.setItemText(2, local_table['CopyGreen'][lang])
            CB.setItemText(3, local_table['CopyBlue'][lang])
        labels_ms = common_labels_ms.copy()
        labels_ms.extend(profile_labels_ms)
        for label in labels_ms:
            current = label.text()[:-5]
            label.setText(local_table[current][lang] + ', ' + local_table['ms'][lang] + ':')
        for label in labels_s:
            current = label.text()[:-4]
            label.setText(local_table[current][lang] + ', ' + local_table['s'][lang] + ':')
        if self.language != 'ru':
            label = local_table['Add Effect to @@@'][lang].replace("@@@", local_table['PowerOn'][lang])
            self.BtnCReateAux.setText(label)
        else:
            self.BtnCReateAux.setText(
                local_table['Add Effect to @@@'][lang][:-3] + 'режиму\n«' + local_table['PowerOn'][
                    lang] + '»')
        for i in range(Mediator.effects_number):
            current = self.TabEffects.tabText(i)
            self.TabEffects.setTabText(i, local_table[current][lang])
        self.CBFlickeringAlwaysOn.setText(local_table['Always On'][lang] +
                                          local_table['(only for Blade2, see Working Mode for Blade1)'][lang])
        self.CBFlamingAlwaysOn.setText((local_table['Always On'][lang] +
                                        local_table['(only for Blade2, see Working Mode for Blade1)'][lang]))
        self.CBBlade.clear()
        self.CBBlade.addItem(local_table['Current Blade'][lang] + ": " + local_table['Blade1'][lang])
        self.CBBlade.addItem(local_table['Current Blade'][lang] + ": " + local_table['Blade2'][lang])
        auxtitle = local_table['Select AUXLEDs Effects for @@@ Effect'][lang].split('@@@')
        self.GBAuxLeds.setTitle(auxtitle[0] + ' ' + local_table['PowerOn'][lang] + ' ' + auxtitle[1])
        auxleds_label = local_table['AuxLEDs'][lang]
        common_label = local_table['Common'][lang]
        profiletab_label = local_table['Profiles'][lang]
        fonttab_label = local_table['Font optimizing'][lang]
        self.change_tab_title(auxleds_label, 0)
        self.change_tab_title(common_label, 1)
        self.change_tab_title(profiletab_label, 2)
        self.tabWidget.setTabText(3, fonttab_label)
        self.menuFile.setTitle(local_table['File'][lang])
        self.menuHelp.setTitle(local_table['MANUAL'][lang])
        self.actionOpen.setText(local_table['Open'][lang] + '...')
        self.actionOpenAll.setText(local_table['Open All'][lang] + '...')
        self.actionSave.setText(local_table['Save'][lang])
        self.actionSave_As.setText(local_table['Save As'][lang] + '...')
        self.actionSave_All.setText(local_table['Save All'][lang])
        self.actionNew.setText(local_table['New'][lang])
        self.actionExit.setText(local_table['Exit'][lang])
        self.actionProfiles_Edtor_Help.setText(local_table['Profiles Editor Manual'][lang])
        self.actionCommon_Editor_Help.setText(local_table['Common Editor Manual'][lang])
        self.actionAuxLeds_Editor_Help.setText(local_table['AuxLeds Editor Manual'][lang])
        self.actionAbout.setText(local_table['About'][lang])

    # auxleds part
    # ################################################################################################################ #
    def add_group(self):
        """
        Adds group to UI and data if name is correct
        disables used leds
        """
        name: str = self.TxtGroup.text()
        # get clicked leds and create new group
        leds_clicked: List[QtWidgets.QComboBox] = [CB for CB in self.leds_combo_list if
                                                   CB.isChecked() and CB.isEnabled()]
        leds_list: List[str] = [self.leds_cb_str[CB] for CB in leds_clicked]
        group_to_add, error = self.auxdata.add_group(name, leds_list)
        if group_to_add is None:
            self.error_message(local_table[error][self.language])
        else:
            # add group to group liat and sequencer, disable its leds
            self.LstGroup.addItem(str(group_to_add))
            self.LstGroup.setCurrentRow(self.auxdata.LedGroups.index(group_to_add))
            self.group_clicked()
            self.CBGroup.addItem(group_to_add.Name)
            for led in leds_clicked:
                led.setEnabled(False)
            self.BtnAddGroup.setEnabled(False)
            # leds are now available for change
            leds_to_add = [local_table['LED'][self.language] + self.leds_cb_str[led] for led in leds_clicked]
            self.CBFirstLED.addItems(leds_to_add)
            self.CBSecondLED.addItems(leds_to_add)
            self.BtnChange.setEnabled(True)
            # data is unsaved now
            self.saved[0] = False
            self.change_tab_title(auxleds, self.tabWidget.currentIndex())

    def update_group(self):
        """
        changes group name on gui and data
        :return:
        """
        # get group with new name
        new = self.TxtGroup.text()
        old = self.LstGroup.currentItem().text()
        group, error = self.auxdata.rename_group(old, new)
        if error:
            if error == 'no_group':
                msg: List[str] = local_table['no_group'].split()
                error_msg: str = msg[0] + LedGroup.get_name(old) + msg[1]
            else:
                error_msg = local_table[error][self.language]
            self.error_message(error_msg)
        else:
            # reload group list
            self.LstGroup.clear()
            self.CBGroup.clear()
            for group in self.auxdata.LedGroups:
                self.LstGroup.addItem(str(group))
                self.CBGroup.addItem(group.Name)
            # reload tree with sequencers with new groups
            self.TrStructure.clear()
            for seq in self.auxdata.Sequencers:
                item = SequencerTreeItem(str(seq))
                self.TrStructure.addTopLevelItem(item)
                for step in seq.Sequence:
                    if isinstance(step, Step):
                        step_descr = Mediator.translate_step(str(step), self.language)
                        step_item = StepTreeItem(step_descr)
                        item.addChild(step_item)
                    elif isinstance(step, Repeater):
                        repeat_descr = Mediator.translate_repeat(str(step), self.language)
                        step_item = RepeatTreeItem(repeat_descr)
                        item.addChild(step_item)
            self.step_controls_disable()
            self.repeat_controls_disable()
            self.BtnUpdate.setEnabled(False)
            # data is unsaved now
            self.saved[0] = False
            self.change_tab_title(auxleds, 0)

    def group_name_changed(self, name):
        """
        enables add group button if name is not empty and some leds are checked
        :param name:
        :return:
        """
        enabled = True if name and any([CB.isChecked() and CB.isEnabled() for CB in self.leds_combo_list]) else False
        self.BtnAddGroup.setEnabled(enabled)

    def led_clicked(self):
        """
        changes status of add group button if some leds are selected/are not selected
        :return:
        """
        name = self.TxtGroup.text()
        enabled = True if name and any([CB.isChecked() and CB.isEnabled() for CB in self.leds_combo_list]) else False
        self.BtnAddGroup.setEnabled(enabled)

    def change_pressed(self):
        """
        exchanges two leds in groups
        :return:
        """
        led1 = self.CBFirstLED.currentText().replace(local_table["LED"][self.language], "")
        led2 = self.CBSecondLED.currentText().replace(local_table["LED"][self.language], "")
        error = self.auxdata.change_leds(led1, led2)
        if error:
            msg = local_table[error[0]][self.language].split('@@@')
            self.error_message(msg[0] + error[1] + msg[1])
        else:
            self.LstGroup.clear()
            self.LstGroup.addItems([str(group) for group in self.auxdata.LedGroups])
            self.BtnAddGroup.setEnabled(False)
            self.BtnUpdate.setEnabled(False)
            self.BtnDeleteGroup.setEnabled(False)
            self.saved[0] = False
            self.change_tab_title(auxleds, 0)
        current = self.TrStructure.currentItem()
        if current and isinstance(current, StepTreeItem):
            self.tree_item_changed(current)

    def group_clicked(self):
        """
        enables Sequence controls and Delete Button
        :return:
        """
        self.BtnDeleteGroup.setEnabled(True)
        self.BtnUpdate.setEnabled(True)

    def delete_group(self):
        """
        deletes group if it is not used in any Sequencer
        :return:
        """
        group = self.LstGroup.currentItem().text()
        leds_to_free = self.auxdata.delete_group_and_enable_leds(group)
        if not leds_to_free:
            self.error_message(local_table['group_used'][self.language])
        else:
            # enabled freed leds
            for led in leds_to_free:
                self.leds[led].setEnabled(True)
                self.leds[led].setChecked(False)
            # reload leds to change list
            leds = self.auxdata.get_leds_used()
            self.CBFirstLED.clear()
            self.CBSecondLED.clear()
            if leds:
                leds_to_add = [(local_table['LED'][self.language] + led) for led in leds]
                self.CBFirstLED.addItems(leds_to_add)
                self.CBSecondLED.addItems(leds_to_add)
            self.BtnChange.setEnabled(bool(leds))

            # reload group list
            self.LstGroup.clear()
            self.CBGroup.clear()
            for group in self.auxdata.LedGroups:
                self.LstGroup.addItem(str(group))
                self.CBGroup.addItem(group.Name)
            # disable delete button and sequencer controls
            self.BtnDeleteGroup.setEnabled(False)
            self.sequence_control_disable()
            # data is unsaved now
            self.saved[0] = False
            self.change_tab_title(auxleds, 0)

    def group_controls_clear(self):
        """
        clears all group controls
        :return:
        """
        self.TxtGroup.clear()
        # check and disable used leds
        leds_used = self.auxdata.get_leds_used()
        for led in self.leds_cb_str.keys():
            if self.leds_cb_str[led] in leds_used:
                led.setEnabled(False)
                led.setChecked(True)
            else:
                led.setChecked(False)
                led.setEnabled(True)
        # reload leds for change
        self.CBFirstLED.clear()
        self.CBSecondLED.clear()
        if leds_used:
            leds_to_add = [local_table["LED"][self.language] + led for led in leds_used]
            self.CBFirstLED.addItems(leds_to_add)
            self.CBSecondLED.addItems(leds_to_add)
            self.BtnChange.setEnabled(True)
        else:
            self.BtnChange.setEnabled(False)
        # disable group buttons
        self.BtnAddGroup.setEnabled(False)
        self.BtnDeleteGroup.setEnabled(False)
        self.BtnUpdate.setEnabled(False)
        self.CBGroup.clear()
        # reload group list
        for group in self.auxdata.LedGroups:
            self.CBGroup.addItem(group.Name)

    def sequence_controls_enable(self):
        """
        enables all sequencer controls
        :return:
        """
        self.TxtSeqName.setEnabled(True)
        self.BtnAddSequencer.setEnabled(True)
        self.CBSeqList.setEnabled(True)
        if self.CBSeqList.count() > 0:
            self.BtnCopySeq.setEnabled(True)

    def sequence_control_disable(self):
        """
        disables all sequencer controls
        :return:
        """
        self.TxtSeqName.setEnabled(False)
        self.BtnAddSequencer.setEnabled(False)
        self.CBSeqList.setEnabled(False)
        self.BtnCopySeq.setEnabled(False)

    def group_changed(self):
        """
        if there are items in gropu comboobox, Sequencer fata is enabled, otherwise disabled
        :return:
        """
        if self.CBGroup.count() > 0:
            self.sequence_controls_enable()
            seqs = self.auxdata.get_corresponding_seqs(self.CBGroup.currentText())
            self.CBSeqList.clear()
            self.CBSeqList.addItems(seqs)
            if not seqs:
                self.BtnCopySeq.setEnabled(False)
            else:
                self.BtnCopySeq.setEnabled(True)
        else:
            self.sequence_control_disable()

    def add_sequencer(self):
        """
        Adds new Sequencer to gui and data
        :return:
        """
        seq_name = self.TxtSeqName.text()
        group_name = self.CBGroup.currentText()
        seq, error = self.auxdata.create_sequence(group_name, seq_name)
        if not seq:
            self.error_message(local_table[error][self.language])
        else:
            seq_item = SequencerTreeItem(str(seq))
            self.TrStructure.addTopLevelItem(seq_item)
            self.saved[0] = False
            self.change_tab_title(auxleds, self.tabWidget.currentIndex())
            self.CBAuxList.addItem(seq_name)  # add sequencer to aux section on profile tab
            self.CBSeqList.addItem(seq_name)  # add sequencer to copy sequencer section
            self.BtnCopySeq.setEnabled(True)
            self.TrStructure.setCurrentItem(seq_item)
            self.tree_item_changed(seq_item)

    def step_controls_disable(self):
        """
        disable all step controls
        :return:
        """
        self.TxtStepName.setEnabled(False)
        self.SpinWait.setEnabled(False)
        self.SpinSmooth.setEnabled(False)
        self.BtnAddStep.setEnabled(False)
        self.BtnDeleteStep.setEnabled(False)
        self.BtnEditStep.setEnabled(False)
        self.BtnEditRepeat.setEnabled(False)
        for brightness in self.step_leds_brightnesses:
            brightness.setEnabled(False)
        for channel in self.step_channels:
            channel.setEnabled(False)

    def repeat_controls_disable(self):
        """
        disables all repeat controls
        :return:
        """
        self.CBStartrom.setEnabled(False)
        self.SpinCount.setEnabled(False)
        self.CBForever.setEnabled(False)
        self.BtnAddRepeat.setEnabled(False)
        self.BtnDeleteRepeat.setEnabled(False)

    def step_controls_enable(self):
        """
        enable step controls, enable only used in tis sequencer led group led brightness and channels
        :return:
        """
        self.TxtStepName.setEnabled(True)
        self.SpinWait.setEnabled(True)
        self.SpinSmooth.setEnabled(True)
        self.BtnAddStep.setEnabled(True)
        self.TxtNewName.setEnabled(True)
        # get leds for tis sequencer led group and enable its brightnesses and channels
        current = self.TrStructure.currentItem()
        if isinstance(current, SequencerTreeItem):
            leds_list = self.auxdata.get_led_list(current.text(0))
        else:
            leds_list = self.auxdata.get_led_list(current.parent().text(0))

        for brightness in self.step_brightness_dict.keys():
            if brightness in leds_list:
                self.step_brightness_dict[brightness].setEnabled(True)
            else:
                self.step_brightness_dict[brightness].setEnabled(False)
        for channel in self.step_channels_dict.keys():
            if channel in leds_list:
                self.step_channels_dict[channel].setEnabled(True)
            else:
                self.step_channels_dict[channel].setEnabled(False)

    def repeat_controls_enable(self):
        """
        enable repeat controls
        :return:
        """
        if self.CBStartrom.count() > 0:
            self.CBStartrom.setEnabled(True)
            self.SpinCount.setEnabled(True)
            self.BtnAddRepeat.setEnabled(True)
            self.CBForever.setEnabled(True)
        else:
            self.repeat_controls_disable()

    def clear_step_controls(self):
        """
        load new data for step controls
        :return:
        """
        current = self.TrStructure.currentItem()
        if current:
            if isinstance(current, SequencerTreeItem):
                seq = self.auxdata.get_seq_by_name(Sequencer.get_name(current.text(0)))
            else:
                seq = self.auxdata.get_seq_by_name(Sequencer.get_name(current.parent().text(0)))

            max_step = seq.get_max_step_number()
            self.TxtStepName.setText('Step' + str(max_step + 1))
            self.CBStartrom.clear()
            self.CBStartrom.addItems(seq.get_steps_names())
        else:
            self.TxtStepName.clear()
        for led in self.step_leds_brightnesses:
            led.setValue(0)
        for channel in self.step_channels:
            channel.setCurrentIndex(0)
        self.SpinWait.setValue(0)
        self.SpinSmooth.setValue(0)

    def clear_repeat_controls(self):
        """
        clears repeat controls
        :return:
        """
        self.CBForever.setChecked(False)
        self.CBStartrom.setCurrentIndex(0)
        self.SpinCount.setValue(0)
        self.CBStartrom.clear()
        current = self.TrStructure.currentItem()
        if current:
            if isinstance(current, SequencerTreeItem):
                seq = self.auxdata.get_seq_by_name(Sequencer.get_name(current.text(0)))
            else:
                seq = self.auxdata.get_seq_by_name(Sequencer.get_name(current.parent().text(0)))
            steps_used = seq.get_steps_names()
            self.CBStartrom.addItems(steps_used)

    def load_step_controls(self):
        """
        load data for selected step
        :return:
        """
        current = self.TrStructure.currentItem()
        if isinstance(current, StepTreeItem):
            name = Step.get_name(current.text(0))
            self.TxtNewName.setText(name)
            parent = current.parent()
            seq_descr = parent.text(0)
            seq = self.auxdata.get_seq_by_name(Sequencer.get_name(seq_descr))
            self.TxtStepName.setText('Step' + str(seq.get_max_step_number() + 1))
            index = self.get_item_id(current)
            brightnesses, wait, smooth = self.auxdata.get_step_info(parent.text(0), index)
            self.SpinWait.setValue(wait)
            self.SpinSmooth.setValue(smooth)
            leds = self.auxdata.get_led_list(parent.text(0))
            for i in range(len(leds)):
                if isinstance(brightnesses[i], int):
                    self.step_brightness_dict[leds[i]].setValue(brightnesses[i])
                    self.step_channels_dict[leds[i]].setCurrentText(local_table['None'][self.language])
                else:
                    self.step_channels_dict[leds[i]].setCurrentText(Mediator.get_color_text(brightnesses[i],
                                                                                            self.language))
            for led in Mediator.leds_list:
                if led not in leds:
                    self.step_channels_dict[led].setCurrentText(local_table['None'][self.language])
                    self.step_brightness_dict[led].setValue(0)
        else:
            print("Wrong type selected")

    def load_repeat_controls(self):
        """
        load data for selected repeat
        :return:
        """
        current = self.TrStructure.currentItem()
        if isinstance(current, RepeatTreeItem):
            index = self.get_item_id(current)
            repeat_info = self.auxdata.get_repeat_info(current.parent().text(0), index)
            if repeat_info:
                self.CBStartrom.setCurrentText(repeat_info[0])
                if isinstance(repeat_info[1], str) and repeat_info[1].lower() == 'forever':
                    self.CBForever.setChecked(True)
                elif isinstance(repeat_info[1], int):
                    self.CBForever.setChecked(False)
                    self.SpinCount.setValue(int(repeat_info[1]))
                else:
                    self.error_message(local_table['step_count_error'][self.language])
        else:
            print("Wrong type selected!")

    def tree_item_changed(self, current):
        self.BtnAddStep.setEnabled(False)  # for not top-level items sequencer and leds are not available
        if isinstance(current, SequencerTreeItem):
            self.clear_step_controls()
            self.clear_repeat_controls()
            self.step_controls_enable()
            self.repeat_controls_enable()
            self.BtnDeleteSeq.setEnabled(True)
            self.BtnDeleteStep.setEnabled(False)
            self.BtnEditStep.setEnabled(False)
        if isinstance(current, StepTreeItem):
            self.BtnDeleteStep.setEnabled(True)
            self.BtnDeleteSeq.setEnabled(False)
            self.load_step_controls()
            self.clear_repeat_controls()
            self.BtnEditStep.setEnabled(True)
            self.step_controls_enable()
            self.repeat_controls_enable()
            self.BtnEditRepeat.setEnabled(False)
            self.BtnDeleteRepeat.setEnabled(False)
        if isinstance(current, RepeatTreeItem):
            self.clear_step_controls()
            self.step_controls_enable()
            self.repeat_controls_enable()
            self.load_repeat_controls()
            self.BtnEditStep.setEnabled(False)
            self.BtnDeleteStep.setEnabled(False)
            self.BtnEditRepeat.setEnabled(True)
            self.BtnDeleteRepeat.setEnabled(True)

    def get_item_id(self, item):
        parent = self.TrStructure.invisibleRootItem() if type(item) == SequencerTreeItem else item.parent()
        for i in range(parent.childCount()):
            if parent.child(i) == item:
                return i

    def add_step(self):
        current = self.TrStructure.currentItem()
        name = self.TxtStepName.text()
        brightnesses = list()
        if isinstance(current, SequencerTreeItem):
            seq_name = current.text(0)
            seq = self.auxdata.get_seq_by_name(Sequencer.get_name(seq_name))
            for i in range(len(self.auxdata.get_group_by_name(seq.Group).Leds)):
                brightnesses.append(0)
            step, error = self.auxdata.create_step(seq_name, -1, name, brightnesses, 0, 0)
        else:
            seq_name = current.parent().text(0)
            index = self.get_item_id(current)
            seq = self.auxdata.get_seq_by_name(Sequencer.get_name(seq_name))
            for i in range(len(self.auxdata.get_group_by_name(seq.Group).Leds)):
                brightnesses.append(0)
            step, error = self.auxdata.create_step(seq_name, index, name, brightnesses, 0, 0)
        if error:
            self.error_message(local_table[error][self.language])
            return
        step_descr: str = Mediator.translate_step(str(step), self.language)
        step_item = StepTreeItem(step_descr)
        if isinstance(current, SequencerTreeItem):
            current.addChild(step_item)
        else:
            current.parent().insertChild(index + 1, step_item)
        self.saved[0] = False
        self.change_tab_title(auxleds, self.tabWidget.currentIndex())
        self.TrStructure.expandItem(current)
        if name:
            self.CBStartrom.addItem(name)
            self.BtnAddRepeat.setEnabled(True)
            self.CBStartrom.setEnabled(True)
            self.SpinCount.setEnabled(True)
            self.CBForever.setEnabled(True)
        self.TrStructure.setCurrentItem(step_item)
        self.tree_item_changed(step_item)

    def edit_step(self):
        """
        edit step in data
        :return:
        """
        current = self.TrStructure.currentItem()
        seq_name = current.parent().text(0)
        name = self.TxtNewName.text()
        brightnesses = list()
        led_group = self.auxdata.get_group_by_name(
            self.auxdata.get_seq_by_name(Sequencer.get_name(seq_name)).Group).Leds
        for led in led_group:
            # for led in Mediator.leds_list:
            if self.step_channels_dict[led].isEnabled() and self.step_channels_dict[led].currentIndex() != 0:
                translated_color = self.step_channels_dict[led].currentText()
                brightnesses.append(Mediator.retranslate_color(translated_color, self.language))
            elif self.step_brightness_dict[led].isEnabled():
                brightnesses.append(self.step_brightness_dict[led].value())
        wait = self.SpinWait.value()
        smooth = self.SpinSmooth.value()
        index = self.get_item_id(current)
        step, old_step, changed = self.auxdata.update_step(seq_name, index, name, brightnesses, wait, smooth)
        if old_step:
            # to do update repeat steps
            self.CBStartrom.clear()
            seq = self.auxdata.get_seq_by_name(Sequencer.get_name(seq_name))
            step_names = seq.get_steps_names()
            for name in step_names:
                self.CBStartrom.addItem(name)
        # edit item in tree
        step_descr: str = Mediator.translate_step(str(step), self.language)
        current.setText(0, step_descr)
        # update repeat items
        for i in changed:
            item = current.parent().child(i)
            current_text: str = item.text(0)
            item.setText(0, current_text.replace(old_step, self.TxtNewName.text()))
        # profile is not saved now
        self.saved[0] = False
        self.change_tab_title(auxleds, 0)

    def add_repeat_step(self):
        current = self.TrStructure.currentItem()
        startstep: str = self.CBStartrom.currentText()
        if self.CBForever.isChecked():
            count: Union[str, int] = 'forever'
        else:
            count = self.SpinCount.value()
        if isinstance(current, SequencerTreeItem):
            repeat, error = self.auxdata.add_repeat(current.text(0), -1, startstep, count)
        else:
            parent = current.parent()
            index = self.get_item_id(current)
            repeat, error = self.auxdata.add_repeat(parent.text(0), index, startstep, count)
        if error:
            self.error_message(local_table[error][self.language])
        else:
            repeat_descr = Mediator.translate_repeat(str(repeat), self.language)
            repeat_item = RepeatTreeItem(repeat_descr)
            if isinstance(current, SequencerTreeItem):
                current.addChild(repeat_item)
            else:
                current.parent().insertChild(index + 1, repeat_item)
            self.TrStructure.setCurrentItem(repeat_item)
            self.tree_item_changed(repeat_item)
            self.saved[0] = False
            self.change_tab_title(auxleds, self.tabWidget.currentIndex())

    def edit_repeater(self):
        """
        update gui and data for repeater
        :return:
        """
        current = self.TrStructure.currentItem()
        seq_name: str = current.parent().text(0)
        index = self.get_item_id(current)
        new_start = self.CBStartrom.currentText()
        if self.CBForever.isChecked():
            new_count = 'Forever'
        else:
            new_count = self.SpinCount.value()
        repeat, error = self.auxdata.update_repeat(seq_name, index, new_start, new_count)
        if error:
            self.error_message(local_table[error][self.language])
            return
        current.setText(0, Mediator.translate_repeat(str(repeat), self.language))
        self.saved[0] = False
        self.change_tab_title(auxleds, 0)

    def delete_item(self):
        current = self.TrStructure.currentItem()
        current_name = current.text(0)
        if current.childCount() > 0:
            reply = QMessageBox.question(self, 'Message', local_table['sequencer_delete_error'][self.language],
                                         QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.No:
                return
        self.change_tab_title(auxleds, self.tabWidget.currentIndex())
        if isinstance(current, SequencerTreeItem):
            parent = self.TrStructure.invisibleRootItem()
            parent.removeChild(current)
            self.auxdata.delete_sequence(current_name)
            # delete seq from copy sequncer block and aux block in profile tab
            self.CBSeqList.clear()
            self.CBAuxList.clear()
            for sequencer in self.auxdata.Sequencers:
                self.CBSeqList.addItem(sequencer.Name)
                self.CBAuxList.addItem(sequencer.Name)
            if self.CBSeqList.count() == 0:
                self.BtnCopySeq.setEnabled(False)
            self.clear_step_controls()
            self.step_controls_disable()
            self.repeat_controls_disable()

        if isinstance(current, StepTreeItem):
            index = self.get_item_id(current)
            parent = current.parent()
            seq_name = parent.text(0)
            step_name = Step.get_name(current_name)

            seq = self.auxdata.get_seq_by_name(Sequencer.get_name(seq_name))
            used_repeat_steps = seq.get_repeat_steps_names()
            if step_name.lower() in used_repeat_steps:
                self.error_message(local_table['stepUsed_error'][self.language])
                return
            parent.removeChild(current)
            self.auxdata.delete_step(current_name, seq_name)
            # reload steps for repeat
            used_steps = seq.get_steps_names()
            if not used_steps:
                self.CBForever.setEnabled(False)
                self.CBStartrom.setEnabled(False)
                self.SpinCount.setEnabled(False)
                self.BtnAddRepeat.setEnabled(False)
            else:
                self.CBStartrom.clear()
                for step in used_steps:
                    self.CBStartrom.addItem(step)
        if isinstance(current, RepeatTreeItem):
            parent: SequencerTreeItem = current.parent()
            seq_name: str = parent.text(0)
            index = self.get_item_id(current)
            error = self.auxdata.delete_repeat(seq_name, index)
            if error:
                self.error_message(local_table[error][self.language])
                return
            parent.removeChild(current)
        # select next step if any, or previous, or none if there are no steps
        if not isinstance(current, SequencerTreeItem):
            print(parent.childCount())
            if index < parent.childCount():
                self.TrStructure.setCurrentItem(parent.child(index))
                # self.TreeItemChanged(self.TrStructure.currentItem())
            elif parent.childCount() > 0:
                # TODO get last element instead of -1
                last_index = parent.childCount() - 1
                self.TrStructure.setCurrentItem(parent.child(last_index))
            else:
                # disable step controls
                self.clear_step_controls()
                self.clear_repeat_controls()
                self.step_controls_disable()
                self.repeat_controls_disable()
                self.BtnEditStep.setEnabled(False)
                self.BtnEditRepeat.setEnabled(False)
                self.BtnDeleteRepeat.setEnabled(False)
        # data is unsaved now
        self.saved[0] = False
        self.change_tab_title(auxleds, self.tabWidget.currentIndex())

    def copy_sequencer(self):

        """
        Adds new Sequencer with steps of selected to gui and data
        :return:
        """
        seq_name = self.TxtSeqName.text()
        group_name = self.CBGroup.currentText()
        seq, error = self.auxdata.create_sequence(group_name, seq_name)
        if not seq:
            self.error_message(local_table[error][self.language])
        else:
            seq_item = SequencerTreeItem(str(seq))
            self.TrStructure.addTopLevelItem(seq_item)
            seq_old = self.auxdata.get_seq_by_name(self.CBSeqList.currentText())
            for step in seq_old.Sequence:
                if isinstance(step, Step):
                    self.auxdata.create_step(str(seq), -1, step.Name, step.Brightness, step.Smooth, step.Wait)
                    step_descr: str = Mediator.translate_step(str(step), self.language)
                    step_item = StepTreeItem(step_descr)
                    seq_item.addChild(step_item)
                elif isinstance(step, Repeater):
                    self.auxdata.add_repeat(str(seq), -1, step.StartingFrom, step.Count)
                    repeat_descr = Mediator.translate_repeat(str(step), self.language)
                    step_item = RepeatTreeItem(repeat_descr)
                    seq_item.addChild(step_item)

            self.saved[0] = False
            self.change_tab_title(auxleds, self.tabWidget.currentIndex())
            self.CBAuxList.addItem(seq_name)  # add sequencer to aux section on profile tab
            self.CBSeqList.addItem(seq_name)  # add sequencer to copy sequencer section

    def load_data_to_tree(self):
        self.TrStructure.clear()
        self.LstGroup.clear()
        self.CBStartrom.clear()
        self.CBAuxList.clear()
        self.CBSeqList.clear()
        self.CBGroup.clear()
        for group in self.auxdata.LedGroups:
            self.LstGroup.addItem(str(group))
            self.CBGroup.addItem(group.Name)
        for seq in self.auxdata.Sequencers:
            item = SequencerTreeItem(str(seq))
            self.TrStructure.addTopLevelItem(item)
            self.CBAuxList.addItem(seq.get_name(str(seq)))
            self.CBSeqList.addItem(seq.get_name(str(seq)))
            for step in seq.Sequence:
                if isinstance(step, Step):
                    step_descr: str = Mediator.translate_step(str(step), self.language)
                    step_item = StepTreeItem(step_descr)
                    item.addChild(step_item)
                elif isinstance(step, Repeater):
                    repeat_descr: str = Mediator.translate_repeat(str(step), self.language)
                    step_item = RepeatTreeItem(repeat_descr)
                    item.addChild(step_item)
        self.clear_step_controls()
        self.clear_repeat_controls()
        self.repeat_controls_disable()
        self.step_controls_disable()
        # self.SequenceControlsDisable()
        self.TxtSeqName.clear()
        self.group_controls_clear()
        if self.CBSeqList.count() > 0:
            self.BtnCopySeq.setEnabled(True)

    # common tab part
    # ################################################################################################################ #
    def cb_clicked(self):
        cb = self.sender()
        if cb in self.common_dict.keys():
            key_list = self.common_dict[cb]
        else:
            key_list = self.motion_dict[cb]
        if cb.isChecked():
            self.commondata.update_value(key_list, 1)
        else:
            self.commondata.update_value(key_list, 0)
        if self.saved[1]:
            self.saved[1] = False
            self.change_tab_title(common, self.tabWidget.currentIndex())
        self.BtnSave.setEnabled(True)
        self.BtnDefault.setEnabled(True)

    def spin_changed(self):
        spin = self.sender()
        if spin in self.common_dict.keys():
            key_list = Mediator.change_keylist(self.common_dict[spin])
        else:
            key_list = self.motion_dict[spin]
        self.commondata.update_value(key_list, spin.value())
        if self.saved[1]:
            self.saved[1] = False
            self.change_tab_title(common, 1)
        self.BtnSave.setEnabled(True)
        self.BtnDefault.setEnabled(True)

    def set_default_common(self):
        for key in self.common_dict.keys():
            value = self.commondata.get_default_value(Mediator.change_keylist(self.common_dict[key]))
            if key in [self.CBBlade2Enabled, self.CBOneButton, self.CBPowerOnByStab]:
                key.setChecked(value)
            else:
                key.setValue(value)
        for key in self.motion_dict.keys():
            value = self.commondata.get_default_value(Mediator.change_keylist(self.motion_dict[key]))
            if key in [self.CBStabEnabled, self.CBScrewEnabled, self.CBSpinEnabled]:
                key.setChecked(value)
            else:
                key.setValue(value)

    def load_common_data(self, data):
        try:
            for key in self.common_dict.keys():
                path = Mediator.change_keylist(self.common_dict[key])
                value = data
                for path_key in path:
                    value = value[path_key]
                if key in [self.CBBlade2Enabled, self.CBOneButton, self.CBPowerOnByStab]:
                    key.setChecked(value)
                else:
                    key.setValue(value)
            for key in self.motion_dict.keys():
                path = Mediator.change_keylist(self.motion_dict[key])
                value = data
                for path_key in path:
                    value = value[path_key]
                if key in [self.CBStabEnabled, self.CBScrewEnabled, self.CBSpinEnabled]:
                    key.setChecked(value)
                else:
                    key.setValue(value)
            self.CBBlade2Enabled.setChecked(data[Mediator.blade2_key[0]]['Enabled'])
        except Exception:
            e = sys.exc_info()[1]
            self.error_message(e.args[0])

    def blade2_clicked(self):
        """
        writes 0 or 1 to corresponding data field
        :return:
        """
        if self.CBBlade2Enabled.isChecked():
            self.commondata.update_value(Mediator.blade2_enabled_keys, 1)
            self.SpinPixPerBand2.setEnabled(True)
            self.SpinBandNumber.setEnabled(True)
        else:
            self.commondata.update_value(Mediator.blade2_enabled_keys, 0)
            self.SpinPixPerBand2.setEnabled(False)
            self.SpinBandNumber.setEnabled(False)
        self.saved[1] = False
        self.change_tab_title(common, 1)

    # profiles tab
    # ################################################################################################################ #
    def effect_tab_changed(self):
        """
        changes group and button label for auxleds group when tab changes
        :return:
        """
        current = self.TabEffects.currentIndex()
        text = tabnames[current]
        if self.language != 'ru':
            label = local_table['Add Effect to @@@'][self.language].replace("@@@", local_table[text][self.language])
            self.BtnCReateAux.setText(label)
        else:
            self.BtnCReateAux.setText(
                local_table['Add Effect to @@@'][self.language][:-3] + 'режиму\n«' + local_table[text][self.language] +
                '»')
        auxtitle = local_table['Select AUXLEDs Effects for @@@ Effect'][self.language].split('@@@')
        self.GBAuxLeds.setTitle(auxtitle[0] + ' ' + local_table[text][self.language] + ' ' + auxtitle[1])
        # load data or current tab if profile is selected
        if self.BtnCReateAux.isEnabled():
            profile = self.LstProfile.currentItem().text()
            auxeffects = self.profiledata.get_aux_effects(text, profile)
            self.LstAuxProfile.clear()
            for aux in auxeffects:
                self.LstAuxProfile.addItem(aux)

    def min_hanged(self, min_control):
        """
        when min data changes corresponding max border changes too
        :param min_control: control that changes
        :return:
        """
        max_control = self.min_max_dict[min_control]
        max_control.setMinimum(min_control.value())

    def max_changed(self, max_control):
        """
        when max data changes corresponding min border changes too
        :param max_control: control that changes
        :return:
        """
        min_control = self.max_min_dict[max_control]
        min_control.setMaximum(max_control.value())

    def profile_name_changed(self, name):
        """
        if text in profile field changed and this name is not used yet and it is valid make add profile button enabled
        :param name:
        :return:
        """
        effects = self.profiledata.get_profiles_list()
        has_symbol = any([ch.isalpha() for ch in name])
        valid = all(ch.isalpha() or ch.isdigit() or ch == "_" for ch in name)
        enabled = True if name and name not in effects and valid and has_symbol else False
        self.BtnProfile.setEnabled(enabled)
        self.BtnEditProfile.setEnabled(enabled)

    def add_profile(self):
        """
        adds new profile with current name to Profile List and profile data
        :return:
        """
        name = self.TxtAddProfile.text()
        self.profiledata.add_profile(name)
        self.BtnProfile.setEnabled(False)
        self.LstProfile.addItem(name)
        # data is unsaved now
        self.saved[2] = False
        self.change_tab_title(profiletab, self.tabWidget.currentIndex())

    def profile_cb_clicked(self):
        """
        any check box in profile controls clicked. we get key path for it and save to data to current profile
        (checked = 1, otherwise 0)
        :return:
        """
        cb = self.sender()
        if cb.isEnabled():
            key_list = self.profile_dict[cb]
            profile = self.LstProfile.currentItem().text()
            if cb.isChecked():
                self.profiledata.update_value(key_list, profile, 1)
                # disable coupled checkbox
                self.CB_single_dict[cb].setEnabled(False)
            else:
                self.profiledata.update_value(key_list, profile, 0)
                # enable coupled checkbox
                self.CB_single_dict[cb].setEnabled(True)
            # data now is unsaved
            if self.saved[2]:
                self.saved[2] = False
                self.change_tab_title(profiletab, self.tabWidget.currentIndex())

    def load_profile_controls(self, profile):
        """
        enables all neeeded controls for selected profile
        load data for selected profile to profile controls (Main Blade section)
        :param profile:
        :return:
        """
        # enable all control for all tabs
        for key in self.control_tab_dict.keys():
            for control in self.control_tab_dict[key]:
                control.setEnabled(True)
        for key in self.color_dict.keys():
            key.setEnabled(True)
        for key in self.color_CB_dict.keys():
            key.setEnabled(True)
        self.BtnAddColor.setEnabled(True)
        self.BtnAddRandom.setEnabled(True)
        self.CBBlade.setEnabled(True)
        # aux block enable
        self.TxtCreateAux.setEnabled(True)
        self.BtnCReateAux.setEnabled(True)
        self.CBAuxList.setEnabled(True)

        # loads data for main blade
        for control in self.profile_dict.keys():
            value = self.profiledata.get_value(self.profile_dict[control], profile)
            # Combo Box
            if control in self.CB_list:
                control.setChecked(value)
            else:
                # color text
                if control in self.color_list:
                    text = Mediator.color_data_to_str(value)
                    control.setText(text)
                else:
                    # spin box
                    control.setValue(value)

        # controls under Blade selection loaded
        value = self.profiledata.get_value(Mediator.indicate_path, profile)
        self.CBIndicate.setChecked(value)
        value = self.profiledata.get_value(Mediator.delay_path, profile)
        self.SpinDelayBeforeOn.setValue(value)

        # flaming colors list loaded
        self.LstFlamingColor.clear()
        flaming_colors = self.profiledata.get_colors(Mediator.flaming_color_path, profile)
        for color in flaming_colors:
            item = Mediator.color_data_to_str(color)
            self.LstFlamingColor.addItem(item)

        # auxleds section
        index = self.TabEffects.currentIndex()
        effect = tabnames[index]
        auxeffects = self.profiledata.get_aux_effects(effect, profile)
        self.LstAuxProfile.clear()
        for aux in auxeffects:
            self.LstAuxProfile.addItem(aux)

        # you may delete profile now
        self.BtnDeleteProfile.setEnabled(True)

    def profile_clicked(self, item):
        """
        profile item in Profile List clicked. All neseccary data loaded, controls enabled
        :param item:
        :return:
        """
        if item:
            profile = item.text()
            self.CBBlade.setCurrentIndex(0)
            self.load_profile_controls(profile)
            self.blade_changed(self.CBBlade.currentIndex())
            i = self.LstProfile.currentRow()
            # enable BtnUp and Down
            enabled = True if i > 0 else False
            self.BtnUp.setEnabled(enabled)
            enabled = True if (i < self.LstProfile.count() - 1) else False
            self.BtnDown.setEnabled(enabled)
            # enable profile editing
            has_symbol = any([s.isalpha() for s in self.TxtAddProfile.text()])
            valid = all(s.isalpha() or s.isdigit() or s == "_" for s in self.TxtAddProfile.text())
            if valid and has_symbol and self.TxtAddProfile.text() != "" \
                    and self.TxtAddProfile.text() not in self.profiledata.get_profiles_list():
                self.BtnEditProfile.setEnabled(True)

    def delete_profile(self):
        """
        delete profile from data and UI with question, disables delete button, loads default data to all controls
        :return:
        """
        name = self.LstProfile.currentItem().text()
        # warning message
        reply = QMessageBox.question(self, 'Message', "Do you realy want to delete this profile?",
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.profiledata.delete_profile(name)
            self.LstProfile.clear()
            for profile in self.profiledata.get_profiles_list():
                self.LstProfile.addItem(profile)
            self.profile_control_disable()
            # file is unsaved now
            self.saved[2] = False
            self.change_tab_title(profiletab, self.tabWidget.currentIndex())

    def profile_control_disable(self):
        """
        desables and loads default for all profile controls
        :return:
        """
        self.BtnDeleteProfile.setEnabled(False)

        # disable all profile controls
        for key in self.control_tab_dict.keys():
            for control in self.control_tab_dict[key]:
                control.setEnabled(False)
        for key in self.color_dict.keys():
            key.setEnabled(False)
        for key in self.color_CB_dict.keys():
            key.setEnabled(False)
        self.BtnAddColor.setEnabled(False)
        self.CBBlade.setEnabled(False)
        self.SpinDelayBeforeOn.setEnabled(False)
        self.CBIndicate.setEnabled(False)
        # and auxleds group
        self.BtnAuxDelete.setEnabled(False)
        self.BtnCReateAux.setEnabled(False)
        self.CBAuxList.setEnabled(False)
        self.TxtCreateAux.setEnabled(False)

        # load default data
        for key in self.profile_dict.keys():
            value = self.profiledata.get_default(self.profile_dict[key])
            if key in self.CB_list:
                key.setChecked(value)
            else:
                if key in self.color_list:
                    text = Mediator.color_data_to_str(value)
                    key.setText(text)
                else:
                    key.setValue(value)
        self.LstFlamingColor.clear()
        value = self.profiledata.get_default(Mediator.indicate_path)
        self.CBIndicate.setChecked(value)
        value = self.profiledata.get_default(Mediator.delay_path)
        self.SpinDelayBeforeOn.setValue(value)
        self.TxtAddProfile.clear()
        self.BtnEditProfile.setEnabled(False)
        self.BtnUp.setEnabled(False)
        self.BtnDown.setEnabled(False)

    def profile_spin_changed(self):
        """
        saves new value of any profile spin control to corresponding data using path of keys, changes min/max controls
        borders if nesessary
        :return:
        """
        spin = self.sender()
        if spin.isEnabled():
            blade = self.CBBlade.currentIndex()
            key_list = self.profile_dict[spin]
            # for second blade Blade2 key added to key path
            if blade == 1:
                key_list = Mediator.blade2_key + key_list
            text = self.LstProfile.currentItem().text()
            self.profiledata.update_value(key_list, text, spin.value())
            # data may be unsaved now
            if self.saved[2]:
                self.saved[2] = False
                self.change_tab_title(profiletab, self.tabWidget.currentIndex())
            # update min and max controls
            # if spin in self.min_max_dict.keys():
            #     self.MinChanged(spin)
            # if spin in self.max_min_dict.keys():
            #     self.MaxChanged(spin)

    def profile_text_changed(self):
        """
        saves data if text changed
        :return:
        """
        text = self.sender()
        label = text.text()
        label = Mediator.str_to_color_data(label)
        # not save id control is disabled (may occur when we load default settings if no profile is selected
        if text.isEnabled():
            if label:
                key_list = self.profile_dict[text]
                # add blade2 key to path for second blade
                blade = self.CBBlade.currentIndex()
                if blade == 1:
                    key_list = Mediator.blade2_key + key_list
                profile = self.LstProfile.currentItem().text()
                self.profiledata.update_value(key_list, profile, label)
                # profile is not saved now
                if self.saved[2]:
                    self.saved[2] = False
                    self.change_tab_title(profiletab, self.tabWidget.currentIndex())
        color_widget = self.selected_color_dict[text]
        color_widget.setAutoFillBackground(True)
        color = text.text().split(', ')
        color_isvalid = len(color) == 3 and all([col.isdigit() for col in color])
        if label != 'random' and color_isvalid:
            try:
                rgb_shifted = ",".join(str(color) for color in palitra.ColorDialog.getColornoWindow(text.text())[0][1])
                color_widget.setStyleSheet("QWidget { background-color: rgba(%s); }" % rgb_shifted)
            except IndexError:
                color_widget.setStyleSheet("QWidget { background-color: %s }") % 'gray'
        else:
            color_widget.setStyleSheet("QWidget { background-color: %s }" % 'gray')

        for key in self.color_CB_dict.keys():
            if self.color_CB_dict[key] == text:
                if isinstance(label, str) and label.lower() == 'random':
                    key.setChecked(True)
                else:
                    key.setChecked(False)

    def profile_edit_pressed(self):
        """
        edit profile name
        :return:
        """
        result, i = self.profiledata.change_key_order(self.LstProfile.currentItem().text(), self.TxtAddProfile.text())
        if result != "":
            self.error_message(result)
        else:
            self.load_profile_list()
            self.LstProfile.setCurrentRow(i)
            self.profile_clicked(self.LstProfile.currentItem())

    def color_changed(self):
        """
        adds new color selected with color dialog to control
        :return:
        """
        color_button = self.sender()
        color_input = self.color_dict[color_button]
        color = color_input.text().split(', ')
        color_isvalid = len(color) == 3 and all([col.isdigit() for col in color])
        if color_isvalid:
            color_data = palitra.ColorDialog.getColor(color_input.text(), self.language)
        else:
            color_data = palitra.ColorDialog.getColor("255, 0, 0", self.language)
        if color_data[1]:
            color_input.setText(color_data[0][0])
            color_widget = self.selected_color_dict[color_input]
            color_widget.setAutoFillBackground(True)
            rgb_shifted = ",".join(str(color) for color in color_data[0][1])
            color_widget.setStyleSheet("QWidget { background-color: rgb(%s); }" % rgb_shifted)

    def add_color(self):
        """
        adds color to flaming color list and saves color data to profile
        :return:
        """
        color_data = palitra.ColorDialog.getColor("255, 0, 0", self.language)
        if color_data[1]:
            self.LstFlamingColor.addItem(color_data[0][0])
            # save to profile adding Blade2 key if Blade2 selected
            profile = self.LstProfile.currentItem().text()
            path = Mediator.flaming_color_path
            index = self.CBBlade.currentIndex()
            if index == 1:
                path = Mediator.blade2_key + path
            rgb = list(map(int, color_data[0][0].split(', ')))
            self.profiledata.save_color(path, rgb, profile)
        # profile is unsaved now
        self.saved[2] = False
        self.change_tab_title(profiletab, self.tabWidget.currentIndex())

    def color_random_clicked(self):
        """
        disables color selection and sets color to random
        :return:
        """
        CB = self.sender()
        txt_color = self.color_CB_dict[CB]
        if CB.isChecked():
            txt_color.setText('random')
            txt_color.setEnabled(False)
            for key in self.color_dict.keys():
                if self.color_dict[key] == txt_color:
                    key.setEnabled(False)
        else:
            txt_color.setText(Mediator.color_data_to_str(self.profiledata.get_default(self.profile_dict[txt_color])))
            txt_color.setEnabled(True)
            for key in self.color_dict.keys():
                if self.color_dict[key] == txt_color:
                    key.setEnabled(True)
        if CB.isEnabled:
            self.saved[2] = False
            self.change_tab_title(profiletab, 2)

    def color_clocked(self):
        """
        if any color selected we may delete it
        :return:
        """
        self.BtnDeleteColor.setEnabled(True)

    def add_random_color(self):
        """
        adds random string to color list
        :return:
        """
        self.LstFlamingColor.addItem('random')
        # save to profile adding Blade2 key if Blade2 selected
        profile = self.LstProfile.currentItem().text()
        path = Mediator.flaming_color_path
        index = self.CBBlade.currentIndex()
        if index == 1:
            path = Mediator.blade2_key + path
        self.profiledata.save_color(path, 'random', profile)
        # profile is unsaved now
        self.saved[2] = False
        self.change_tab_title(profiletab, self.tabWidget.currentIndex())

    def delete_color(self):
        current_color = self.LstFlamingColor.currentItem().text()
        current_index = self.LstFlamingColor.currentIndex()
        current_color = Mediator.str_to_color_data(current_color)
        path = Mediator.flaming_color_path
        index = self.CBBlade.currentIndex()
        if index == 1:
            path = Mediator.blade2_key + path
        self.profiledata.delete_color(path, current_color, self.LstProfile.currentItem().text())
        self.LstFlamingColor.clear()
        flaming_colors = self.profiledata.get_colors(path, self.LstProfile.currentItem().text())
        for color in flaming_colors:
            item = Mediator.color_data_to_str(color)
            self.LstFlamingColor.addItem(item)
        self.saved[2] = False
        self.change_tab_title(profiletab, self.tabWidget.currentIndex())
        # select next color (previous if the color is last) or disable delete button if there are no colors
        count = self.LstFlamingColor.count()
        if current_index.row() < count:
            self.LstFlamingColor.setCurrentIndex(current_index)
        elif count > 0:
            self.LstFlamingColor.setCurrentRow(current_index.row() - 1)
        else:
            self.BtnDeleteColor.setEnabled(False)

    def blade_changed(self, index):
        """
        enable necessary controls for selected blade and disable unnecessary and loads data
        :param index: index of blade
        :return:
        """
        if self.CBBlade.isEnabled():
            profile = self.LstProfile.currentItem().text()
            if index == 0:
                # main blade
                # all tabs enabled
                self.TabPowerOn.setEnabled(True)
                self.TabPowerOff.setEnabled(True)
                self.TabClash.setEnabled(True)
                self.TabStab.setEnabled(True)
                self.TabLockup.setEnabled(True)
                self.TabBlaster.setEnabled(True)

                # enables and loads all tab controls for main blade
                self.load_profile_controls(profile)

                # disable extra blade2 comboboxes
                self.CBFlickeringAlwaysOn.setEnabled(False)
                self.CBFlamingAlwaysOn.setEnabled(False)

                # disables controls for blade2
                self.CBIndicate.setEnabled(False)
                self.SpinDelayBeforeOn.setEnabled(False)
            else:
                # blade2
                # disables unused tabs
                self.TabPowerOn.setEnabled(False)
                self.TabPowerOff.setEnabled(False)
                self.TabClash.setEnabled(False)
                self.TabStab.setEnabled(False)
                self.TabLockup.setEnabled(False)
                self.TabBlaster.setEnabled(False)
                # enables special Blade2 Comboboxes
                self.CBFlamingAlwaysOn.setEnabled(True)
                self.CBFlickeringAlwaysOn.setEnabled(True)
                # enables blade2 settings
                self.CBIndicate.setEnabled(True)
                self.SpinDelayBeforeOn.setEnabled(True)
                # disables AuxEffects section
                self.BtnCReateAux.setEnabled(False)
                self.TxtCreateAux.setEnabled(False)
                self.CBAuxList.setEnabled(False)
                self.BtnAuxDelete.setEnabled(False)
                self.LstAuxProfile.clear()
                # disable unused comboboxes
                self.CBFlaming.setEnabled(False)
                self.CBFlickering.setEnabled(False)
                # load data for blade2
                self.load_blade2_controls()

    def load_blade2_controls(self):
        """
        loads data for blade2 for selected profile
        :return:
        """
        # all paths must start with Mediator.blade2_keys.
        # Done automatically for self.extra_blade_CB and self.spinDelayBeforeOn
        profile = self.LstProfile.currentItem().text()
        # flickering and flaming tabs
        controls = self.flickering + self.flaming
        for spin in controls:
            path = self.profile_dict[spin]
            path = Mediator.blade2_key + path
            value = self.profiledata.get_value(path, profile)
            spin.setValue(value)
        # color for working mode
        path = self.profile_dict[self.TxtWorkingColor]
        color = self.profiledata.get_value(Mediator.blade2_key + path, profile)
        text = Mediator.color_data_to_str(color)
        self.TxtWorkingColor.setText(text)
        # extrs Blade2 comboboxes
        for CB in self.extra_blade_CB_dict.keys():
            value = self.profiledata.get_value(self.extra_blade_CB_dict[CB], profile)
            CB.setChecked(value)
        # dalay before blade2
        delay = self.profiledata.get_value(Mediator.delay_path, profile)
        self.SpinDelayBeforeOn.setValue(delay)
        # flaming colors fpr blade2
        self.LstFlamingColor.clear()
        flaming_colors = self.profiledata.get_colors(Mediator.blade2_key + Mediator.flaming_color_path,
                                                     self.LstProfile.currentItem().text())
        for color in flaming_colors:
            item = Mediator.color_data_to_str(color)
            self.LstFlamingColor.addItem(item)

    def extra_blade_clicked(self):
        """
        handlers for extra comboboxes for blade2, saves to profile data
        :return:
        """
        cb = self.sender()
        path = self.extra_blade_CB_dict[cb]
        profile = self.LstProfile.currentItem().text()
        if cb.isChecked():
            value = 1
            # disable coupled checkbox
            self.CB_single_dict[cb].setEnabled(False)
        else:
            value = 0
            # enable coupled checkbox
            self.CB_single_dict[cb].setEnabled(True)
        # data is unsaved now
        self.profiledata.update_value(path, profile, value)
        self.saved[2] = False

    def delay_changed(self):
        """
        delay before handler, saves to profile data
        :return:
        """
        if self.SpinDelayBeforeOn.isEnabled():
            path = Mediator.delay_path
            value = self.SpinDelayBeforeOn.value()
            profile = self.LstProfile.currentItem().text()
            self.profiledata.update_value(path, profile, value)

    def profile_add_aux(self):
        """
        adds aux effect from test field if it is correcty filled or from auxlist
        :return:
        """
        current = self.TabEffects.currentIndex()
        effect = tabnames[current]
        profile = self.LstProfile.currentItem().text()
        auxeffect = self.TxtCreateAux.text()
        valid = [ch.isalpha() or ch.isdigit() or ch == '_' for ch in auxeffect]
        existing = [seq.lower() for seq in self.profiledata.get_aux_effects(effect, profile)]
        if auxeffect != "" and all(valid) and auxeffect.lower() not in existing:
            self.LstAuxProfile.addItem(auxeffect)
            self.TxtCreateAux.clear()
            self.profiledata.save_aux(auxeffect, effect, profile)
        else:
            auxeffect = self.CBAuxList.currentText()
            groups_used = list()
            for sequencer in existing:
                seq = self.auxdata.get_seq_by_name(sequencer)
                if seq:
                    groups_used.append(seq.Group)
            group_selected = self.auxdata.get_seq_by_name(auxeffect).Group
            if group_selected.lower() in groups_used:
                self.error_message(local_table['effect_exists'][self.language])
                return
            if auxeffect and auxeffect.lower() not in existing:
                self.LstAuxProfile.addItem(auxeffect)
                self.profiledata.save_aux(auxeffect, effect, profile)
            else:
                self.error_message(local_table['effect_used'][self.language])

    def aux_clicked(self):
        """
        button Delete AuxEffect activated
        :return:
        """
        self.BtnAuxDelete.setEnabled(True)

    def delete_aux(self):
        """
        delete selected aux from UI and profile data for tos effect. AuxSetion is cleared if it was last effect
        :return:
        """
        current = self.LstAuxProfile.currentItem().text()
        current_tab = self.TabEffects.currentIndex()
        effect = tabnames[current_tab]
        profile = self.LstProfile.currentItem().text()
        self.profiledata.delete_aux(current, effect, profile)
        auxeffects = self.profiledata.get_aux_effects(effect, profile)
        self.LstAuxProfile.clear()
        for aux in auxeffects:
            self.LstAuxProfile.addItem(aux)
        self.BtnAuxDelete.setEnabled(False)

    def load_profile_list(self):
        """
        loads from data all profiles to list
        :return:
        """
        self.LstProfile.clear()
        for profile in self.profiledata.order:
            self.LstProfile.addItem(profile)
        self.BtnDeleteProfile.setEnabled(False)

        # disable all profile controls
        for key in self.control_tab_dict.keys():
            for control in self.control_tab_dict[key]:
                control.setEnabled(False)
        for key in self.color_dict.keys():
            key.setEnabled(False)
        for key in self.color_CB_dict.keys():
            key.setEnabled(False)
        self.BtnAddColor.setEnabled(False)
        self.BtnAddRandom.setEnabled(False)
        self.CBBlade.setEnabled(False)
        self.SpinDelayBeforeOn.setEnabled(False)
        self.CBIndicate.setEnabled(False)
        # and auxleds group
        self.BtnAuxDelete.setEnabled(False)
        self.BtnCReateAux.setEnabled(False)
        self.CBAuxList.setEnabled(False)
        self.TxtCreateAux.setEnabled(False)

        # load default data
        for key in self.profile_dict.keys():
            value = self.profiledata.get_default(self.profile_dict[key])
            if key in self.CB_list:
                key.setChecked(value)
            else:
                if key in self.color_list:
                    text = Mediator.color_data_to_str(value)
                    key.setText(text)
                else:
                    key.setValue(value)
        self.LstFlamingColor.clear()
        value = self.profiledata.get_default(Mediator.indicate_path)
        self.CBIndicate.setChecked(value)
        value = self.profiledata.get_default(Mediator.delay_path)
        self.SpinDelayBeforeOn.setValue(value)
        self.TxtAddProfile.clear()

    def move_up(self):
        """
        moves selected profile upper in order
        :return:
        """
        i = self.profiledata.order_changed(self.LstProfile.currentItem().text(), "Up")
        self.load_profile_list()
        self.LstProfile.setCurrentRow(i - 1)
        self.profile_clicked(self.LstProfile.currentItem())

    def move_down(self):
        """
        moves selected profile down in order
        :return:
        """
        i = self.profiledata.order_changed(self.LstProfile.currentItem().text(), "Down")
        self.load_profile_list()
        self.LstProfile.setCurrentRow(i + 1)
        self.profile_clicked(self.LstProfile.currentItem())

    def save_pressed(self):
        self.save(False)

    def save(self, save_as: bool):
        index = self.tabWidget.currentIndex()
        if save_as or not self.filename[index]:
            new_filename = QtWidgets.QFileDialog.getSaveFileName(self, local_table['save_file'][self.language], "")[0]
            if new_filename:
                self.filename[index] = new_filename
            else:
                return
        if index < 2:
            self.savefunctions[index](self.filename[index])
        else:
            self.profiledata.save_to_file(self.profiledata.data, self.filename[2])
        self.saved[index] = True
        self.change_tab_title(tabnames_global[index], self.tabWidget.currentIndex())
        if index == 1:
            self.BtnSave.setEnabled(False)
        self.statusfields[index].setText('%s %s' % (local_table['success_save'][self.language], self.filename[index]))

    def new_pressed(self):
        """
        clears all gui data for profile and auxleds
        :return:
        """
        i = self.tabWidget.currentIndex()
        if not self.saved[i]:
            msg = local_table['unsaved_warning'][self.language].split('@@@')
            quit_msg = msg[0] + tabnames_global[i] + msg[1]
            reply = QMessageBox.question(self, ' ', quit_msg, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.save_pressed()
        if i == 0:
            self.auxdata = AuxEffects()
            self.TrStructure.clear()
            self.LstGroup.clear()
            self.CBAuxList.clear()
            self.group_controls_clear()
            self.repeat_controls_disable()
            self.clear_repeat_controls()
            self.clear_step_controls()
            self.step_controls_disable()
            self.sequence_control_disable()
            self.BtnDeleteSeq.setEnabled(False)
            for led in self.leds_combo_list:
                led.setChecked(False)
                led.setEnabled(True)
        if i == 2:
            self.profiledata = Profiles()
            self.LstProfile.clear()
            self.LstProfile.clear()
            self.profile_control_disable()
            self.TxtAddProfile.clear()
            self.TxtAddProfile.setEnabled(True)
            self.BtnProfile.setEnabled(False)
            self.BtnDeleteProfile.setEnabled(False)
            self.BtnEditProfile.setEnabled(False)
            self.BtnUp.setEnabled(False)
            self.BtnDown.setEnabled(False)
            # file is saved now
        self.saved[i] = True
        self.filename[i] = ""
        self.statusfields[i].clear()
        self.change_tab_title(tabnames_global[i], i)

    def save_as_pressed(self):
        self.save(True)

    def save_all_pressed(self):
        """
        saves files from all three tabs
        :return:
        """
        index = self.tabWidget.currentIndex()
        for i in range(3):
            self.tabWidget.setCurrentIndex(i)
            self.save(False)
        self.tabWidget.setCurrentIndex(index)

    def open_pressed(self):
        index = self.tabWidget.currentIndex()
        openfilename = QtWidgets.QFileDialog.getOpenFileName(self, local_table['open_file'][self.language], "")[0]
        if openfilename:
            if "auxleds" in openfilename.lower():
                index = 0
            if "common" in openfilename.lower():
                index = 1
            if "profile" in openfilename.lower():
                index = 2
            if not self.saved[index]:
                msg = local_table['unsaved_warning'][self.language].split('@@@')
                save_msg = msg[0] + tabnames_global[index] + msg[1]
                reply = QMessageBox.question(self, 'Message', save_msg, QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.save_pressed()
            openfile = open(openfilename, encoding='utf-8')
            text = openfile.read()
            self.tabWidget.setCurrentIndex(index)
            gui_data, error, warning = self.openfunctions[index](text)
            if error:
                self.error_message("Could not load file % s: % s" % (openfilename, error))
            else:
                if warning:
                    if index == 1:
                        warning = warning.replace("Data error in", local_table['wrong_data_in'][self.language])
                        warning = warning.replace("Sequencer error in", local_table['seq_error'][self.language])
                        warning = warning.replace("LED Group error in", local_table['leg_group_error'][self.language])
                        warning = warning.replace("Step error in", local_table['step_error'][self.language])
                    self.statusfields[index].setText("Try to open %s...\n %s" % (openfilename, warning))
                else:
                    self.statusfields[index].setText("%s successfully loaded" % openfilename)
                self.loadfunctions[index](gui_data)
                self.filename[index] = openfilename
                self.saved[index] = True
                self.change_tab_title(tabnames_global[index], self.tabWidget.currentIndex())

    def open_all_pressed(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        dialog.exec_()
        openfiledir = dialog.selectedFiles()[0]
        if openfiledir:
            for i in range(3):
                filename = assistant.find_file(self.default_names[i], openfiledir)
                if filename:
                    filename = openfiledir + r'/' + filename
                    openfile = open(filename, encoding='utf-8')
                    text = openfile.read()
                    if not self.saved[i]:
                        save_msg = "You have unsaved %s settings. Do you want to save?" % tabnames_global[i]
                        reply = QMessageBox.question(self, 'Message', save_msg, QMessageBox.Yes, QMessageBox.No)
                        if reply == QMessageBox.Yes:
                            self.save_pressed()
                    gui_data, error, warning = self.openfunctions[i](text)
                    if error:
                        self.error_message("Could not load file % s: % s" % (filename, error))
                        self.statusfields[i].setText("Could not load file % s: % s" % (filename, error))
                    else:
                        if warning:
                            if i == 1:
                                warning = warning.replace("Data error in", local_table['wrong_data_in'][self.language])
                                warning = warning.replace("Sequencer error in", local_table['seq_error'][self.language])
                                warning = warning.replace("LED Group error in",
                                                          local_table['leg_group_error'][self.language])
                                warning = warning.replace("Step error in", local_table['step_error'][self.language])
                            self.statusfields[i].setText("Try to open %s...\n %s" % (filename, warning))
                        else:
                            self.statusfields[i].setText("%s successfully loaded" % filename)
                        self.loadfunctions[i](gui_data)
                        self.filename[i] = filename
                        self.saved[i] = True
                        self.change_tab_title(tabnames_global[i], i)
                else:
                    self.statusfields[i].setText("No %s file in %s directory" % (self.default_names[i], openfiledir))

    def load_auxleds(self, gui_data):
        """
        load auxleds data to tree
        :param gui_data: data
        :return:
        """
        self.auxdata.LedGroups = list()
        self.auxdata.Sequencers = list()
        for group in gui_data.LedGroups:
            self.auxdata.LedGroups.append(group)
        for sequencer in gui_data.Sequencers:
            self.auxdata.Sequencers.append(sequencer)
        self.load_data_to_tree()

    def load_common(self, gui_data):
        """
        load common data to tab
        :param gui_data: data
        :return:
        """
        self.load_common_data(gui_data)
        self.BtnSave.setEnabled(False)

    def load_profiles(self, gui_data):
        """
        Load profile data to tree
        :param gui_data: data
        :return:
        """
        self.profiledata.data = gui_data
        self.profiledata.order = list(gui_data.keys())
        self.load_profile_list()

    def error_message(self, text):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText(text)
        error.setWindowTitle(local_table['Error'][self.language])
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()

    def change_tab_title(self, filetype, index):
        if self.filename[index]:
            text = "%s - %s" % (filetype, self.filename[index].split(r'/')[-1])
        else:
            text = filetype
        if not self.saved[index]:
            text += "*"
        self.tabWidget.setTabText(index, text)

    def closeEvent(self, event):
        for i in range(3):
            if not self.saved[i]:
                msg = local_table['unsaved_warning'][self.language].split('@@@')
                quit_msg = msg[0] + tabnames_global[i] + msg[1]
                reply = QMessageBox.question(self, ' ', quit_msg, QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.save_pressed()
        event.accept()

    def auxled_help(self):
        """
        calls auxleds help with current language
        :return:
        """
        assistant.auxleds_help(self.language)

    def common_help(self):
        """
        calls common help with current language
        :return:
        """
        assistant.common_help(self.language)

    def profile_help(self):
        """
        calls profiles help with current language
        :return:
        """
        assistant.profile_help(self.language)

    def about_help(self):
        """
        calls About help with current language
        :return:
        """
        assistant.about_help(self.language)

    def font_folder_clicked(self):
        """
        selected folder with fonts to optimize
        :return:
        """
        current_folder = os.path.dirname(os.path.abspath(__file__))
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, local_table['Select folder'][self.language],
                                                            current_folder)
        if folder:
            self.font_folder = folder
            self.BtnOptimize.setEnabled(True)
            self.LblStatus.setText(local_table['Path to fonts'][self.language] + ': ' + folder)
            self.LineFontPath.setText(folder)
            
    def get_folder_from_field(self):
        """
        gets font path from field
        :return:
        """
        folder = self.LineFontPath.text()
        if os.path.exists(folder):
            self.font_folder= folder if os.path.isdir(folder) else os.path.split(folder)[0]
            self.BtnOptimize.setEnabled(True)
            self.LblStatus.setText(local_table['Path to fonts'][self.language] + ': ' + folder)

    def optimize_fonts(self):
        """
        change all fonts bitrait in folder to 44100
        :return:
        """
        path_to_converter = 'ffmpeg.exe' if os.path.exists('ffmpeg.exe') else \
            os.path.join(self.font_folder, 'ffmpeg.exe')
        if not os.path.exists(path_to_converter):
            assistant.ffmpeg_missing(self.language)
            return
        self.optimize_list, self.failed_list = wav_convertion.optimize_fonts(self.font_folder)
        self.current_file = 0
        if self.optimize_list:
            self.BtnOptimize.setEnabled(False)
            self.BtnSelectFont.setEnabled(False)
            self.LblStatus.setText(local_table["Optimization started"][self.language])
            for path in self.optimize_list:
                path = os.path.normpath(path)
                print(path)
                dst_base = os.path.splitext(path)[0]
                dst_base += '_resampled'
                dst = dst_base + '.wav'
                if os.path.exists(dst):
                    os.remove(dst)
                command, args = path_to_converter, ["-i", path,  '-ac', '1', '-ar', '44100', '-sample_fmt', 's16',
                                                    os.path.normpath(dst)]
                process = QtCore.QProcess(self)
                process.finished.connect(self.file_converted)
                process.start(command, args)
        else:
            self.LblStatus.setText(datetime.datetime.now().strftime('%H:%M') + ': ' +
                                   local_table['Fonts optimized'][self.language])
        wav_convertion.rename_hum(self.font_folder)

    def file_converted(self):
        """
        run when one of subprocesses are converted
        :return:
        """
        sender = self.sender()
        if sender.exitCode() != 0:
            print("Fail")
        self.current_file += 1
        self.LblStatus.setText(local_table['Convertation...'][self.language] + "%i/%i" % (self.current_file,
                                                                                          len(self.optimize_list)))
        if self.current_file >= len(self.optimize_list):
            failed_text = "\n" + local_table['Optimization failed for:'][self.language] + \
                          ', '.join(self.failed_list) if self.failed_list else ""
            self.LblStatus.setText(datetime.datetime.now().strftime('%H:%M') + ': ' +
                                   local_table['Fonts optimized'][self.language] + failed_text)
            wav_convertion.move_files(self.optimize_list)
            self.BtnSelectFont.setEnabled(True)
        return


@logger.catch
def main():
    initiate_exception_logging()
    app = QtWidgets.QApplication(sys.argv)
    window = ProfileEditor()
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
