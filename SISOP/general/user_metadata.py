import json
import os

from .utils import red_txt, make_directory, write_txt
from config.settings_base_dir import BASE_DIR


class UserPreference:
    """ class that contrl user preferences"""

    def __init__(self, user):
        self.user = user
        list_attr = ['__per_page_list_sist_inst', '__per_page_list_sol_proc', '__per_page_list_pago_lic']
        dict_preferences = self.__read_preferences()
        for attr in list_attr:
            setattr(self, attr, dict_preferences.get(attr, None))

    @ property
    def per_page_list_sist_inst(self):
        return getattr(self, '__per_page_list_sist_inst')

    @ per_page_list_sist_inst.setter
    def per_page_list_sist_inst(self, value):
        if value != getattr(self, '__per_page_list_sist_inst'):
            setattr(self, '__per_page_list_sist_inst', value)
            self.__make_directory_preference()
            self.__write_preference()

    @property
    def per_page_list_sol_proc(self):
        return getattr(self, '__per_page_list_sol_proc')

    @per_page_list_sol_proc.setter
    def per_page_list_sol_proc(self, value):
        setattr(self, '__per_page_list_sol_proc', value)
        self.__make_directory_preference()
        self.__write_preference()

    @property
    def per_page_list_pago_lic(self):
        return getattr(self, '__per_page_list_pago_lic')

    @per_page_list_pago_lic.setter
    def per_page_list_pago_lic(self, value):
        setattr(self, '__per_page_list_pago_lic', value)
        self.__make_directory_preference()
        self.__write_preference()

    def __read_preferences(self):
        """
        read the preferences of the user
        :return:
        """
        dirr = os.path.join(BASE_DIR, 'usuarios', self.user.usuario, 'preferencias', 'preferencias.txt')
        return {} if not red_txt(dirr, 1) else json.loads(red_txt(dirr, 1)[0])

    def __make_directory_preference(self):
        """
        make directory if not exist yet
        :return:
        """
        dir_directory = os.path.join(BASE_DIR, 'usuarios', self.user.usuario, 'preferencias')
        make_directory(dir_directory)

    def __write_preference(self):
        """
        write in file preference
        :return:
        """
        dir_file_preference = os.path.join(BASE_DIR, 'usuarios', self.user.usuario, 'preferencias', 'preferencias.txt')
        dict_aux = self.__dict__.copy()
        del dict_aux['user']
        write_txt(dir_file_preference, str(json.dumps(dict_aux)))

    @staticmethod
    def determine_value_preference(data_from_user, data_preference, data_system):
        """
        determine value
        1-datos from user if is in list of the system
        2- datos preference if is in list of the system
        else dato system
        :param data_from_user:
        :param data_preference:
        :param data_system:
        :return:
        """
        if data_from_user and data_from_user in data_system:
            return [data_from_user]
        if data_preference and data_preference in data_system:
            return [data_preference]
        return [data_system[0]]
