# Marca nueva, tienda con la cara de la v6 y ficha — Plan de implementación

> **Para agentes:** SUB-SKILL OBLIGATORIA: usar superpowers:subagent-driven-development (recomendado) o superpowers:executing-plans para ejecutar este plan tarea por tarea. Los pasos llevan casillas (`- [ ]`) para ir marcando.

**Objetivo:** que el sitio y la tienda de SENTIDA compartan el logo nuevo, la paleta del logo y Playfair; que la tienda Flask entre directo al catálogo con la cara de la v6; y que la ficha deje elegir sabor y medida y respete la anticipación de cada categoría.

**Arquitectura:**
- `sentida-site` es la fuente de la marca: `comun/marca.css`, `assets/marca/` y las fuentes.
- `sentida-tienda` la copia con un comando (`sincronizar-marca`), y un test compara la copia con el sitio.
- La tienda saca su tema del `<style>` de `base.html` a `static/tema.css` y usa el mismo marcado que el sitio para la cabecera, la cinta y el pie.
- Las opciones de la ficha son presentaciones (`productos`) con dos columnas nuevas, `sabor` y `medida`. El importador las arma desde `catalogo.json`.

**Stack:**
- Sitio: HTML, CSS y JS sin framework; el generador en Python (`herramientas/generar_tienda.py`); tests con pytest y Playwright.
- Tienda: Flask 3, Jinja, SQLite y pytest.

**Spec:** `sentida-site/docs/superpowers/specs/2026-09-28-marca-tienda-ficha-design.md` (leerlo antes de empezar).

**Repos y ramas:**
- Sitio: `E:\E descargas\SENTIDA-sitio-web\sentida-site`, rama `v6`. Tests: `python -m pytest -q`, unos 6 minutos.
- Tienda: `E:\E descargas\SENTIDA-sitio-web\sentida-tienda`, rama `main`. Tests: `python -m pytest -q -p no:cacheprovider`.
- Preview: worktree `E:\E descargas\SENTIDA-sitio-web\sentida-tienda-preview`, rama `preview-render`. Se toca solo en la Tarea 15.

## Restricciones globales

- **Colores (del logo):**

  | Token | Antes | Ahora |
  |---|---|---|
  | `--marron` | `#402D21` | `#4E2C1E` |
  | `--celeste-filete` | `#8FB1C9` | `#7EAFD6` |
  | `--blanco` | `#FEFAF8` | `#FCF9F2` |

  Los demás no cambian: `--crema #F8EADE`, `--crema-suave #F9F3EE`, `--beige #CFB59E`, `--celeste #DDE6ED`, `--marron-medio #6C4D38`, `--celeste-profundo #46627A`.
- **Transparencias:** `--linea rgba(207,181,158,.6)`, `--sombra rgba(78,44,30,.28)`, `--sombra-suave rgba(78,44,30,.19)` y `--velo rgba(78,44,30,.45)`.
- **El celeste de filetes** (`--celeste-filete`) nunca se usa en texto.
- **Tipografías:** títulos en `--display: Playfair, "Playfair respaldo", Georgia, serif`, peso 400. Texto en `--ui: Montserrat, "Montserrat respaldo", system-ui, sans-serif`. Nada de Erode, ni en archivos ni en referencias. Las fuentes se sirven desde el propio sitio o la tienda, nunca desde `fonts.googleapis`.
- **Nada de texto por debajo de 11 px, radio de 2 px y sin cursivas** (regla de la tienda, `test_publico_tema.py`).
- **Precios:** quedan en NULL («A consultar»). No se inventan precios, fechas ni promesas.
- **Pago online:** no se toca (`pago_online_habilitado` queda como está).
- **Voz:** voseo y «nosotras». Los textos inventados llevan `"texto_provisorio": true` en `catalogo.json`.
- **El menú del sitio no cambia:** Nuestras tortas y Pastelería siguen yendo a `tortas/` y `pasteleria/`, las páginas estáticas.
- **Commits:** en español, con el prefijo del repo que ya se usa (`v6:` en el sitio, `marca:`/`tienda:`/`ficha:` en la tienda). Siempre terminan con `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Foco de la revisión

Lo que el spec implica y es más probable que falle al usarse. Cada punto tiene su test en la tarea indicada.

1. **Un pedido que mezcla una torta (48 h) y pastelería (96 h):** el primer día de retiro tiene que respetar las 96 h, no las 48 (Tarea 14, `test_la_anticipacion_manda_la_mas_larga`).
2. **Volver a correr el importador sobre una base que ya tenía el producto sin sabor ni medida** (la semilla de Render): no tiene que duplicarlo, sino adoptar la presentación existente como la primera combinación (Tarea 12, `test_reimportar_adopta_la_presentacion_vieja`).
3. **La ficha de un producto con sabores abierta sin JavaScript:** tiene que poder pedirse una combinación concreta con una sola lista de radios (Tarea 13, `test_sin_js_una_lista_con_todas_las_combinaciones`).
4. **Una combinación apagada desde el panel** (por ejemplo, «De maracuyá · Docena» sin disponibilidad): no puede quedar elegible ni marcada de entrada (Tarea 13, `test_combinacion_sin_disponibilidad_no_viene_marcada`).
5. **La copia de la marca en Render,** donde no está `../sentida-site`: el test de sincronía se saltea en lugar de fallar, y la tienda arranca con su copia (Tarea 4, `test_sin_el_sitio_al_lado_se_saltea`).

---

## Parte 1 — La marca en `sentida-site`

### Tarea 1: Los archivos de la marca (logos, sello, favicon y Playfair)

**Archivos:**
- Crear: `assets/marca/logo.svg`, `assets/marca/logo-pasteleria.svg`, `assets/marca/logo-claro.svg`, `assets/marca/sello.svg` y `assets/marca/favicon.svg`.
- Crear: `assets/fuentes/playfair-latin.woff2` y `assets/fuentes/playfair-latin-ext.woff2`.
- Crear: `herramientas/limpiar_svg.py`.
- Test: `tests/sitio/test_marca.py`.

**Interfaces:**
- Produce: las rutas de los cinco SVG y las dos fuentes, que usan las Tareas 2, 3 y 4. `limpiar_svg.limpiar(texto_svg, color=None) -> str`.

- [ ] **Paso 1: Escribir el test que falla**

```python
# tests/sitio/test_marca.py
"""La marca del sitio: logos, sello, favicon y fuentes. Es la fuente de verdad
que la tienda copia (sentida-tienda: flask sincronizar-marca)."""
import pathlib
import re

RAIZ = pathlib.Path(__file__).resolve().parents[2]
MARCA = RAIZ / "assets" / "marca"
SVGS = ["logo.svg", "logo-pasteleria.svg", "logo-claro.svg", "sello.svg", "favicon.svg"]


def test_estan_los_cinco_svg_limpios():
    for nombre in SVGS:
        texto = (MARCA / nombre).read_text(encoding="utf-8")
        assert texto.startswith("<svg"), nombre
        assert "Illustrator" not in texto and "<?xml" not in texto, nombre
        assert 'id="Capa_1"' not in texto, nombre
        assert re.search(r'viewBox="[\d. ]+"', texto), nombre


def test_los_colores_son_los_del_logo():
    assert "#4e2c1e" in (MARCA / "logo.svg").read_text(encoding="utf-8").lower()
    pasteleria = (MARCA / "logo-pasteleria.svg").read_text(encoding="utf-8").lower()
    assert "#4e2c1e" in pasteleria and "#7eafd6" in pasteleria
    claro = (MARCA / "logo-claro.svg").read_text(encoding="utf-8").lower()
    assert "#fcf9f2" in claro and "#4e2c1e" not in claro


def test_playfair_esta_y_erode_no():
    fuentes = RAIZ / "assets" / "fuentes"
    assert (fuentes / "playfair-latin.woff2").stat().st_size > 20_000
    assert (fuentes / "playfair-latin-ext.woff2").stat().st_size > 20_000
    assert not list(fuentes.glob("erode*"))
```

- [ ] **Paso 2: Correrlo y verificar que falla**

Correr: `python -m pytest -q tests/sitio/test_marca.py`
Esperado: FALLA, con `FileNotFoundError` en `assets/marca/logo.svg`.

- [ ] **Paso 3: Escribir el limpiador de SVG**

```python
# herramientas/limpiar_svg.py
"""Deja un SVG de Illustrator listo para la web: sin la declaración XML, sin
comentarios ni id de capa, y con las clases .st0/.st1… pasadas a `fill`
directo (el <style> interno de un SVG pisa estilos si el SVG va inline).

Uso, desde sentida-site/:
    python herramientas/limpiar_svg.py <origen.svg> <destino.svg> [--color #HEX]

Con --color, TODOS los rellenos pasan a ese color (el logo claro del pie).
"""
import re
import sys


def limpiar(texto, color=None):
    estilos = {}
    bloque = re.search(r"<style>(.*?)</style>", texto, re.S)
    if bloque:
        for sel, cuerpo in re.findall(r"([^{}]+)\{([^}]*)\}", bloque.group(1)):
            for clase in re.findall(r"\.(st\d+)", sel):
                estilos.setdefault(clase, []).append(cuerpo.strip())
    texto = re.sub(r"<\?xml.*?\?>\s*", "", texto, flags=re.S)
    texto = re.sub(r"<!--.*?-->\s*", "", texto, flags=re.S)
    texto = re.sub(r"<defs>.*?</defs>\s*", "", texto, flags=re.S)
    texto = texto.replace(' id="Capa_1"', "").replace(' version="1.1"', "")

    def atributos(m):
        props = {}
        for cuerpo in estilos.get(m.group(1), []):
            for decl in cuerpo.split(";"):
                if ":" in decl:
                    k, v = decl.split(":", 1)
                    props[k.strip()] = v.strip()
        if color:
            if props.get("fill", "none") != "none":
                props["fill"] = color
            if "stroke" in props:
                props["stroke"] = color
        return " ".join(f'{k}="{v}"' for k, v in props.items())

    texto = re.sub(r'class="(st\d+)"', atributos, texto)
    return texto.strip() + "\n"


if __name__ == "__main__":
    args = sys.argv[1:]
    color = None
    if "--color" in args:
        i = args.index("--color")
        color = args[i + 1]
        del args[i:i + 2]
    origen, destino = args
    with open(origen, encoding="utf-8") as f:
        salida = limpiar(f.read(), color)
    with open(destino, "w", encoding="utf-8", newline="\n") as f:
        f.write(salida)
```

- [ ] **Paso 4: Generar los cinco SVG y copiar las fuentes**

```bash
cd "/e/E descargas/SENTIDA-sitio-web/sentida-site"
mkdir -p assets/marca
python herramientas/limpiar_svg.py ../solo-sentida-nuevo.svg assets/marca/logo.svg
python herramientas/limpiar_svg.py ../logo-sentida-nuevo-01.svg assets/marca/logo-pasteleria.svg
python herramientas/limpiar_svg.py ../solo-sentida-nuevo.svg assets/marca/logo-claro.svg --color "#FCF9F2"
python herramientas/limpiar_svg.py ../SELLO-SENTIDA-NUEVO-01.svg assets/marca/sello.svg
cp ../comparacion-tipografias/fuentes/playfair-300-700-lat.woff2 assets/fuentes/playfair-latin.woff2
cp ../comparacion-tipografias/fuentes/playfair-300-700-ext.woff2 assets/fuentes/playfair-latin-ext.woff2
```

El favicon es la S del sello sola: el `<path>` marrón de `sello.svg` (el que lleva `fill="#4e2c1e"`) dentro de un círculo crema. Hay que armarlo a mano:

```bash
python - <<'EOF'
import re, pathlib
s = pathlib.Path("assets/marca/sello.svg").read_text(encoding="utf-8")
vb = re.search(r'viewBox="([\d. ]+)"', s).group(1).split()
cx, cy = float(vb[2]) / 2, float(vb[3]) / 2
ese = [m for m in re.findall(r"<path[^>]*>", s) if "#4e2c1e" in m.lower()]
assert ese, "no encontré la S marrón del sello"
r = min(cx, cy)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{cx - r} {cy - r} {2 * r} {2 * r}">'
       f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#FCF9F2"/>' + "".join(ese) + "</svg>\n")
pathlib.Path("assets/marca/favicon.svg").write_text(svg, encoding="utf-8", newline="\n")
EOF
```

Abrir los cinco SVG en el navegador y mirarlos. La S del favicon tiene que verse entera y centrada; si queda chica, achicar el `viewBox` al rectángulo de la S con un margen del 12 %.

- [ ] **Paso 5: Correr el test y verificar que pasa**

Correr: `python -m pytest -q tests/sitio/test_marca.py`
Esperado: `test_playfair_esta_y_erode_no` sigue FALLANDO, porque Erode se borra en la Tarea 2. Los otros dos pasan.

- [ ] **Paso 6: Commit**

```bash
git add assets/marca assets/fuentes/playfair-latin.woff2 assets/fuentes/playfair-latin-ext.woff2 herramientas/limpiar_svg.py tests/sitio/test_marca.py
git commit -m "v6: los archivos de la marca nueva (logos, sello, favicon y Playfair)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarea 2: `marca.css`, los colores del logo y Playfair en todo el sitio

**Archivos:**
- Crear: `comun/marca.css`.
- Modificar: `comun/base.css` (se van las líneas 7-11 con los `@font-face` y el bloque `:root`).
- Modificar: `herramientas/generar_tienda.py` (el `<head>` de `pagina()`).
- Modificar: `index.html`, `nosotras/index.html` y `arma-tu-torta/index.html` (los `<link>` del `<head>`).
- Modificar: `home.css`, `comun/ticket.css`, `comun/tienda.css`, `nosotras/nosotras.css` y `arma-tu-torta/decoradas.css`, solo si les quedó algún hex o rgba suelto.
- Borrar: `assets/fuentes/erode-400.woff2` y `assets/fuentes/erode-500.woff2`.
- Test: `tests/sitio/test_marca.py`.

**Interfaces:**
- Consume: `assets/fuentes/playfair-latin*.woff2` (Tarea 1).
- Produce: `comun/marca.css` con los `@font-face` y todos los tokens. Todas las páginas lo cargan antes que `base.css`. La tienda lo copia en la Tarea 4.

- [ ] **Paso 1: Sumar los tests que fallan**

```python
# agregar al final de tests/sitio/test_marca.py
import pytest

PAGINAS = ["", "tortas/", "pasteleria/", "nosotras/", "arma-tu-torta/"]
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")


def _css(nombre):
    return (RAIZ / nombre).read_text(encoding="utf-8")


def test_marca_css_tiene_los_colores_del_logo_y_playfair():
    css = _css("comun/marca.css").lower()
    for valor in ("--marron:#4e2c1e", "--celeste-filete:#7eafd6", "--blanco:#fcf9f2",
                  "font-family:playfair", "playfair-latin.woff2"):
        assert valor in css.replace(" ", ""), valor
    assert "erode" not in css


def test_ningun_css_declara_colores_fuera_de_marca():
    for nombre in ["comun/base.css", "comun/ticket.css", "comun/tienda.css", "home.css",
                   "nosotras/nosotras.css", "arma-tu-torta/decoradas.css"]:
        css = re.sub(r"mask(?:-image)?\s*:[^;}]*", "", _css(nombre))
        assert HEX.findall(css) == [], nombre
        assert "rgba(" not in css, nombre


@pytest.mark.parametrize("pagina", PAGINAS)
def test_cada_pagina_carga_marca_antes_que_base_y_nada_de_erode(abrir, pagina):
    pg = abrir(pagina=pagina)
    hrefs = pg.eval_on_selector_all('link[rel="stylesheet"]', "ls => ls.map(l => l.getAttribute('href'))")
    marca = next(i for i, h in enumerate(hrefs) if h.endswith("comun/marca.css"))
    base = next(i for i, h in enumerate(hrefs) if h.endswith("comun/base.css"))
    assert marca < base
    assert "erode" not in pg.content().lower()
    familia = pg.evaluate("getComputedStyle(document.querySelector('h1')).fontFamily")
    assert familia.lower().startswith("playfair")
```

La fixture `abrir` es la de `tests/conftest.py` (sirve el sitio y abre la página con Playwright).

- [ ] **Paso 2: Correrlos y verificar que fallan**

Correr: `python -m pytest -q tests/sitio/test_marca.py`
Esperado: FALLAN los cuatro nuevos, con `FileNotFoundError` en `comun/marca.css`.

- [ ] **Paso 3: Escribir `comun/marca.css`**

```css
/* ============================================================
   SENTIDA · la marca (28/09/2026)
   Fuentes y tokens del logo nuevo. Es la FUENTE DE VERDAD: la tienda
   (sentida-tienda) la copia con `flask sincronizar-marca` y un test compara
   las dos. Acá se cambia la marca; en ningún otro CSS hay colores ni fuentes.
   ============================================================ */
@font-face{font-family:Playfair; src:url("../assets/fuentes/playfair-latin.woff2") format("woff2"); font-weight:300 700; font-display:swap;
  unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD}
@font-face{font-family:Playfair; src:url("../assets/fuentes/playfair-latin-ext.woff2") format("woff2"); font-weight:300 700; font-display:swap;
  unicode-range:U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF}
@font-face{font-family:Montserrat; src:url("../assets/fuentes/montserrat-latin.woff2") format("woff2"); font-weight:100 900; font-display:swap}
@font-face{font-family:"Montserrat respaldo"; src:local("Arial"), local("Helvetica"); size-adjust:109.2%; ascent-override:88.6%; descent-override:23%; line-gap-override:0%}
@font-face{font-family:"Playfair respaldo"; src:local("Georgia"); size-adjust:103%; ascent-override:92%; descent-override:24%; line-gap-override:0%}

:root{
  --blanco:#FCF9F2;
  --crema:#F8EADE;
  --crema-suave:#F9F3EE;      /* fondos intermedios y hover de tarjetas */
  --beige:#CFB59E;
  --celeste:#DDE6ED;          /* solo relleno chico, nunca texto */
  --marron:#4E2C1E;
  --marron-medio:#6C4D38;
  --celeste-profundo:#46627A;
  --celeste-filete:#7EAFD6;   /* solo filetes, puntos y aros; nunca texto */
  --linea:rgba(207,181,158,.6);
  --sombra:rgba(78,44,30,.28);
  --sombra-suave:rgba(78,44,30,.19);
  --velo:rgba(78,44,30,.45);

  --display:Playfair, "Playfair respaldo", Georgia, serif;
  --ui:Montserrat, "Montserrat respaldo", system-ui, sans-serif;
}
```

- [ ] **Paso 4: Sacar de `base.css` lo que pasó a `marca.css`**

Borrar las líneas 7-11 de `comun/base.css` (los cinco `@font-face`). En su `:root`, borrar todo desde `--blanco` hasta `--ui` y dejar solo lo de la maqueta:

```css
:root{
  --lateral:clamp(20px,4vw,56px);
  --ancho:1440px;
  --cab:88px;
}
```

Actualizar también el comentario de arriba de `base.css`: «Los colores y las fuentes viven en comun/marca.css».

- [ ] **Paso 5: Cargar `marca.css` y precargar Playfair en todas las páginas**

En `index.html`, reemplazar:

```html
<link rel="preload" href="assets/fuentes/erode-400.woff2" as="font" type="font/woff2" crossorigin>
```

por:

```html
<link rel="preload" href="assets/fuentes/playfair-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="comun/marca.css">
```

En `nosotras/index.html` y `arma-tu-torta/index.html`, lo mismo con el prefijo `../`.

En `herramientas/generar_tienda.py`, dentro de `pagina()`, reemplazar:

```python
<link rel="preload" href="../assets/fuentes/erode-400.woff2" as="font" type="font/woff2" crossorigin>
```

por:

```python
<link rel="preload" href="../assets/fuentes/playfair-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="../comun/marca.css">
```

- [ ] **Paso 6: Buscar y resolver los colores sueltos**

Correr: `grep -nE "#[0-9a-fA-F]{3,8}\b|rgba\(" comun/*.css home.css nosotras/nosotras.css arma-tu-torta/decoradas.css`

Cada resultado que no esté dentro de un `mask:` pasa a su token:
- `#FEFAF8` → `var(--blanco)`
- `#F9F3EE` o `#FBF3ED` → `var(--crema-suave)`
- `rgba(64,45,33,.45)` → `var(--velo)`
- `rgba(64,45,33,.28)` → `var(--sombra)`
- cualquier otro `rgba(64,45,33,…)` o `rgba(108,77,56,…)` → `var(--sombra-suave)`
- en `ticket.css`, `var(--velo, rgba(64,45,33,.45))` pasa a `var(--velo)`.

- [ ] **Paso 7: Borrar Erode, regenerar y correr todo**

```bash
git rm assets/fuentes/erode-400.woff2 assets/fuentes/erode-500.woff2
python herramientas/generar_tienda.py
python -m pytest -q
```

Esperado: PASAN todos, incluido `test_playfair_esta_y_erode_no`. Si falla alguno que comparaba colores o fuentes viejos (por ejemplo, el `theme-color`), actualizar el valor esperado al nuevo; no borrar el test.

Actualizar también el `<meta name="theme-color">`: en `index.html`, `nosotras/index.html`, `arma-tu-torta/index.html` y `pagina()` del generador pasa a `#FCF9F2`.

- [ ] **Paso 8: Commit**

```bash
git add -A comun home.css nosotras arma-tu-torta index.html tortas pasteleria herramientas tests assets/fuentes
git commit -m "v6: marca.css con los colores del logo y Playfair; fuera Erode

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarea 3: El logo dibujado en la cabecera, el hero y el pie, y el sello nuevo

**Archivos:**
- Modificar: `herramientas/generar_tienda.py` (`cabecera()` y `pie()`).
- Modificar: `index.html` (el `h1` del hero y los `<img>` del sello en el hero y el cierre), `nosotras/index.html` y `arma-tu-torta/index.html` (los usos de `SENTIDASELLO.svg`, si los hay).
- Modificar: `comun/base.css` (`.cab-marca`, `.marca-texto`, `.pie-nombre`) y `home.css` (`.hero-marca`).
- Modificar: los `<link rel="icon">` de todas las páginas y de `pagina()` para que apunten a `assets/marca/favicon.svg`.
- Test: `tests/sitio/test_sitio.py` y `tests/home/test_home.py`.

**Interfaces:**
- Consume: `assets/marca/logo.svg`, `logo-pasteleria.svg`, `logo-claro.svg`, `sello.svg` y `favicon.svg` (Tarea 1).
- Produce: el marcado `<a class="cab-marca" …><img class="marca-logo" src="…/assets/marca/logo.svg" alt="SENTIDA" …></a>`. La tienda lo replica en la Tarea 6.

- [ ] **Paso 1: Cambiar los tests para lo nuevo**

En `tests/sitio/test_sitio.py`, `test_la_marca_en_texto` pasa a:

```python
@pytest.mark.parametrize("pagina", PAGINAS)
def test_la_marca_es_el_logo(abrir, pagina):
    pg = abrir(pagina=pagina)
    assert pg.get_attribute(".cab-marca", "aria-label") == "SENTIDA Pastelería, inicio"
    assert pg.get_attribute(".cab-marca img", "src").endswith("assets/marca/logo.svg")
    assert pg.get_attribute(".cab-marca img", "alt") == "SENTIDA"
    assert pg.get_attribute(".pie-marca img", "src").endswith("assets/marca/logo-claro.svg")
    assert pg.get_attribute(".pie-sello", "src").endswith("assets/marca/sello.svg")
    assert "SENTIDASELLO" not in pg.content()
```

En `test_el_pie_nuevo`, reemplazar la línea de `.pie-nombre` por:

```python
    assert pg.get_attribute(".pie-marca img", "alt") == "SENTIDA"
```

En `tests/home/test_home.py`, dentro de `test_el_hero`, reemplazar la línea de `.hero-marca` por:

```python
    assert pg.get_attribute(".hero-marca", "src").endswith("assets/marca/logo-pasteleria.svg")
    assert pg.evaluate("document.querySelector('#hero-t').textContent.replace(/\\s+/g, ' ').trim()") == "Lo soñás,lo creamos."
    assert pg.get_attribute(".hero-marca", "alt") == "Sentida"
    assert pg.get_attribute(".hero-sello", "src").endswith("assets/marca/sello.svg")
```

`textContent` no incluye el `alt`, así que el nombre «Sentida» se controla por el `alt` del `<img>` dentro del `h1`:

```python
    assert pg.locator("#hero-t img.hero-marca").count() == 1
```

- [ ] **Paso 2: Correrlos y verificar que fallan**

Correr: `python -m pytest -q tests/sitio/test_sitio.py -k "marca or pie" tests/home/test_home.py -k hero`
Esperado: FALLAN, porque `.cab-marca img` no existe.

- [ ] **Paso 3: Cabecera y pie del generador**

En `cabecera()` de `generar_tienda.py`, reemplazar la línea de `cab-marca` por:

```python
    <a class="cab-marca" href="{inicio}" aria-label="SENTIDA Pastelería, inicio"><img class="marca-logo" src="{raiz}assets/marca/logo.svg" alt="SENTIDA" width="132" height="36"></a>
```

En `pie()`, reemplazar el bloque `pie-marca` por:

```python
    <div class="pie-marca">
      <img class="pie-logo" src="{raiz}assets/marca/logo-claro.svg" alt="SENTIDA" width="150" height="41" loading="lazy">
      <p class="pie-lema display">Lo soñás, lo creamos.</p>
    </div>
```

y el `<img class="pie-sello" …>` por:

```python
    <img class="pie-sello" src="{raiz}assets/marca/sello.svg" alt="" width="105" height="105" loading="lazy">
```

El `width` y el `height` salen del `viewBox` del logo (1029.11 × 282.2, proporción 3,65:1).

- [ ] **Paso 4: El hero y el cierre de la home**

En `index.html`, el `h1` del hero pasa a:

```html
<h1 id="hero-t"><img class="hero-marca" src="assets/marca/logo-pasteleria.svg" alt="Sentida" width="520" height="190"><span class="hero-lema display">Lo soñás,<br>lo creamos.</span></h1>
```

Los dos `src="assets/SENTIDASELLO.svg"` (el `.hero-sello` y el `.cierre-sello`) pasan a `assets/marca/sello.svg`.

En `nosotras/index.html` y `arma-tu-torta/index.html`, reemplazar cualquier `../assets/SENTIDASELLO.svg` por `../assets/marca/sello.svg`. Para encontrarlos: `grep -rn SENTIDASELLO --include=*.html .`

- [ ] **Paso 5: CSS del logo**

En `comun/base.css`, reemplazar `.marca-texto{…}` y `.marca-punto{…}` por:

```css
.marca-logo{display:block; width:132px; height:auto}
```

`.pie-nombre{…}` y `.pie-nombre span{…}` pasan a:

```css
.pie-logo{display:block; width:150px; height:auto}
```

Dentro de `@media (max-width:899px)`, `.marca-texto{font-size:25px}` pasa a `.marca-logo{width:104px}`.

En `home.css`, `.hero-marca{…}` pasa a:

```css
.hero-marca{display:block; width:clamp(260px,34vw,480px); height:auto}
```

y en el `@media (max-width:899px)`, `.hero-marca{font-size:…}` pasa a:

```css
  .hero-marca{width:min(78vw,320px); margin-inline:auto}
```

- [ ] **Paso 6: Favicon**

En las tres páginas escritas a mano y en `pagina()` del generador, `href="…assets/favicon.svg"` pasa a `…assets/marca/favicon.svg`. Borrar `assets/favicon.svg`, `assets/SENTIDASELLO.svg` y `assets/logo-sentida.svg` solo si `grep -rn` no los encuentra en ningún `.html`, `.css` o `.py` fuera de `docs/`, `home-v1.html` y `styles.css`.

- [ ] **Paso 7: Regenerar, correr todo y mirar**

```bash
python herramientas/generar_tienda.py
python -m pytest -q
```

Esperado: PASAN todos. Sacar capturas de la home, Tortas y Nosotras en 1440 y 390 y revisar: el logo nítido en la cabecera, el hero sin saltos ni cortes, el logo claro en el pie y el sello nuevo.

- [ ] **Paso 8: Commit**

```bash
git add -A
git commit -m "v6: el logo nuevo en la cabecera, el hero y el pie, y el sello nuevo

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

## Parte 2 — La tienda con la cara de la v6 (`sentida-tienda`)

### Tarea 4: `sincronizar-marca`, la copia de la marca desde el sitio

**Archivos:**
- Crear: `servicios/marca.py`.
- Modificar: `app.py` (el comando CLI, junto a `importar-catalogo`).
- Crear: `static/marca.css`, `static/fuentes/playfair-latin*.woff2` y `static/logos/{logo,logo-pasteleria,logo-claro,sello,favicon}.svg` (los genera el comando).
- Test: `tests/test_marca.py`.

**Interfaces:**
- Consume: `sentida-site/comun/marca.css`, `sentida-site/assets/fuentes/*.woff2` y `sentida-site/assets/marca/*.svg` (Tareas 1 y 2).
- Produce: `servicios.marca.ARCHIVOS: list[tuple[str, str]]` (origen relativo al sitio, destino relativo a `static/`), `servicios.marca.sincronizar(sitio: str, static: str) -> list[str]` y `servicios.marca.diferencias(sitio: str, static: str) -> list[str]`.

- [ ] **Paso 1: Escribir el test que falla**

```python
# tests/test_marca.py
"""La marca de la tienda es una COPIA de la del sitio (sentida-site). La copia
la hace `flask sincronizar-marca`; este test avisa si quedó vieja."""
import os

import pytest

from servicios import marca

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITIO = os.path.join(os.path.dirname(RAIZ), 'sentida-site')
STATIC = os.path.join(RAIZ, 'static')


def test_la_copia_es_igual_a_la_del_sitio():
    if not os.path.isdir(SITIO):
        pytest.skip('sentida-site no está al lado (Render, CI): se usa la copia')
    assert marca.diferencias(SITIO, STATIC) == []


def test_sin_el_sitio_al_lado_se_saltea(tmp_path):
    with pytest.raises(FileNotFoundError):
        marca.diferencias(str(tmp_path / 'no-existe'), STATIC)


def test_sincronizar_copia_y_reescribe_las_rutas(tmp_path):
    sitio = tmp_path / 'sitio'
    (sitio / 'comun').mkdir(parents=True)
    (sitio / 'assets' / 'fuentes').mkdir(parents=True)
    (sitio / 'assets' / 'marca').mkdir(parents=True)
    (sitio / 'comun' / 'marca.css').write_text(
        '@font-face{src:url("../assets/fuentes/playfair-latin.woff2")}', encoding='utf-8')
    for origen, _ in marca.ARCHIVOS:
        p = sitio / origen
        if not p.exists():
            p.write_bytes(b'x')
    destino = tmp_path / 'static'
    copiados = marca.sincronizar(str(sitio), str(destino))
    assert 'marca.css' in copiados
    css = (destino / 'marca.css').read_text(encoding='utf-8')
    assert 'url("fuentes/playfair-latin.woff2")' in css
    assert marca.diferencias(str(sitio), str(destino)) == []
```

- [ ] **Paso 2: Correrlo y verificar que falla**

Correr: `python -m pytest -q -p no:cacheprovider tests/test_marca.py`
Esperado: FALLA con `ImportError: cannot import name 'marca'`.

- [ ] **Paso 3: Escribir `servicios/marca.py`**

```python
"""La marca de la tienda sale del sitio (sentida-site): colores, fuentes,
logos y sello. La tienda guarda una COPIA en static/, porque se publica sola
(Render, VPS) sin el sitio al lado. `sincronizar` la trae; `diferencias` dice
si quedó vieja (tests/test_marca.py).

El único cambio al copiar: en marca.css las rutas `../assets/fuentes/` del
sitio pasan a `fuentes/`, relativas a static/marca.css.
"""
import os
import shutil

# (origen relativo a sentida-site, destino relativo a static/)
ARCHIVOS = [
    ('comun/marca.css', 'marca.css'),
    ('assets/fuentes/playfair-latin.woff2', 'fuentes/playfair-latin.woff2'),
    ('assets/fuentes/playfair-latin-ext.woff2', 'fuentes/playfair-latin-ext.woff2'),
    ('assets/fuentes/montserrat-latin.woff2', 'fuentes/montserrat-latin.woff2'),
    ('assets/marca/logo.svg', 'logos/logo.svg'),
    ('assets/marca/logo-pasteleria.svg', 'logos/logo-pasteleria.svg'),
    ('assets/marca/logo-claro.svg', 'logos/logo-claro.svg'),
    ('assets/marca/sello.svg', 'logos/sello.svg'),
    ('assets/marca/favicon.svg', 'logos/favicon.svg'),
]
# Lo que la marca vieja dejó en static/ y ya no existe en el sitio.
VIEJOS = ['fuentes/erode-400.woff2', 'fuentes/erode-500.woff2',
          'logos/logo-sentida.svg', 'logos/SENTIDASELLO.svg']


def _contenido(sitio, origen):
    with open(os.path.join(sitio, origen), 'rb') as f:
        datos = f.read()
    if origen.endswith('marca.css'):
        datos = datos.replace(b'../assets/fuentes/', b'fuentes/')
    return datos


def sincronizar(sitio, static):
    """Copia la marca del sitio a static/. Devuelve los destinos copiados."""
    if not os.path.isdir(sitio):
        raise FileNotFoundError(sitio)
    copiados = []
    for origen, destino in ARCHIVOS:
        ruta = os.path.join(static, destino)
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, 'wb') as f:
            f.write(_contenido(sitio, origen))
        copiados.append(destino)
    for viejo in VIEJOS:
        ruta = os.path.join(static, viejo)
        if os.path.exists(ruta):
            os.remove(ruta)
    return copiados


def diferencias(sitio, static):
    """Los destinos que faltan o no son iguales al sitio. [] = al día."""
    if not os.path.isdir(sitio):
        raise FileNotFoundError(sitio)
    malos = []
    for origen, destino in ARCHIVOS:
        ruta = os.path.join(static, destino)
        if not os.path.exists(ruta):
            malos.append(destino)
            continue
        with open(ruta, 'rb') as f:
            if f.read() != _contenido(sitio, origen):
                malos.append(destino)
    malos += [v for v in VIEJOS if os.path.exists(os.path.join(static, v))]
    return malos
```

- [ ] **Paso 4: El comando en `app.py`**

Agregarlo al lado de `importar-catalogo`, dentro de `create_app`:

```python
    @app.cli.command('sincronizar-marca')
    @click.argument('sitio', type=click.Path(exists=True, file_okay=False))
    def sincronizar_marca_cmd(sitio):
        """Copia la marca de sentida-site (colores, fuentes, logos) a static/."""
        from servicios import marca
        for destino in marca.sincronizar(sitio, app.static_folder):
            click.echo(f'  {destino}')
        click.echo('marca al día')
```

- [ ] **Paso 5: Correr el comando y los tests**

```bash
python -m flask --app app sincronizar-marca ../sentida-site
python -m pytest -q -p no:cacheprovider tests/test_marca.py
```

Esperado: PASAN los tres.

- [ ] **Paso 6: Commit**

```bash
git add servicios/marca.py app.py tests/test_marca.py static/marca.css static/fuentes static/logos
git commit -m "marca: sincronizar-marca copia la marca del sitio y un test la vigila

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

`base.html` todavía referencia Erode, así que otros tests pueden fallar hasta la Tarea 5. Si falla algo más que `test_publico_tema.py`, revisar antes de seguir.

---

### Tarea 5: El tema sale de `base.html` a `static/tema.css` y usa `marca.css`

**Archivos:**
- Crear: `static/tema.css` (el contenido del `<style>` de `templates/themes/sentida/base.html`, líneas 40 a ~350, sin los `@font-face` ni el `:root` de colores).
- Modificar: `templates/themes/sentida/base.html` (el `<head>`).
- Modificar: `tests/test_publico_tema.py`.

**Interfaces:**
- Consume: `static/marca.css` (Tarea 4).
- Produce: `<link rel="stylesheet" href="{{ url_for('static', filename='marca.css') }}">`, seguido del de `tema.css`, en todas las páginas públicas. `--display` es Playfair.

- [ ] **Paso 1: Actualizar los tests de tema**

En `tests/test_publico_tema.py`:

```python
# Los colores del logo (sentida-site/comun/marca.css, copiado a static/marca.css).
PALETA = {'#fcf9f2', '#f8eade', '#f9f3ee', '#cfb59e', '#dde6ed', '#4e2c1e', '#6c4d38',
          '#46627a', '#7eafd6'}
TRANSPARENCIAS = {'rgba(207,181,158,.6)', 'rgba(78,44,30,.28)', 'rgba(78,44,30,.19)',
                  'rgba(78,44,30,.45)'}
```

`test_las_fuentes_son_propias_y_no_de_google` pasa a:

```python
def test_las_fuentes_son_propias_y_no_de_google(client, base, app):
    r = client.get('/catalogo')
    assert 'static/marca.css' in r.text and 'static/tema.css' in r.text
    assert r.text.index('static/marca.css') < r.text.index('static/tema.css')
    assert 'fuentes/playfair-latin.woff2' in r.text          # el preload
    assert 'erode' not in r.text.lower()
    assert 'fonts.googleapis' not in r.text
    import os
    with open(os.path.join(os.path.dirname(app.root_path), os.path.basename(app.root_path),
                           'static', 'marca.css'), encoding='utf-8') as f:
        assert 'Playfair' in f.read()
```

Los tests que juntan el CSS de la página para revisar colores tienen que leer también `static/marca.css` y `static/tema.css`, porque el color ya no está en un `<style>` del HTML. Donde hoy se hace algo como `css = re.findall(r'<style>(.*?)</style>', r.text, re.S)`, sumar la lectura de esos dos archivos con `open()` desde `app.root_path` + `static/`.

- [ ] **Paso 2: Correrlos y verificar que fallan**

Correr: `python -m pytest -q -p no:cacheprovider tests/test_publico_tema.py`
Esperado: FALLAN, porque `static/tema.css` no existe y todavía está Erode.

- [ ] **Paso 3: Mover el `<style>` a `static/tema.css`**

1. Copiar el contenido que va entre `<style>` y `</style>` de `base.html` a `static/tema.css`, con este encabezado:

   ```css
   /* ============================================================
      SENTIDA · el tema de la tienda (la cara de la v6 del sitio).
      Los colores y las fuentes NO van acá: vienen de marca.css, la copia
      de sentida-site/comun/marca.css (flask sincronizar-marca).
      ============================================================ */
   ```

2. En `tema.css`, borrar los cinco `@font-face` y, del `:root`, todas las líneas de color y de fuente (`--blanco` … `--velo`, `--display`, `--ui`). Dejar solo los tokens de maqueta (`--lateral`, `--ancho`, `--cab` y los que no sean color ni fuente).
3. Reemplazar cualquier `{{ url_for(...) }}` que haya quedado dentro del CSS por una ruta relativa a `static/` (por ejemplo, `url("logos/sello.svg")`). Un `.css` estático no pasa por Jinja.
4. Reemplazar hex y rgba sueltos por sus tokens, con la misma tabla del Paso 6 de la Tarea 2.

- [ ] **Paso 4: El `<head>` de `base.html`**

Reemplazar las dos líneas de preload y el bloque `<style>…</style>` por:

```html
<link rel="preload" href="{{ url_for('static', filename='fuentes/playfair-latin.woff2') }}" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{{ url_for('static', filename='fuentes/montserrat-latin.woff2') }}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{{ url_for('static', filename='marca.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='tema.css') }}">
```

`<meta name="theme-color">` pasa a `#FCF9F2`, y `<link rel="icon">` apunta a `logos/favicon.svg` (la copia nueva). Actualizar también el comentario de arriba de `base.html` (líneas 1 a 17): tema v6, Playfair y los colores en `marca.css`.

- [ ] **Paso 5: Correr todo**

Correr: `python -m pytest -q -p no:cacheprovider`
Esperado: PASAN todos. Si alguno fallaba porque buscaba `logos/logo-sentida.svg`, cambiarlo a `logos/logo.svg`; la cabecera se rehace en la Tarea 6.

- [ ] **Paso 6: Commit**

```bash
git add static/tema.css templates/themes/sentida/base.html tests/test_publico_tema.py
git commit -m "tienda: el tema pasa a static/tema.css y usa la marca del sitio (Playfair, colores del logo)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarea 6: La cabecera, la cinta y el pie de la v6 en la tienda

**Archivos:**
- Modificar: `templates/themes/sentida/base.html` (el `<header class="cab">`, la cinta, el `<footer class="pie">` y el `<script>` del menú).
- Crear: `static/cabecera.js` (el menú del celular y la pausa de la cinta: el mismo código que `sentida-site/comun/menu.js`).
- Modificar: `static/tema.css` (las reglas de `.cab`, `.marquesina`, `.pie` y el menú: copiarlas de `sentida-site/comun/base.css` y reemplazar las de la v4).
- Test: `tests/test_publico_tema.py`.

**Interfaces:**
- Consume: `static/logos/logo.svg`, `logo-claro.svg` y `sello.svg` (Tarea 4), y `sitio` y `menu` del context processor (`publico/__init__.py`).
- Produce: `.cab` con `.cab-marca img.marca-logo`, `nav.cab-nav` con cuatro enlaces, `.marquesina` con `.marquesina-pausa` y `.pie` con `.pie-logo` y `.pie-sello`.

- [ ] **Paso 1: Escribir los tests que fallan**

```python
# agregar a tests/test_publico_tema.py
def test_la_cabecera_es_la_del_sitio(client, base, app):
    with app.app_context():
        _cat('Tortas', 'tortas')
        _cat('Pastelería', 'pasteleria')
    r = client.get('/catalogo?cat=tortas')
    cab = r.text.split('<header class="cab">', 1)[1].split('</header>', 1)[0]
    nav = cab.split('class="cab-nav"', 1)[1].split('</nav>', 1)[0]
    assert [t.strip() for t in re.findall(r'>([^<>]+)</a>', nav)] == \
        ['Nuestras tortas', 'Armá tu torta', 'Pastelería', 'Nosotras']
    assert 'href="/catalogo?cat=tortas" aria-current="page"' in nav
    assert 'logos/logo.svg' in cab and 'alt="SENTIDA"' in cab
    assert 'Decoradas' not in r.text and 'Inicio de la tienda' not in r.text


def test_la_cinta_con_pausa_y_el_pie_nuevo(client, base):
    r = client.get('/catalogo')
    assert 'class="marquesina"' in r.text and 'class="marquesina-pausa"' in r.text
    assert 'aria-label="Pausar la cinta"' in r.text
    assert 'static/cabecera.js' in r.text
    pie = r.text.split('<footer class="pie"', 1)[1]
    assert 'logos/logo-claro.svg' in pie and 'logos/sello.svg' in pie
```

- [ ] **Paso 2: Correrlos y verificar que fallan**

Correr: `python -m pytest -q -p no:cacheprovider tests/test_publico_tema.py -k "cabecera or cinta"`
Esperado: FALLAN.

- [ ] **Paso 3: La cabecera nueva en `base.html`**

Reemplazar todo el `<header class="cab">…</header>` por lo siguiente (mismo marcado que `cabecera()` del sitio, con los enlaces de la tienda):

```html
{%- set tortas = url_for('publico.catalogo', cat='tortas') -%}
{%- set pasteleria = url_for('publico.catalogo', cat='pasteleria') -%}
<header class="cab">
  <div class="cab-in">
    <a class="cab-marca" href="{{ sitio }}" aria-label="{{ nombre }}, inicio"><img class="marca-logo" src="{{ url_for('static', filename='logos/logo.svg') }}" alt="SENTIDA" width="132" height="36"></a>
    <nav class="cab-nav" aria-label="Secciones">
      <a href="{{ tortas }}"{% if cat_actual == 'tortas' %} aria-current="page"{% endif %}>Nuestras tortas</a><a href="{{ sitio }}arma-tu-torta/">Armá tu torta</a><a href="{{ pasteleria }}"{% if cat_actual == 'pasteleria' %} aria-current="page"{% endif %}>Pastelería</a><a href="{{ sitio }}nosotras/" class="solo-ancho">Nosotras</a>
    </nav>
    <div class="cab-acc">
      {% if cliente %}
      <a class="cab-cuenta" href="{{ url_for('publico.mis_pedidos') }}"{% if en_cuenta %} aria-current="page"{% endif %}>{{ cliente.nombre }}</a>
      {% else %}
      <a class="cab-cuenta" href="{{ url_for('publico.login') }}"{% if en_cuenta %} aria-current="page"{% endif %}>Ingresar</a>
      {% endif %}
      <a class="mi-pedido" href="{{ url_for('publico.carrito_ver') }}"><svg class="ico" aria-hidden="true" focusable="false"><use href="#i-bolsa"/></svg><span class="mi-pedido-t">Mi pedido</span><span class="mi-pedido-n js-cart-count{% if not carrito_cant %} js-off{% endif %}">{{ carrito_cant or '' }}</span></a>
      <details class="menu">
        <summary><span class="menu-abrir">Menú</span><span class="menu-cerrar">Cerrar</span><svg class="ico menu-i-abrir" aria-hidden="true" focusable="false"><use href="#i-menu"/></svg><svg class="ico menu-i-cerrar" aria-hidden="true" focusable="false"><use href="#i-cerrar"/></svg></summary>
        <nav aria-label="Menú">
          <a href="{{ tortas }}"{% if cat_actual == 'tortas' %} aria-current="page"{% endif %}>Nuestras tortas</a>
          <a href="{{ sitio }}arma-tu-torta/">Armá tu torta</a>
          <a href="{{ pasteleria }}"{% if cat_actual == 'pasteleria' %} aria-current="page"{% endif %}>Pastelería</a>
          <a href="{{ sitio }}nosotras/">Nosotras</a>
          {% if cliente %}<a class="chico" href="{{ url_for('publico.mis_pedidos') }}">Mis pedidos</a>{% else %}<a class="chico" href="{{ url_for('publico.login') }}">Ingresar</a>{% endif %}
          <a class="chico" href="{{ url_for('publico.contacto') }}">Contacto</a>
          <a class="chico" href="{{ sitio }}">Volver a {{ nombre }}</a>
        </nav>
      </details>
    </div>
  </div>
</header>
<div class="marquesina"><div class="marquesina-pista" aria-hidden="true"><span>Lo soñás, lo creamos <i></i> Pastelería artesanal <i></i> Tortas a medida <i></i> Hecho a mano <i></i></span><span>Lo soñás, lo creamos <i></i> Pastelería artesanal <i></i> Tortas a medida <i></i> Hecho a mano <i></i></span></div><button type="button" class="marquesina-pausa" aria-pressed="false" aria-label="Pausar la cinta"><svg class="ico ico-pausar" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M9 6v12M15 6v12"/></svg><svg class="ico ico-seguir" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M8 5.5v13l10-6.5-10-6.5Z"/></svg></button></div>
```

La búsqueda del menú del celular sale de acá y queda solo en la barra del catálogo (Tarea 8).

- [ ] **Paso 4: El pie nuevo**

Reemplazar `<footer class="pie" id="pie">…</footer>` por:

```html
<footer class="pie" id="pie">
  <div class="pie-in envoltorio">
    <div class="pie-marca">
      <img class="pie-logo" src="{{ url_for('static', filename='logos/logo-claro.svg') }}" alt="SENTIDA" width="150" height="41" loading="lazy">
      <p class="pie-lema display">Lo soñás, lo creamos.</p>
    </div>
    <nav class="pie-links" aria-label="Pie">
      <div>
        <p class="pie-eti">Explorá</p>
        <ul role="list">
          <li><a href="{{ tortas }}">Nuestras tortas</a></li>
          <li><a href="{{ sitio }}arma-tu-torta/">Armá tu torta</a></li>
          <li><a href="{{ pasteleria }}">Pastelería</a></li>
          <li><a href="{{ sitio }}nosotras/">Nosotras</a></li>
          <li><a href="{{ url_for('publico.contacto') }}">Contacto</a></li>
        </ul>
      </div>
      <div>
        <p class="pie-eti">Tu pedido</p>
        <ul role="list">
          <li><a href="{{ url_for('publico.carrito_ver') }}">Mi pedido</a></li>
          {% if cliente %}<li><a href="{{ url_for('publico.mis_pedidos') }}">Mis pedidos</a></li>{% else %}<li><a href="{{ url_for('publico.login') }}">Ingresar</a></li>{% endif %}
          {% if wa %}<li><a href="https://wa.me/{{ wa }}" target="_blank" rel="noopener">WhatsApp · {{ cfg.whatsapp | telefono }}</a></li>{% endif %}
          <li><a href="https://www.instagram.com/sentidapasteleria/" target="_blank" rel="noopener">@sentidapasteleria</a></li>
        </ul>
        <p>{% if cfg.direccion %}{{ cfg.direccion }}<br>{% endif %}{{ txt_envio }}<br>{{ txt_pago }}</p>
      </div>
    </nav>
    <img class="pie-sello" src="{{ url_for('static', filename='logos/sello.svg') }}" alt="" width="105" height="105" loading="lazy">
  </div>
  <div class="pie-fin envoltorio"><span>© 2026 {{ nombre }} · Hecho a mano</span><a href="{{ sitio }}">Volver a {{ nombre }}</a></div>
</footer>
```

- [ ] **Paso 5: El JS de la cabecera y la cinta**

Crear `static/cabecera.js` con el contenido de `sentida-site/comun/menu.js` tal cual, porque tiene las dos IIFE: el menú y la cinta. En el `<script>` inline de `base.html`, borrar el bloque del menú (desde `/* El menú del celular es un <details>` hasta el final de su IIFE) y sumar, antes de `{% block scripts %}`:

```html
<script src="{{ url_for('static', filename='cabecera.js') }}" defer></script>
```

- [ ] **Paso 6: El CSS de la cabecera, la cinta y el pie**

En `static/tema.css`, reemplazar las reglas de la v4 de `.cab`, `.cab-*`, `.menu*`, `.pie*` y la cinta por las del sitio. Copiarlas de `sentida-site/comun/base.css`, en los bloques «Cabecera», «Marquesina» y «Pie», incluidas sus `@media`. Si `.cab-cuenta` y `.menu nav a.chico` todavía no tienen reglas, sumarlas:

```css
.cab-cuenta{display:inline-flex; align-items:center; min-height:44px; font-size:11px; font-weight:600; letter-spacing:.18em; text-transform:uppercase}
.cab-cuenta[aria-current="page"]{text-decoration:underline; text-decoration-thickness:1px; text-underline-offset:7px}
.menu nav a.chico{font-family:var(--ui); font-size:13px; font-weight:600; letter-spacing:.12em; text-transform:uppercase; min-height:48px}
@media (max-width:899px){ .cab-cuenta{display:none} }
```

- [ ] **Paso 7: Correr y mirar**

Correr: `python -m pytest -q -p no:cacheprovider`
Esperado: PASAN todos. Levantar `python local.py`, abrir `http://127.0.0.1:5050/catalogo` en 1440 y 390 y comparar la cabecera, la cinta y el pie con el sitio v6: tienen que verse iguales.

- [ ] **Paso 8: Commit**

```bash
git add templates/themes/sentida/base.html static/cabecera.js static/tema.css tests/test_publico_tema.py
git commit -m "tienda: cabecera, cinta con pausa y pie de la v6, con el logo nuevo

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarea 7: La tienda entra directo al catálogo (sin home)

**Archivos:**
- Modificar: `publico/home.py` (queda solo la redirección).
- Borrar: `templates/themes/sentida/home.html`, `static/img/hero.webp`, `static/img/idea.webp` y `static/img/tortas-decoradas.webp`.
- Modificar: `tests/test_publico_home.py` (se reescribe) y cualquier test que haga `client.get('/')` esperando 200.

**Interfaces:**
- Produce: `GET /` → 302 a `/catalogo`, conservando el query string. El endpoint `publico.home` sigue existiendo (lo usan `url_for` en templates viejos y en el panel).

- [ ] **Paso 1: Reescribir el test**

```python
# tests/test_publico_home.py
"""La tienda no tiene home: entra directo al catálogo (spec del 28/09)."""


def test_la_raiz_va_al_catalogo(client, base):
    r = client.get('/')
    assert r.status_code == 302
    assert r.headers['Location'].endswith('/catalogo')


def test_la_raiz_conserva_la_busqueda(client, base):
    r = client.get('/?q=lima')
    assert r.headers['Location'].endswith('/catalogo?q=lima')


def test_no_quedan_las_imagenes_del_home():
    import os
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for nombre in ('hero.webp', 'idea.webp', 'tortas-decoradas.webp'):
        assert not os.path.exists(os.path.join(raiz, 'static', 'img', nombre))
```

- [ ] **Paso 2: Correrlo y verificar que falla**

Correr: `python -m pytest -q -p no:cacheprovider tests/test_publico_home.py`
Esperado: FALLA, porque hoy `/` da 200.

- [ ] **Paso 3: `publico/home.py`**

```python
"""La tienda no tiene home: el sitio (sentida-site) es la portada y la tienda
entra directo al catálogo. El endpoint `publico.home` se queda porque hay
enlaces que lo usan; solo redirige, conservando la búsqueda si vino."""
from flask import redirect, request, url_for

from publico import bp


@bp.get('/', endpoint='home')
def home():
    return redirect(url_for('publico.catalogo', **request.args.to_dict()))
```

Borrar `home.html` y las tres imágenes. Buscar referencias con `grep -rn "home.html\|static/img/\|filename='img/" templates publico admin`: no tiene que quedar ninguna en la parte pública. El panel de banners puede seguir existiendo sin uso.

- [ ] **Paso 4: Arreglar los tests que pedían `/`**

Correr: `python -m pytest -q -p no:cacheprovider`

Donde un test pedía `client.get('/')` para mirar algo del tema (por ejemplo, en `test_publico_tema.py` o `test_seguridad.py`), cambiarlo a `client.get('/catalogo')`. En `_todas_las_paginas`, sacar `'/'` de la lista. Esperado al final: PASAN todos.

- [ ] **Paso 5: Commit**

```bash
git add -A publico/home.py templates/themes/sentida static/img tests
git commit -m "tienda: sin home, la tienda entra directo al catálogo

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarea 8: El catálogo con la cabecera y las tarjetas de la v6

**Archivos:**
- Modificar: `templates/publico/catalogo.html` (la cabecera del listado, la barra de búsqueda y orden, y se sacan «Solo ofertas» y grilla/lista).
- Modificar: `templates/publico/_card.html` (la tarjeta `.producto` de la v6).
- Modificar: `static/tema.css` (`.tienda-cab`, `.productos`, `.producto*`: copiar de `sentida-site/comun/tienda.css`).
- Modificar: `templates/publico/_catalogo_js.html` (quitar lo que manejaba los toggles de oferta y modo).
- Test: `tests/test_publico_catalogo.py`.

**Interfaces:**
- Consume: `datos.items` de `models.catalogo.publicados()` (cada card con `slug`, `nombre`, `descripcion`, `foto`, `precio`, `presentaciones`, `hay`, `desde` e `id`).
- Produce: `_card.html::card(p)`. Si el producto obliga a elegir, el «+» es un `<a class="producto-agregar" href="{ficha}">`; si no, es un `<form>` que agrega la presentación que viene marcada. La Tarea 13 cambia qué cuenta como «obliga a elegir».

- [ ] **Paso 1: Escribir los tests que fallan**

```python
# agregar a tests/test_publico_catalogo.py
import re

import db


def _cat(nombre, slug):
    return db.insertar('INSERT INTO categorias (nombre, slug) VALUES (?, ?)', [nombre, slug])


def _prod(nombre, slug, cat, precio=None):
    return db.insertar('INSERT INTO productos (nombre, slug, categoria_id, precio, stock, publicado) '
                       'VALUES (?, ?, ?, ?, 5, 1)', [nombre, slug, cat, precio])


def test_la_cabecera_del_catalogo_es_la_de_la_v6(client, base, app):
    with app.app_context():
        _prod('Key Lime Pie', 'key-lime-pie', _cat('Tortas', 'tortas'))
    r = client.get('/catalogo?cat=tortas')
    assert 'class="eti con-linea">Las de la casa<' in r.text
    assert re.search(r'<h1 class="display"[^>]*>Nuestras tortas\.</h1>', r.text)
    r = client.get('/catalogo?cat=pasteleria')
    assert re.search(r'<h1 class="display"[^>]*>Pastelería\.</h1>', r.text)
    assert 'Para regalar y compartir' in r.text


def test_la_tarjeta_es_la_de_la_v6(client, base, app):
    with app.app_context():
        _prod('Key Lime Pie', 'key-lime-pie', _cat('Tortas', 'tortas'))
    r = client.get('/catalogo')
    tarjeta = r.text.split('class="producto"', 1)[1].split('</li>', 1)[0]
    assert 'class="producto-foto' in tarjeta
    assert 'Precio a consultar' in tarjeta
    assert 'aria-label="Agregar al pedido: Key Lime Pie"' in tarjeta
    assert 'Solo ofertas' not in r.text and 'i-grilla' not in r.text
    assert 'name="q"' in r.text and 'name="orden"' in r.text
```

- [ ] **Paso 2: Correrlos y verificar que fallan**

Correr: `python -m pytest -q -p no:cacheprovider tests/test_publico_catalogo.py`
Esperado: FALLAN.

- [ ] **Paso 3: La cabecera del catálogo**

En `catalogo.html`, el bloque de título pasa a lo siguiente. Los textos vienen de un diccionario al principio del template:

```html
{%- set CABS = {
  'tortas': ('Las de la casa', 'Nuestras tortas.', 'Las tortas de la casa, hechas a mano y por encargo. Sumalas a tu pedido y te confirmamos precio y disponibilidad.'),
  'pasteleria': ('Para regalar y compartir', 'Pastelería.', 'Alfajores, galletas, cupcakes, shots y cuadraditos dulces, para regalar o para la mesa dulce.'),
} -%}
{%- set eti, titulo, bajada = CABS.get(cat_activa, ('Todo lo que hacemos', 'Catálogo.', 'Todo lo hacemos a mano y por encargo. Sumalo a tu pedido y te confirmamos precio y disponibilidad.')) -%}
<div class="tienda-cab">
  <div><p class="eti con-linea">{{ eti }}</p>
  <h1 class="display" id="tienda-t">{{ titulo }}</h1></div>
  <p>{{ bajada }}</p>
</div>
<form class="tienda-barra js-buscar" action="{{ url_for('publico.catalogo') }}" method="get" role="search">
  {% if cat_activa %}<input type="hidden" name="cat" value="{{ cat_activa }}">{% endif %}
  <label class="sr" for="buscar-t">Buscar</label>
  <input type="search" id="buscar-t" name="q" class="js-buscar-campo" value="{{ q }}" placeholder="Buscar: torta, alfajores, cheesecake…" autocomplete="off">
  <label class="sr" for="orden-t">Ordenar</label>
  <select id="orden-t" name="orden" onchange="this.form.submit()">
    {% for clave, texto in ordenes.items() %}<option value="{{ clave }}"{% if clave == orden %} selected{% endif %}>{{ texto }}</option>{% endfor %}
  </select>
</form>
```

Sacar del template los controles «Solo ofertas», «Solo disponibles» y grilla/lista, y del `_catalogo_js.html` el código que los escuchaba. La lógica de `publicados()` no se toca.

- [ ] **Paso 4: La tarjeta de la v6 en `_card.html`**

Reemplazar la macro `card(p)` por lo siguiente, que es el mismo marcado que `tarjeta()` de `sentida-site/herramientas/generar_tienda.py` más los datos de la tienda:

```html
{% macro card(p, nivel=2) -%}
{%- set url = url_for('publico.ficha', slug=p.slug, presentacion=p.presentacion_elegida) -%}
{%- set elegir = p.hay and p.desde -%}
<li class="producto{% if not p.hay %} agotado{% endif %}" id="{{ p.slug }}">
  <div class="producto-foto{% if not p.foto %} sin-foto{% endif %}">
    <a href="{{ url }}" class="producto-foto-link" tabindex="-1" aria-hidden="true">
      {% if p.foto %}<img src="{{ url_for('static', filename='fotos/' ~ p.foto) }}" alt="" loading="lazy" decoding="async">{% else %}<span class="display">{{ p.nombre }}</span>{% endif %}
    </a>
    {% if p.oferta_activa %}<span class="producto-marca">Oferta</span>{% endif %}
    {% if elegir %}
    <a class="producto-agregar" href="{{ url }}" aria-label="Elegir opciones: {{ p.nombre }}">+</a>
    {% elif p.hay %}
    <form method="post" action="{{ url_for('publico.carrito_agregar') }}" data-nombre="{{ p.nombre }}">
      {{ campo_csrf() }}
      <input type="hidden" name="producto_id" value="{{ p.id }}">
      <input type="hidden" name="cantidad" value="{{ p.cantidad_minima or 1 }}">
      <button type="submit" class="producto-agregar" aria-label="Agregar al pedido: {{ p.nombre }}">+</button>
    </form>
    {% endif %}
  </div>
  <p class="producto-meta"><span class="producto-tipo">{{ p.categoria_nombre or '' }}</span></p>
  <h{{ nivel }} class="display"><a href="{{ url }}" class="producto-nombre">{{ p.nombre }}</a></h{{ nivel }}>
  {% if p.descripcion %}<p class="producto-desc">{{ p.descripcion }}</p>{% endif %}
  <p class="producto-precio">{% if p.precio is none %}Precio a consultar{% else %}{% if p.desde %}Desde {% endif %}{{ p.precio | plata }}{% endif %}</p>
  {% if not p.hay %}<p class="producto-agotado">Agotado por ahora</p>{% endif %}
</li>
{%- endmacro %}
```

`p.categoria_nombre` no existe todavía. Sumarlo en `models/catalogo.py`:
1. En el `SELECT` de `publicados()`, agregar `COALESCE(s.nombre, c.nombre) AS categoria_nombre` después de `ci.estado AS item_estado`.
2. En `_card(fila)`, agregar `'categoria_nombre': fila['categoria_nombre'],`.

`_cards_productos.html` y `ficha.html` («Seguir mirando») llaman a `card(...)`: la lista que las contiene pasa de `<div class="productos">` a `<ul class="productos" role="list">`.

- [ ] **Paso 5: El CSS**

En `static/tema.css`, reemplazar las reglas de `.tienda-cab`, `.productos`, `.producto`, `.producto-*` y `.sin-foto` por las de `sentida-site/comun/tienda.css` (tarjeta, meta, «+», `.en-pedido`, `.marcada` y las `@media`). Sumar la barra:

```css
.tienda-barra{display:flex; flex-wrap:wrap; gap:10px; margin:0 0 clamp(24px,4vh,40px)}
.tienda-barra input[type=search]{flex:1 1 260px; min-height:44px; padding:10px 12px; font:inherit; font-size:15px; color:var(--marron); background:var(--blanco); border:1px solid var(--linea); border-radius:2px}
.tienda-barra select{min-height:44px; padding:0 12px; font:inherit; font-size:13px; color:var(--marron); background:var(--blanco); border:1px solid var(--linea); border-radius:2px}
.producto-foto-link{display:block; width:100%; height:100%}
.producto-agregar{text-decoration:none}
.producto.agotado .producto-foto img{opacity:.55}
.producto-agotado{margin-top:4px; font-size:12px; color:var(--marron-medio)}
```

- [ ] **Paso 6: Correr, mirar y ajustar**

Correr: `python -m pytest -q -p no:cacheprovider`
Esperado: PASAN todos. Algunos tests viejos buscaban «Agregar al pedido» en un botón de texto o «Ver presentaciones»: cambiarlos para buscar el `aria-label` del «+» (`Agregar al pedido: …` o `Elegir opciones: …`). En `test_publico_presentaciones.py::test_la_card_no_agrega_al_carrito_sin_elegir`, la aserción pasa a `'Elegir opciones' in r.text`.

Capturas de `/catalogo?cat=tortas` y `/catalogo?cat=pasteleria` en 1440 y 390, comparadas con `tortas/` del sitio v6.

- [ ] **Paso 7: Commit**

```bash
git add templates/publico static/tema.css models/catalogo.py tests
git commit -m "tienda: el catálogo con la cabecera y las tarjetas de la v6

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarea 9: Las demás páginas públicas con los componentes de la v6

**Archivos:**
- Modificar: `templates/publico/carrito.html`, `checkout.html`, `checkout_ok.html`, `cuenta_login.html`, `cuenta_registro.html`, `mis_pedidos.html` y `contacto.html`.
- Modificar: `static/tema.css` (campos, títulos de página y notas).
- Test: `tests/test_publico_tema.py`.

**Interfaces:**
- Consume: las clases de la v6 (`.eti.con-linea`, `h1.display`, `.btn-1`, `.btn-2`, `.cf`, `.cf-t`, `.ticket`, `.papel` y `.ticket-lineas`), definidas en `static/tema.css`.
- Produce: nada nuevo para otras tareas. Es solo presentación.

- [ ] **Paso 1: Escribir el test que falla**

```python
# agregar a tests/test_publico_tema.py
def test_cada_pagina_tiene_su_cabecera_v6(client, base, app, post):
    paginas = _todas_las_paginas(client, app, post)
    for url in ['/carrito', '/checkout', '/contacto', '/ingresar', '/registro']:
        r = paginas[url]
        assert re.search(r'<p class="eti con-linea">[^<]+</p>\s*<h1 class="display"', r.text), url
```

- [ ] **Paso 2: Correrlo y verificar que falla**

Correr: `python -m pytest -q -p no:cacheprovider tests/test_publico_tema.py -k cabecera_v6`
Esperado: FALLA.

- [ ] **Paso 3: Una cabecera de página por template**

En cada template, el título de la página pasa a este patrón, con la etiqueta y el título de la tabla:

```html
<div class="pagina-cab envoltorio">
  <p class="eti con-linea">{ETIQUETA}</p>
  <h1 class="display">{TÍTULO}</h1>
</div>
```

| Template | Etiqueta | Título |
|---|---|---|
| `carrito.html` | Hacé tu pedido | Tu pedido. |
| `checkout.html` | Casi listo | ¿Cuándo pasás a buscarlo? |
| `checkout_ok.html` | Pedido n.º {{ pedido.numero }} | ¡Gracias! |
| `cuenta_login.html` | Tu cuenta | Ingresar. |
| `cuenta_registro.html` | Tu cuenta | Crear tu cuenta. |
| `mis_pedidos.html` | Tu cuenta | Mis pedidos. |
| `contacto.html` | Escribinos | Contacto. |

No cambiar nada más del contenido de cada página: formularios, textos, cálculos y enlaces quedan igual.

- [ ] **Paso 4: Los campos y la cabecera en `tema.css`**

```css
.pagina-cab{padding-block:clamp(40px,7vh,80px) clamp(20px,4vh,36px)}
.pagina-cab .eti{margin-bottom:18px}
.pagina-cab h1{font-size:clamp(2.6rem,5vw,4.3rem); line-height:1.05; letter-spacing:-.03em}
.cf{display:flex; flex-direction:column; gap:6px; width:100%; min-width:0; margin:0; padding:0; border:0}
.cf-t{font-size:11px; font-weight:600; letter-spacing:.16em; text-transform:uppercase; line-height:1.5; color:var(--marron-medio)}
.cf input[type=text],.cf input[type=email],.cf input[type=tel],.cf input[type=password],.cf textarea,.cf select{width:100%; min-height:48px; padding:10px 12px; font-family:var(--ui); font-size:16px; color:var(--marron); background:var(--blanco); border:1px solid var(--marron); border-radius:2px}
```

Los formularios que ya usan `.campo` u otra clase propia pasan a `.cf` y `.cf-t` en el label, sin tocar los `name` ni los `id`.

- [ ] **Paso 5: Correr y mirar**

Correr: `python -m pytest -q -p no:cacheprovider`
Esperado: PASAN todos. Sacar capturas de las siete páginas en 1440 y 390 y guardarlas en `docs/capturas/fase3/`, con el nombre de la página y el ancho.

- [ ] **Paso 6: Commit**

```bash
git add templates/publico static/tema.css tests docs/capturas/fase3
git commit -m "tienda: carrito, reserva, cuenta y contacto con los componentes de la v6

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

## Parte 3 — Sabores, medidas, anticipación y la ficha

### Tarea 10: El esquema: sabor, medida, anticipación y texto provisorio

**Archivos:**
- Modificar: `schema.sql`. En `productos`: `sabor`, `medida` y `medida_nota`. En `categorias`: `anticipacion_horas` y `anticipacion_texto`. En `catalogo_items`: `texto_provisorio`.
- Modificar: `db.py` (`init_db` suma las columnas que falten a una base vieja).
- Test: `tests/test_schema.py`.

**Interfaces:**
- Produce:
  - `productos.sabor TEXT`, `productos.medida TEXT` y `productos.medida_nota TEXT`;
  - `categorias.anticipacion_horas INTEGER NOT NULL DEFAULT 0` y `categorias.anticipacion_texto TEXT`;
  - `catalogo_items.texto_provisorio INTEGER NOT NULL DEFAULT 0`;
  - `db.COLUMNAS_NUEVAS: list[tuple[str, str, str]]` (tabla, columna, definición).

- [ ] **Paso 1: Escribir los tests que fallan**

```python
# agregar a tests/test_schema.py
import sqlite3

import db


def _columnas(tabla):
    return {f['name'] for f in db.query(f'PRAGMA table_info({tabla})')}


def test_las_columnas_nuevas_existen(base):
    assert {'sabor', 'medida', 'medida_nota'} <= _columnas('productos')
    assert {'anticipacion_horas', 'anticipacion_texto'} <= _columnas('categorias')
    assert 'texto_provisorio' in _columnas('catalogo_items')


def test_una_base_vieja_recibe_las_columnas_al_arrancar(app, tmp_path):
    vieja = tmp_path / 'vieja.db'
    con = sqlite3.connect(vieja)
    con.executescript('CREATE TABLE categorias (id INTEGER PRIMARY KEY, nombre TEXT NOT NULL, '
                      'slug TEXT NOT NULL UNIQUE, orden INTEGER NOT NULL DEFAULT 0, '
                      'activa INTEGER NOT NULL DEFAULT 1);')
    con.close()
    app.config['DB_PATH'] = str(vieja)
    with app.app_context():
        db.init_db()
        assert 'anticipacion_horas' in _columnas('categorias')
        db.init_db()                     # dos veces no rompe
```

- [ ] **Paso 2: Correrlos y verificar que fallan**

Correr: `python -m pytest -q -p no:cacheprovider tests/test_schema.py`
Esperado: FALLAN.

- [ ] **Paso 3: Sumar las columnas a `schema.sql`**

En `CREATE TABLE productos`, después de `etiqueta TEXT,`:

```sql
    -- Las dos caras de una presentación, para que la ficha arme dos grupos de
    -- opciones en vez de una lista larga: 'De frutillas' y '½ docena'. NULL =
    -- el producto no se elige por eso. `etiqueta` sigue siendo el texto entero
    -- («De frutillas · ½ docena»), el que congela pedidos_items.
    sabor             TEXT,
    medida            TEXT,
    -- Lo que la ficha dice debajo de esa medida: «Tamaño y precio a consultar
    -- por WhatsApp» en la torta más grande.
    medida_nota       TEXT,
```

En `CREATE TABLE categorias`, después de `activa …`:

```sql
    -- Cuánto antes hay que pedir: la reserva no ofrece días de retiro antes de
    -- ahora + la más larga de las categorías del pedido. El texto es el sello
    -- de la ficha («Pedila con 48 h»).
    anticipacion_horas INTEGER NOT NULL DEFAULT 0 CHECK (anticipacion_horas >= 0),
    anticipacion_texto TEXT
```

(Cuidado con la coma de la línea `activa`.)

En `CREATE TABLE catalogo_items`, antes de `creado`:

```sql
    -- 1 = la descripción la escribió TRAMA a partir de las fotos y todavía no
    -- la revisaron Anto y Nadia. El panel lo avisa; guardar el producto lo apaga.
    texto_provisorio  INTEGER NOT NULL DEFAULT 0 CHECK (texto_provisorio IN (0, 1)),
```

- [ ] **Paso 4: Las columnas de una base vieja en `db.py`**

```python
# Columnas que se sumaron después de que existieran bases en uso (local.db, la
# semilla de Render). `CREATE TABLE IF NOT EXISTS` no agrega columnas a una
# tabla que ya existe: esto sí, y es idempotente.
COLUMNAS_NUEVAS = [
    ('productos', 'sabor', 'TEXT'),
    ('productos', 'medida', 'TEXT'),
    ('productos', 'medida_nota', 'TEXT'),
    ('categorias', 'anticipacion_horas', 'INTEGER NOT NULL DEFAULT 0'),
    ('categorias', 'anticipacion_texto', 'TEXT'),
    ('catalogo_items', 'texto_provisorio', 'INTEGER NOT NULL DEFAULT 0'),
]


def _sumar_columnas():
    con = get_db()
    for tabla, columna, definicion in COLUMNAS_NUEVAS:
        existe = con.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", [tabla]).fetchone()
        if not existe:
            continue
        cols = {f[1] for f in con.execute(f'PRAGMA table_info({tabla})')}
        if columna not in cols:
            con.execute(f'ALTER TABLE {tabla} ADD COLUMN {columna} {definicion}')
```

`init_db()` queda así:

```python
def init_db():
    """Crea el esquema y suma las columnas nuevas a una base vieja. Idempotente."""
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')
    con = get_db()
    # Primero las columnas: schema.sql puede traer índices o triggers que las usan.
    _sumar_columnas()
    with open(ruta, encoding='utf-8') as f:
        con.executescript(f.read())
    _sumar_columnas()
```

- [ ] **Paso 5: Correr todo**

Correr: `python -m pytest -q -p no:cacheprovider`
Esperado: PASAN todos.

- [ ] **Paso 6: Commit**

```bash
git add schema.sql db.py tests/test_schema.py
git commit -m "ficha: sabor y medida en las presentaciones, anticipación por categoría y texto provisorio

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarea 11: `catalogo.json` con medidas, anticipación, sabores y textos provisorios (sitio)

**Archivos:**
- Modificar: `sentida-site/datos/catalogo.json`.
- Test: `sentida-site/tests/tienda/test_generador.py`.

**Interfaces:**
- Produce el formato que lee el importador (Tarea 12):
  - `secciones.<clave>.medidas: [{"nombre": str, "nota"?: str}]`;
  - `secciones.<clave>.anticipacion_horas: int`;
  - `secciones.<clave>.anticipacion_texto: str`;
  - `productos[].variantes: [{"nombre": str, "foto": str}]` (ya existe);
  - `productos[].descripcion_larga: str`;
  - `productos[].texto_provisorio: bool`.

- [ ] **Paso 1: Escribir el test que falla**

```python
# agregar a sentida-site/tests/tienda/test_generador.py
import json
import pathlib

CATALOGO = pathlib.Path(__file__).resolve().parents[2] / "datos" / "catalogo.json"


def test_el_catalogo_trae_medidas_y_anticipacion():
    d = json.loads(CATALOGO.read_text(encoding="utf-8"))
    tortas, past = d["secciones"]["tortas"], d["secciones"]["pasteleria"]
    assert [m["nombre"] for m in tortas["medidas"]] == ["20 a 22 cm", "Más grande"]
    assert tortas["medidas"][1]["nota"] == "Tamaño y precio a consultar por WhatsApp"
    assert [m["nombre"] for m in past["medidas"]] == ["½ docena", "Docena"]
    assert (tortas["anticipacion_horas"], past["anticipacion_horas"]) == (48, 96)
    assert tortas["anticipacion_texto"] == "Pedila con 48 h"
    assert past["anticipacion_texto"] == "De 4 a 7 días, según el trabajo"


def test_cada_producto_visible_tiene_descripcion_larga():
    d = json.loads(CATALOGO.read_text(encoding="utf-8"))
    for p in d["productos"]:
        if p.get("visible", True):
            assert len(p.get("descripcion_larga", "")) > 40, p["slug"]
            assert p.get("texto_provisorio") is True, p["slug"]


def test_los_sabores_son_solo_los_que_se_ven():
    d = json.loads(CATALOGO.read_text(encoding="utf-8"))
    sabores = {p["slug"]: [v["nombre"] for v in p.get("variantes", [])] for p in d["productos"]}
    assert sabores["shots"] == ["Con flores", "De frutillas", "De maracuyá"]
    assert sabores["cuadraditos-dulces"] == ["Carrot cake"]
    assert all(not v for s, v in sabores.items() if s not in ("shots", "cuadraditos-dulces"))
```

- [ ] **Paso 2: Correrlo y verificar que falla**

Correr: `python -m pytest -q tests/tienda/test_generador.py`
Esperado: FALLA, con `KeyError: 'medidas'`.

- [ ] **Paso 3: Ampliar `catalogo.json`**

En `secciones.tortas` sumar:

```json
"medidas": [{"nombre": "20 a 22 cm"}, {"nombre": "Más grande", "nota": "Tamaño y precio a consultar por WhatsApp"}],
"anticipacion_horas": 48,
"anticipacion_texto": "Pedila con 48 h"
```

En `secciones.pasteleria`:

```json
"medidas": [{"nombre": "½ docena"}, {"nombre": "Docena"}],
"anticipacion_horas": 96,
"anticipacion_texto": "De 4 a 7 días, según el trabajo"
```

En cada producto visible, sumar `"texto_provisorio": true` y `"descripcion_larga"` con estos textos. Son provisorios: los escribió TRAMA mirando las fotos, en el tono de las chicas. Donde la descripción corta está vacía, completarla también con la que figura acá.

| slug | descripcion (solo si hoy está vacía) | descripcion_larga |
|---|---|---|
| key-lime-pie | — | Una tarta fresca y ácida: base crocante de galletitas, curd de lima hecho por nosotras y rosetas de crema chantilly con ralladura. Ideal para después de un almuerzo largo. |
| cheesecake-new-york | — | Nuestro cheesecake cremoso al estilo New York, horneado despacio sobre base de galletitas de vainilla, con salsa de frutos rojos y un copete de crema. |
| marquise | — | Base húmeda de brownie, una capa generosa de dulce de leche, crema chantilly y frutillas frescas arriba. De las que vuelven a pedir. |
| frutillas-con-crema | — | Un clásico que nunca falla: base sablée de vainilla, crema y frutillas frescas cortadas a mano, bien cargada. |
| sablee | — | Masa sablée de manteca, dulce de leche, crema chantilly y frutos rojos. Simple, rica y linda para la mesa. |
| pavlova-lima | — | Merengue crocante por fuera y suave por dentro, con crema, curd de lima y las frutas de la estación. Liviana y fresca. |
| choco-oreo | — | Capas de galletitas Oreo, dulce de leche y crema chantilly, terminada con galletitas enteras. Para los fanáticos del chocolate. |
| carrot-cake | Bizcochuelo de zanahoria especiado con frosting de queso crema. | Capas de bizcochuelo de zanahoria especiado y un frosting de queso crema bien cremoso. Húmeda, aromática y con el toque justo de dulce. |
| cheesecake-marroc | — | Cheesecake con cobertura de chocolate y trozos de Marroc. El postre para los que no se deciden entre cheesecake y bombón. |
| chocotorta | — | La de siempre, hecha como en casa: galletitas de chocolate y crema de dulce de leche, capa por capa, con cobertura de chocolate. |
| brownie-chantilly | Brownie húmedo con dulce de leche y crema chantilly. | Base de brownie húmedo, dulce de leche y crema chantilly, terminada con chocolate. Una torta de chocolate para compartir. |
| torta-matilda | Torta de chocolate con cobertura de ganache. | Bizcochuelo de chocolate húmedo y cobertura de ganache de chocolate en remolino, como la de la película. Para los que aman el chocolate. |
| torta-havannet | Dulce de leche y baño de chocolate, como el alfajor. | Inspirada en el havannet: base de galletita, mucho dulce de leche y un baño de chocolate que la envuelve. |
| alfajores-maicena | — | Alfajores de maicena tiernos, rellenos de dulce de leche y con coco rallado en el borde. Se venden por media docena o docena. |
| galletas-corazon | — | Galletas de manteca en forma de corazón, decoradas con glasé y con el mensaje que quieras escrito a mano. Para regalar. |
| galletas-tematicas | — | Galletas decoradas con la temática del cumpleaños, para acompañar la torta o para la mesa dulce. Nos contás la idea y la armamos. |
| galletas-decoradas | — | Galletas de manteca decoradas con pasta de azúcar y glasé: con el nombre, con personajes o con la temática que elijas. |
| cupcakes-decorados | — | Cupcakes esponjosos con frosting en la paleta que elijas y detalles decorados a mano. Lindos para una celebración chica. |
| cupcakes-tematicos | — | Cupcakes con figuras en pasta de azúcar según la temática del festejo. Nos pasás la idea y los armamos a medida. |
| shots | — | Postres en vaso para la mesa dulce: capas de crema y bizcochuelo con fruta, flores o maracuyá, según el sabor que elijas. |
| cuadraditos-dulces | — | Cuadraditos para la mesa dulce, en distintos sabores. Hoy te ofrecemos carrot cake con su frosting; pronto se suman más. |

Los productos con `"visible": false` (Pan dulce, Rosca de Pascua) no llevan estos campos.

- [ ] **Paso 4: Verificar que el generador lo ignora**

```bash
python herramientas/generar_tienda.py
git diff --stat tortas pasteleria index.html
```

Esperado: solo cambian las tarjetas cuya descripción corta estaba vacía (Carrot cake, Brownie, Matilda y Havannet), que ahora la muestran.

- [ ] **Paso 5: Correr los tests del sitio**

Correr: `python -m pytest -q tests/tienda tests/home`
Esperado: PASAN.

- [ ] **Paso 6: Commit**

```bash
git add datos/catalogo.json tortas pasteleria index.html tests/tienda/test_generador.py
git commit -m "v6: el catálogo con medidas, anticipación y descripciones provisorias

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarea 12: El importador arma las combinaciones sabor × medida (tienda)

**Archivos:**
- Modificar: `servicios/importar_catalogo.py`.
- Modificar: `admin/productos.py` (guardar el producto apaga `texto_provisorio`) y `templates/admin/producto_editar.html` (el aviso).
- Test: `tests/test_importar_catalogo.py`.

**Interfaces:**
- Consume: el formato de `catalogo.json` de la Tarea 11 y las columnas de la Tarea 10.
- Produce: `importar_catalogo.combinaciones(producto_json, seccion_json) -> list[dict]`, donde cada dict tiene `sabor`, `medida`, `medida_nota`, `etiqueta` y `foto`, en orden: primero cada sabor y, dentro de cada sabor, cada medida. La primera combinación es la que viene marcada en la ficha.

- [ ] **Paso 1: Escribir los tests que fallan**

```python
# agregar a tests/test_importar_catalogo.py
import json

import db
from servicios import importar_catalogo as imp

CATALOGO = {
    "secciones": {
        "tortas": {"medidas": [{"nombre": "20 a 22 cm"},
                               {"nombre": "Más grande", "nota": "Tamaño y precio a consultar por WhatsApp"}],
                   "anticipacion_horas": 48, "anticipacion_texto": "Pedila con 48 h"},
        "pasteleria": {"medidas": [{"nombre": "½ docena"}, {"nombre": "Docena"}],
                       "anticipacion_horas": 96, "anticipacion_texto": "De 4 a 7 días, según el trabajo"}},
    "tipos": {"shots": "Shots"},
    "productos": [
        {"slug": "key-lime-pie", "nombre": "Key Lime Pie", "seccion": "tortas",
         "descripcion_larga": "Larga.", "texto_provisorio": True},
        {"slug": "shots", "nombre": "Shots", "seccion": "pasteleria", "tipo": "shots",
         "variantes": [{"nombre": "Con flores", "foto": "vasitos-flores"},
                       {"nombre": "De frutillas", "foto": "vasitos-frutillas"}]},
    ],
}


def _importar(tmp_path, datos=CATALOGO):
    ruta = tmp_path / 'catalogo.json'
    ruta.write_text(json.dumps(datos), encoding='utf-8')
    with db.transaccion():
        return imp.importar(str(ruta), None, str(tmp_path / 'fotos'))


def test_combinaciones_sabor_por_medida():
    c = imp.combinaciones(CATALOGO["productos"][1], CATALOGO["secciones"]["pasteleria"])
    assert [x['etiqueta'] for x in c] == ['Con flores · ½ docena', 'Con flores · Docena',
                                          'De frutillas · ½ docena', 'De frutillas · Docena']
    c = imp.combinaciones(CATALOGO["productos"][0], CATALOGO["secciones"]["tortas"])
    assert [(x['sabor'], x['medida']) for x in c] == [(None, '20 a 22 cm'), (None, 'Más grande')]
    assert c[1]['medida_nota'] == 'Tamaño y precio a consultar por WhatsApp'


def test_importar_crea_una_presentacion_por_combinacion_en_un_solo_item(base, tmp_path):
    _importar(tmp_path)
    filas = db.query("SELECT p.sabor, p.medida, p.etiqueta, p.precio, p.catalogo_item_id "
                     "FROM productos p JOIN catalogo_items ci ON ci.id = p.catalogo_item_id "
                     "WHERE ci.slug = 'shots' ORDER BY p.orden, p.id")
    assert len(filas) == 4 and len({f['catalogo_item_id'] for f in filas}) == 1
    assert all(f['precio'] is None for f in filas)
    item = db.query_one("SELECT * FROM catalogo_items WHERE slug = 'key-lime-pie'")
    assert item['descripcion_larga'] == 'Larga.' and item['texto_provisorio'] == 1
    cat = db.query_one("SELECT * FROM categorias WHERE slug = 'pasteleria'")
    assert (cat['anticipacion_horas'], cat['anticipacion_texto']) == (96, 'De 4 a 7 días, según el trabajo')


def test_importar_dos_veces_no_duplica(base, tmp_path):
    _importar(tmp_path)
    _importar(tmp_path)
    assert db.query_one("SELECT COUNT(*) n FROM productos")['n'] == 6


def test_reimportar_adopta_la_presentacion_vieja(base, tmp_path):
    # La semilla de Render: un producto sin sabor ni medida.
    db.insertar("INSERT INTO productos (nombre, slug, publicado) VALUES ('Key Lime Pie', 'key-lime-pie', 1)")
    _importar(tmp_path)
    filas = db.query("SELECT p.slug, p.medida FROM productos p JOIN catalogo_items ci "
                     "ON ci.id = p.catalogo_item_id WHERE ci.slug = 'key-lime-pie' ORDER BY p.id")
    assert [f['medida'] for f in filas] == ['20 a 22 cm', 'Más grande']
    assert filas[0]['slug'] == 'key-lime-pie'


def test_guardar_en_el_panel_apaga_el_texto_provisorio(admin_client, post, tmp_path, app):
    with app.app_context():
        _importar(tmp_path)
        pid = db.query_one("SELECT id FROM productos WHERE slug = 'key-lime-pie'")['id']
    r = admin_client.get(f'/admin/productos/{pid}/editar')
    assert 'Texto provisorio' in r.text
    post(admin_client, f'/admin/productos/{pid}/editar',
         {'nombre': 'Key Lime Pie', 'descripcion': 'Corta', 'descripcion_larga': 'Revisada.',
          'precio': '', 'orden': '0'})
    with app.app_context():
        item = db.query_one("SELECT texto_provisorio FROM catalogo_items WHERE slug = 'key-lime-pie'")
    assert item['texto_provisorio'] == 0
```

- [ ] **Paso 2: Correrlos y verificar que fallan**

Correr: `python -m pytest -q -p no:cacheprovider tests/test_importar_catalogo.py`
Esperado: FALLAN, con `AttributeError: combinaciones`.

- [ ] **Paso 3: Las combinaciones**

Agregar a `servicios/importar_catalogo.py`:

```python
def combinaciones(p, seccion):
    """Las presentaciones de un producto del catálogo: cada sabor por cada
    medida de su sección. Sin sabores, solo las medidas; sin medidas, una
    presentación sola (el caso de siempre). La primera es la que viene marcada.
    """
    sabores = [(v['nombre'], v.get('foto')) for v in (p.get('variantes') or [])] or [(None, None)]
    medidas = [(m['nombre'], m.get('nota')) for m in (seccion.get('medidas') or [])] or [(None, None)]
    salida = []
    for sabor, foto in sabores:
        for medida, nota in medidas:
            salida.append({
                'sabor': sabor, 'medida': medida, 'medida_nota': nota, 'foto': foto,
                'etiqueta': ' · '.join(x for x in (sabor, medida) if x) or None,
            })
    return salida
```

- [ ] **Paso 4: Usarlas en `importar()`**

Dentro del `for orden, p in enumerate(productos, start=1):`, después de crear o actualizar el producto base (`pid`), reemplazar el bloque de la foto (desde `tiene = db.query_one('SELECT 1 FROM fotos …` hasta `resumen['fotos'] += 1`) por lo siguiente:

```python
        item_id = db.query_one('SELECT catalogo_item_id i FROM productos WHERE id = ?', [pid])['i']
        seccion_json = (datos.get('secciones') or {}).get(seccion) or {}
        db.execute('UPDATE catalogo_items SET descripcion_larga = COALESCE(?, descripcion_larga), '
                   'texto_provisorio = ? WHERE id = ?',
                   [(p.get('descripcion_larga') or '').strip() or None,
                    1 if p.get('texto_provisorio') else 0, item_id])
        for n, combo in enumerate(combinaciones(p, seccion_json)):
            cid_prod = _presentacion(item_id, pid if n == 0 else None, slug, nombre, descripcion,
                                     cid, sid, orden, combo, p)
            ruta = buscar_foto(carpeta_fotos, combo['foto'] or p.get('foto') or slug)
            ya = db.query_one('SELECT 1 FROM fotos WHERE producto_id = ? AND activa = 1', [cid_prod])
            if ya:
                continue
            if ruta is None:
                if n == 0:
                    resumen['sin_foto'].append(slug)
                continue
            db.insertar('INSERT INTO fotos (producto_id, archivo, orden) VALUES (?, ?, 1)',
                        [cid_prod, _guardar_foto(ruta, destino_fotos)])
            resumen['fotos'] += 1
```

Y la función que busca, adopta o crea cada presentación:

```python
def _presentacion(item_id, base_id, slug, nombre, descripcion, cid, sid, orden, combo, p):
    """El id de la presentación de `combo` en el ítem, creándola si no existe.

    La primera combinación ADOPTA la presentación base (la que creó el alta del
    ítem, con el slug del producto): así una base vieja, sin sabor ni medida,
    no queda con una presentación de más. Idempotente por (ítem, sabor, medida).
    """
    fila = db.query_one('SELECT id FROM productos WHERE catalogo_item_id = ? '
                        "AND IFNULL(sabor, '') = ? AND IFNULL(medida, '') = ?",
                        [item_id, combo['sabor'] or '', combo['medida'] or ''])
    if fila is None and base_id is not None:
        fila = {'id': base_id}
    if fila is not None:
        db.execute('UPDATE productos SET sabor = ?, medida = ?, medida_nota = ?, etiqueta = ? '
                   'WHERE id = ?', [combo['sabor'], combo['medida'], combo['medida_nota'],
                                    combo['etiqueta'], fila['id']])
        return fila['id']
    sufijo = '-'.join(slugify(x) for x in (combo['sabor'], combo['medida']) if x)
    publicado = 0 if p.get('visible') is False else 1
    return db.insertar(
        'INSERT INTO productos (nombre, slug, descripcion, categoria_id, subcategoria_id, precio, '
        '                       publicado, orden, catalogo_item_id, sabor, medida, medida_nota, etiqueta) '
        'VALUES (?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, ?, ?, ?)',
        [nombre, f'{slug}--{sufijo}', descripcion, cid, sid, publicado, orden, item_id,
         combo['sabor'], combo['medida'], combo['medida_nota'], combo['etiqueta']])
```

Antes de escribir esto, leer los triggers de `schema.sql` (líneas 120 a 155: `productos_alta_item` y el «espejo»). Hay que confirmar dos cosas:
1. Un INSERT con `catalogo_item_id` ya cargado no crea un ítem propio. Si lo crea, borrar ese ítem huérfano después del INSERT y dejar el comentario de por qué.
2. El espejo nombre/descripción del ítem se apaga solo cuando el ítem pasa a tener más de una presentación.

Al principio de `importar()`, en el bucle que crea las categorías, sumar la anticipación:

```python
    for clave, s in (datos.get('secciones') or {}).items():
        cid = _categoria(clave)
        if 'anticipacion_horas' in s:
            db.execute('UPDATE categorias SET anticipacion_horas = ?, anticipacion_texto = ? '
                       'WHERE id = ?', [int(s['anticipacion_horas']), s.get('anticipacion_texto'), cid])
```

Actualizar el docstring del módulo con el formato nuevo (medidas, anticipación, variantes, descripcion_larga y texto_provisorio) y las reglas de combinación.

- [ ] **Paso 5: El aviso en el panel y apagarlo al guardar**

En `templates/admin/producto_editar.html`, arriba de la sección «El producto»:

```html
{% if item and item.texto_provisorio %}
<p class="aviso">Texto provisorio: esta descripción la escribimos nosotros mirando la foto. Revisala, corregila y guardá; al guardar deja de ser provisoria.</p>
{% endif %}
```

En `admin/productos.py`, `producto_editar()`:
1. En el GET, pasarle `item=db.query_one('SELECT * FROM catalogo_items WHERE id = ?', [producto['catalogo_item_id']])` al template.
2. En el POST, después de guardar sin errores: `db.execute('UPDATE catalogo_items SET texto_provisorio = 0 WHERE id = ?', [producto['catalogo_item_id']])`.

- [ ] **Paso 6: Correr todo**

Correr: `python -m pytest -q -p no:cacheprovider`
Esperado: PASAN todos.

- [ ] **Paso 7: Commit**

```bash
git add servicios/importar_catalogo.py admin/productos.py templates/admin/producto_editar.html tests/test_importar_catalogo.py
git commit -m "ficha: el importador arma sabor × medida y la anticipación; el panel avisa el texto provisorio

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarea 13: La ficha con «Elegí el sabor», la medida y los sellos

**Archivos:**
- Modificar: `templates/publico/_ficha_cuerpo.html`, `templates/publico/_ficha_js.html` y `templates/publico/_ficha_estilos.html`.
- Modificar: `models/catalogo.py` (`publicados()` trae `sabor`, `medida` y `medida_nota` en cada presentación, y la categoría con su anticipación).
- Modificar: `templates/publico/_card.html` (el «+» abre la ficha si hay sabores).
- Test: `tests/test_publico_ficha.py`.

**Interfaces:**
- Consume: las presentaciones con `sabor`, `medida`, `medida_nota`, `hay`, `precio` y `foto` (Tareas 10 y 12). `categoria` en la ficha, con `anticipacion_texto`.
- Produce: en la ficha, `fieldset.fic-sabores` (radios `name="sabor"`) y `fieldset.fic-medidas` (radios `name="medida"`) cuando hay JavaScript, más el `input[name="producto_id"]` oculto que el script llena. Sin JavaScript, `fieldset.fic-presentaciones` con radios `name="producto_id"`. En `models.catalogo`, `con_sabores(card) -> bool`.

- [ ] **Paso 1: Escribir los tests que fallan**

```python
# agregar a tests/test_publico_ficha.py
import re

import db


def _shots():
    cat = db.insertar("INSERT INTO categorias (nombre, slug, anticipacion_horas, anticipacion_texto) "
                      "VALUES ('Pastelería', 'pasteleria', 96, 'De 4 a 7 días, según el trabajo')")
    base = db.insertar("INSERT INTO productos (nombre, slug, categoria_id, publicado, stock, sabor, medida, etiqueta) "
                       "VALUES ('Shots', 'shots', ?, 1, 5, 'Con flores', '½ docena', 'Con flores · ½ docena')", [cat])
    item = db.query_one('SELECT catalogo_item_id i FROM productos WHERE id = ?', [base])['i']
    db.execute("UPDATE catalogo_items SET categoria_id = ? WHERE id = ?", [cat, item])
    ids = [base]
    for sabor, medida in [('Con flores', 'Docena'), ('De frutillas', '½ docena'), ('De frutillas', 'Docena')]:
        ids.append(db.insertar(
            "INSERT INTO productos (nombre, slug, categoria_id, publicado, stock, catalogo_item_id, "
            "sabor, medida, etiqueta) VALUES ('Shots', ?, ?, 1, 5, ?, ?, ?, ?)",
            [f'shots--{len(ids)}', cat, item, sabor, medida, f'{sabor} · {medida}']))
    return ids


def test_la_ficha_arma_dos_grupos(client, base, app):
    with app.app_context():
        _shots()
    r = client.get('/producto/shots')
    sab = r.text.split('class="fic-sabores', 1)[1].split('</fieldset>', 1)[0]
    med = r.text.split('class="fic-medidas', 1)[1].split('</fieldset>', 1)[0]
    assert re.findall(r'name="sabor" value="([^"]+)"', sab) == ['Con flores', 'De frutillas']
    assert re.findall(r'name="medida" value="([^"]+)"', med) == ['½ docena', 'Docena']
    assert 'De 4 a 7 días, según el trabajo' in r.text


def test_sin_js_una_lista_con_todas_las_combinaciones(client, base, app):
    with app.app_context():
        ids = _shots()
    r = client.get('/producto/shots')
    lista = r.text.split('class="opciones fic-presentaciones', 1)[1].split('</fieldset>', 1)[0]
    assert re.findall(r'name="producto_id" value="(\d+)"', lista) == [str(i) for i in ids]
    assert 'Con flores · ½ docena' in lista


def test_combinacion_sin_disponibilidad_no_viene_marcada(client, base, app):
    with app.app_context():
        ids = _shots()
        db.execute("UPDATE productos SET disponible_manual = 0, stock = 0 WHERE id = ?", [ids[0]])
    r = client.get('/producto/shots')
    lista = r.text.split('class="opciones fic-presentaciones', 1)[1].split('</fieldset>', 1)[0]
    primero = re.search(rf'value="{ids[0]}"[^>]*>', lista).group(0)
    assert 'disabled' in primero and 'checked' not in primero
    assert re.search(rf'value="{ids[1]}"[^>]*checked', lista)


def test_agregar_una_combinacion_la_lleva_al_pedido(client, base, app, post):
    with app.app_context():
        ids = _shots()
    post(client, '/carrito/agregar', {'producto_id': ids[2], 'cantidad': '2'})
    r = client.get('/carrito')
    assert 'De frutillas · ½ docena' in r.text


def test_el_popup_y_la_pagina_dicen_lo_mismo(client, base, app):
    with app.app_context():
        _shots()
    pagina = client.get('/producto/shots').text
    popup = client.get('/producto/shots?vista=rapida').text
    for pieza in ('class="opciones fic-sabores', 'class="opciones fic-medidas',
                  'class="opciones fic-presentaciones', 'De 4 a 7 días, según el trabajo'):
        assert pieza in pagina and pieza in popup, pieza


def test_la_tarjeta_con_sabores_abre_la_ficha(client, base, app):
    with app.app_context():
        _shots()
    r = client.get('/catalogo')
    assert 'aria-label="Elegir opciones: Shots"' in r.text
```

Si en este esquema la disponibilidad se apaga distinto (según `modo_stock`), usar el mismo mecanismo que `tests/test_stock.py`.

- [ ] **Paso 2: Correrlos y verificar que fallan**

Correr: `python -m pytest -q -p no:cacheprovider tests/test_publico_ficha.py`
Esperado: FALLAN.

- [ ] **Paso 3: Los datos en `models/catalogo.py`**

`p.*` en el `SELECT` de `publicados()` ya trae `sabor`, `medida` y `medida_nota`, porque son columnas de `productos`. Agregar:

```python
def con_sabores(card):
    """True si la card se elige por sabor: la ficha muestra «Elegí el sabor» y
    el «+» de la tarjeta abre la ficha en vez de sumar."""
    return len({p['sabor'] for p in card['presentaciones'] if p['sabor']}) > 1


def grupos(card):
    """Los sabores y las medidas de la card, en el orden de las presentaciones,
    sin repetir: [('Con flores', foto), …] y [('½ docena', nota), …]."""
    sabores, medidas = {}, {}
    for p in card['presentaciones']:
        if p['sabor'] and p['sabor'] not in sabores:
            sabores[p['sabor']] = p['foto']
        if p['medida'] and p['medida'] not in medidas:
            medidas[p['medida']] = p['medida_nota']
    return list(sabores.items()), list(medidas.items())
```

En `publico/catalogo.py::ver_ficha`:
- Sumar `c.anticipacion_texto` al `SELECT` de `categoria`.
- Pasarle al template (en los dos `render_template`, el de la vista rápida y el de la página) `sabores, medidas = catalogo.grupos(p)` como `sabores=sabores, medidas=medidas`.

Registrar `con_sabores` como global de Jinja en `publico/__init__.py`, dentro de `_globales()`: `'con_sabores': catalogo.con_sabores,`.

- [ ] **Paso 4: La ficha**

En `_ficha_cuerpo.html`, reemplazar el `{% if p.desde %}…{% else %}…{% endif %}` del formulario por:

```html
{% if p.desde %}
{# Con JavaScript: dos grupos (sabor y medida) y el id de la combinación en el
   oculto. Sin JavaScript: la lista entera de combinaciones, que manda el
   producto_id directo. Las dos salen de las mismas presentaciones. #}
<input type="hidden" name="producto_id" value="{{ sel.id }}" id="fic-elegida" disabled>
{% if sabores|length > 1 %}
<fieldset class="opciones fic-sabores solo-js">
  <legend class="campo-t">Elegí el sabor</legend>
  {% for sabor, foto in sabores %}
  <label class="opcion fic-sabor">
    <input type="radio" name="sabor" value="{{ sabor }}" data-foto="{{ url_for('static', filename='fotos/' ~ foto) if foto else '' }}"{% if sabor == sel.sabor %} checked{% endif %}>
    <span>{% if foto %}<img src="{{ url_for('static', filename='fotos/' ~ foto) }}" alt="" loading="lazy">{% endif %}<b>{{ sabor }}</b></span>
  </label>
  {% endfor %}
</fieldset>
{% endif %}
{% if medidas|length > 1 %}
<fieldset class="opciones fic-medidas solo-js">
  <legend class="campo-t">{{ 'Tamaño' if categoria and categoria.slug == 'tortas' else '¿Cuántos?' }}</legend>
  {% for medida, nota in medidas %}
  <label class="opcion">
    <input type="radio" name="medida" value="{{ medida }}"{% if medida == sel.medida %} checked{% endif %}>
    <span><b>{{ medida }}</b>{% if nota %}<small>{{ nota }}</small>{% endif %}</span>
  </label>
  {% endfor %}
</fieldset>
{% endif %}
<fieldset class="opciones fic-presentaciones solo-sin-js">
  <legend class="campo-t">Elegí</legend>
  {% for pres in p.presentaciones %}
  <label class="opcion fic-pres{% if not pres.hay %} agotada{% endif %}">
    <input type="radio" name="producto_id" value="{{ pres.id }}"
           data-sabor="{{ pres.sabor or '' }}" data-medida="{{ pres.medida or '' }}"
           data-precio="{{ pres.precio | precio }}" data-minimo="{{ pres.cantidad_minima or '' }}"
           {% if not pres.hay %}disabled{% endif %}{% if pres.id == sel.id %} checked{% endif %}>
    <span><b>{{ pres.etiqueta or pres.nombre }}</b>
    {% if pres.medida_nota %}<small>{{ pres.medida_nota }}</small>{% endif %}
    {% if not pres.hay %}<small>Agotada por ahora</small>{% endif %}
    <small{% if pres.precio is not none %} class="precio"{% endif %}>{{ pres.precio | precio }}</small></span>
  </label>
  {% endfor %}
</fieldset>
<p class="ayuda fic-combo-aviso" id="fic-combo-aviso" role="status" aria-live="polite" hidden>Esa combinación no está disponible por ahora.</p>
{% else %}
<input type="hidden" name="producto_id" value="{{ p.id }}">
{% endif %}
```

`sel` ya elige la primera presentación con `hay` y sin mínimo (líneas 18 a 22 del parcial), así que una combinación apagada nunca viene marcada.

Reemplazar la `<dl class="ficha-datos …">` por los tres sellos:

```html
<ul class="fic-sellos" role="list">
  {% if categoria and categoria.anticipacion_texto %}<li><b>Anticipación</b><span>{{ categoria.anticipacion_texto }}</span></li>{% endif %}
  <li><b>{{ txt_envio }}</b><span>{% if cfg.direccion %}{{ cfg.direccion }} · {% endif %}{{ txt_pago }}</span></li>
  <li><b>Precio</b><span>{% if sel.precio is none %}A consultar: te lo confirmamos por WhatsApp{% else %}{{ sel.precio | plata }}{% endif %}</span></li>
</ul>
```

Borrar la `<p class="nota">` de «El precio de … todavía no está cargado», porque el sello ya lo dice.

- [ ] **Paso 5: El script de la ficha**

En `_ficha_js.html`, dentro de `montarFicha(raiz)`, agregar al principio:

```js
    /* Sabor × medida: con JS se eligen por separado y acá se busca la
       presentación que coincide. La lista de combinaciones (sin JS) queda
       escondida pero es la fuente: cada radio tiene su data-sabor/data-medida. */
    var lista = [].slice.call(raiz.querySelectorAll('.fic-presentaciones input[name="producto_id"]'));
    var oculto = raiz.querySelector('#fic-elegida');
    if (lista.length && oculto && (raiz.querySelector('.fic-sabores') || raiz.querySelector('.fic-medidas'))) {
        raiz.classList.add('fic-con-grupos');
        lista.forEach(function (r) { r.disabled = true; r.dataset.hay = r.hasAttribute('disabled') ? '' : '1'; });
        oculto.disabled = false;
        var aviso = raiz.querySelector('#fic-combo-aviso');
        var boton = raiz.querySelector('.fic-agregar');
        function elegido(nombre) {
            var r = raiz.querySelector('input[name="' + nombre + '"]:checked');
            return r ? r.value : '';
        }
        function combo() {
            var s = elegido('sabor'), m = elegido('medida');
            return lista.filter(function (r) {
                return (!s || r.dataset.sabor === s) && (!m || r.dataset.medida === m);
            })[0];
        }
        function pintar() {
            var r = combo();
            var hay = r && r.dataset.hay === '1';
            oculto.value = r ? r.value : '';
            if (aviso) aviso.hidden = hay;
            if (boton) boton.disabled = !hay;
            var valor = raiz.querySelector('#fic-precio-valor');
            if (valor && r) valor.textContent = r.dataset.precio;
            /* Las medidas que con este sabor no hay, apagadas. */
            raiz.querySelectorAll('input[name="medida"]').forEach(function (i) {
                var s = elegido('sabor');
                i.disabled = !lista.some(function (x) {
                    return x.dataset.hay === '1' && x.dataset.medida === i.value && (!s || x.dataset.sabor === s);
                });
            });
        }
        raiz.querySelectorAll('input[name="sabor"]').forEach(function (i) {
            i.addEventListener('change', function () {
                var grande = raiz.querySelector('#fic-foto-grande');
                if (grande && i.dataset.foto) grande.src = i.dataset.foto;
                pintar();
            });
        });
        raiz.querySelectorAll('input[name="medida"]').forEach(function (i) {
            i.addEventListener('change', pintar);
        });
        pintar();
    }
```

En `_ficha_estilos.html`:

```css
.solo-js{display:none}
.fic-con-grupos .solo-js{display:flex}
.fic-con-grupos .solo-sin-js{display:none}
.fic-sabor span{flex-direction:row; align-items:center; gap:10px; text-transform:none; letter-spacing:0}
.fic-sabor img{width:40px; height:40px; object-fit:cover; border-radius:50%}
.fic-sellos{list-style:none; margin:20px 0 0; padding:16px 0; display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; border-block:1px solid var(--linea)}
.fic-sellos b{display:block; font-size:12px; font-weight:600; line-height:1.3}
.fic-sellos span{font-size:12px; line-height:1.45; color:var(--marron-medio)}
@media (max-width:899px){.fic-sellos{grid-template-columns:1fr}}
```

`.solo-js` usa `display:flex` porque `.opciones` es flex en el sitio.

- [ ] **Paso 6: El «+» de la tarjeta**

En `_card.html`, `elegir` pasa a:

```html
{%- set elegir = p.hay and con_sabores(p) -%}
```

Una torta con dos medidas y sin sabores suma directo la primera (20 a 22 cm). Si eso pide una presentación que no es la marcada, cambiar `{{ p.id }}` en el form por el id de la primera presentación con `hay`:

```html
{%- set primera = (p.presentaciones | selectattr('hay') | first) or p -%}
```

y usar `{{ primera.id }}` en el `<input name="producto_id">`.

- [ ] **Paso 7: Correr todo y mirar la ficha**

Correr: `python -m pytest -q -p no:cacheprovider`
Esperado: PASAN todos.

Revisar a mano en `python local.py`, con la base importada (`python -m flask --app local importar-catalogo ../sentida-site/datos/catalogo.json`):
- `/producto/shots`: elegir sabor cambia la foto, y elegir medida cambia la combinación.
- En la vista rápida (tocar la tarjeta en el catálogo) pasa lo mismo.
- Con el JavaScript apagado aparece la lista de combinaciones.

Capturas de `/producto/shots` y `/producto/key-lime-pie` en 1440 y 390, en `docs/capturas/fase3/`.

- [ ] **Paso 8: Commit**

```bash
git add templates/publico models/catalogo.py publico tests/test_publico_ficha.py docs/capturas/fase3
git commit -m "ficha: elegí el sabor y la medida, sellos con la anticipación y el precio a consultar

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarea 14: La anticipación manda en la reserva

**Archivos:**
- Modificar: `horarios.py` (`opciones` y `texto_retiro` reciben `anticipacion_horas`; `DIAS_A_OFRECER = 14`).
- Modificar: `servicios/carrito.py` (`anticipacion_horas()`).
- Modificar: `publico/checkout.py` (le pasa la anticipación a `horarios`).
- Modificar: `templates/publico/checkout.html` (explica por qué no aparecen los primeros días).
- Test: `tests/test_horarios.py` y `tests/test_publico_checkout.py`.

**Interfaces:**
- Consume: `categorias.anticipacion_horas` (Tarea 10).
- Produce:
  - `horarios.opciones(momento=None, anticipacion_horas=0) -> list[dict]`;
  - `horarios.texto_retiro(valor, momento=None, anticipacion_horas=0) -> str | None`;
  - `servicios.carrito.anticipacion_horas() -> int`.

- [ ] **Paso 1: Escribir los tests que fallan**

```python
# agregar a tests/test_horarios.py
from datetime import datetime

import horarios


def test_sin_anticipacion_ofrece_hoy():
    lunes = datetime(2026, 9, 28, 9, 0)
    assert horarios.opciones(lunes)[0]['dia'].startswith('Hoy')


def test_con_48_horas_el_primer_dia_es_pasado_manana():
    lunes = datetime(2026, 9, 28, 9, 0)
    primero = horarios.opciones(lunes, anticipacion_horas=48)[0]['franjas'][0][0]
    assert primero.startswith('2026-09-30|')


def test_texto_retiro_rechaza_un_dia_antes_del_plazo():
    lunes = datetime(2026, 9, 28, 9, 0)
    hoy = horarios.opciones(lunes)[0]['franjas'][0][0]
    assert horarios.texto_retiro(hoy, lunes, anticipacion_horas=48) is None


def test_hay_dos_semanas_para_elegir():
    lunes = datetime(2026, 9, 28, 9, 0)
    dias = horarios.opciones(lunes, anticipacion_horas=96)
    assert len(dias) >= 10
```

Y la franja que empieza antes del plazo:

```python
def test_una_franja_que_empieza_antes_del_plazo_no_se_ofrece():
    lunes = datetime(2026, 9, 28, 17, 0)
    ofrecidas = [v for d in horarios.opciones(lunes, anticipacion_horas=48) for v, _ in d['franjas']]
    assert '2026-09-30|0' not in ofrecidas        # miércoles 7:30, antes de las 17
    assert '2026-10-01|0' in ofrecidas            # jueves a la mañana, sí
```

```python
# agregar a tests/test_publico_checkout.py
def test_la_anticipacion_manda_la_mas_larga(client, base, post, app):
    with app.app_context():
        t = db.insertar("INSERT INTO categorias (nombre, slug, anticipacion_horas) VALUES ('Tortas', 'tortas', 48)")
        p = db.insertar("INSERT INTO categorias (nombre, slug, anticipacion_horas) VALUES ('Pastelería', 'pasteleria', 96)")
        a = db.insertar("INSERT INTO productos (nombre, slug, categoria_id, precio, stock, publicado) "
                        "VALUES ('Torta', 'torta', ?, 100000, 5, 1)", [t])
        b = db.insertar("INSERT INTO productos (nombre, slug, categoria_id, precio, stock, publicado) "
                        "VALUES ('Shots', 'shots-x', ?, 100000, 5, 1)", [p])
        for pid in (a, b):
            ci = db.query_one('SELECT catalogo_item_id i FROM productos WHERE id = ?', [pid])['i']
            cat = t if pid == a else p
            db.execute('UPDATE catalogo_items SET categoria_id = ? WHERE id = ?', [cat, ci])
    post(client, '/carrito/agregar', {'producto_id': a, 'cantidad': '1'})
    post(client, '/carrito/agregar', {'producto_id': b, 'cantidad': '1'})
    r = client.get('/checkout')
    minimo = horarios.opciones(anticipacion_horas=96)[0]['franjas'][0][0]
    temprano = horarios.opciones(anticipacion_horas=48)[0]['franjas'][0][0]
    assert f'value="{minimo}"' in r.text
    if temprano != minimo:
        assert f'value="{temprano}"' not in r.text
    assert 'con 4 días' in r.text or 'anticipación' in r.text.lower()
```


La constante `RETIRO` de `tests/test_publico_checkout.py` se sigue calculando con `horarios.opciones()[-1]`: sin categorías con anticipación, da lo mismo que hoy.

- [ ] **Paso 2: Correrlos y verificar que fallan**

Correr: `python -m pytest -q -p no:cacheprovider tests/test_horarios.py tests/test_publico_checkout.py`
Esperado: FALLAN, con `TypeError: unexpected keyword argument 'anticipacion_horas'`.

- [ ] **Paso 3: `horarios.py`**

```python
DIAS_A_OFRECER = 14


def opciones(momento=None, anticipacion_horas=0):
    """[{'dia': 'Hoy, sábado 13/09', 'franjas': [(valor, '7:30 a 14 h'), ...]}, ...]

    Una franja se ofrece si EMPIEZA después de ahora + la anticipación (y, sin
    anticipación, si todavía no terminó). Se ofrecen DIAS_A_OFRECER días desde
    el primero posible.

    `valor` es 'AAAA-MM-DD|n' (n = índice de la franja en ese día)."""
    momento = momento or ahora()
    desde = momento + timedelta(hours=anticipacion_horas)
    dias = []
    primero = desde.date()
    for n in range((primero - momento.date()).days, (primero - momento.date()).days + DIAS_A_OFRECER):
        fecha = momento.date() + timedelta(days=n)
        franjas = []
        for i, (inicio, fin) in enumerate(FRANJAS[fecha.weekday()]):
            if anticipacion_horas:
                entra = datetime.combine(fecha, inicio) >= desde
            else:
                entra = datetime.combine(fecha, fin) > momento
            if entra:
                franjas.append((f'{fecha.isoformat()}|{i}', _franja(inicio, fin)))
        if not franjas:
            continue
        nombre = f'{_DIAS[fecha.weekday()]} {fecha:%d/%m}'
        prefijo = 'Hoy, ' if n == 0 else 'Mañana, ' if n == 1 else ''
        dias.append({'dia': prefijo + nombre if prefijo else nombre.capitalize(),
                     'franjas': franjas})
    return dias


def texto_retiro(valor, momento=None, anticipacion_horas=0):
    """El valor elegido -> 'Martes 16/09, de 16 a 18:30 h'. None si no es una
    opción válida AHORA con esa anticipación."""
    momento = momento or ahora()
    for dia in opciones(momento, anticipacion_horas):
        for v, franja in dia['franjas']:
            if v == valor:
                fecha = datetime.strptime(valor.split('|')[0], '%Y-%m-%d').date()
                return f'{_DIAS[fecha.weekday()].capitalize()} {fecha:%d/%m}, de {franja}'
    return None
```

Actualizar el docstring del módulo: la frase «no se inventa una demora mínima de preparación» ya no vale. La anticipación viene de las categorías (panel e importador).

- [ ] **Paso 4: La anticipación del carrito**

En `servicios/carrito.py`:

```python
def anticipacion_horas():
    """La anticipación más larga entre las categorías de lo que hay en el
    carrito (0 si no hay nada o ninguna la tiene)."""
    c = _carrito()
    if not c:
        return 0
    ids = [int(k) for k in c]
    marcas = ','.join('?' * len(ids))
    fila = db.query_one(
        'SELECT MAX(cat.anticipacion_horas) h FROM productos p '
        '  JOIN catalogo_items ci ON ci.id = p.catalogo_item_id '
        '  JOIN categorias cat ON cat.id = ci.categoria_id '
        f' WHERE p.id IN ({marcas})', ids)
    return (fila['h'] or 0) if fila else 0
```

- [ ] **Paso 5: El checkout**

En `publico/checkout.py`:
- `datos_pedido['retiro']` pasa a `horarios.texto_retiro(request.form.get('retiro') or '', anticipacion_horas=srv.anticipacion_horas())`.
- En `_form`, `turnos=horarios.opciones(anticipacion_horas=srv.anticipacion_horas())` y sumar `anticipacion=srv.anticipacion_horas()`.

En `templates/publico/checkout.html`, arriba de los turnos:

```html
{% if anticipacion %}
<p class="ayuda">Lo que pediste lleva {% if anticipacion >= 96 %}al menos 4 días{% else %}{{ anticipacion }} h{% endif %} de anticipación: por eso los primeros días no aparecen.</p>
{% endif %}
```

- [ ] **Paso 6: Correr todo**

Correr: `python -m pytest -q -p no:cacheprovider`
Esperado: PASAN todos.

- [ ] **Paso 7: Commit**

```bash
git add horarios.py servicios/carrito.py publico/checkout.py templates/publico/checkout.html tests/test_horarios.py tests/test_publico_checkout.py
git commit -m "tienda: la reserva respeta la anticipación más larga del pedido y ofrece dos semanas

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarea 15: Documentación, preview en Render y verificación en vivo

**Archivos:**
- Modificar: `sentida-tienda/README.md` (las cinco cosas: tema v6, marca sincronizada, sin home, sabores y medidas, anticipación; los comandos `sincronizar-marca` e `importar-catalogo`).
- Modificar: `sentida-site/README.md` (sección «Marca: comun/marca.css y assets/marca/»).
- Worktree `sentida-tienda-preview` (rama `preview-render`): merge de `main`, semilla nueva y push.

**Interfaces:**
- Consume: todo lo anterior.

- [ ] **Paso 1: Los README**

`sentida-tienda/README.md`:
- En «Las cinco cosas…», el punto 5 pasa a decir que la marca viene de `sentida-site` con `python -m flask --app app sincronizar-marca ../sentida-site` (el test `tests/test_marca.py` la vigila), que el tema está en `static/tema.css` y los títulos en Playfair.
- En «Qué hace»: sin home, `/` → `/catalogo`; y la ficha con sabor × medida y los sellos.
- En «Pendientes»: el horario de retiro real, los precios y el pago online (los activan Anto y Nadia) y revisar los textos provisorios.

`sentida-site/README.md`: nueva sección «Marca (28/09/2026)», que dice:
- los colores y las fuentes viven en `comun/marca.css`, y los logos en `assets/marca/`;
- los SVG de Illustrator se pasan por `herramientas/limpiar_svg.py`;
- después de cambiar la marca, correr `sincronizar-marca` en la tienda.

- [ ] **Paso 2: Commits de los README**

```bash
cd "/e/E descargas/SENTIDA-sitio-web/sentida-tienda" && git add README.md && git commit -m "docs: la tienda con la cara de la v6, la marca sincronizada y la ficha nueva

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
cd "../sentida-site" && git add README.md && git commit -m "docs: dónde vive la marca y cómo se pasa a la tienda

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Paso 3: Preview: merge y semilla nueva**

```bash
cd "/e/E descargas/SENTIDA-sitio-web/sentida-tienda-preview"
git merge --no-edit main
rm deploy/preview/sentida-preview.db static/fotos/*.webp
SECRET_KEY=semilla DB_PATH="$PWD/deploy/preview/sentida-preview.db" python -m flask --app app importar-catalogo ../sentida-site/datos/catalogo.json
python -c "import sqlite3;c=sqlite3.connect('deploy/preview/sentida-preview.db');c.execute('pragma wal_checkpoint(TRUNCATE)');c.execute('pragma journal_mode=DELETE');c.close()"
rm -f deploy/preview/*-wal deploy/preview/*-shm
python -m pytest -q -p no:cacheprovider
```

Esperado: PASAN todos. `tests/test_marca.py::test_la_copia_es_igual_a_la_del_sitio` corre porque `../sentida-site` existe también para el worktree.

- [ ] **Paso 4: Commit y push del preview**

```bash
git add -A deploy/preview static/fotos
git commit -m "preview: semilla con sabores, medidas y anticipación (28/09)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git push origin preview-render
cd ../sentida-tienda && git push origin main
cd ../sentida-site && git push v6 v6:main
```

- [ ] **Paso 5: Verificar en vivo (después de 5 a 8 minutos)**

```bash
for u in "" catalogo "catalogo?cat=tortas" "catalogo?cat=pasteleria" producto/shots producto/key-lime-pie carrito; do
  printf "/%s " "$u"; curl -s -o /dev/null -w "%{http_code}\n" --max-time 90 "https://sentida-tienda.onrender.com/$u"; done
curl -s https://sentida-tienda.onrender.com/producto/shots | grep -c 'name="sabor"'
```

Esperado: `/` da 302 y el resto 200. En Shots hay tres `name="sabor"`. Abrir `https://sentida-tienda.onrender.com/catalogo?cat=pasteleria` en 1440 y 390 y revisar la cabecera, las tarjetas, la ficha de Shots (cambiar de sabor) y una reserva con una torta y un shot: el primer día tiene que respetar los 4 días.
