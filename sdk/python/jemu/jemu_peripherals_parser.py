"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
import os
import json


class JemuPeripheralsParser:
    __peripherals_json_path = None

    def __init__(self, peripherals_json_path):
        self.__peripherals_json_path = peripherals_json_path

    def get_buttons(self):
        buttons_list = []

        if not os.path.isfile(self.__peripherals_json_path):
            raise Exception(self.__peripherals_json_path + ' is not found')
        elif not os.access(self.__peripherals_json_path, os.R_OK):
            raise Exception(self.__peripherals_json_path + ' is not readable')
        else:
            with open(self.__peripherals_json_path) as peripherals_json_file:
                peripherals_json = json.load(peripherals_json_file)

                for peripheral in peripherals_json["Peripherals"]:

                    if "Button" == peripheral["class"]:
                        buttons_list.append({"name": peripheral["name"], "id": peripheral["id"]})

            return buttons_list
