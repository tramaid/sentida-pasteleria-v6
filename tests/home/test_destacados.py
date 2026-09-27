import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "herramientas"))
import generar_tienda as G  # noqa: E402

DATOS = json.loads((RAIZ / "datos" / "catalogo.json").read_text(encoding="utf-8"))
DESTACADOS = [p["slug"] for p in DATOS["productos"] if p.get("destacado") and p.get("visible", True)]


def test_la_home_muestra_los_destacados_del_catalogo(abrir):
    pg = abrir()
    assert len(DESTACADOS) == 6
    assert pg.eval_on_selector_all("#destacados [data-producto]", "ls => ls.map(l => l.dataset.producto)") == DESTACADOS
    assert pg.text_content("#destacados .producto-precio") == "Precio a consultar"
    assert pg.text_content("#destacados .producto-meta span:last-child") == "01 / 06"


def test_el_mas_suma_al_mismo_pedido_de_la_tienda(abrir, sitio):
    pg = abrir()
    primero = f'#destacados [data-producto="{DESTACADOS[0]}"]'
    pg.click(primero + " .producto-agregar")
    assert pg.text_content(".cab .mi-pedido-n") == "1"
    pg.goto(sitio + "tortas/")
    pg.wait_for_load_state("networkidle")
    assert pg.text_content(".cab .mi-pedido-n") == "1"
    assert pg.text_content(f'[data-producto="{DESTACADOS[0]}"] .contador output') == "1"


def test_sin_javascript_cada_destacado_se_pide_por_whatsapp(abrir):
    pg = abrir(java_script_enabled=False)
    assert pg.locator("#destacados .producto-wa").first.is_visible()
    assert pg.locator("#destacados .producto-agregar").first.is_hidden()


def test_el_generador_saltea_los_ocultos_y_resuelve_la_falta_de_foto():
    datos = {"tipos": {}, "productos": [
        {"slug": "oculto", "nombre": "Oculto", "seccion": "tortas", "destacado": True, "visible": False},
        {"slug": "sin-foto-de-prueba", "nombre": "Sin foto", "seccion": "tortas", "destacado": True},
    ]}
    html = G.destacados(datos)
    assert 'data-producto="oculto"' not in html
    assert 'data-producto="sin-foto-de-prueba"' in html
    assert "sin-foto" in html
    assert "01 / 01" in html


def test_con_destacados_reemplaza_solo_entre_marcadores():
    base = "a<!-- destacados:inicio -->viejo<!-- destacados:fin -->z"
    assert G.con_destacados(base, "nuevo") == "a<!-- destacados:inicio -->\nnuevo\n<!-- destacados:fin -->z"
