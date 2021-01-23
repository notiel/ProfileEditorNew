import wave
import os
from typing import List, Tuple


def optimize_fonts(font_folder: str) -> Tuple[List[str], List[str]]:
    """
    change all fonts bitrait in folder to 44100
    :return:
    """
    optimize_list: List[str] = list()
    failed_list: List[str] = list()
    add_files_to_convert_list(font_folder, optimize_list, failed_list)
    for folder in [filename for filename in os.listdir(font_folder)
                   if os.path.isdir(os.path.join(font_folder, filename))]:
        full_path = os.path.join(font_folder, folder)
        add_files_to_convert_list(os.path.join(full_path), optimize_list, failed_list)
        for subfolder in [filename for filename in os.listdir(full_path) if
                          os.path.isdir(os.path.join(full_path, filename))]:
            add_files_to_convert_list(os.path.join(full_path, subfolder), optimize_list, failed_list)
    return optimize_list, failed_list


def add_files_to_convert_list(path: str, optimize_list: List[str], failed_list: List[str]):
    """
    adds files in folder with right extension and wrong bitrate to convert list
    :return:
    """
    if path.lower().endswith('settings'):
        return
    for filename in os.listdir(path):
        if os.path.splitext(filename)[1] == ".wav":
            try:
                with wave.open(os.path.join(path, filename), mode='rb') as sound:
                    if sound.getsampwidth() != 2 or sound.getframerate() != 44100:
                        optimize_list.append(os.path.join(path, filename))
            except (wave.Error, EOFError):
                failed_list.append(os.path.join(path, filename))


def move_files(optimized_list: List[str]):
    """
    moves resamples files on the place of old
    :param optimized_list:
    :return:
    """
    for filename in optimized_list:
        if os.path.exists(filename):
            try:
                os.remove(filename)
                os.rename(os.path.splitext(filename)[0] +  '_resampled' + '.wav', filename)
            except OSError:
                pass


def rename_hum(font_folder: str):
    """
    if we have hum1.wav file in root folder of font, we rename it to hum.wav
    :param font_folder:
    :return:
    """
    for filename in os.listdir(font_folder):
        if filename.lower() == 'hum1.wav':
            os.rename(os.path.join(font_folder, filename), os.path.join(font_folder,'hum.wav'))
    for folder in [path for path in os.listdir(font_folder) if os.path.isdir(os.path.join(font_folder, path))]:
        for filename in os.listdir(os.path.join(font_folder, folder)):
            if filename.lower() == 'hum1.wav':
                os.rename(os.path.join(font_folder, folder, filename), os.path.join(font_folder, folder, 'hum.wav'))
