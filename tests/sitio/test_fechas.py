from fechas import FUTURA, FUTURA_TEXTO


def test_la_fecha_de_las_pruebas_es_futura_y_se_lee_igual_que_en_la_pagina(abrir):
    # Las pruebas no pueden depender del día en que se corren: un borrador con
    # fecha pasada se descarta, y el pedido no deja mandar una fecha pasada.
    pg = abrir(pagina="arma-tu-torta/")
    assert FUTURA > pg.evaluate("Sentida.hoyISO()")
    assert pg.evaluate(f"Sentida.fecha('{FUTURA}')") == FUTURA_TEXTO
