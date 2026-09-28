import pytest

# Las direcciones viejas siguen andando: pueden estar compartidas en Instagram o
# en un WhatsApp. Se conservan la búsqueda (?…) y el # (el paso de la comanda).
VIEJAS = [
    ("comanda/?x=1#inicio", "/arma-tu-torta/?x=1#inicio"),
    ("decoradas/?x=1#inicio", "/arma-tu-torta/?x=1#inicio"),
    ("antojos/", "/pasteleria/"),
]


@pytest.mark.parametrize("vieja,nueva", VIEJAS)
def test_la_direccion_vieja_redirige(abrir, vieja, nueva):
    # #inicio no es un paso: pasos.js no lo toca, así se ve que el # llega entero.
    pg = abrir(pagina=vieja)
    pg.wait_for_url(lambda u: u.endswith(nueva))
    assert pg.errores == []


@pytest.mark.parametrize("vieja,nueva", [("comanda/", "/arma-tu-torta/"), ("decoradas/", "/arma-tu-torta/"),
                                         ("antojos/", "/pasteleria/")])
def test_la_redireccion_funciona_sin_javascript(abrir, vieja, nueva):
    pg = abrir(pagina=vieja, java_script_enabled=False)
    pg.wait_for_url(lambda u: u.endswith(nueva))
