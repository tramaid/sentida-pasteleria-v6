import pytest

from ayuda_decoradas import armar
from reglas import CEL, CONTRASTE


@pytest.mark.parametrize("w,h,kw", [(390, 844, CEL), (360, 740, CEL), (1440, 900, {})])
def test_primer_frame(abrir, w, h, kw):
    pg = abrir(w, h, **kw)
    for sel in (".ticket-portada h1", "#empezar"):
        b = pg.locator(sel).bounding_box()
        assert b["y"] >= 0 and b["y"] + b["height"] <= h, sel


def test_teclado_recorre_todo_con_foco_visible(abrir):
    pg = abrir()
    visitados = 0
    for _ in range(80):
        pg.keyboard.press("Tab")
        pg.wait_for_timeout(600)
        info = pg.evaluate("""(() => {
            const e = document.activeElement;
            if (e === document.body) return null;
            const r = e.getBoundingClientRect();
            return {que: (e.id || e.name || e.textContent || '').trim().slice(0, 24),
                    visible: r.width > 0 && r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth};
        })()""")
        if info is None:
            break
        assert info["visible"], info
        visitados += 1
    assert visitados > 15  # un paso por vez: solo se recorre el paso actual


@pytest.mark.parametrize("w,h,kw", [(390, 844, CEL), (1440, 900, {})])
def test_contraste_aa_con_una_opcion_elegida(abrir, w, h, kw):
    pg = abrir(w, h, **kw)
    armar(pg, hasta=2)
    pg.check("input[name=tamano][value=mediana]")
    pg.wait_for_timeout(400)  # la opción elegida tiene una transición de 0,2 s
    assert pg.evaluate(CONTRASTE) == []
