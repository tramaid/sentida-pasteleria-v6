import pytest

from reglas import CEL, CELESTE_EN_TEXTO, CONTRASTE, ITALICAS, TAMANOS, TEXTO_CHICO

PAGINAS = ["", "arma-tu-torta/", "tortas/", "pasteleria/", "nosotras/"]
VISIBLE = """(() => {
    const e = document.activeElement;
    if (e === document.body) return null;
    const r = e.getBoundingClientRect();
    return {que: (e.id || e.textContent || '').trim().slice(0, 24),
            visible: r.width > 0 && r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth};
})()"""


@pytest.mark.parametrize("pagina", PAGINAS)
@pytest.mark.parametrize("w,h,kw", TAMANOS)
def test_sin_desborde_ni_reglas_rotas(abrir, pagina, w, h, kw):
    pg = abrir(w, h, pagina=pagina, **kw)
    assert pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth") == 0
    assert pg.evaluate(TEXTO_CHICO) == []
    assert pg.evaluate(CELESTE_EN_TEXTO) == []
    assert pg.evaluate(ITALICAS) == 0
    assert pg.errores == []


@pytest.mark.parametrize("pagina", PAGINAS)
@pytest.mark.parametrize("w,h,kw", [(390, 844, CEL), (1440, 900, {})])
def test_contraste_aa(abrir, pagina, w, h, kw):
    pg = abrir(w, h, pagina=pagina, **kw)
    pg.wait_for_timeout(400)
    assert pg.evaluate(CONTRASTE) == []


@pytest.mark.parametrize("pagina", PAGINAS)
def test_sin_javascript_se_ve_y_no_desborda(abrir, pagina):
    pg = abrir(390, 844, pagina=pagina, java_script_enabled=False, **CEL)
    assert pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth") == 0
    assert pg.locator("main").is_visible()


@pytest.mark.parametrize("pagina", PAGINAS)
def test_la_misma_cabecera(abrir, sitio, pagina):
    pg = abrir(pagina=pagina)
    assert pg.eval_on_selector_all(".cab-nav a", "as => as.map(a => a.href)") == \
        [sitio + "tortas/", sitio + "arma-tu-torta/", sitio + "pasteleria/", sitio + "nosotras/"]
    assert pg.eval_on_selector_all(".cab-nav a", "as => as.map(a => a.textContent)") == \
        ["Nuestras tortas", "Armá tu torta", "Pastelería", "Nosotras"]
    assert pg.locator(".cab [data-mi-pedido]").count() == 1


@pytest.mark.parametrize("pagina", PAGINAS)
@pytest.mark.parametrize("w", [1100, 1280, 1440, 1920])
def test_la_cabecera_no_se_pisa(abrir, pagina, w):
    pg = abrir(w, 900, pagina=pagina)
    r = pg.evaluate("""(() => {
        const vis = [...document.querySelectorAll('.cab-nav a')].filter(a => a.getClientRects().length);
        const m = document.querySelector('.cab-marca').getBoundingClientRect();
        const p = document.querySelector('.cab [data-mi-pedido]').getBoundingClientRect();
        return {n: vis.length, der: Math.max(...vis.map(a => a.getBoundingClientRect().right)),
                marcaIzq: m.left, marcaDer: m.right, pedidoIzq: p.left};
    })()""")
    assert r["n"] == (4 if w >= 1280 else 3)
    assert r["der"] < r["marcaIzq"]
    assert r["marcaDer"] < r["pedidoIzq"]


@pytest.mark.parametrize("pagina", PAGINAS)
@pytest.mark.parametrize("w,h", [(360, 740), (1000, 800)])
def test_en_angosto_entran_el_logo_mi_pedido_y_el_menu(abrir, pagina, w, h):
    pg = abrir(w, h, pagina=pagina, **(CEL if w < 900 else {}))
    assert pg.is_hidden(".cab-nav")
    for sel in (".cab-marca", ".cab [data-mi-pedido]", ".menu summary"):
        b = pg.locator(sel).bounding_box()
        assert b and b["x"] >= 0 and b["x"] + b["width"] <= w, sel


@pytest.mark.parametrize("pagina", ["tortas/", "pasteleria/"])
def test_teclado_en_la_tienda(abrir, pagina):
    pg = abrir(pagina=pagina, reduced_motion="reduce")
    visitados = 0
    for _ in range(120):
        pg.keyboard.press("Tab")
        pg.wait_for_timeout(50)
        info = pg.evaluate(VISIBLE)
        if info is None:
            break
        assert info["visible"], info
        visitados += 1
    assert visitados > 20
