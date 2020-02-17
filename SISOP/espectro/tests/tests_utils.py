from django.test import TestCase
from espectro.utiles import pagina_valida


class UtilsTest(TestCase):
    """
    text for utils methods
    """

    def test_pagina_valida(self):
        """
        test gor pagina_valida
        :return:
        """
        cases = [{'num_page': 1, 'elem_per_page': 10, 'cant_elem': 20, 'out': 1},
                 {'num_page': 2, 'elem_per_page': 10, 'cant_elem': 20, 'out': 2},
                 {'num_page': 2, 'elem_per_page': 10, 'cant_elem': 10, 'out': 1},
                 {'num_page': 7, 'elem_per_page': 3, 'cant_elem': 20, 'out': 7},
                 {'num_page': 8, 'elem_per_page': 3, 'cant_elem': 20, 'out': 7},
                 {'num_page': 1, 'elem_per_page': 10, 'cant_elem': 20, 'out': 1},
                 {'num_page': 5, 'elem_per_page': 10, 'cant_elem': 20, 'out': 2}]

        for case in cases:
            self.assertIs(pagina_valida(case['num_page'], case['elem_per_page'], case['cant_elem']), case['out'])
