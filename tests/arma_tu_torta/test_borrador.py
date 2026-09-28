from ayuda_decoradas import armar, visibles

CLAVE = "sentida-comanda-v1"


def test_el_borrador_sobrevive_la_recarga(abrir, sitio):
    pg = abrir()
    armar(pg, hasta=3)
    pg.goto(sitio + "arma-tu-torta/")
    pg.wait_for_load_state("networkidle")
    assert pg.is_checked("input[name=tamano][value=mediana]")
    assert "Tamaño: mediana (15 a 25 porciones)" in pg.input_value("#mensaje")
    assert pg.inner_text('.panel [data-clave="tamano"] dd') == "mediana (15 a 25 porciones)"


def test_empezar_de_nuevo_lo_borra(abrir, sitio):
    pg = abrir()
    armar(pg)
    pg.click("#reiniciar")
    assert visibles(pg) == [1]
    assert pg.evaluate("document.activeElement.id") == "fecha"
    assert pg.evaluate(f"localStorage.getItem('{CLAVE}')") is None
    pg.goto(sitio + "arma-tu-torta/")
    pg.wait_for_load_state("networkidle")
    assert not pg.is_checked("input[name=tamano][value=mediana]")


def test_borrador_con_fecha_pasada(abrir):
    pg = abrir(init=f"localStorage.setItem('{CLAVE}', JSON.stringify({{fecha:'2020-01-01', tamano:'chica'}}))")
    assert pg.input_value("#fecha") == ""
    assert pg.is_checked("input[name=tamano][value=chica]")
    assert pg.errores == []


def test_borrador_roto_no_rompe_nada(abrir):
    pg = abrir(init=f"localStorage.setItem('{CLAVE}', '{{roto')")
    assert pg.errores == []
    assert pg.input_value("#mensaje").startswith("Hola SENTIDA, les paso mi comanda:")


def test_retoma_en_el_paso_guardado(abrir, sitio):
    pg = abrir()
    armar(pg, hasta=4)
    pg.goto(sitio + "arma-tu-torta/")
    pg.wait_for_load_state("networkidle")
    assert pg.text_content("#empezar") == "Seguir mi comanda"
    assert visibles(pg) == [4]
    pg.click("#empezar")
    assert pg.url.endswith("#paso-4")
    assert pg.evaluate("document.activeElement.id") == "paso-4-t"


def test_sin_borrador_dice_empezar_y_no_guarda_nada(abrir):
    pg = abrir()
    assert pg.text_content("#empezar") == "Empezar mi comanda"
    assert pg.evaluate(f"localStorage.getItem('{CLAVE}')") is None


def test_un_borrador_viejo_con_referencia_no_rompe_nada(abrir):
    # Antes el paso 6 tenía «Una referencia» (y la home la mandaba con ?ref=).
    viejo = "{tamano: 'chica', idea: 'rosa', referencia: 'flores', fotos: 3, paso: {actual: 6, alcanzado: 6}}"
    pg = abrir(pagina="arma-tu-torta/?ref=petalos", init=f"localStorage.setItem('{CLAVE}', JSON.stringify({viejo}))")
    msj = pg.input_value("#mensaje")
    assert "Decoración: rosa\n" in msj + "\n"
    assert "como la de" not in msj and "Fotos" not in msj
    assert pg.locator("input[name=referencia]").count() == 0
    assert pg.errores == []


def test_borrador_con_forma_rara(abrir):
    raro = "{agregados: 5, tamano: ['x'], sinFecha: 'si', idea: {a: 1}, paso: {actual: 99, alcanzado: 'a'}}"
    pg = abrir(init=f"localStorage.setItem('{CLAVE}', JSON.stringify({raro}))")
    assert pg.errores == []
    assert visibles(pg) == [1]
    assert not pg.is_checked("#sin-fecha")
    pg.check("#sin-fecha")
    assert '"sinFecha":true' in pg.evaluate(f"localStorage.getItem('{CLAVE}')")


def test_borrador_viejo_con_lo_charlamos(abrir):
    viejo = "{sinFecha: true, tamano: 'charlamos', paso: {actual: 3, alcanzado: 3}}"
    pg = abrir(init=f"localStorage.setItem('{CLAVE}', JSON.stringify({viejo}))")
    assert pg.errores == []
    assert visibles(pg) == [2]
    assert pg.evaluate("document.querySelector('input[name=tamano]:checked')") is None
    assert "Tamaño: a definir" in pg.input_value("#mensaje")
    assert pg.get_attribute("#siguiente", "aria-disabled") == "true"
