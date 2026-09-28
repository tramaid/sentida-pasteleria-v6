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
    # Una sola torta y el sello: las chicas pidieron sacar la foto de la masa (28/09).
    assert pg.locator(".hero .circulo img").count() == 1
    assert pg.locator(".hero .hero-sello").count() == 1


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


def test_idea_nosotras_y_cierre(abrir):
    pg = abrir()
    assert pg.get_attribute(".idea .btn-1", "href") == "arma-tu-torta/"
    assert pg.eval_on_selector_all(".idea-pasos h3", "hs => hs.map(h => h.textContent)") == \
        ["Nos contás", "Te la cotizamos", "La hacemos a mano"]
    assert pg.get_attribute(".anto-nadia .enlace", "href") == "nosotras/"
    assert pg.text_content("#cierre-t") == "¿Qué vamos a crear juntas?"
    wa = pg.get_attribute(".cierre a[href^='https://wa.me/']", "href")
    assert wa.startswith("https://wa.me/5491158300787?text=")


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


def test_el_pedido_de_la_home_tiene_sus_iconos(abrir):
    pg = abrir()
    assert pg.evaluate("[...document.querySelectorAll('use')].map(u => u.getAttribute('href'))"
                       ".filter(h => h.startsWith('#') && !document.querySelector(h))") == []


def test_el_hero_queda_entero(abrir):
    for w in (900, 1024, 1280, 1440, 1920):
        pg = abrir(w, 900)
        der = pg.evaluate("Math.max(...[...document.querySelectorAll('.hero-nota, .hero-sello, .circulo-grande')]"
                          ".map(e => e.getBoundingClientRect().right))")
        assert der <= w, w
