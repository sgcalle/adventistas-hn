# -*- coding: utf-8 -*-

import math

class NumberToTextConverter:

    def _unidades(self, num):
        unidades = {
            1: "UN",
            2: "DOS",
            3: "TRES",
            4: "CUATRO",
            5: "CINCO",
            6: "SEIS",
            7: "SIETE",
            8: "OCHO",
            9: "NUEVE",
        }
        return unidades.get(num, "")
    
    def _decenas(self, num):

        decena = math.floor(num / 10)
        unidad = num - (decena * 10)

        numero = ""

        if decena == 1:
            numero = {
                0: "DIEZ",
                1: "ONCE",
                2: "DOCE",
                3: "TRECE",
                4: "CATORCE",
                5: "QUINCE",
            }.get(unidad, "DIECI" + self._unidades(unidad))
        elif decena == 2:
            numero = {
                0: "VEINTE"
            }.get(unidad, "VEINTI" + self._unidades(unidad))
        else:
            if decena > 0:
                decena_str = {
                    3: "TREINTA",
                    4: "CUARENTA",
                    5: "CINCUENTA",
                    6: "SESENTA",
                    7: "SETENTA",
                    8: "OCHENTA",
                    9: "NOVENTA",
                }.get(decena, "UNKNOWN")
                numero = "%s Y %s" % (decena_str, self._unidades(unidad))
            else:
                numero = self._unidades(unidad)

        return numero
    
    def _centenas(self, num):
        centena = math.floor(num / 100)
        decena = num - (centena * 100)

        numero = ""

        if centena == 1:
            if decenas > 0:
                numero = "CIENTO %s" % self._decenas(decena) 
            else:
                numero = "CIEN"
        else:
            centena_str = {
                2: "DOSCIENTOS",
                3: "TRECIENTOS",
                4: "CUATROCIENTOS",
                5: "QUINIENTOS",
                6: "SEISCIENTOS",
                7: "SETECIENTOS",
                8: "OCHOCIENTOS",
                9: "NOVECIENTOS",
            }.get(centena, "UNKNOWN")

            numero = "%s %s" % (centena_str, self._decenas(decena))

        return numero
    
    def _miles(self, num):
        pass

# Testing
if __name__ == "__main__":
    converter = NumberToTextConverter()
    print(converter._centenas(999))