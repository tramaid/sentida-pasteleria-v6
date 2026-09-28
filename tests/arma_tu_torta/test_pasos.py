from ayuda_decoradas import adelante, armar, atras, completar, siguiente, visibles

CEL = dict(is_mobile=True, has_touch=True)
FALTA_FECHA = "Elegí una fecha o marcá «Todavía no sé»."


def test_se_ve_un_paso_por_vez(abrir):
    pg = abrir()
    assert "en-pasos" in pg.evaluate("document.documentElement.className")
    assert visibles(pg) == [1]
    assert pg.is_hidden("#volver")
    assert pg.get_attribute("#siguiente", "aria-disabled") == "true"
    assert pg.get_attribute("#avance", "data-paso") == "1"
    assert pg.errores == []


def test_siguiente_sin_respuesta_dice_que_falta(abrir):
    pg = abrir()
    # Playwright no toca un botón con aria-disabled: acá se fuerza el clic, como lo haría una persona.
    pg.click("#siguiente", force=True)
    assert visibles(pg) == [1]
    assert pg.text_content("#pasos-falta") == FALTA_FECHA
    assert pg.evaluate("document.activeElement.id") == "fecha"


def test_con_respuesta_avanza_y_vuelve(abrir):
    pg = abrir()
    pg.check("#sin-fecha")
    assert pg.get_attribute("#siguiente", "aria-disabled") is None
    siguiente(pg)
    assert visibles(pg) == [2]
    assert pg.evaluate("document.activeElement.id") == "paso-2-t"
    assert pg.is_visible("#volver")
    assert pg.url.endswith("#paso-2")
    assert pg.get_attribute("#avance", "data-paso") == "2"
    pg.click("#volver")
    assert visibles(pg) == [1]
    assert pg.is_checked("#sin-fecha")


def test_elegir_no_avanza_solo(abrir):
    pg = abrir()
    pg.check("#sin-fecha")
    siguiente(pg)
    pg.check("input[name=tamano][value=chica]")
    assert visibles(pg) == [2]


def test_paso_seis_se_puede_pasar_vacio_y_dice_ver_mi_comanda(abrir):
    pg = abrir()
    armar(pg, hasta=6)
    assert pg.text_content("#siguiente-t") == "Ver mi comanda"
    assert pg.get_attribute("#siguiente", "aria-disabled") is None
    assert pg.is_hidden(".solo-sin-js")
    siguiente(pg)
    assert visibles(pg) == [7]
    assert pg.is_hidden("#siguiente")
    assert pg.is_visible("#volver")
    assert pg.url.endswith("#cierre")
    assert pg.evaluate("document.activeElement.id") == "cierre-t"


def test_atras_del_navegador_vuelve_un_paso(abrir):
    pg = abrir()
    armar(pg, hasta=4)
    atras(pg)
    assert visibles(pg) == [3]
    atras(pg)
    assert visibles(pg) == [2]
    adelante(pg)
    assert visibles(pg) == [3]


def test_atras_hasta_la_portada_y_adelante(abrir):
    pg = abrir()
    pg.click("#empezar")
    completar(pg, 1)
    siguiente(pg)
    pg.check("input[name=tamano][value=grande]")
    atras(pg)
    assert visibles(pg) == [1]
    atras(pg)
    assert pg.evaluate("location.hash") == ""
    adelante(pg)
    adelante(pg)
    assert visibles(pg) == [2]
    assert pg.is_checked("input[name=tamano][value=grande]")
    siguiente(pg)
    assert visibles(pg) == [3]
    assert pg.errores == []


def test_la_linea_del_ticket_lleva_a_su_paso(abrir):
    pg = abrir()
    armar(pg)
    pg.click('.panel [data-clave="bizcochuelo"] .ticket-ir')
    assert visibles(pg) == [3]
    assert pg.evaluate("document.activeElement.id") == "paso-3-t"
    assert pg.get_attribute('.panel [data-clave="bizcochuelo"] .ticket-ir', "aria-label") == "Cambiar: Bizcochuelo"


def test_no_se_salta_a_pasos_no_alcanzados(abrir):
    pg = abrir()
    assert pg.is_enabled('.panel [data-clave="fecha"] .ticket-ir')
    assert pg.is_disabled('.panel [data-clave="tamano"] .ticket-ir')
    pg.check("#sin-fecha")
    siguiente(pg)
    assert pg.is_enabled('.panel [data-clave="tamano"] .ticket-ir')
    assert pg.is_disabled('.panel [data-clave="bizcochuelo"] .ticket-ir')


def test_desde_el_dialogo_del_celular_se_salta_y_cierra(abrir):
    pg = abrir(390, 844, **CEL)
    pg.click("#empezar")
    armar(pg, hasta=4)
    pg.click(".tira-ver")
    pg.click('#comanda-dialogo [data-clave="tamano"] .ticket-ir')
    pg.wait_for_timeout(100)
    assert not pg.evaluate("document.getElementById('comanda-dialogo').open")
    assert visibles(pg) == [2]
    assert pg.evaluate("document.activeElement.id") == "paso-2-t"


def test_entrar_con_un_paso_sin_los_anteriores_va_al_que_falta(abrir):
    pg = abrir(pagina="arma-tu-torta/#paso-5")
    assert visibles(pg) == [1]
    assert pg.url.endswith("#paso-1")


def test_el_cierre_con_la_fecha_borrada_vuelve_al_paso_uno(abrir):
    pg = abrir()
    armar(pg)
    pg.click('.panel [data-clave="fecha"] .ticket-ir')
    pg.fill("#fecha", "")
    pg.evaluate("ComandaPasos.ir(7)")
    assert visibles(pg) == [1]
    assert pg.text_content("#pasos-falta") == FALTA_FECHA


def test_enter_en_un_campo_avanza(abrir):
    pg = abrir()
    armar(pg, hasta=6)
    pg.fill("#nombre-torta", "Lu")
    pg.press("#nombre-torta", "Enter")
    assert visibles(pg) == [7]
    assert "Nombre: Lu" in pg.input_value("#mensaje")


def test_enter_en_la_idea_no_avanza(abrir):
    pg = abrir()
    armar(pg, hasta=6)
    pg.press("#idea", "Enter")
    assert visibles(pg) == [6]


def test_en_celular_la_barra_queda_abajo_y_a_la_vista(abrir):
    pg = abrir(390, 844, **CEL)
    pg.click("#empezar")
    caja = pg.locator("#pasos-nav").bounding_box()
    assert caja["y"] + caja["height"] <= 844 + 1
    assert caja["y"] > 844 / 2


def test_sin_movimiento_cambia_de_paso_sin_animar(abrir):
    pg = abrir(reduced_motion="reduce")
    pg.check("#sin-fecha")
    siguiente(pg)
    assert pg.evaluate("document.getElementById('paso-2').getAnimations().length") == 0


def test_con_movimiento_la_pregunta_entra(abrir):
    pg = abrir()
    pg.check("#sin-fecha")
    siguiente(pg)
    assert pg.evaluate("document.getElementById('paso-2').getAnimations().length") == 1


def test_atras_sin_haber_tocado_empezar_vuelve_al_paso_uno(abrir):
    # Revisión final: quien baja con el scroll (o llega de la home sin #) no tocó «Empezar».
    pg = abrir()
    pg.check("#sin-fecha")
    siguiente(pg)
    assert visibles(pg) == [2]
    atras(pg)
    assert visibles(pg) == [1]
    assert pg.errores == []


def test_atras_despues_del_salto_a_la_comanda(abrir):
    pg = abrir()
    pg.evaluate("location.hash = '#comanda'")  # como el enlace «Saltar a la comanda»
    pg.check("#sin-fecha")
    siguiente(pg)
    atras(pg)
    assert visibles(pg) == [1]
    assert pg.evaluate("location.hash") == "#comanda"


def test_una_fecha_pasada_no_deja_seguir(abrir):
    pg = abrir()
    pg.fill("#fecha", "2020-01-01")
    assert pg.get_attribute("#siguiente", "aria-disabled") == "true"
    pg.click("#siguiente", force=True)
    assert visibles(pg) == [1]
    assert pg.text_content("#pasos-falta") == "Elegí una fecha de hoy en adelante."


def test_en_el_cierre_la_barra_no_tapa_el_envio(abrir):
    pg = abrir(1440, 900)
    armar(pg)
    envio = pg.locator("#envio [type=submit]").bounding_box()
    nav = pg.locator("#pasos-nav").bounding_box()
    assert envio["y"] + envio["height"] <= nav["y"]


def test_en_celular_la_barra_entra_en_una_fila(abrir):
    pg = abrir(390, 844, **CEL)
    pg.click("#empezar")
    armar(pg, hasta=6)
    assert pg.locator("#pasos-nav").bounding_box()["height"] < 90
    assert pg.get_by_role("button", name="Volver").is_visible()
