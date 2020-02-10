from typing import Sequence, Tuple, Optional, Any, List, Callable, Dict, Union
import pprint
import IniToJson
import profilechecker
from collections import OrderedDict

default_profile = OrderedDict({'AfterWake': {},
                               'PowerOn': {'Blade': {'Speed': 144}},
                               'WorkingMode': {'Color': [0, 255, 0], 'Flaming': 0, 'FlickeringAlways': 0},
                               'PowerOff': {'Blade': {'Speed': 144, 'MoveForward': 0}},
                               'Flaming': {'Size': {'Min': 2, 'Max': 9}, 'Speed': {'Min': 12, 'Max': 27},
                                           'Delay_ms': {'Min': 54, 'Max': 180},
                                           'Colors': ['random']},
                               'Flickering': {'Time': {'Min': 90, 'Max': 360}, 'Brightness': {'Min': 50, 'Max': 100}},
                               'Blaster': {'Color': [255, 0, 0], 'Duration_ms': 720, 'SizePix': 7},
                               'Clash': {'Color': [255, 0, 0], 'Duration_ms': 720, 'SizePix': 11},
                               'Stab': {'Color': [255, 0, 0], 'Duration_ms': 720, 'SizePix': 11},
                               'Lockup': {'Flicker': {'Color': [255, 0, 0], 'Time': {'Min': 45, 'Max': 80},
                                                      'Brightness': {'Min': 50, 'Max': 100}},
                                          'Flashes': {'Period': {'Min': 15, 'Max': 25}, 'Color': [255, 0, 0],
                                                      'Duration_ms': 50,
                                                      'SizePix': 7}},
                               'Blade2': {
                                   'IndicateBlasterClashLockup': 1,
                                   'WorkingMode': {'Color': [0, 255, 0]},
                                   'Flaming': {'AlwaysOn': 0, 'Size': {'Min': 2, 'Max': 9},
                                               'Speed': {'Min': 12, 'Max': 27},
                                               'Delay_ms': {'Min': 54, 'Max': 180},
                                               'Colors': ['random']},
                                   'Flickering': {'AlwaysOn': 0, 'Time': {'Min': 90, 'Max': 360},
                                                  'Brightness': {'Min': 50, 'Max': 100}},
                                   'DelayBeforeOn': 200}})

aux_key = 'AuxLeds'

tabulation_list = ['Speed', 'Delay_ms', 'Colors', 'Brightness', 'Flashes', 'Color']


class Profiles:

    def __init__(self):
        self.data = OrderedDict()
        self.order = list()

    def get_profiles_list(self):
        """
        returns list of profile keys
        :return:
        """
        return self.data.keys()

    def add_profile(self, name: str):
        """
        adds profile with given name and default values
        :param name: name of profile
        :return:
        """
        self.data[name] = {'AfterWake': {},
                           'PowerOn': {'Blade': {'Speed': 144}},
                           'WorkingMode': {'Color': [0, 0, 255], 'Flaming': 0, 'FlickeringAlways': 0},
                           'PowerOff': {'Blade': {'Speed': 144, 'MoveForward': 0}},
                           'Flaming': {'Size': {'Min': 2, 'Max': 9}, 'Speed': {'Min': 12, 'Max': 27},
                                       'Delay_ms': {'Min': 54, 'Max': 180},
                                       'Colors': ['random']},
                           'Flickering': {'Time': {'Min': 90, 'Max': 360}, 'Brightness': {'Min': 50, 'Max': 100}},
                           'Blaster': {'Color': [255, 0, 0], 'Duration_ms': 720, 'SizePix': 7},
                           'Clash': {'Color': [255, 0, 0], 'Duration_ms': 720, 'SizePix': 11},
                           'Stab': {'Color': [255, 0, 0], 'Duration_ms': 720, 'SizePix': 11},
                           'Lockup': {'Flicker': {'Color': [255, 0, 0], 'Time': {'Min': 45, 'Max': 80},
                                                  'Brightness': {'Min': 50, 'Max': 100}},
                                      'Flashes': {'Period': {'Min': 15, 'Max': 25}, 'Color': [255, 0, 0],
                                                  'Duration_ms': 50,
                                                  'SizePix': 7}},
                           'Blade2': {
                               'IndicateBlasterClashLockup': 1,
                               'WorkingMode': {'Color': [0, 0, 255]},
                               'Flaming': {'AlwaysOn': 0, 'Size': {'Min': 2, 'Max': 9},
                                           'Speed': {'Min': 12, 'Max': 27},
                                           'Delay_ms': {'Min': 54, 'Max': 180},
                                           'Colors': ['random']},
                               'Flickering': {'AlwaysOn': 0, 'Time': {'Min': 90, 'Max': 360},
                                              'Brightness': {'Min': 50, 'Max': 100}},
                               'DelayBeforeOn': 200}
                           }
        self.order.append(name)

    def delete_profile(self, name: str):
        """
        deletes profile by key
        :param name: name of profile
        :return:
        """
        self.data.pop(name)
        self.order.remove(name)

    def get_default(self, path: List[str]) -> Dict[str, Any]:
        """
        gets default value for key path
        :param path: pat of keys
        :return: default value
        """
        data = default_profile
        for key in path:
            data = data[key]
        return data

    def get_value(self, path: List[str], profile: str) -> Dict[str, Any]:
        """
        gets value of field configured with pat for profile
        :param path: path of keys
        :param profile: profile key
        :return: value
        """
        data = self.data[profile]
        for key in path:
            data = data[key]
        return data

    def update_value(self, path: List[str], profile: str, value: object):
        """
        updates field for given keys in given profile, makes in given value
        :param path: key path
        :param profile: profile
        :param value: given new value
        :return:
        """
        try:
            data = self.data[profile]
            for key in path[:-1]:
                data = data[key]
            data[path[-1]] = value
        except (KeyError, IndexError):
            print("no such key or keypath is empty")  # to do logging

    def save_color(self, path: Sequence[str], color: Union[Sequence[int], str], profile: str):
        """
        saves color given as a list of rgb components to path in profiledata dict
        :param path: path of keys
        :param color: rgb components
        :param profile: current profile
        :return:
        """
        try:
            data = self.data[profile]
            for key in path[:-1]:
                data = data[key]
            data[path[-1]].append(color)
        except (IndexError, TypeError, ValueError):
            print("wrong keypath or color data")  # to do logging

    def get_colors(self, path: List[str], profile: str) -> Optional[List[str]]:
        """
        gets colors list for profile and path
        :param path: list of keys
        :param profile: current profile
        :return: list of colors
        """
        try:
            data = self.data[profile]
            for key in path:
                data = data[key]
            return data
        except KeyError:
            print("Wrong keys used")  # to do logging
            return None

    def delete_color(self, path: List[int], color: List[int], profile: str):
        """
        deletes color given as a list of rgb components from path in profiledata dict
        :param path: path of keys
        :param color: rgb components
        :param profile: current profile
        :return:
        """
        try:
            data = self.data[profile]
            for key in path[:-1]:
                data = data[key]
            data[path[-1]].remove(color)
        except (IndexError, TypeError, ValueError):
            print("wrong keypath or color data")  # to do logging

    def save_aux(self, aux: str, effect: str, profile: str):
        """
        save aux effect to effect in profile
        :param aux:
        :param effect:
        :param profile:
        :return:
        """
        data = self.data[profile][effect]
        if aux_key not in data.keys():
            data[aux_key] = [aux]
        else:
            data[aux_key].append(aux)

    def delete_aux(self, aux: str, effect: str, profile: str):
        try:
            data = self.data[profile][effect]
            data[aux_key].remove(aux)
            if not data[aux_key]:
                data.pop(aux_key)
        except (IndexError, KeyError):
            print("Incorrects key or aux name")  # to do logging

    def get_aux_effects(self, effect: str, profile: str):
        """
        gets list of auxeffects for selected profile and effect
        :param effect: effect to get aux effects for
        :param profile: profile get auxeffects for
        :return:
        """
        data = self.data
        data = data[profile][effect]
        return data.get(aux_key, [])

    def change_key_order(self, old: str, new: str):
        """
        removes old key, adds new key to profile data dict, renames key in order list
        :param old: old key
        :param new: new key
        :return:
        """
        real_key = ""
        for key in self.data.keys():
            if key.lower() == old.lower():
                real_key = old
        if real_key == "":
            return "No % s profile" % old, -1
        self.data[new] = self.data[real_key]
        self.data.pop(old)
        i = self.order.index(old)
        self.order[i] = new
        return "", i

    def order_changed(self, key: str, direction: str):
        """
        changes key order in order list, moves selected key up or down
        :param key: selected profile name
        :param direction: up or down
        :return:
        """
        i = self.order.index(key)
        self.order.remove(key)
        if direction == "Up":
            self.order.insert(i - 1, key)
        if direction == "Down":
            self.order.insert(i + 1, key)
        return i

    def save_to_file(self, data, filename: str):
        """
        saves to filename as pseudo-json (no quotes)
        :param data: data to save
        :param filename: name of file to save
        :return:
        """
        # text: str = ""
        # for key in self.data.keys():
        #    inner: str = pprint.pformat(self.data[key], indent=0)
        #    inner_draft: List[str] = inner.split('\n')
        #    inner = ""
        #    for line in inner_draft:
        #        inner += "\t"+line+'\n'
        #    text += "%s:\n %s, " % (key, inner)
        pprint.sorted = lambda x, key=None: x
        new_data = {key: data[key] for key in self.order}
        text = pprint.pformat(new_data)
        text = text.replace(r"'", "")
        text = text[1:-1]
        f = open(filename, "w", encoding="utf-8")
        f.write(text)

    @staticmethod
    def get_default_value(key_list: List[str]) -> Dict[str, Any]:
        """
        get value from defaults using key path
        :param key_list: path of keys
        :return: value
        """
        temp_data = default_profile
        for key in key_list:
            temp_data = temp_data[key]
        return temp_data

    @staticmethod
    def check_section(new_data: dict, check_function: Callable, param: str, profile: str) -> str:
        """
        checks section of loaded from text data
        :param new_data: data
        :param check_function: function to check with
        :param param: key of section
        :param profile: name of profile for error
        :return: warning text
        """
        checker = profilechecker.ProfileChecker()
        if check_function.__name__ == "check_flaming":
            e = check_function(new_data, ['size', 'speed', 'delay_ms', 'colors', 'auxleds'])
        elif check_function.__name__ == 'check_flickering':
            e = check_function(new_data, ['time', 'brightness', 'auxleds'])
        elif check_function.__name__ == 'check_movement':
            e = check_function(new_data, param)
        else:
            e = check_function(new_data)
        if e:
            section_key = checker.get_key(new_data, param)
            if section_key:
                new_data.pop(section_key)
            return "ERROR! " + profile + ": " + param + ': ' + e + " profile not loaded;\n"
        return ""

    @staticmethod
    def load_data_from_text(text: str):
        """
        loads data from texts
        :param text: text with data
        :return:
        """
        new_data, error = IniToJson.get_json(text)
        if error or new_data is None:
            return None, error, ""
        if not isinstance(new_data, dict):
            return None, "Wrong profile data format", ""
        new_data = OrderedDict(new_data)
        warning = ""
        wrong_profile_keys = list()
        checker = profilechecker.ProfileChecker()
        for profile in new_data.keys():
            if not isinstance(new_data[profile], dict):
                warning += ("Wrong settings format for profile %s, profile not loaded\n" % profile)
                wrong_profile_keys.append(profile)
                continue
            w, wrong_keys = profilechecker.check_keys(new_data[profile],
                                                      [key.lower() for key in default_profile.keys()])
            if w:
                warning += profile + ': ' + w + '\n'
            for key in wrong_keys:
                new_data[profile].pop(key)
            warning += Profiles.check_section(new_data[profile], checker.check_afterwake, "afterwake", profile)
            warning += Profiles.check_section(new_data[profile], checker.check_poweron, "poweron", profile)
            warning += Profiles.check_section(new_data[profile], checker.check_workingmode, "workingmode", profile)
            warning += Profiles.check_section(new_data[profile], checker.check_poweroff, "powefoff", profile)
            warning += Profiles.check_section(new_data[profile], checker.check_flaming, "flaming", profile)
            warning += Profiles.check_section(new_data[profile], checker.check_flickering, "flickering", profile)
            warning += Profiles.check_section(new_data[profile], checker.check_movement, "blaster", profile)
            warning += Profiles.check_section(new_data[profile], checker.check_movement, "stab", profile)
            warning += Profiles.check_section(new_data[profile], checker.check_movement, "clash", profile)
            warning += Profiles.check_section(new_data[profile], checker.check_lockup, "lockup", profile)
            warning += Profiles.check_section(new_data[profile], checker.check_blade2, "lockup", profile)

            for key in default_profile.keys():
                if key.lower() not in [key.lower() for key in new_data[profile].keys()]:
                    wrong_profile_keys.append(profile)

        for key in set(wrong_profile_keys):
            new_data.pop(key)
        return new_data, "", warning
