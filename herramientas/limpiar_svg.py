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
