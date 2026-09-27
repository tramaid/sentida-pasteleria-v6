from urllib.parse import unquote

PUERTAS = [("arma-tu-torta/", "Armá tu torta"), ("tortas/", "Nuestras tortas"), ("pasteleria/", "Pastelería")]


def hrefs(pg, sel):
    return pg.eval_on_selector_all(sel, "as => as.map(a => a.getAttribute('href'))")


def test_el_menu(abrir):
    pg = abrir()
    assert hrefs(pg, ".cab-nav a") == ["tortas/", "arma-tu-torta/", "pasteleria/", "nosotras/"]
    assert pg.eval_on_selector_all(".cab-nav a", "as => as.map(a => a.textContent)") == \
        ["Nuestras tortas", "Armá tu torta", "Pastelería", "Nosotras"]
    assert hrefs(pg, ".menu nav a") == ["tortas/", "arma-tu-torta/", "pasteleria/", "nosotras/"]
    assert pg.get_attribute(".cab [data-mi-pedido]", "href") == "tortas/#pedido"


def test_el_hero(abrir):
    pg = abrir()
    assert pg.text_content(".hero-marca") == "SENTIDA"
    assert pg.text_content(".hero-lema") == "Lo soñás,lo creamos."
    assert pg.get_attribute(".hero .btn-1", "href") == "arma-tu-torta/"
    assert pg.get_attribute(".hero .enlace", "href") == "#empezar"
    assert pg.locator(".hero .circulo img").count() == 2


def test_elegi_por_donde_empezar(abrir):
    pg = abrir()
    assert pg.text_content("#empezar-t") == "Elegí por dónde empezar."
    assert hrefs(pg, ".puerta") == [h for h, _ in PUERTAS]
    assert pg.eval_on_selector_all(".puerta h3", "hs => hs.map(h => h.textContent)") == [t for _, t in PUERTAS]
    assert pg.locator(".puerta .circulo img").count() == 3


def test_en_el_celular_el_hero_entra_y_las_puertas_siguen(abrir):
    pg = abrir(390, 844, is_mobile=True, has_touch=True)
    assert pg.evaluate("document.querySelector('.hero .btn-1').getBoundingClientRect().bottom") <= 844 * 1.6
    assert pg.evaluate("document.documentElement.scrollWidth") == 390


def test_la_home_no_repite_las_secciones(abrir):
    pg = abrir()
    for fuera in ("#carta", "#decoradas", "#antojos", "#madre", ".manif", ".mano", ".hero-foto", ".entrada"):
        assert pg.locator(fuera).count() == 0, fuera
    assert "Madre" not in pg.text_content("body")


def test_lleva_a_nosotras_y_explica_como_pedir(abrir):
    pg = abrir()
    assert pg.get_attribute(".nos-linea a", "href") == "nosotras/"
    assert pg.locator(".como-pedir ol > li").count() == 3


def test_el_pie_lleva_a_las_secciones(abrir):
    pg = abrir()
    assert hrefs(pg, ".pie-links a")[:4] == ["tortas/", "arma-tu-torta/", "pasteleria/", "nosotras/"]
    wa = [h for h in hrefs(pg, ".pie-links a") if h.startswith("https://wa.me/")]
    assert unquote(wa[0].split("?text=", 1)[1]).startswith("Hola SENTIDA")


def test_el_pie_no_lleva_el_sentida_gigante(abrir):
    pg = abrir()
    mayor = pg.eval_on_selector_all(".pie *", "es => Math.max(...es.map(e => parseFloat(getComputedStyle(e).fontSize)))")
    assert mayor <= 28


def test_sin_errores(abrir):
    assert abrir().errores == []
