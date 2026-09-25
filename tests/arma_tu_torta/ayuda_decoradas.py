"""Ayudas para recorrer la comanda paso a paso en las pruebas."""
from fechas import FUTURA


def visibles(pg):
    """Los pasos que se ven (1 a 7)."""
    return pg.evaluate(
        "[...document.querySelectorAll('.paso[data-n], #cierre')].filter(p => !p.hidden).map(p => +p.dataset.n)")


def siguiente(pg):
    pg.click("#siguiente")


def atras(pg):
    """El botón atrás del navegador (navegación dentro del mismo documento)."""
    pg.evaluate("history.back()")
    pg.wait_for_timeout(150)


def adelante(pg):
    pg.evaluate("history.forward()")
    pg.wait_for_timeout(150)


def completar(pg, n):
    """Elige lo del paso n como en la especificación (una fecha futura, mediana, vainilla…)."""
    if n == 1:
        pg.fill("#fecha", FUTURA)
    elif n == 2:
        pg.check("input[name=tamano][value=mediana]")
    elif n == 3:
        pg.check("input[name=bizcochuelo][value=vainilla]")
    elif n == 4:
        pg.check("input[name=relleno][value=ddl]")
        pg.check("input[name=agregado][value=nuez]")
        pg.check("input[name=agregado][value=chips]")
    elif n == 5:
        pg.check("input[name=relleno2][value=frutos-rojos]")
    elif n == 6:
        pg.fill("#idea", "flores naturales en tonos pastel")
        pg.check("input[name=referencia][value=flores]")
        pg.fill("#nombre-torta", "Mamá")
        pg.fill("#numero", "60")


def armar(pg, hasta=7):
    """Completa los pasos 1 a hasta-1 con Siguiente y queda parada en `hasta`."""
    for n in range(1, hasta):
        completar(pg, n)
        siguiente(pg)
    assert visibles(pg) == [hasta]
