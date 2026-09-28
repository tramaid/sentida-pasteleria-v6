import pytest

PAGINAS = ["", "arma-tu-torta/", "tortas/", "pasteleria/", "nosotras/"]


@pytest.mark.parametrize("pagina", PAGINAS)
def test_los_tokens_nuevos(abrir, pagina):
    pg = abrir(pagina=pagina)
    raiz = "getComputedStyle(document.documentElement)"
    assert pg.evaluate(f"{raiz}.getPropertyValue('--celeste-filete').trim()") == "#7EAFD6"
    assert pg.evaluate(f"{raiz}.getPropertyValue('--cab').trim()") == "88px"
    assert pg.evaluate("getComputedStyle(document.querySelector('.cab')).height") == "88px"


def test_los_titulos_van_en_peso_400(abrir):
    pg = abrir(pagina="tortas/")
    assert pg.evaluate("getComputedStyle(document.querySelector('h1.display')).fontWeight") == "400"
