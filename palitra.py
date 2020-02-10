from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QDialog
from colorpicker import Ui_SelectColor
from typing import Tuple, List, Any
from localtable import local_table


class ColorDialog(QtWidgets.QDialog, Ui_SelectColor):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.language = 'en'
        self.palitra = QtGui.QPixmap(":/palette/palette.png")
        self.LblColor.show()
        self.TxtColor.setAutoFillBackground(True)
        self.ColorSlider.valueChanged.connect(self.ValueChange)
        self.BrightnessSlider.valueChanged.connect(self.ValueChange)
        self.SuturationSlider.valueChanged.connect(self.ValueChange)
        self.image = self.palitra.toImage()
        self.SuturationSlider.valueChanged['int'].connect(self.ChangeBrightnessLabel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.rgb = [255, 0, 0]
        self.LanguageInit()

    def LanguageInit(self):
        """
        inits language data
        :return:
        """
        lang = self.language
        self.setWindowTitle(local_table['Select Color'][lang])
        if lang != 'en':
            labels = [self.LblColorSelected, self.LblBrightness, self.LblSaturation]
            for label in labels:
                current = label.text().split(':')[0]
                label.setText(local_table[current][lang]+':')
            self.LblBrightness.setText(self.LblBrightness.text()+  str(self.SuturationSlider.value()))
            self.groupBox.setTitle(local_table['Select Color'][lang])


    def Color(self):
        """
        returns color label and rgb parts
        :return:
        """
        return self.LblColor.text(), self.rgb

    def SetColor(self, color: str):
        """
        get shifted color
        :param color: color string
        :return:
        """
        self.LblColor.setText(color)
        self.mColor = color.split(",")
        self.mColor = [float(x) for x in self.mColor]

        # get max value and divide at 255 to get brightness
        s_color = (max(float(self.mColor[0]), max(self.mColor[1], self.mColor[2]))/255.0)*100.0
        self.SuturationSlider.setValue(round(s_color))
        self.mColor = [(x * 100)/s_color for x in self.mColor]

        # get min value for saturation
        b_color = min(self.mColor[0], min(self.mColor[1], self.mColor[2]))
        self.BrightnessSlider.setValue(round(b_color))

        # get max value index
        max_ind = self.mColor.index(max(self.mColor))
        # other decrease by saturation
        self.mColor = [x - b_color if i != max_ind else x for (i, x) in enumerate(self.mColor)]

        # get color
        if round(self.mColor[1]) == 255:
            h_color = 510 - self.mColor[0] + self.mColor[2]
        elif round(self.mColor[2]) == 255:
            h_color = 1020 + self.mColor[0] - self.mColor[1]
        else:
            h_color = (1530 + self.mColor[1] - self.mColor[2]) % 1530
        self.ColorSlider.setValue(h_color)

    def ValueChange(self):
        """
        change color value
        :return:
        """
        hValue = self.ColorSlider.value()
        bValue = self.BrightnessSlider.value()
        sValue = self.SuturationSlider.value()
        Color = [0, 0, 0]
        # print(hValue)
        if hValue < 255:
            Color[0] = 255
            Color[1] = hValue
        if 254 < hValue < 510:
            Color[0] = 255 - (hValue % 255)
            Color[1] = 255
        if 509 < hValue < 765:
            Color[1] = 255
            Color[2] = hValue % 255
        if 764 < hValue < 1020:
            Color[1] = 255 - (hValue % 255)
            Color[2] = 255
        if 1019 < hValue < 1275:
            Color[0] = hValue % 255
            Color[2] = 255
        if 1274 < hValue < 1530:
            Color[0] = 255
            Color[2] = 255 - hValue % 255
        if 1530 == hValue:
            Color[0] = 255

        # get text
        Color = [255 if x + bValue >= 256 else x + bValue for x in Color]
        Color = [(x*sValue)/100 for x in Color]

        # show
        c = self.image.pixel(1023 if hValue == 1530 else hValue*1024/1530, 0)
        cpix = QtGui.QColor(c).getRgbF()
        cpix = [int(x * 255) for x in cpix]
        cpix = [255 if x + bValue >= 256 else x + bValue for x in cpix]
        cpix[3] = (cpix[3] * sValue) / 100

        # for dinamic
        self.LblColor.setText('%d, %d, %d' % (Color[0], Color[1], Color[2]))
        # modified color with shifted palette
        self.TxtColor.setStyleSheet(
            "QWidget{ background-color : rgba(%d, %d, %d, %d)}" % (cpix[0], cpix[1], cpix[2], cpix[3]))
        self.rgb = [cpix[0], cpix[1], cpix[2], cpix[3]]

    def ChangeBrightnessLabel(self):
        """
        adds to Brightness label current brightness value
        :return:
        """
        brightness = int(self.SuturationSlider.value())
        self.LblBrightness.setText("%s: %i" % (local_table['Brightness'][self.language], brightness))

    @staticmethod
    def getColor(color_main, lang) -> Tuple[Tuple[Any, List[int]], bool]:
        """
        gets shifted color
        :param color_main: color in rgb without shift
        :param lang: form language
        :return:
        """
        dialog = ColorDialog()
        dialog.language = lang
        dialog.LanguageInit()
        dialog.SetColor(color_main)
        result = dialog.exec_()
        color = dialog.Color()
        return color, result == QDialog.Accepted

    @staticmethod
    def getColornoWindow(color_main: str) -> Tuple[Tuple[Any, List[int]], bool]:
        dialog = ColorDialog()
        dialog.SetColor(color_main)
        color = dialog.Color()
        return color, True