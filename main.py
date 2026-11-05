import json
import math
import os
import random
import sys
import time
from array import array

import pygame

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

ANCHO, ALTO, FPS = 1000, 700, 60

# Avioncito del ícono, en coordenadas de 256x256: (alas, cola, fuselaje)
ICONO_ALAS = [(128, 95), (225, 160), (225, 185), (128, 150), (31, 185), (31, 160)]
ICONO_COLA = [(128, 175), (180, 215), (180, 230), (128, 212), (76, 230), (76, 215)]
ICONO_CUERPO = [(128, 28), (143, 70), (143, 190), (128, 215), (113, 190), (113, 70)]


def crear_icono(tam=64):
    k = tam / 256
    icono = pygame.Surface((tam, tam), pygame.SRCALPHA)
    pygame.draw.rect(icono, (12, 18, 40), icono.get_rect(), border_radius=round(40 * k))
    pygame.draw.rect(icono, (50, 240, 255), icono.get_rect(), max(1, round(8 * k)), border_radius=round(40 * k))
    for puntos, color in ((ICONO_ALAS, (50, 240, 255)), (ICONO_COLA, (30, 170, 200)), (ICONO_CUERPO, (235, 245, 255))):
        pygame.draw.polygon(icono, color, [(x * k, y * k) for x, y in puntos])
    pygame.draw.ellipse(icono, (12, 18, 40), (116 * k, 66 * k, 24 * k, 40 * k))  # cabina
    return icono


pygame.display.set_icon(crear_icono())
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Glitch Survivor")
RELOJ = pygame.time.Clock()
CAPA_ALERTA = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)

NEGRO, BLANCO, CIAN, ROSA, MORADO = (8, 10, 24), (235, 245, 255), (50, 240, 255), (255, 55, 170), (175, 80, 255)
ROJO, NARANJA, VERDE, AMARILLO = (255, 75, 85), (255, 155, 55), (80, 255, 150), (255, 230, 90)
DORADO, PANEL = (255, 215, 0), (16, 25, 48)

FUENTE, FUENTE_GRANDE, FUENTE_CHICA = (22, False), (48, True), (16, False)
TAM_MINIMO = 10
NOMBRES_FUENTE = "consolas,dejavusansmono,couriernew,monospace"
_cache_fuentes = {}

# Carpeta del juego: junto al .exe cuando está empaquetado, o junto a main.py al ejecutarlo con Python
CARPETA = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
RUTA_DATOS = os.path.join(CARPETA, "data", "scores.json")
RUTA_CONFIG = os.path.join(CARPETA, "data", "settings.json")
CONJUNTOS_POR_OLEADA = 8
PORCENTAJE_PARA_JEFE = 0.85
HITBOX_JUGADOR = 10
DURACION_AVISO_JEFE = 1.5
DURACION_GOLPE = 1.0
ACCIONES = ("arriba", "abajo", "izquierda", "derecha", "dash")
ETIQUETAS_ACCION = {a: a.upper() for a in ACCIONES}

CALIDADES = {
    "normal": {"nombre": "NORMAL", "color": (235, 245, 255), "prob": 60},
    "raro": {"nombre": "RARO", "color": (50, 160, 255), "prob": 30},
    "epico": {"nombre": "ÉPICO", "color": (175, 80, 255), "prob": 8},
    "legendario": {"nombre": "LEGENDARIO", "color": DORADO, "prob": 1.5},
}

MEJORAS = [
    ("Turbo", "Velocidad de movimiento +15%", "turbo", "normal"),
    ("Cadencia", "Aumenta la velocidad de disparo", "cadencia", "normal"),
    ("Imán", "Atrae cristales desde más lejos", "iman", "normal"),
    ("Disparo Doble", "Añade proyectiles adicionales", "doble", "raro"),
    ("Escudo", "Absorbe un impacto enemigo", "escudo", "raro"),
    ("Corazón Extra", "+1 vida máxima y la restaura", "vida", "raro"),
    ("Dash Mejorado", "Reduce el cooldown del dash", "dash", "raro"),
    ("Nanobots", "Regenera vida con el tiempo", "nanobots", "epico"),
    ("Campo Distorsión", "Desacelera proyectiles enemigos", "distorsion", "epico"),
    ("Hipercargador", "Los cristales otorgan más XP", "hipercargador", "epico"),
    ("Misiles Perforantes", "Balas atraviesan enemigos", "perforante", "epico"),
    ("Propulsión Térmica", "Dash deja estela de fuego letal", "termica", "legendario"),
    ("Escudo Espejo", "Probabilidad de rebotar proyectiles", "espejo", "legendario"),
    ("Núcleo Sobrecarga", "Añade disparos laterales de cobertura", "lateral", "legendario"),
    ("Ancla Gravitacional", "Atrae enemigos menores al centro", "ancla", "legendario"),
    ("Condensador Plasma", "Añade probabilidad de daño crítico", "critico", "legendario"),
    ("Estabilizador", "Elimina casi todo el cooldown de Dash", "estabilizador", "legendario"),
]

NIVEL_MAX = {"termica": 1, "lateral": 1, "ancla": 1, "doble": 4}


def nivel_maximo(tipo):
    return NIVEL_MAX.get(tipo, 5)


def salir():
    pygame.quit()
    sys.exit()


def eventos():
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            salir()
        yield e


def limitar(v, minimo=0.0, maximo=1.0):
    return max(minimo, min(maximo, v))


def obtener_fuente(tam, negrita=False):
    if (tam, negrita) not in _cache_fuentes:
        _cache_fuentes[(tam, negrita)] = pygame.font.SysFont(NOMBRES_FUENTE, tam, bold=negrita)
    return _cache_fuentes[(tam, negrita)]


_cache_texto = {}


def imagen_texto(contenido, tam, negrita, color, ancho_max):
    """Texto ya renderizado (con la letra reducida hasta que quepa). Se guarda en caché: renderizar fuentes cuesta."""
    clave = (contenido, tam, negrita, tuple(color), ancho_max)
    img = _cache_texto.get(clave)
    if img is None:
        while tam > TAM_MINIMO and obtener_fuente(tam, negrita).size(contenido)[0] > ancho_max:
            tam -= 1
        img = obtener_fuente(tam, negrita).render(contenido, True, color)
        if len(_cache_texto) >= 1500:
            _cache_texto.clear()
        _cache_texto[clave] = img
    return img


def texto(sup, contenido, x, y, fuente=FUENTE, color=BLANCO, centrado=False, ancho_max=ANCHO - 30):
    tam, negrita = fuente
    img = imagen_texto(str(contenido), tam, negrita, color, ancho_max)
    sup.blit(img, img.get_rect(**{"center" if centrado else "topleft": (x, y)}))


def partir_texto(contenido, tam, ancho_max):
    fuente, lineas, actual = obtener_fuente(tam), [], ""
    for palabra in str(contenido).split():
        prueba = (actual + " " + palabra).strip()
        if fuente.size(prueba)[0] <= ancho_max:
            actual = prueba
        else:
            lineas += [actual] if actual else []
            actual = palabra
    return lineas + ([actual] if actual else [])


def ajustar_descripcion(contenido, ancho_max, tam_max=16, tam_min=11):
    contenido = str(contenido)
    for tam in range(tam_max, tam_min - 1, -1):
        if obtener_fuente(tam).size(contenido)[0] <= ancho_max:
            return [contenido], tam
    return partir_texto(contenido, 14, ancho_max), 14


def caja(sup, rect, borde, fondo=PANEL, grosor=2, r=8):
    pygame.draw.rect(sup, fondo, rect, border_radius=r)
    pygame.draw.rect(sup, borde, rect, grosor, border_radius=r)


def boton_dibujar(rect, titulo, color=CIAN, sup=None):
    sup = sup if sup is not None else VENTANA
    caja(sup, rect, color)
    texto(sup, titulo, rect.centerx, rect.centery, FUENTE, color, True, rect.width - 24)


_FONDO = None


def fondo(sup=None):
    """Pinta el fondo cuadriculado. La cuadrícula se dibuja una sola vez y después solo se copia."""
    global _FONDO
    sup = sup if sup is not None else VENTANA
    if _FONDO is None:
        _FONDO = pygame.Surface((ANCHO, ALTO)).convert()
        _FONDO.fill(NEGRO)
        for x in range(0, ANCHO, 50):
            pygame.draw.line(_FONDO, (17, 25, 48), (x, 45), (x, ALTO), 1)
        for y in range(50, ALTO, 50):
            pygame.draw.line(_FONDO, (17, 25, 48), (0, y), (ANCHO, y), 1)
    sup.blit(_FONDO, (0, 0))


ESTADO = {"error_guardado": False}  # True si la última escritura en la carpeta data falló


def leer_json(ruta):
    try:
        with open(ruta, encoding="utf-8") as f:
            datos = json.load(f)
        return datos if isinstance(datos, dict) else {}
    except (OSError, ValueError):
        return {}


def escribir_json(ruta, datos):
    """Guarda el JSON de forma segura (archivo temporal + reemplazo). Devuelve False y lo anota en ESTADO si falla."""
    temporal = ruta + ".tmp"
    try:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(temporal, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
        os.replace(temporal, ruta)
        ESTADO["error_guardado"] = False
        return True
    except (OSError, TypeError, ValueError):
        ESTADO["error_guardado"] = True
        return False


def limpiar_iniciales(texto_):
    return "".join(c for c in str(texto_).upper() if c.isascii() and c.isalnum())[:3]


def limpiar_record(r):
    """Devuelve un récord válido o None. Así un scores.json editado a mano no puede romper el ranking."""
    if not isinstance(r, dict):
        return None
    puntaje = r.get("score")
    if isinstance(puntaje, bool) or not isinstance(puntaje, (int, float)):
        return None
    if isinstance(puntaje, float) and not math.isfinite(puntaje):
        return None
    limpio = {"name": str(r.get("name") or "JUGADOR")[:12], "score": int(puntaje), "time": str(r.get("time") or "00:00")[:8]}
    mejoras = r.get("mejoras")
    if isinstance(mejoras, list) and mejoras and all(isinstance(m, dict) for m in mejoras):
        limpio["mejoras"] = [{str(t): n for t, n in m.items() if isinstance(n, int) and not isinstance(n, bool)} for m in mejoras]
    return limpio


def es_coop(r):
    return len(r.get("mejoras") or []) > 1


def cargar_todos_records():
    datos, brutos = leer_json(RUTA_DATOS), []
    for clave in ("high_scores", "high_scores_coop"):
        if isinstance(datos.get(clave), list):
            brutos += datos[clave]
    return [r for r in map(limpiar_record, brutos) if r]


def cargar_records(coop=False):
    """Top 10 de un jugador (coop=False) o de cooperativo (coop=True). Los récords viejos se reparten según sus jugadores."""
    return sorted((r for r in cargar_todos_records() if es_coop(r) == coop), key=lambda r: r["score"], reverse=True)[:10]


def califica(puntaje, coop=False):
    records = cargar_records(coop)
    return len(records) < 10 or puntaje > records[-1]["score"]


def guardar_record(puntaje, tiempo, mejoras=None, nombre="JUGADOR", coop=False):
    nuevo = limpiar_record({"name": nombre, "score": puntaje, "time": tiempo, "mejoras": mejoras})
    if nuevo is None:
        return False
    todos = cargar_todos_records() + [nuevo]
    salida = {clave: sorted((r for r in todos if es_coop(r) == modo), key=lambda r: r["score"], reverse=True)[:10]
              for modo, clave in ((False, "high_scores"), (True, "high_scores_coop"))}
    return escribir_json(RUTA_DATOS, salida)


def configuracion_predeterminada():
    k = pygame
    return {"version": 1, "volumen": 0.65, "vibracion": True, "iniciales": "AAA",
            "controles1": dict(zip(ACCIONES, (k.K_w, k.K_s, k.K_a, k.K_d, k.K_SPACE))),
            "controles2": dict(zip(ACCIONES, (k.K_UP, k.K_DOWN, k.K_LEFT, k.K_RIGHT, k.K_RETURN)))}


def cargar_configuracion():
    config, datos = configuracion_predeterminada(), leer_json(RUTA_CONFIG)
    if isinstance(datos.get("volumen"), (int, float)):
        config["volumen"] = limitar(float(datos["volumen"]))
    if isinstance(datos.get("vibracion"), bool):
        config["vibracion"] = datos["vibracion"]
    if isinstance(datos.get("iniciales"), str) and limpiar_iniciales(datos["iniciales"]):
        config["iniciales"] = limpiar_iniciales(datos["iniciales"])
    for jug in ("controles1", "controles2"):
        guardados = datos.get(jug) if isinstance(datos.get(jug), dict) else {}
        for accion in ACCIONES:
            tecla = guardados.get(accion)
            try:
                if isinstance(tecla, int) and tecla > 0 and pygame.key.name(tecla):
                    config[jug][accion] = tecla
            except (ValueError, OverflowError, TypeError):
                pass
    return config


def guardar_configuracion():
    escribir_json(RUTA_CONFIG, CONFIG)


def nombre_tecla(tecla):
    nombre = pygame.key.name(tecla).upper()
    return {"SPACE": "ESPACIO", "RETURN": "ENTER", "UP": "FLECHA ↑", "DOWN": "FLECHA ↓", "LEFT": "FLECHA ←",
            "RIGHT": "FLECHA →", "LEFT SHIFT": "SHIFT IZQ.", "RIGHT SHIFT": "SHIFT DER."}.get(nombre, nombre)


CONFIG = cargar_configuracion()


class GestorAudio:
    SONIDOS = {"click": (520, 660, 0.06, 0.18), "dash": (180, 720, 0.13, 0.25), "golpe": (150, 65, 0.20, 0.35),
               "explosion": (240, 90, 0.10, 0.16), "alerta": (740, 980, 0.22, 0.42), "jefe": (130, 55, 0.55, 0.45),
               "mejora": (440, 1040, 0.24, 0.28), "legendario": (300, 1400, 0.80, 0.50)}

    INTERVALO_MIN = {"explosion": 0.05, "golpe": 0.10, "click": 0.03}  # segundos mínimos entre repeticiones

    def __init__(self):
        self.sonidos, self.ultimo = {}, {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 1, 512)
            pygame.mixer.set_num_channels(24)
            self.sonidos = {n: (self.crear_tono(*s[:3]), s[3]) for n, s in self.SONIDOS.items()}
        except pygame.error:
            self.sonidos = {}

    @staticmethod
    def crear_tono(f_ini, f_fin, duracion):
        fm = pygame.mixer.get_init()[0]
        total, muestras, fase = max(1, int(fm * duracion)), array("h"), 0.0
        for i in range(total):
            prog = i / total
            fase += math.tau * (f_ini + (f_fin - f_ini) * prog) / fm
            envolvente = min(1.0, i / (fm * 0.008)) * (1.0 - prog) ** 1.4
            muestras.append(round(22000 * envolvente * math.sin(fase)))
        return pygame.mixer.Sound(buffer=muestras.tobytes())

    def reproducir(self, nombre):
        if nombre in self.sonidos and CONFIG["volumen"] > 0:
            ahora = time.monotonic()
            if ahora - self.ultimo.get(nombre, -1.0) < self.INTERVALO_MIN.get(nombre, 0.0):
                return  # evita que decenas de explosiones simultáneas saturen los canales
            self.ultimo[nombre] = ahora
            sonido, volumen = self.sonidos[nombre]
            sonido.set_volume(CONFIG["volumen"] * volumen)
            sonido.play()


AUDIO = GestorAudio()


# --- SPRITES PIXEL ART (diseños de los archivos HTML de naves y jefes) ---
# Cada forma guarda la mitad izquierda de la nave (se espeja para formar la nave completa).
# Letras: o = contorno, a/b = color principal y sombra, c = brillo, g = cabina/detalle, r = detalle rojo,
# f/e = fuego de los propulsores. "." = transparente.
FORMAS = {
    "player": (False, [
        ".......o", "......oc", "......oc", ".....oac",
        ".....oag", "....oaag", "...oaaag", "..oabaab",
        ".oaabaab", "oaaabaab", "oraaabab", "orraabab",
        "orroaoab", "oro.oaao", ".o..offf", ".....fff",
    ]),
    "fast": (False, [
        "o.....", "oo..oo", "oao.oa", "oaaooa",
        ".oaaaa", ".oabgg", "..oabg", "..oaab",
        "...oab", "...ooa", "....oa", ".....o",
    ]),
    "med": (False, [
        ".oo.....oo", ".oao...oao", ".oab.oooab", "oaabooaaab",
        "oaaabaaaab", "oabbaaacgg", "oabaaacggg", ".oaaaaaccg",
        "..oaabbaac", "..oaabaaac", "...oaabaab", "...oaaabab",
        "....oaaabb", "....obbaab", ".....ooaab", ".......ooa",
    ]),
    "tank": (True, [
        ".ooo......oo", ".oco....oooc", ".oao..ooaaac", ".oaooooaaaac",
        ".oabaaaaaaac", "oaabbaaaaccc", "oabbaaaacrcg", "oabaabbaccgg",
        "oaaaabbaaccg", "oaaabbbaaaac", "obaabaaabbaa", "obbaaaaaabaa",
        ".obbaaaaaabb", ".obaaaoaaabb", "..obaooaaaab", "..oooorraaab",
        "....orrraaab", ".....oraaabb", "......ooaabb", "........oooa",
    ]),
    "boss": (True, [
        ".ooo.......ooccc", ".oao......ooaaac", ".oao.....oaaaaac", ".oab..oooaabbaac",
        ".oabooaaaabbbaac", "oaabbaaaaccbaaac", "oaabaaaccggcbaac", "oabbaaccggggcaac",
        "oabaaccggggccaar", "oaaaabcggeegcaar", "obaaabcggeeeccar", "obbaaabcggeegcar",
        ".obbaaabcgggccaa", ".obaaaabbcccbaaa", ".oabaaabbbbbaabb", ".oaabaaaaaabbbbb",
        "..oabbaaaaaabbrr", "..oaobbbaaabbrrr", "..ooo.obbaabbrrr", ".orro..obbbbaabb",
        ".orro...oobbaabb", "..oo......oooabb", "...........oofff", "..........ooffff",
    ]),
    "fort": (True, [
        "..............oo", ".............ooc", "............ooac", ".ooo.......oaaac",
        ".oao......ooaggc", ".oao..oooooaaggc", ".oabooaaaaaabbac", "ooabaaaaabbbbbac",
        "oaabaaccaabbbbac", "oaabaacrcaabbbac", "oabbaaccaabbbbac", "oabaaaaaaaabbbac",
        "oabbbbbbbbbbbbac", "oaabaaaaaaaaaaac", "ooabaooooooooaac", ".oabo.........ac",
        ".oabo.....oooooa", ".ooo....oobbbbba", "........obbbbaaa", "........oorrbaaa",
        ".........orrrbaa", ".........oorrraa", "..........oooeff", ".............eff",
    ]),
    "mantis": (True, [
        "...............o", "..............oc", "..............oc", ".............oac",
        ".............ogc", "o............ogc", "oo...........oac", "oao..........oac",
        "oaao.....oooaaac", "oabaooooaabbaaac", ".oabaaaabbbcaaac", "..oabaaabbbccgac",
        "..oaabaabbcggeac", "...oabaabbcgeeac", "...oaabbbbccggac", "....oabbbbbbbaac",
        "....ooabbbbbaaac", ".....oobaaaaaabc", "......ooaaaaaabb", ".......oobbaaabb",
        "........oobrraab", ".........orrrrab", ".........ooorrab", "............offf",
    ]),
    "manta": (True, [
        "...............o", "..............oc", ".............oac", "............oagc",
        "...........oaggc", ".........ooaaggc", ".......ooaabaagc", ".....ooaabbaaacc",
        "...ooaabbaaacggc", "..oaabbaaaacggec", ".oaabaaaaaccggec", "oaabaaabbbccggac",
        "oabaaabbbbbccgac", "oabaabbbbbbbbbac", "ooabbabbbbbbbaac", ".ooabaaabbbbbaac",
        "..ooabaaaaaabaac", "....ooabaaaabbac", "......ooabbbbaaa", "........oorbbaaa",
        ".........orrrbaa", ".........oorrraa", "...........ooeff", "..............ff",
    ]),
    "orb": (True, [
        "...............o", ".............ooc", "...ooo......oacc", "..oaao.....oaagc",
        "..oaco...ooaaggc", "..oaao..oaaaaggc", "..ooo..oaabbaggc", ".....ooaabbbaggc",
        "...ooaabbaaacggc", "..oaabbaaaaccgec", ".oaabaaaaaccggec", ".oabaaabbbccggec",
        ".oabaabbbbbbcgec", ".oabaabbbbbbbaac", "..oabaaabbbbbaac", "..ooabaaaaaabaac",
        "...ooabaaaaabbac", ".....ooabbbbbaaa", "......oobbbbbaaa", ".......oorrbbaaa",
        "........orrrbbaa", "........oorrrbaa", "..........ooeeff", ".............eff",
    ]),
}

PALETAS = {
    "b1": dict(zip("oabcgrfe", ('#3a0b0b', '#dc2626', '#8f1b1b', '#fecaca', '#7dd3fc', '#fbbf24', '#fb923c', '#fde047'))),
    "b2": dict(zip("oabcgrfe", ('#06302b', '#14b8a6', '#0b7266', '#c7fff5', '#fde047', '#f472b6', '#fb923c', '#fde047'))),
    "b3": dict(zip("oabcgrfe", ('#26104a', '#8b5cf6', '#5b32b0', '#ddd0ff', '#34d399', '#f472b6', '#fb923c', '#fde047'))),
    "b4": dict(zip("oabcgrfe", ('#3d2a05', '#f59e0b', '#a8650a', '#fff0c2', '#ef4444', '#38bdf8', '#fb923c', '#fde047'))),
    "fast": dict(zip("oabcgrfe", ('#0f2a14', '#4ade80', '#1f8a43', '#d9ffe3', '#fde047', '#fb7185', '#fb923c', '#fde047'))),
    "fort1": dict(zip("oabcgrfe", ('#1f1305', '#a16207', '#6b4204', '#fde68a', '#38bdf8', '#ef4444', '#fb923c', '#fde047'))),
    "fort2": dict(zip("oabcgrfe", ('#0f1f12', '#4d7c0f', '#2f4d0a', '#d9f99d', '#f97316', '#facc15', '#fb923c', '#fde047'))),
    "man1": dict(zip("oabcgrfe", ('#07203a', '#0ea5e9', '#0b6a9a', '#bae6fd', '#fde047', '#f472b6', '#fb923c', '#fde047'))),
    "man2": dict(zip("oabcgrfe", ('#1b0f3a', '#a78bfa', '#6d4fd1', '#ede9fe', '#34d399', '#fb7185', '#fb923c', '#fde047'))),
    "mant1": dict(zip("oabcgrfe", ('#2a0a1f', '#ec4899', '#9d2467', '#fbcfe8', '#a3e635', '#fde047', '#fb923c', '#fde047'))),
    "mant2": dict(zip("oabcgrfe", ('#06242a', '#10b981', '#0a7357', '#bbf7d0', '#f43f5e', '#fde047', '#fb923c', '#fde047'))),
    "med": dict(zip("oabcgrfe", ('#2a0f3d', '#9333ea', '#5b1b9a', '#e9c8ff', '#f472b6', '#f472b6', '#fb923c', '#fde047'))),
    "orb1": dict(zip("oabcgrfe", ('#222a33', '#cbd5e1', '#7b8794', '#ffffff', '#ef4444', '#38bdf8', '#fb923c', '#fde047'))),
    "orb2": dict(zip("oabcgrfe", ('#2a0a0a', '#f87171', '#b13a3a', '#fee2e2', '#fde047', '#22d3ee', '#fb923c', '#fde047'))),
    "p1": dict(zip("oabcgrfe", ('#0b1d3a', '#3b82f6', '#1e4fa8', '#bfdcff', '#7ee7ff', '#ef4444', '#fb923c', '#fde047'))),
    "p2": dict(zip("oabcgrfe", ('#3a0b0b', '#ef4444', '#a32222', '#ffd0cc', '#fde68a', '#fbbf24', '#fb923c', '#fde047'))),
    "tank": dict(zip("oabcgrfe", ('#1a1a1a', '#8b93a1', '#555c69', '#d1d5db', '#f59e0b', '#f97316', '#fb923c', '#fde047'))),
}
ESCALA_SPRITE = 2  # tamaño de cada "píxel" del sprite en pantalla
_CACHE_SPRITES, _CACHE_DESTELLOS = {}, {}


def construir_sprite(forma, paleta, mezcla=0.0, tinte=None):
    """Dibuja un sprite. Con tinte y mezcla (0-1) todos sus colores se acercan al tinte (nave dañada)."""
    voltear, mitades = FORMAS[forma]
    colores = {}
    for letra, hexa in PALETAS[paleta].items():
        base = pygame.Color(hexa)
        colores[letra] = tuple(round(c + (t - c) * mezcla) for c, t in zip(base[:3], tinte)) if tinte else tuple(base[:3])
    filas = [fila + fila[::-1] for fila in mitades]
    if voltear:
        filas.reverse()
    esc = ESCALA_SPRITE
    sup = pygame.Surface((len(filas[0]) * esc, len(filas) * esc), pygame.SRCALPHA)
    for j, fila in enumerate(filas):
        for i, letra in enumerate(fila):
            if letra != ".":
                sup.fill(colores[letra], (i * esc, j * esc, esc, esc))
    return sup.convert_alpha()


def sprite(forma, paleta, mezcla=0.0, tinte=None):
    clave = (forma, paleta, mezcla, tinte)
    if clave not in _CACHE_SPRITES:
        _CACHE_SPRITES[clave] = construir_sprite(forma, paleta, mezcla, tinte)
    return _CACHE_SPRITES[clave]


def destello(img, color):
    """Versión más brillante/coloreada del sprite (golpes e invencibilidad), conservando sus detalles."""
    clave = (id(img), color)
    if clave not in _CACHE_DESTELLOS:
        copia = img.copy()
        copia.fill(color, special_flags=pygame.BLEND_RGB_ADD)
        _CACHE_DESTELLOS[clave] = copia
    return _CACHE_DESTELLOS[clave]


# --- ESTELA DE FUEGO (Propulsión Térmica): sprites sacados de la imagen de llamas ---
# 4 formas de llama; letras a (borde) -> d (núcleo). Cada etapa de vida usa una paleta distinta (recién creada -> brasa).
LLAMAS_FORMAS = (
    ("...a....", "...a....", "..aba...", "..abb.a.", ".abcca..", ".abccba.", "abcddcba", "abcddcba", ".abccba.", "..aaaa.."),
    ("....a...", "...aa...", "...aba..", "..abba..", ".abccba.", ".abccba.", "abcddcba", "abcddcba", ".abccba.", "..aaaa.."),
    ("..a.....", "..aa....", ".aba....", ".abba.a.", ".abccaa.", ".abccba.", "abcddcba", "abcddcba", ".abccba.", "..aaaa.."),
    ("........", "........", "........", "...a....", "..aba...", "..abba..", ".abccba.", ".abccba.", "..abba..", "...aa..."),
)
LLAMAS_PALETAS = (
    {"a": "#dc2626", "b": "#fb923c", "c": "#fde047", "d": "#fff7c2"},  # recién creada
    {"a": "#7f1d1d", "b": "#dc2626", "c": "#fb923c", "d": "#fde047"},  # a mitad de vida
    {"a": "#3b1010", "b": "#7f1d1d", "c": "#dc2626", "d": "#fb923c"},  # brasa
)
_CACHE_LLAMAS = {}


def sprite_llama(forma, etapa, esc=3):
    clave = (forma, etapa, esc)
    if clave not in _CACHE_LLAMAS:
        filas = LLAMAS_FORMAS[forma]
        sup = pygame.Surface((len(filas[0]) * esc, len(filas) * esc), pygame.SRCALPHA)
        for j, fila in enumerate(filas):
            for i, letra in enumerate(fila):
                if letra != ".":
                    sup.fill(pygame.Color(LLAMAS_PALETAS[etapa][letra]), (i * esc, j * esc, esc, esc))
        _CACHE_LLAMAS[clave] = sup.convert_alpha()
    return _CACHE_LLAMAS[clave]


# Orden en que cada llama recorre las 4 formas según su etapa de vida (la forma 3 es la llama chica que se apaga).
LLAMAS_SECUENCIAS = ((0, 1, 2, 1), (1, 2, 0, 2), (1, 3, 2, 3))
LLAMAS_FPS = 9  # cambios de forma por segundo (parpadeo de la llama)


class Llama:
    """Una llama de la estela del dash: parpadea, se enfría de recién creada a brasa, quema a los enemigos y se apaga sola."""
    VIDA, DANO_CADA = 2.1, 0.3  # segundos que dura / segundos entre quemaduras a un mismo enemigo
    ASCENSO = 5  # píxeles que sube la llama a lo largo de su vida (solo visual)

    def __init__(self, pos, tiempo):
        self.pos = pygame.Vector2(pos) + (random.uniform(-3, 3), random.uniform(-3, 3))
        self.nacida = tiempo
        self.fase = random.randrange(4)  # cada llama arranca en un punto distinto, así no parpadean todas a la vez
        self.rect = pygame.Rect(0, 0, 18, 24)
        self.rect.center = round(self.pos.x), round(self.pos.y)

    def vive(self, tiempo):
        return tiempo - self.nacida < self.VIDA

    def dibujar(self, sup, tiempo):
        edad = tiempo - self.nacida
        etapa = min(2, int(edad / self.VIDA * 3))
        secuencia = LLAMAS_SECUENCIAS[etapa]
        forma = secuencia[(int(edad * LLAMAS_FPS) + self.fase) % len(secuencia)]
        img = sprite_llama(forma, etapa)
        centro = (self.rect.centerx, self.rect.centery - round(self.ASCENSO * edad / self.VIDA))
        sup.blit(img, img.get_rect(center=centro))


class Jugador(pygame.sprite.Sprite):
    def __init__(self, x, y, controles, color, segundo=False):
        super().__init__()
        self.pos, self.controles, self.color, self.segundo = pygame.Vector2(x, y), controles, color, segundo
        self.velocidad, self.vidas, self.vidas_max = 260, 3, 3
        self.xp, self.nivel, self.xp_siguiente = 0, 1, 5
        self.dash_hasta = self.dash_recarga = self.invencible_hasta = self.golpe_hasta = 0
        self.ultimo_disparo = -99.0  # todos los relojes del jugador usan el tiempo de juego (se detiene en pausa)
        self.escudo, self.iman, self.cadencia, self.proyectiles = 0, 90, 0.70, 1
        self.rect = pygame.Rect(0, 0, 28, 28)
        self.hitbox = pygame.Rect(0, 0, HITBOX_JUGADOR, HITBOX_JUGADOR)
        self.rect.center = self.hitbox.center = self.pos
        self.muerto, self.vida_visual = False, float(self.vidas)
        self.niveles_mejoras = {}
        self.niveles_al_morir = None  # copia de sus habilidades en el momento de morir (para los récords)
        self.nanobots_timer, self.distorsion, self.mult_xp, self.perforante = 0, 1.0, 1.0, 0
        self.termica = self.disparo_lateral = self.ancla = False
        self.ultima_llama = pygame.Vector2(-999, -999)  # donde se dejó la última llama de la estela
        self.espejo_prob = self.prob_critico = 0.0
        self.reduc_dash = 1.0

    def actualizar(self, dt, teclas, ahora):
        c = self.controles
        d = pygame.Vector2(teclas[c["derecha"]] - teclas[c["izquierda"]], teclas[c["abajo"]] - teclas[c["arriba"]])
        if d.length_squared():
            d = d.normalize()
        self.pos += d * self.velocidad * (2.6 if ahora < self.dash_hasta else 1) * dt
        self.pos.x, self.pos.y = limitar(self.pos.x, 16, ANCHO - 16), limitar(self.pos.y, 72, ALTO - 16)
        self.rect.center = self.hitbox.center = round(self.pos.x), round(self.pos.y)
        self.vida_visual += (self.vidas - self.vida_visual) * min(1, 8 * dt)
        nv = self.niveles_mejoras.get("nanobots", 0)
        if nv and self.vidas < self.vidas_max:
            self.nanobots_timer += dt
            if self.nanobots_timer >= (0, 25, 20, 15, 10, 7)[nv]:
                self.vidas, self.nanobots_timer = min(self.vidas_max, self.vidas + 1), 0

    def recibir_dano(self, ahora):
        if self.espejo_prob > 0 and random.random() < self.espejo_prob:
            return
        if self.escudo:
            self.escudo -= 1
        else:
            self.vidas -= 1
        self.invencible_hasta, self.golpe_hasta = ahora + 1.2, ahora + DURACION_GOLPE
        self.muerto = self.vidas <= 0

    def dibujar(self, sup, ahora, vibracion_activada=True):
        restante = self.golpe_hasta - ahora
        golpeado, vib = restante > 0, pygame.Vector2()
        if golpeado:
            amp = 2 + 5 * restante / DURACION_GOLPE
            if vibracion_activada:
                vib.update(random.uniform(-amp, amp), random.uniform(-amp, amp))
            brillo = (170, 25, 25) if int(ahora * 20) % 2 == 0 else (230, 110, 110)
        px, py = self.pos.x + vib.x, self.pos.y + vib.y
        # cuanta más vida pierde, más se tiñe de rojo el sprite (11 pasos para reutilizar imágenes)
        perdida = round(1 - limitar(self.vida_visual / self.vidas_max), 1)
        if self.segundo:  # la nave 2 ya es roja: se oscurece hacia un carmesí profundo
            img = sprite("player", "p2", perdida * 0.92, (150, 0, 0))
        else:
            img = sprite("player", "p1", perdida * 0.92, (255, 25, 25))
        if golpeado:
            img = destello(img, brillo)
            pygame.draw.circle(sup, (140, 15, 15), (round(px), round(py)), 24, 3)
        elif ahora < self.invencible_hasta and int(ahora * 12) % 2 == 0:
            img = destello(img, (140, 140, 140))
        sup.blit(img, img.get_rect(center=(round(px), round(py))))
        if self.escudo > 0:
            pygame.draw.circle(sup, CIAN, self.rect.center, 23, 2)
        fr = limitar(self.vida_visual / self.vidas_max)
        barra = pygame.Rect(round(self.pos.x - 25), round(self.pos.y + 24), 50, 6)
        pygame.draw.rect(sup, (30, 36, 60), barra, border_radius=3)
        if fr > 0:
            pygame.draw.rect(sup, VERDE if fr > 0.6 else AMARILLO if fr > 0.3 else ROJO,
                             (barra.x, barra.y, max(2, round(50 * fr)), 6), border_radius=3)
        pygame.draw.rect(sup, BLANCO, barra, 1, border_radius=3)


STATS = {"zombi": (1, 95, 13, MORADO, 10), "rapido": (1, 160, 9, ROJO, 15),
         "tanque": (3, 55, 19, NARANJA, 30), "tirador": (2, 85, 12, VERDE, 25)}


class Enemigo(pygame.sprite.Sprite):
    def __init__(self, jugador, tipo="zombi", x=None, y=-25, mov="recto", vx=0.0, vy=None,
                 amp=0.0, fase=0.0, y_stop=150, escala=1.0, dispara=False):
        super().__init__()
        self.tipo, self.mov, self.vx, self.amp, self.fase, self.y_stop, self.dispara = tipo, mov, vx, amp, fase, y_stop, dispara
        self.x0 = random.randint(40, ANCHO - 40) if x is None else x
        self.pos, self.edad = pygame.Vector2(self.x0, y), 0.0
        self.vida, self.velocidad, self.radio, self.color, self.puntos = STATS[tipo]
        self.velocidad *= escala
        self.vy = self.velocidad if vy is None else vy
        self.rect = pygame.Rect(0, 0, self.radio * 2, self.radio * 2)
        self.rect.center = self.pos
        self.ultimo_tiro = None  # se inicia con el reloj de juego en la primera actualización
        self.oleada_id = None  # oleada a la que cuenta (los enemigos del jefe no cuentan para el 85%)
        self.escapo = False  # True si se fue por un costado o por arriba sin morir

    def actualizar(self, dt, objetivo, balas_enemigas, ahora):
        self.edad += dt
        if self.ultimo_tiro is None:
            self.ultimo_tiro = ahora - random.uniform(0, 1)
        if objetivo.ancla and self.tipo in ("zombi", "rapido"):
            v = objetivo.pos - self.pos
            if 0 < v.length() < 250:
                self.pos += v.normalize() * 35 * dt
        fd = objetivo.distorsion
        if self.mov == "seno":
            self.pos.y += self.vy * dt
            self.pos.x = self.x0 + self.amp * math.sin(self.edad * 2.2 + self.fase)
        elif self.mov == "tirador":
            if self.edad > 10:
                self.pos.y -= 120 * dt
                if self.pos.y < -40:
                    self.escapo = True
                    self.kill()
            elif self.pos.y < self.y_stop:
                self.pos.y += self.vy * 1.8 * dt
            else:
                self.pos.x = self.x0 + self.amp * math.sin(self.edad * 1.2 + self.fase)
                if ahora - self.ultimo_tiro > 2.0:
                    v = objetivo.pos - self.pos
                    if v.length_squared():
                        balas_enemigas.add(Bala(self.pos, v.normalize() * 220 * fd, ROJO, 7))
                    self.ultimo_tiro = ahora
        else:
            self.pos += pygame.Vector2(self.vx, self.vy) * dt
        if self.dispara and self.mov != "tirador" and self.pos.y > 20 and ahora - self.ultimo_tiro > 2.2:
            balas_enemigas.add(Bala(self.pos, pygame.Vector2(0, 230 * fd), AMARILLO, 6))
            self.ultimo_tiro = ahora
        self.rect.center = round(self.pos.x), round(self.pos.y)
        if self.pos.y > ALTO + 30:
            self.pos.update(random.randint(40, ANCHO - 40), -25)
            self.x0 = self.pos.x
        elif not -80 <= self.pos.x <= ANCHO + 80:
            self.escapo = True
            self.kill()

    SPRITES = {"zombi": ("med", "med"), "rapido": ("fast", "fast"), "tanque": ("tank", "tank"), "tirador": ("med", "b4")}

    def dibujar(self, sup):
        x, y = self.rect.center
        img = sprite(*self.SPRITES[self.tipo])
        sup.blit(img, img.get_rect(center=(x, y)))
        if self.dispara:  # marca de los enemigos que disparan
            pygame.draw.circle(sup, AMARILLO, (x, y), max(3, self.radio // 3))


class Jefe(Enemigo):
    TIPOS = (("ESPIRAL", ROSA), ("CAZADOR", NARANJA), ("PULSAR", VERDE), ("INVOCADOR", MORADO),
             ("BARRIDO", AMARILLO), ("MURALLA", ROJO), ("ENJAMBRE", (255, 140, 200)), ("SINGULARIDAD", (140, 120, 255)))
    MOVIMIENTO = {"MURALLA": (0.7, 110), "PULSAR": (0.6, 120), "BARRIDO": (0.45, 160),
                  "ENJAMBRE": (1.2, 120), "SINGULARIDAD": (0.3, 70)}

    def __init__(self, jugador, nivel=1):
        super().__init__(jugador, "tanque", ANCHO / 2, -60, "jefe")
        self.nivel = max(1, nivel)
        self.tipo_jefe = (self.nivel - 1) % len(self.TIPOS)
        self.nombre, self.color = self.TIPOS[self.tipo_jefe]
        self.vida = self.vida_max = 28 + (self.nivel - 1) * 12
        self.radio, self.puntos = 30, 300 * self.nivel
        self.rect = pygame.Rect(0, 0, 60, 60)
        self.rect.center = self.pos
        self.ritmo = min(2.0, 1 + 0.1 * (self.nivel - 1))
        self.relojes, self.angulo = {}, 0.0

    def listo(self, clave, intervalo, ahora):
        if ahora - self.relojes.get(clave, 0) >= intervalo / self.ritmo:
            self.relojes[clave] = ahora
            return True
        return False

    # (forma, paleta) de cada jefe: primer ciclo de jefes y segundo ciclo (otro color)
    SPRITES_JEFE = {
        "ESPIRAL": (("boss", "b2"), ("boss", "b3")), "CAZADOR": (("boss", "b4"), ("boss", "b1")),
        "PULSAR": (("orb", "orb1"), ("orb", "orb2")), "INVOCADOR": (("boss", "b3"), ("boss", "b2")),
        "BARRIDO": (("fort", "fort1"), ("fort", "fort2")), "MURALLA": (("boss", "b1"), ("boss", "b4")),
        "ENJAMBRE": (("mantis", "mant1"), ("mantis", "mant2")), "SINGULARIDAD": (("manta", "man2"), ("manta", "man1")),
    }

    def dibujar(self, sup):
        img = sprite(*self.SPRITES_JEFE[self.nombre][((self.nivel - 1) // len(self.TIPOS)) % 2])
        sup.blit(img, img.get_rect(center=self.rect.center))
        if self.nombre == "SINGULARIDAD":
            radio = 120 + round(10 * math.sin(self.edad * 4))
            pygame.draw.circle(sup, self.color, self.rect.center, radio, 1)

    def actualizar_jefe(self, dt, objetivo, balas, enemigos, ahora):
        self.edad += dt
        p, n, fd = self.pos, self.nombre, objetivo.distorsion
        v, ciclo = objetivo.pos - p, self.edad % 4
        y_obj, vel_y = 150, 110
        if n == "CAZADOR":
            vel_y = 300
            if ciclo < 2.4:
                p.x += limitar(v.x, -170 * dt, 170 * dt)
            elif ciclo < 3.0:
                y_obj, vel_y = ALTO - 130, 650
        else:
            freq, amp = self.MOVIMIENTO.get(n, (0.9, 130))
            p.x += math.cos(self.edad * freq) * amp * dt
        p.y += limitar(y_obj - p.y, -vel_y * dt, vel_y * dt)
        p.x = limitar(p.x, 60, ANCHO - 60)
        self.rect.center = round(p.x), round(p.y)
        if p.y < 60:
            return

        def disparar(ang, vel, color, radio=7):
            balas.add(Bala(p, pygame.Vector2(math.cos(ang), math.sin(ang)) * vel * fd, color, radio))

        apunte = math.atan2(v.y, v.x)
        if n == "ESPIRAL":
            if self.edad % 6 < 4 and self.listo("espiral", 0.14, ahora):
                self.angulo += 0.42
                for k in range(2):
                    disparar(self.angulo + k * math.pi, 150, ROSA)
        elif n == "CAZADOR":
            if ciclo < 2.4 and p.y < 200 and self.listo("abanico", 0.9, ahora):
                for i in range(5):
                    disparar(apunte + (i - 2) * 0.18, 220, NARANJA, 6)
        elif n == "PULSAR":
            if self.listo("anillo", 1.5, ahora):
                self.angulo += 0.21
                for k in range(18):
                    disparar(self.angulo + k * math.tau / 18, 130, VERDE)
            if self.edad % 6 > 4 and self.listo("racha", 0.5, ahora):
                disparar(apunte, 240, VERDE, 6)
        elif n == "INVOCADOR":
            if self.listo("lluvia", 1.2, ahora):
                for _ in range(6):
                    balas.add(Bala((random.randint(30, ANCHO - 30), 68), (0, 230 * fd), MORADO, 6))
            if len(enemigos) < 14 and self.listo("invocar", 3.0, ahora):
                for lado in (-50, 50):
                    enemigos.add(Enemigo(objetivo, random.choice(["zombi", "rapido"]), p.x + lado, p.y + 30))
        elif n == "BARRIDO":  # 5to jefe: se suavizó la frecuencia y densidad para reducir dificultad
            base = math.pi / 2 + 0.6 * math.sin(self.edad * 0.8)
            if self.listo("barrido", 0.35, ahora):  # intervalo más amplio
                for ang in (base, math.pi - base):
                    disparar(ang, 140, AMARILLO, 6)  # velocidad más baja
            if self.listo("trio", 4.0, ahora):
                for i in range(2):  # menos proyectiles
                    disparar(apunte + (i - 0.5) * 0.16, 180, DORADO, 6)
        elif n == "MURALLA":
            if self.listo("muro", 2.4, ahora):
                hueco = random.randint(80, ANCHO - 80)
                for x in range(30, ANCHO, 45):
                    if abs(x - hueco) > 80:
                        balas.add(Bala((x, p.y + 30), (0, 140 * fd), ROJO, 7))
            if self.listo("apuntado", 0.8, ahora):
                disparar(apunte, 230, AMARILLO, 6)
        elif n == "ENJAMBRE":
            if len(enemigos) < 16 and self.listo("enjambre", 3.2, ahora):
                lado, y0 = random.choice((-1, 1)), random.randint(90, 260)
                for i in range(4):
                    enemigos.add(Enemigo(objetivo, "rapido", -25 if lado == 1 else ANCHO + 25, y0 + i * 40,
                                         vx=lado * 190, vy=25))
            if self.listo("trio", 1.1, ahora):
                for i in range(3):
                    disparar(apunte + (i - 1) * 0.3, 190, self.color, 6)
        else:
            if v.length() > 120:
                objetivo.pos += v.normalize() * 60 * dt
            if self.listo("orbita", 0.35, ahora):
                self.angulo += 0.6
                for k in range(3):
                    disparar(self.angulo + k * math.tau / 3, 110, self.color)
            if self.listo("meteoros", 2.6, ahora):
                for _ in range(5):
                    balas.add(Bala((random.randint(30, ANCHO - 30), 68),
                                   (random.uniform(-40, 40), 200 * fd), self.color, 7))


def crear_oleada(nivel):
    tipo = random.choice(["zombi", "rapido", "tanque", "tirador"][:min(4, nivel)])
    base = {"tipo": tipo, "escala": 1 + min(0.5, (nivel - 1) * 0.08)}
    if tipo == "tirador":
        centro, cant = random.randint(ANCHO // 2 - 100, ANCHO // 2 + 100), random.randint(2, 4)
        return [(i * 0.4, dict(base, x=centro + (i - (cant - 1) / 2) * 160, mov="tirador", amp=50, fase=i,
                               y_stop=random.randint(110, 200))) for i in range(cant)]
    n = random.randint(3, 7 + min(4, nivel // 2))
    if tipo == "tanque":
        n = random.randint(2, max(3, n // 2))
    sep = 80 if tipo == "tanque" else 58
    ancho = (n - 1) * sep
    holgura, medio = ancho / 2 + 40, (n - 1) / 2
    centro = limitar(ANCHO / 2 + random.uniform(-holgura, holgura), 60 + ancho / 2, ANCHO - 60 - ancho / 2)
    patron = random.choice(["fila", "uve", "columna", "serpiente", "diagonal", "bloque", "lateral"])
    if patron == "fila":
        oleada = [(0, dict(base, x=centro + (i - medio) * sep)) for i in range(n)]
    elif patron == "uve":
        oleada = [(0, dict(base, x=centro + (i - medio) * sep, y=-25 - abs(i - medio) * sep * 0.8)) for i in range(n)]
    elif patron == "columna":
        x = random.randint(ANCHO // 2 - 60, ANCHO // 2 + 60)
        oleada = [(i * (0.9 if tipo == "tanque" else 0.45), dict(base, x=x)) for i in range(n)]
    elif patron == "serpiente":
        x = random.randint(ANCHO // 2 - 100, ANCHO // 2 + 100)
        oleada = [(i * 0.35, dict(base, x=x, mov="seno", amp=110)) for i in range(n)]
    elif patron == "diagonal":
        lado = random.choice([-1, 1])
        x = 40 if lado == 1 else ANCHO - 40
        vx = lado * abs(ANCHO / 2 - x) * {"zombi": 95, "rapido": 160, "tanque": 55}[tipo] * base["escala"] / 300
        oleada = [(i * 0.4, dict(base, x=x, vx=vx)) for i in range(n)]
    elif patron == "bloque":
        cols = min(4, n)
        ancho_b = (cols - 1) * sep
        centro_b = ANCHO / 2 + random.uniform(-(ancho_b / 2 + 40), ancho_b / 2 + 40)
        oleada = [(0, dict(base, x=centro_b + (i % cols - (cols - 1) / 2) * sep, y=-25 - (i // cols) * sep)) for i in range(n)]
    else:
        lado, y = random.choice([-1, 1]), random.randint(80, 170)
        oleada = [(i * 0.5, dict(base, x=-25 if lado == 1 else ANCHO + 25, y=y, vx=lado * 150, vy=20)) for i in range(n)]
    if random.random() < 0.35:
        random.choice(oleada)[1]["dispara"] = True
    return oleada


class Bala(pygame.sprite.Sprite):
    def __init__(self, posicion, velocidad, color=CIAN, radio=5, penetracion=1, dano=1):
        super().__init__()
        self.pos, self.velocidad = pygame.Vector2(posicion), pygame.Vector2(velocidad)
        self.color, self.radio, self.penetracion, self.dano = color, radio, penetracion, dano
        self.golpeados = set()  # enemigos que esta bala ya dañó (cada uno recibe el daño una sola vez)
        self.rect = pygame.Rect(0, 0, radio * 2, radio * 2)
        self.rect.center = self.pos

    def update(self, dt):
        self.pos += self.velocidad * dt
        self.rect.center = round(self.pos.x), round(self.pos.y)
        if not (-40 <= self.pos.x <= ANCHO + 40 and -40 <= self.pos.y <= ALTO + 40):
            self.kill()

    def dibujar(self, sup):
        pygame.draw.circle(sup, self.color, self.rect.center, self.radio)


class Cristal(pygame.sprite.Sprite):
    # El panel superior (HUD) tapa los primeros 64 px de la pantalla. Un cristal que nace por encima de ese límite
    # no se ve, así que baja solo hasta Y_CAIDA_FINAL para que el jugador note que ahí hay experiencia.
    Y_OCULTO = 72
    Y_CAIDA_FINAL = 110
    VIDA, PARPADEO = 20.0, 4.0  # segundos que dura un cristal sin recoger / segundos finales en que parpadea

    def __init__(self, posicion, valor=1):
        super().__init__()
        self.pos, self.valor = pygame.Vector2(posicion), valor
        self.rect = pygame.Rect(0, 0, 12, 12)
        self.rect.center = self.pos
        self.cayendo = self.pos.y < self.Y_OCULTO
        self.edad = 0.0

    def caer(self, dt):
        """Baja el cristal (frenando al llegar) si nació fuera de la vista por arriba. Se llama una vez por fotograma."""
        if not self.cayendo:
            return
        falta = self.Y_CAIDA_FINAL - self.pos.y
        if falta <= 1:
            self.cayendo = False
            return
        self.pos.y += min(falta, limitar(falta * 2.5, 70, 260) * dt)
        self.rect.center = round(self.pos.x), round(self.pos.y)

    def actualizar(self, dt, jugadores):
        """Envejece el cristal y lo atrae hacia el jugador más cercano que lo tenga dentro de su imán (se mueve una sola vez)."""
        self.edad += dt
        if self.edad >= self.VIDA:
            self.kill()
            return
        objetivo, distancia = None, 0.0
        for j in jugadores:
            d = (j.pos - self.pos).length()
            if 0 < d < j.iman and (objetivo is None or d < distancia):
                objetivo, distancia = j, d
        if objetivo is not None:
            self.pos += (objetivo.pos - self.pos) / distancia * 190 * dt
        self.rect.center = round(self.pos.x), round(self.pos.y)

    def dibujar(self, sup):
        if self.edad > self.VIDA - self.PARPADEO and int(self.edad * 8) % 2 == 0:
            return  # parpadea en sus últimos segundos para avisar que va a desaparecer
        x, y = self.rect.center
        rombo = [(x, y - 7), (x + 7, y), (x, y + 7), (x - 7, y)]
        pygame.draw.polygon(sup, CIAN, rombo)
        pygame.draw.polygon(sup, BLANCO, rombo, 1)


def obtener_opciones_con_calidad(jugador):
    pool = [m for m in MEJORAS if jugador.niveles_mejoras.get(m[2], 0) < nivel_maximo(m[2])]
    pesos, elegidas = [CALIDADES[m[3]]["prob"] for m in pool], []
    while pool and len(elegidas) < 3:
        i = random.choices(range(len(pool)), pesos)[0]
        elegidas.append(pool.pop(i))
        pesos.pop(i)
    return elegidas


def aplicar_mejora(j, tipo):
    # Restricción estricta de nivel máximo (tope por defecto 5)
    max_niv = nivel_maximo(tipo)
    actual = j.niveles_mejoras.get(tipo, 0)
    if actual >= max_niv:
        j.niveles_mejoras[tipo] = max_niv
        return
    nv = j.niveles_mejoras[tipo] = min(max_niv, actual + 1)
    
    if tipo == "turbo":
        j.velocidad *= 1.15
    elif tipo == "cadencia":
        j.cadencia = max(0.20, j.cadencia * 0.80)
    elif tipo == "iman":
        j.iman += 80
    elif tipo == "doble":
        j.proyectiles = min(5, j.proyectiles + 1)
    elif tipo == "escudo":
        j.escudo += 1
    elif tipo == "vida":
        j.vidas_max += 1
        j.vidas = min(j.vidas + 1, j.vidas_max)
    elif tipo == "dash":
        j.reduc_dash *= 0.82
    elif tipo == "distorsion":
        j.distorsion = max(0.50, 1.0 - nv * 0.10)
    elif tipo == "hipercargador":
        j.mult_xp = 1.0 + nv * 0.20
    elif tipo == "perforante":
        j.perforante = nv if nv < 5 else 99
    elif tipo == "termica":
        j.termica = True
    elif tipo == "espejo":
        j.espejo_prob = min(0.75, nv * 0.15)
    elif tipo == "lateral":
        j.disparo_lateral = True
    elif tipo == "ancla":
        j.ancla = True
    elif tipo == "critico":
        j.prob_critico = min(0.35, nv * 0.07)
    elif tipo == "estabilizador":
        j.reduc_dash *= 0.60


def traspasar_mejoras(origen, destino):
    vidas = destino.vidas
    recibidos = 0
    for tipo, nivel in list(origen.niveles_mejoras.items()):
        max_niv = nivel_maximo(tipo)
        objetivo = min(max_niv, destino.niveles_mejoras.get(tipo, 0) + nivel)
        while destino.niveles_mejoras.get(tipo, 0) < objetivo:
            aplicar_mejora(destino, tipo)
            recibidos += 1
    destino.vidas = min(vidas, destino.vidas_max)
    destino.vida_visual = min(destino.vida_visual, float(destino.vidas))
    origen.niveles_mejoras = {}
    return recibidos


def animacion_legendaria(escena, centro, nombre):
    AUDIO.reproducir("legendario")
    cx, cy = round(centro[0]), round(centro[1])
    capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    chispas = [(random.uniform(0, math.tau), random.uniform(0.5, 1.3), random.randint(2, 5)) for _ in range(60)]
    inicio, dur = pygame.time.get_ticks() / 1000, 1.1
    while (t := (pygame.time.get_ticks() / 1000 - inicio) / dur) < 1:
        pygame.event.pump()
        capa.fill((255, 200, 40, round(70 * max(0, 1 - t * 2.5))))
        pygame.draw.circle(capa, (255, 235, 140, round(150 * max(0, 1 - t * 3))), (cx, cy), 34)
        for k in range(3):
            p = (t - 0.09 * k) / 0.65
            if 0 < p < 1:
                radio = round(28 + 950 * (1 - (1 - p) ** 3))
                for grosor, (r, g, b, a) in ((22, (255, 160, 0, 40)), (12, (255, 205, 40, 90)), (5, (255, 250, 200, 255))):
                    pygame.draw.circle(capa, (r, g, b, round(a * (1 - p))), (cx, cy), radio,
                                       min(radio, round(grosor * (1 - p * 0.6)) + 1))
        e = 1 - (1 - t) ** 3
        for ang, vel, tam in chispas:
            d = 30 + 650 * vel * e
            pygame.draw.circle(capa, (255, 230, 120, round(255 * (1 - t))),
                               (round(cx + math.cos(ang) * d), round(cy + math.sin(ang) * d)), tam)
        sacudida = (round(random.uniform(-5, 5) * (1 - t)), round(random.uniform(-5, 5) * (1 - t))) if CONFIG["vibracion"] else (0, 0)
        VENTANA.fill(NEGRO)
        VENTANA.blit(escena, sacudida)
        VENTANA.blit(capa, (0, 0))
        if t > 0.12:
            texto(VENTANA, "¡LEGENDARIO!", ANCHO // 2, 120, FUENTE_GRANDE, DORADO, True)
            texto(VENTANA, nombre, ANCHO // 2, 170, FUENTE, (255, 240, 170), True)
        pygame.display.flip()
        RELOJ.tick(FPS)


def dibujar_aviso_jefe(sup, restante, oleada, ahora):
    pulso = 0.5 + 0.5 * math.sin(ahora * math.tau * 3.2)
    CAPA_ALERTA.fill((210, 0, 35, round(20 + 48 * pulso)))
    sup.blit(CAPA_ALERTA, (0, 0))
    pygame.draw.rect(sup, ROJO, (8, 8, ANCHO - 16, ALTO - 16), 5 + round(5 * pulso), border_radius=10)
    panel = pygame.Rect(ANCHO // 2 - 330, ALTO // 2 - 92, 660, 184)
    caja(sup, panel, ROJO, (35, 5, 18), 3, 12)
    nombre = Jefe.TIPOS[(oleada - 1) % len(Jefe.TIPOS)][0]
    texto(sup, "BOSS IS COMING", ANCHO // 2, ALTO // 2 - 34, (48 + round(pulso * 5), True),
          BLANCO if pulso > 0.45 else ROJO, True, panel.width - 30)
    texto(sup, f"OLEADA {oleada} · {nombre} · PREPÁRATE", ANCHO // 2, ALTO // 2 + 24, FUENTE, BLANCO, True)
    texto(sup, max(1, math.ceil(restante)), ANCHO // 2, ALTO // 2 + 62, (26, True), ROJO, True)


def dibujar_mejoras(sup, opciones, jugador, cooperativo=False):
    color_panel = jugador.color if cooperativo else CIAN
    caja(sup, pygame.Rect(50, 180, 900, 350), color_panel, (12, 18, 40), 2, 12)
    if cooperativo:
        quien = "JUGADOR 2" if jugador.segundo else "JUGADOR 1"
        texto(sup, f"¡{quien} SUBIÓ DE NIVEL! ELIGE UNA MEJORA PARA {quien}", ANCHO // 2, 215, FUENTE, color_panel, True, 840)
    else:
        texto(sup, "¡SUBISTE DE NIVEL! ELEGÍ UNA MEJORA", ANCHO // 2, 215, FUENTE, CIAN, True, 840)
    mouse, rects = pygame.mouse.get_pos(), []
    x0 = (ANCHO - (3 * 270 + 2 * 25)) // 2
    for i, (nombre, descripcion, tipo, calidad) in enumerate(opciones):
        rect = pygame.Rect(x0 + i * 295, 250, 270, 200)
        rects.append(rect)
        color = CALIDADES[calidad]["color"]
        caja(sup, rect, color, (24, 34, 66) if rect.collidepoint(mouse) else PANEL)
        nivel = jugador.niveles_mejoras.get(tipo, 0) + 1
        texto(sup, f"[{CALIDADES[calidad]['nombre']} - NV.{nivel}/{nivel_maximo(tipo)}]", rect.centerx, rect.y + 25, FUENTE_CHICA, color, True, rect.width - 20)
        texto(sup, nombre, rect.centerx, rect.y + 65, FUENTE, BLANCO, True, rect.width - 20)
        lineas, tam = ajustar_descripcion(descripcion, rect.width - 28)
        for j, linea in enumerate(lineas):
            texto(sup, linea, rect.centerx, rect.y + 120 + j * (tam + 6), (tam, False), (200, 220, 240), True, rect.width - 28)
    texto(sup, "Pulsa 1, 2, 3 o haz clic", ANCHO // 2, 490, FUENTE_CHICA, BLANCO, True)
    return rects


MEJORA_POR_TIPO = {m[2]: m for m in MEJORAS}
ORDEN_CALIDAD = ("legendario", "epico", "raro", "normal")


# --- ICONOS DE LAS HABILIDADES (pixel art de iconos_habilidades_glitch_survivor.html) ---
# Cada icono es una cuadrícula de 14x14 que se dibuja dentro de un marco de 16x16 del color de su calidad.
ICONO_PALETA = {
    "r": "#dc2626",
    "R": "#7f1d1d",
    "f": "#fb923c",
    "e": "#fde047",
    "y": "#fff7c2",
    "w": "#ffffff",
    "s": "#9ca3af",
    "S": "#4b5563",
    "c": "#22d3ee",
    "C": "#a5f3fc",
    "d": "#0e7490",
    "b": "#3b82f6",
    "B": "#bfdbfe",
    "g": "#4ade80",
    "G": "#15803d",
    "l": "#bbf7d0",
    "p": "#a855f7",
    "P": "#e9d5ff",
    "m": "#fb7185",
}
MARCOS_ICONO = {  # (borde, esquinas) por calidad
    "normal": ("#d1d5db", "#6b7280"), "raro": ("#3b82f6", "#1e3a8a"),
    "epico": ("#a855f7", "#581c87"), "legendario": ("#fbbf24", "#b45309"),
}
ICONOS = {
    "turbo": (
        "..............", "......ww......",
        ".....wccw.....", "....wccccw....",
        "...wccccccw...", "..wwwwwwwwww..",
        "c....wccw....c", ".....wccw.....",
        "c....wccw....c", ".....feef.....",
        "c....fyyf....c", "......ee......",
        "......ff......", "..............",
    ),
    "cadencia": (
        "......yy......", "......ee......",
        "......ee......", "..yy..ee..yy..",
        "..ee..ff..ee..", "..ee..ff..ee..",
        "..ee..rr..ee..", "..ef......fe..",
        "..ff......ff..", "..rr......rr..",
        "..............", ".....ssss.....",
        "...ssssssss...", "..............",
    ),
    "iman": (
        "..............", "......CC......",
        ".....CccC.....", "......cc......",
        "..............", ".www......www.",
        ".sss......sss.", ".rrr......rrr.",
        ".rrr......rrr.", ".rrr......rrr.",
        ".rrrrrrrrrrrr.", "..rrrrrrrrrr..",
        "...rrrrrrrr...", "..............",
    ),
    "doble": (
        "..............", "......yy......",
        "......ee......", "......ee......",
        "..y...ee...y..", "...e..ee..e...",
        "y..e..ee..e..y", ".e..e.ee.e..e.",
        "..e.e.ee.e.e..", "...e.ffff.e...",
        "....ffffff....", ".....ssss.....",
        "...ssssssss...", "..............",
    ),
    "escudo": (
        "..............", ".dddddddddddd.",
        ".dCCCCccCCCCd.", ".dCcccwwcccCd.",
        ".dCcccwwcccCd.", ".dCwwwwwwwwCd.",
        ".dCcccwwcccCd.", "..dCccwwccCd..",
        "..dCccccccCd..", "...dccccccd...",
        "....dccccd....", ".....dccd.....",
        "......dd......", "..............",
    ),
    "vida": (
        "..............", "..............",
        "..RRR....RRR..", ".RmwrrRRrrwmR.",
        "RmwrrrrrrrrwmR", "RmrrrrrrrrrrmR",
        "RrrrrrrrrrrrrR", ".RrrrrrrrrrrR.",
        "..RrrrrrrrrR..", "...RrrrrrrR...",
        "....RrrrrR....", ".....RrrR.....",
        "......RR......", "..............",
    ),
    "dash": (
        ".....BBBB.....", "......bb......",
        "...bbbbbbbb...", "..bb......bb..",
        ".bb...ee...bb.", ".b....ee....b.",
        ".b....ee....b.", ".bB..yyyy..Bb.",
        ".b..........b.", ".b..........b.",
        ".bb........bb.", "..bb......bb..",
        "...bbbbbbbb...", "..............",
    ),
    "nanobots": (
        "..............", "y....GGGG....y",
        ".c...GggG...c.", ".....GggG.....",
        ".GGGGGggGGGGG.", ".GllggggggllG.",
        ".GggggggggggG.", ".GggggggggggG.",
        ".GGGGGggGGGGG.", ".....GggG.....",
        ".c...GggG...c.", "y....GGGG....y",
        "..............", "..............",
    ),
    "distorsion": (
        ".....pppp.....", "....pppppp....",
        "..............", ".pp..PPPP..pp.",
        ".p..PP..PP..p.", "pp.PP.ww.PP.pp",
        "pp.P.wwww.P.pp", "pp.P.wwww.P.pp",
        "...PP.ww.PP...", "....PP..PP....",
        ".pp..PPPP..pp.", "..pp......pp..",
        "...ppp..ppp...", ".....p..p.....",
    ),
    "hipercargador": (
        ".e..........e.", "eee........eee",
        ".e.dCCCCCCd.e.", "..dCwccccwCd..",
        ".dCwccccccwCd.", "dddddddddddddd",
        ".dCCccccccCCd.", "..dCccccccCd..",
        "...dccccccd...", "....dccccd....",
        ".....dccd.....", "......dd......",
        "..............", "..............",
    ),
    "perforante": (
        "......rr......", ".....rrrr.....",
        ".....swws.....", ".....swws.....",
        ".....swws.....", ".ggggswwsgggg.",
        ".ggggswwsgggg.", ".gGGgswwsgGGg.",
        "..gggswwsggg..", ".....swws.....",
        "...rssssssr...", ".....feef.....",
        "......ff......", "..............",
    ),
    "termica": (
        "..............", "......rr......",
        ".....rffr.....", "....rfeefr....",
        "...rfeyyefr...", "...rfeyyefr...",
        "..rfeyyyyefr..", "..rfeyyyyefr..",
        "...rfeyyefr...", "....rfeefr....",
        ".....rssr.....", "....ssssss....",
        "..............", "..............",
    ),
    "espejo": (
        "SSSSSSSSSSSSSS", "SssssssswwsBsS",
        "SsssssswwsBssS", "SssssswwsBsssS",
        "SsssswwsBssssS", "SssswwsBsssssS",
        "SsswwsBssssssS", "SswwsBsssssssS",
        "..wsBsssssss..", "...SssssssS...",
        "....SssssS....", ".....SssS.....",
        "......SS......", "......SS......",
    ),
    "lateral": (
        "..............", "......yy......",
        "y.....ee.....y", ".e....ee....e.",
        "......ff......", "..e........e..",
        "...f......f...", ".....rffr.....",
        "....rfeefr....", "...rfeyyefr...",
        "...rfeyyefr...", "....rfeefr....",
        ".....rffr.....", "..............",
    ),
    "ancla": (
        ".....wwww.....", ".....w..w.....",
        "g....wwww....g", "gc....ss....cg",
        "...ssssssss...", "......ss......",
        "......ss......", ".w....ss....w.",
        ".s....ss....s.", ".s....ss....s.",
        ".ss...ss...ss.", "..ssssssssss..",
        "gc..........cg", "..............",
    ),
    "critico": (
        "......yyyyy...", ".....yeeeef...",
        "....yeeeff...c", "...yeeeff.....",
        "...yyyyeeeef..", ".......eeff...",
        "c.....eeff....", ".....eeff.....",
        "....eeff......", "...eeff......c",
        "...eff........", "..ef..........",
        "..f...........", "..............",
    ),
    "estabilizador": (
        "......ll......", "......gg......",
        "....gggggg....", "...g..ll..g...",
        "..g........g..", "..g...ww...g..",
        "lggl.wwww.lggl", "lggl.wwww.lggl",
        "..g...ww...g..", "..g........g..",
        "...g..ll..g...", "....gggggg....",
        "......gg......", "......ll......",
    ),
}
_CACHE_ICONOS = {}


def icono_habilidad(tipo, escala=4):
    """Superficie con el icono de una habilidad (16 x 16 píxeles de icono multiplicados por la escala)."""
    clave = (tipo, escala)
    if clave not in _CACHE_ICONOS:
        borde, esquinas = MARCOS_ICONO[MEJORA_POR_TIPO[tipo][3]]
        base = pygame.Surface((16, 16))
        base.fill(pygame.Color(borde))
        base.fill((20, 16, 13), (1, 1, 14, 14))
        for x, y in ((0, 0), (15, 0), (0, 15), (15, 15)):
            base.set_at((x, y), pygame.Color(esquinas))
        for j, fila in enumerate(ICONOS[tipo]):
            for i, letra in enumerate(fila):
                if letra != ".":
                    base.set_at((1 + i, 1 + j), pygame.Color(ICONO_PALETA[letra]))
        _CACHE_ICONOS[clave] = pygame.transform.scale(base, (16 * escala, 16 * escala)).convert()
    return _CACHE_ICONOS[clave]


def texto_partes(sup, partes, cx, cy, tam, ancho_max):
    """Dibuja varios textos de distinto color en una sola línea centrada, reduciendo la letra si no cabe."""
    while tam > TAM_MINIMO and sum(obtener_fuente(tam).size(t)[0] for t, _ in partes) > ancho_max:
        tam -= 1
    fuente = obtener_fuente(tam)
    x = cx - sum(fuente.size(t)[0] for t, _ in partes) // 2
    for t, color in partes:
        img = imagen_texto(t, tam, False, color, 10 ** 6)
        sup.blit(img, (x, cy - img.get_height() // 2))
        x += img.get_width()


def dibujar_iconos_habilidades(sup, titulo, color, niveles, rect, vacio="Sin habilidades elegidas", mostrar_max=False):
    """Cuadrícula de iconos: debajo de cada uno, el nombre de la habilidad y, a su lado, el nivel alcanzado
    (con mostrar_max, también el nivel máximo: NV.2/5)."""
    texto(sup, titulo, rect.centerx, rect.y, FUENTE, color, True, rect.width - 10)
    items = sorted(((MEJORA_POR_TIPO[t], n) for t, n in niveles.items() if t in MEJORA_POR_TIPO and n > 0),
                   key=lambda it: (ORDEN_CALIDAD.index(it[0][3]), it[0][0]))
    if not items:
        texto(sup, vacio, rect.centerx, rect.y + 45, FUENTE_CHICA, (150, 170, 200), True, rect.width - 10)
        return
    # se elige el icono más grande con el que caben todos dentro del rectángulo
    opciones = ((4, 6), (3, 6), (2, 6)) if rect.width >= 560 else ((3, 3), (2, 3), (2, 4))
    for esc, columnas in opciones:
        alto_carta = 16 * esc + 26
        if 34 + math.ceil(len(items) / columnas) * alto_carta <= rect.height:
            break
    ancho_carta = rect.width // columnas
    for i, ((nombre, _, tipo, calidad), nivel) in enumerate(items):
        fila, col = divmod(i, columnas)
        cx = rect.x + col * ancho_carta + ancho_carta // 2
        y = rect.y + 34 + fila * alto_carta
        img = icono_habilidad(tipo, esc)
        sup.blit(img, img.get_rect(midtop=(cx, y)))
        nivel_txt = f"  NV.{nivel}/{nivel_maximo(tipo)}" if mostrar_max else f"  NV.{nivel}"
        texto_partes(sup, [(nombre, CALIDADES[calidad]["color"]), (nivel_txt, AMARILLO)],
                     cx, y + 16 * esc + 12, 15, ancho_carta - 6)


def asignar_tecla(jugador, accion, tecla):
    controles = CONFIG[jugador]
    for otra in ACCIONES:
        if otra != accion and controles[otra] == tecla:
            controles[otra] = controles[accion]
    controles[accion] = tecla
    guardar_configuracion()


def menu_configuracion():
    capturando, mensaje = None, ""
    menos, mas, barra = pygame.Rect(745, 449, 42, 40), pygame.Rect(797, 449, 42, 40), pygame.Rect(360, 463, 360, 12)
    vibracion, restablecer, volver = pygame.Rect(55, 513, 890, 50), pygame.Rect(55, 590, 250, 48), pygame.Rect(695, 590, 250, 48)
    while True:
        RELOJ.tick(FPS)
        fondo()
        mouse, rects = pygame.mouse.get_pos(), {}
        texto(VENTANA, "CONFIGURACIÓN", ANCHO // 2, 58, FUENTE_GRANDE, CIAN, True)
        texto(VENTANA, "Haz clic en una tecla para cambiarla", ANCHO // 2, 103, FUENTE_CHICA, BLANCO, True)
        texto(VENTANA, "JUGADOR 1", 255, 145, FUENTE, CIAN, True)
        texto(VENTANA, "JUGADOR 2", 745, 145, FUENTE, ROSA, True)
        for i, accion in enumerate(ACCIONES):
            for jug, x, color in (("controles1", 55, CIAN), ("controles2", 545, ROSA)):
                rect = rects[(jug, accion)] = pygame.Rect(x, 173 + i * 50, 400, 42)
                activo = capturando == (jug, accion)
                caja(VENTANA, rect, AMARILLO if activo else color, (28, 38, 68) if activo or rect.collidepoint(mouse) else PANEL, r=7)
                texto(VENTANA, ETIQUETAS_ACCION[accion], rect.x + 16, rect.y + 12, FUENTE_CHICA, BLANCO, False, 175)
                texto(VENTANA, "PULSA UNA TECLA..." if activo else nombre_tecla(CONFIG[jug][accion]),
                      rect.right - 102, rect.centery, (15, True), AMARILLO if activo else color, True, 180)
        caja(VENTANA, pygame.Rect(55, 440, 890, 58), CIAN)
        texto(VENTANA, "VOLUMEN", 75, 458)
        pygame.draw.rect(VENTANA, (40, 50, 75), barra, border_radius=6)
        if round(barra.width * CONFIG["volumen"]):
            pygame.draw.rect(VENTANA, CIAN, (barra.x, barra.y, round(barra.width * CONFIG["volumen"]), barra.height), border_radius=6)
        boton_dibujar(menos, "−")
        boton_dibujar(mas, "+")
        texto(VENTANA, f"{round(CONFIG['volumen'] * 100)}%", 895, 469, FUENTE_CHICA, BLANCO, True, 80)
        caja(VENTANA, vibracion, MORADO, (24, 34, 66) if vibracion.collidepoint(mouse) else PANEL)
        texto(VENTANA, "VIBRACIÓN DE PANTALLA", 75, 528, FUENTE, BLANCO, False, 500)
        texto(VENTANA, "ACTIVADA" if CONFIG["vibracion"] else "DESACTIVADA", 835, 538, (18, True),
              VERDE if CONFIG["vibracion"] else ROJO, True, 180)
        boton_dibujar(restablecer, "RESTABLECER", MORADO)
        boton_dibujar(volver, "VOLVER")
        texto(VENTANA, "ESC: volver  ·  ESC cancela una reasignación", ANCHO // 2, 620, FUENTE_CHICA, BLANCO, True, 360)
        msg, col = ((mensaje, ROJO) if mensaje else
                    (f"{capturando[0][-1]} · {ETIQUETAS_ACCION[capturando[1]]}: pulsa la nueva tecla", AMARILLO) if capturando
                    else ("No se pudo guardar: revisa los permisos de la carpeta data", ROJO) if ESTADO["error_guardado"]
                    else ("Los cambios se guardan automáticamente", VERDE))
        texto(VENTANA, msg, ANCHO // 2, 670, FUENTE_CHICA, col, True)
        pygame.display.flip()

        for e in eventos():
            if e.type == pygame.KEYDOWN:
                if capturando:
                    if e.key == pygame.K_p:
                        mensaje = "P está reservada para pausar; elige otra tecla"
                    elif e.key != pygame.K_ESCAPE:
                        asignar_tecla(*capturando, e.key)
                        mensaje = ""
                        AUDIO.reproducir("click")
                    capturando = None
                elif e.key == pygame.K_ESCAPE:
                    return
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and not capturando:
                pos, zona_barra = e.pos, barra.inflate(0, 28)
                clave = next((k for k, r in rects.items() if r.collidepoint(pos)), None)
                if clave:
                    capturando, mensaje = clave, ""
                elif menos.collidepoint(pos) or mas.collidepoint(pos) or zona_barra.collidepoint(pos):
                    if zona_barra.collidepoint(pos) and not (menos.collidepoint(pos) or mas.collidepoint(pos)):
                        CONFIG["volumen"] = limitar((pos[0] - barra.x) / barra.width)
                    else:
                        CONFIG["volumen"] = limitar(round(CONFIG["volumen"] + (0.1 if mas.collidepoint(pos) else -0.1), 2))
                    guardar_configuracion()
                elif vibracion.collidepoint(pos):
                    CONFIG["vibracion"] = not CONFIG["vibracion"]
                    guardar_configuracion()
                elif restablecer.collidepoint(pos):
                    CONFIG.clear()
                    CONFIG.update(configuracion_predeterminada())
                    guardar_configuracion()
                elif volver.collidepoint(pos):
                    AUDIO.reproducir("click")
                    return
                else:
                    continue
                AUDIO.reproducir("click")


def menu():
    botones = (("jugar", "JUGAR", CIAN, 335, 54), ("config", "CONFIGURACIÓN", CIAN, 407, 52),
               ("records", "RÉCORDS", MORADO, 477, 52), ("salir", "SALIR", ROJO, 547, 52))
    rects = {n: pygame.Rect(ANCHO // 2 - 140, y, 280, h) for n, _, _, y, h in botones}
    while True:
        RELOJ.tick(FPS)
        fondo()
        c1 = CONFIG["controles1"]
        texto(VENTANA, "GLITCH SURVIVOR", ANCHO // 2, 120, FUENTE_GRANDE, CIAN, True)
        texto(VENTANA, "SOBREVIVE A LAS OLEADAS. MEJORA TU NAVE.", ANCHO // 2, 180, FUENTE, BLANCO, True)
        teclas_p1 = "".join(nombre_tecla(c1[a]) for a in ("arriba", "izquierda", "abajo", "derecha"))
        texto(VENTANA, f"P1: {teclas_p1}  |  Dash: {nombre_tecla(c1['dash'])}", ANCHO // 2, 248, FUENTE, BLANCO, True)
        texto(VENTANA, "Pulsa 1 para un jugador o 2 para cooperativo", ANCHO // 2, 285, FUENTE_CHICA, BLANCO, True)
        for n, titulo, color, _, _ in botones:
            boton_dibujar(rects[n], titulo, color)
        texto(VENTANA, f"Jefe tras {CONJUNTOS_POR_OLEADA} conjuntos (eliminando el {round(PORCENTAJE_PARA_JEFE * 100)}% de los enemigos)", ANCHO // 2, 640, FUENTE_CHICA, ROSA, True)
        if ESTADO["error_guardado"]:
            texto(VENTANA, "No se pudo guardar en la carpeta data (¿sin permisos?): récords y ajustes no se conservarán",
                  ANCHO // 2, 672, FUENTE_CHICA, ROJO, True)
        pygame.display.flip()
        for e in eventos():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    salir()
                if e.key in (pygame.K_1, pygame.K_2):
                    AUDIO.reproducir("click")
                    return e.key == pygame.K_2
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if rects["jugar"].collidepoint(e.pos):
                    AUDIO.reproducir("click")
                    return False
                if rects["config"].collidepoint(e.pos):
                    AUDIO.reproducir("click")
                    menu_configuracion()
                elif rects["records"].collidepoint(e.pos):
                    AUDIO.reproducir("click")
                    ver_records()
                elif rects["salir"].collidepoint(e.pos):
                    salir()


def ver_detalle_record(posicion, r):
    mejoras = r.get("mejoras")
    colores = (CIAN, ROSA)
    while True:
        RELOJ.tick(FPS)
        fondo()
        texto(VENTANA, f"RÉCORD #{posicion}  ·  {r.get('score', 0)} pts  ·  {r.get('time', '00:00')}",
              ANCHO // 2, 70, FUENTE, AMARILLO, True, 900)
        texto(VENTANA, "HABILIDADES DE ESA PARTIDA", ANCHO // 2, 115, FUENTE_GRANDE, CIAN, True, 900)
        if mejoras is None:
            texto(VENTANA, "Este récord es de una versión anterior y no guardó sus habilidades.",
                  ANCHO // 2, 260, FUENTE_CHICA, BLANCO, True, 900)
        elif len(mejoras) == 1:
            dibujar_iconos_habilidades(VENTANA, "HABILIDADES", CIAN, mejoras[0], pygame.Rect(60, 175, 880, 450))
        else:
            for i, niveles in enumerate(mejoras):
                dibujar_iconos_habilidades(VENTANA, f"JUGADOR {i + 1}", colores[i % 2], niveles,
                                           pygame.Rect(60 + i * 450, 175, 430, 450))
        texto(VENTANA, "Pulsa ESC o haz clic para volver", ANCHO // 2, 650, FUENTE_CHICA, MORADO, True)
        pygame.display.flip()
        for e in eventos():
            if (e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_RETURN)) or e.type == pygame.MOUSEBUTTONDOWN:
                return


def ver_records():
    coop = False
    area = pygame.Rect(ANCHO // 2 - 320, 125, 640, 395)  # zona visible de la lista
    paso, alto_fila = 56, 48
    pista = pygame.Rect(area.right + 14, area.y, 12, area.height)
    btn_volver = pygame.Rect(ANCHO // 2 - 125, 590, 250, 42)
    pestana_solo, pestana_coop = pygame.Rect(ANCHO // 2 - 250, 80, 240, 34), pygame.Rect(ANCHO // 2 + 10, 80, 240, 34)

    def cargar(modo):
        lista = cargar_records(modo)
        alto_total = max(0, len(lista) * paso - (paso - alto_fila))
        return lista, alto_total, max(0, alto_total - area.height)

    records, total, max_scroll = cargar(coop)
    scroll, arrastrando = 0.0, False

    def barra():  # (rectángulo del control deslizante) según el desplazamiento actual
        alto = max(30, round(area.height * area.height / total)) if total > area.height else area.height
        y = pista.y + round((pista.height - alto) * (scroll / max_scroll)) if max_scroll else pista.y
        return pygame.Rect(pista.x, y, pista.width, alto)

    while True:
        RELOJ.tick(FPS)
        fondo()
        mouse = pygame.mouse.get_pos()
        texto(VENTANA, "MEJORES RÉCORDS (TOP 10)", ANCHO // 2, 42, FUENTE_GRANDE, CIAN, True)
        for rect, titulo, activa in ((pestana_solo, "1 JUGADOR", not coop), (pestana_coop, "COOPERATIVO", coop)):
            caja(VENTANA, rect, AMARILLO if activa else MORADO, (28, 38, 68) if activa or rect.collidepoint(mouse) else PANEL, r=7)
            texto(VENTANA, titulo, rect.centerx, rect.centery, FUENTE_CHICA, AMARILLO if activa else BLANCO, True, rect.width - 16)
        if not records:
            texto(VENTANA, "Todavía no hay puntajes guardados.", ANCHO // 2, 240, FUENTE, BLANCO, True)
        VENTANA.set_clip(area)
        for i, r in enumerate(records):
            fila = pygame.Rect(area.x, area.y + i * paso - round(scroll), area.width, alto_fila)
            if fila.bottom < area.y or fila.y > area.bottom:
                continue
            sobre = fila.collidepoint(mouse) and area.collidepoint(mouse)
            caja(VENTANA, fila, MORADO, (24, 34, 66) if sobre else PANEL, r=7)
            texto(VENTANA, f"{i + 1}. {r.get('name', 'JUGADOR')}  {r.get('score', 0)} pts  {r.get('time', '00:00')}",
                  fila.centerx, fila.centery, FUENTE, BLANCO, True, fila.width - 20)
        VENTANA.set_clip(None)
        if max_scroll:
            pygame.draw.rect(VENTANA, (30, 36, 60), pista, border_radius=6)
            pygame.draw.rect(VENTANA, CIAN if arrastrando or barra().collidepoint(mouse) else MORADO, barra(), border_radius=6)
            texto(VENTANA, "Usa la rueda del ratón para desplazarte por la lista", ANCHO // 2, 543, FUENTE_CHICA, ROSA, True)
        texto(VENTANA, "Haz clic en un récord para ver las habilidades elegidas  ·  TAB cambia de lista", ANCHO // 2, 565,
              FUENTE_CHICA, AMARILLO, True)
        boton_dibujar(btn_volver, "VOLVER", MORADO)
        pygame.display.flip()

        for e in eventos():
            nuevo_modo = None
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    return
                if e.key in (pygame.K_TAB, pygame.K_LEFT, pygame.K_RIGHT):
                    nuevo_modo = not coop
                if e.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                    mov = {pygame.K_UP: -paso, pygame.K_DOWN: paso, pygame.K_PAGEUP: -area.height, pygame.K_PAGEDOWN: area.height}[e.key]
                    scroll = limitar(scroll + mov, 0, max_scroll)
            elif e.type == pygame.MOUSEWHEEL:
                scroll = limitar(scroll - e.y * 44, 0, max_scroll)
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                arrastrando = False
            elif e.type == pygame.MOUSEMOTION and arrastrando and max_scroll:
                alto = barra().height
                scroll = limitar((e.pos[1] - pista.y - alto / 2) / max(1, pista.height - alto) * max_scroll, 0, max_scroll)
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if btn_volver.collidepoint(e.pos):
                    AUDIO.reproducir("click")
                    return
                if pestana_solo.collidepoint(e.pos):
                    nuevo_modo = False
                elif pestana_coop.collidepoint(e.pos):
                    nuevo_modo = True
                elif max_scroll and (barra().collidepoint(e.pos) or pista.collidepoint(e.pos)):
                    arrastrando = True
                    alto = barra().height
                    scroll = limitar((e.pos[1] - pista.y - alto / 2) / max(1, pista.height - alto) * max_scroll, 0, max_scroll)
                elif area.collidepoint(e.pos):
                    for i in range(len(records)):
                        fila = pygame.Rect(area.x, area.y + i * paso - round(scroll), area.width, alto_fila)
                        if fila.collidepoint(e.pos):
                            AUDIO.reproducir("click")
                            ver_detalle_record(i + 1, records[i])
                            break
            if nuevo_modo is not None and nuevo_modo != coop:
                coop = nuevo_modo
                records, total, max_scroll = cargar(coop)
                scroll, arrastrando = 0.0, False
                AUDIO.reproducir("click")


def pantalla_fin(oleada, reloj, puntaje, pedir_nombre=False):
    """Pantalla de Game Over. Si el puntaje entra al top 10 pide 3 iniciales y las devuelve ('---' si se omiten)."""
    nombre, primera_tecla, inicio = CONFIG.get("iniciales", "AAA"), True, pygame.time.get_ticks()
    pygame.event.clear()
    while True:
        RELOJ.tick(FPS)
        fondo()
        texto(VENTANA, "GAME OVER", ANCHO // 2, 175, FUENTE_GRANDE, ROJO, True)
        for y, txt, color in ((245, f"Oleada alcanzada: {oleada}", AMARILLO), (290, f"Tiempo: {reloj}", BLANCO),
                              (335, f"Puntaje: {puntaje}", CIAN)):
            texto(VENTANA, txt, ANCHO // 2, y, FUENTE, color, True)
        if pedir_nombre:
            texto(VENTANA, "¡ENTRASTE AL TOP 10! ESCRIBE TUS INICIALES", ANCHO // 2, 400, FUENTE, DORADO, True)
            caja(VENTANA, pygame.Rect(ANCHO // 2 - 110, 430, 220, 64), DORADO)
            texto(VENTANA, " ".join(nombre.ljust(3, "_")), ANCHO // 2, 462, FUENTE_GRANDE, BLANCO, True, 200)
            texto(VENTANA, "ENTER: guardar  ·  ESC: guardar sin nombre", ANCHO // 2, 520, FUENTE_CHICA, BLANCO, True)
        else:
            texto(VENTANA, "ENTER o ESC para volver al menú", ANCHO // 2, 410, FUENTE_CHICA, BLANCO, True)
        pygame.display.flip()
        for e in eventos():
            # un pequeño retardo evita que las teclas pulsadas al morir (WASD, espacio) se cuelen como iniciales
            if e.type != pygame.KEYDOWN or pygame.time.get_ticks() - inicio < 700:
                continue
            if not pedir_nombre:
                if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
                    return None
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if nombre:
                    return nombre
            elif e.key == pygame.K_ESCAPE:
                return "---"
            elif e.key == pygame.K_BACKSPACE:
                nombre, primera_tecla = nombre[:-1], False
            else:
                letra = e.unicode.upper()
                if len(letra) == 1 and letra.isascii() and letra.isalnum():
                    nombre, primera_tecla = (letra if primera_tecla else (nombre + letra)[:3]), False


def activar_dash(jugador, ahora):
    if ahora >= jugador.dash_recarga:
        jugador.dash_hasta = ahora + 0.22
        jugador.dash_recarga = ahora + max(0.15, 1.3 * jugador.reduc_dash)
        AUDIO.reproducir("dash")


PASO_MAX = 0.02  # la simulación avanza en pasos de como máximo 20 ms (evita que las balas atraviesen enemigos con FPS bajos)
FOCO_PERDIDO = getattr(pygame, "WINDOWFOCUSLOST", None)


def jugar(dos_jugadores=False):
    c1, c2 = CONFIG["controles1"], CONFIG["controles2"]
    jugadores = ([Jugador(ANCHO / 2 - 60, ALTO - 90, c1, CIAN), Jugador(ANCHO / 2 + 60, ALTO - 90, c2, ROSA, True)]
                 if dos_jugadores else [Jugador(ANCHO / 2, ALTO - 90, c1, CIAN)])
    enemigos, balas, balas_enemigas, cristales = (pygame.sprite.Group() for _ in range(4))
    jefe = escena = jugador_mejora = None
    jefes_derrotados = conjuntos = 0
    generados = eliminados = puntos_enemigos = 0
    necesarios = 0
    # Todo el juego (cooldowns, dash, invencibilidad, disparos, jefes) usa este único reloj: se detiene en pausa y en el menú de mejoras
    tiempo, oleada, proximo_conjunto, cola = 0.0, 1, 1.5, []
    pendientes = []  # jugadores que subieron de nivel y aún no eligieron mejora (una ganancia grande puede dar varios niveles)
    aviso_traspaso, aviso_traspaso_fin = "", 0.0
    llamas = []  # estela de fuego de Propulsión Térmica
    aviso_jefe, aviso_fin, proximo_beep, pausa = False, 0.0, 0.0, False
    opciones_mejora, rects_mejora = [], []
    lienzo = pygame.Surface((ANCHO, ALTO)).convert()
    rect_continuar, rect_config_pausa, rect_salir_pausa = (pygame.Rect(52 + i * 305, 112, 285, 46) for i in range(3))
    pantalla_pausa = None

    def dar_xp(j, cantidad):
        j.xp += int(cantidad * j.mult_xp)
        while j.xp >= j.xp_siguiente:
            j.xp -= j.xp_siguiente
            j.nivel += 1
            j.xp_siguiente = int(j.xp_siguiente * 1.35) + 2
            pendientes.append(j)

    def abrir_mejora_pendiente():
        nonlocal opciones_mejora, jugador_mejora, aviso_traspaso, aviso_traspaso_fin
        while pendientes and not opciones_mejora:
            j = pendientes.pop(0)
            if j.muerto:
                continue
            opciones = obtener_opciones_con_calidad(j)
            if opciones:
                jugador_mejora, opciones_mejora = j, opciones
                AUDIO.reproducir("mejora")
            else:  # ya tiene todas las habilidades al máximo
                quien = f"P{jugadores.index(j) + 1}: " if dos_jugadores else ""
                aviso_traspaso, aviso_traspaso_fin = f"{quien}TODAS LAS HABILIDADES AL MÁXIMO", tiempo + 3.0

    def eliminar(enemigo):
        nonlocal jefe, jefes_derrotados, oleada, conjuntos, generados, eliminados, puntos_enemigos
        if not enemigo.alive():
            return
        enemigo.kill()
        cristales.add(Cristal(enemigo.pos))
        AUDIO.reproducir("explosion")
        if enemigo is jefe:
            jefe, oleada, conjuntos, generados, eliminados = None, oleada + 1, 0, 0, 0
            jefes_derrotados += 1
            for j in jugadores:
                if not j.muerto:
                    dar_xp(j, 25)
        else:
            puntos_enemigos += enemigo.puntos
            if jefe is None and enemigo.oleada_id == oleada:
                eliminados += 1

    def elegir_mejora(indice):
        nonlocal opciones_mejora, jugador_mejora
        nombre, _, tipo, calidad = opciones_mejora[indice]
        if calidad == "legendario":
            animacion_legendaria(escena, jugador_mejora.pos, nombre)
        else:
            AUDIO.reproducir("mejora")
        aplicar_mejora(jugador_mejora, tipo)
        opciones_mejora, jugador_mejora = [], None
        abrir_mejora_pendiente()

    def construir_pausa(base):
        """Dibuja la pantalla de pausa una sola vez (no cambia mientras dura la pausa)."""
        CAPA_ALERTA.fill((5, 8, 20, 185))
        base.blit(CAPA_ALERTA, (0, 0))
        caja(base, pygame.Rect(40, 30, 920, 640), CIAN, (12, 18, 40), 2, 12)
        texto(base, "PAUSA", ANCHO // 2, 70, FUENTE_GRANDE, CIAN, True)
        boton_dibujar(rect_continuar, "CONTINUAR", VERDE, base)
        boton_dibujar(rect_config_pausa, "CONFIGURACIÓN (C)", MORADO, base)
        boton_dibujar(rect_salir_pausa, "MENÚ PRINCIPAL (M)", ROJO, base)
        texto(base, "ESC o P: continuar", ANCHO // 2, 182, FUENTE_CHICA, BLANCO, True, 400)
        if dos_jugadores:
            for i, j in enumerate(jugadores):
                dibujar_iconos_habilidades(base, f"JUGADOR {i + 1} · HABILIDADES", j.color, j.niveles_mejoras,
                                           pygame.Rect(60 + i * 450, 215, 430, 440),
                                           "Caído: sus habilidades pasaron a su compañero" if j.muerto else "Sin habilidades todavía",
                                           mostrar_max=True)
        else:
            dibujar_iconos_habilidades(base, "TUS HABILIDADES", CIAN, jugadores[0].niveles_mejoras,
                                       pygame.Rect(60, 215, 880, 440), "Sin habilidades todavía", mostrar_max=True)
        return base

    def alternar_pausa():
        nonlocal pausa, pantalla_pausa
        pausa = not pausa
        if pausa:
            pantalla_pausa = construir_pausa(VENTANA.copy())
        AUDIO.reproducir("click")

    def abrir_configuracion_en_pausa():
        menu_configuracion()
        for i, j in enumerate(jugadores, start=1):
            j.controles = CONFIG[f"controles{i}"]

    def avanzar(dt, teclas):
        """Un paso de simulación de duración dt (segundos de juego)."""
        nonlocal tiempo, conjuntos, generados, eliminados, necesarios, proximo_conjunto
        nonlocal aviso_jefe, aviso_fin, proximo_beep, jefe, aviso_traspaso, aviso_traspaso_fin
        tiempo += dt
        ahora = tiempo
        for j in jugadores:
            if not j.muerto:
                j.actualizar(dt, teclas, ahora)

        necesarios = math.ceil(generados * PORCENTAJE_PARA_JEFE)
        if tiempo >= proximo_conjunto and jefe is None and not aviso_jefe:
            if conjuntos < CONJUNTOS_POR_OLEADA:
                conjuntos += 1
                nuevos = crear_oleada(oleada)
                generados += len(nuevos)
                cola.extend((tiempo + retraso, datos) for retraso, datos in nuevos)
                proximo_conjunto = tiempo + 4.5
            elif eliminados >= necesarios or (not cola and not enemigos):
                aviso_jefe, aviso_fin, proximo_beep = True, tiempo + DURACION_AVISO_JEFE, tiempo
                cola.clear()
        if aviso_jefe:
            if tiempo >= proximo_beep:
                AUDIO.reproducir("alerta")
                proximo_beep = tiempo + 0.75
            if tiempo >= aviso_fin:
                jefe = Jefe(jugadores[0], oleada)
                enemigos.add(jefe)
                aviso_jefe = False
                AUDIO.reproducir("jefe")

        listos = [item for item in cola if item[0] <= tiempo]
        cola[:] = [item for item in cola if item[0] > tiempo]
        for _, datos in listos:
            nuevo = Enemigo(random.choice(jugadores), **datos)
            nuevo.oleada_id = oleada
            enemigos.add(nuevo)

        vivos = [j for j in jugadores if not j.muerto] or jugadores
        for enemigo in list(enemigos):
            objetivo = min(vivos, key=lambda j: (j.pos - enemigo.pos).length_squared())
            if isinstance(enemigo, Jefe):
                enemigo.actualizar_jefe(dt, objetivo, balas_enemigas, enemigos, ahora)
            else:
                enemigo.actualizar(dt, objetivo, balas_enemigas, ahora)
                # un enemigo que se fue por un costado cuenta como resuelto: si no, el jefe pedía enemigos que ya no existen
                if enemigo.escapo and jefe is None and enemigo.oleada_id == oleada:
                    eliminados += 1

        for j in jugadores:
            if j.muerto or ahora - j.ultimo_disparo < j.cadencia:
                continue
            critico = random.random() < j.prob_critico
            for i in range(j.proyectiles):
                ang = -math.pi / 2 + (i - (j.proyectiles - 1) / 2) * 0.12
                balas.add(Bala((j.pos.x, j.pos.y - 18), pygame.Vector2(math.cos(ang), math.sin(ang)) * 480,
                               AMARILLO if critico else CIAN, 5 + critico, j.perforante + 1, 2 if critico else 1))
            if j.disparo_lateral:
                balas.add(Bala((j.pos.x - 15, j.pos.y), pygame.Vector2(-400, -100), CIAN, 4))
                balas.add(Bala((j.pos.x + 15, j.pos.y), pygame.Vector2(400, -100), CIAN, 4))
            j.ultimo_disparo = ahora

        balas.update(dt)
        balas_enemigas.update(dt)

        # Colisiones: se arma una sola vez la lista de rectángulos y se consulta con collidelistall (más rápido)
        lista_en = list(enemigos)
        rects_en = [en.rect for en in lista_en]
        for bala in list(balas):
            for i in bala.rect.collidelistall(rects_en):
                enemigo = lista_en[i]
                if not enemigo.alive() or enemigo in bala.golpeados:  # una bala perforante no daña dos veces al mismo enemigo
                    continue
                bala.golpeados.add(enemigo)
                enemigo.vida -= bala.dano
                bala.penetracion -= 1
                if enemigo.vida <= 0:
                    eliminar(enemigo)
                if bala.penetracion <= 0:
                    bala.kill()
                    break

        # Propulsión Térmica: durante el dash se deja una estela de llamas que quema a los enemigos
        for j in jugadores:
            if j.termica and not j.muerto and ahora < j.dash_hasta and (j.pos - j.ultima_llama).length() >= 9:
                j.ultima_llama = pygame.Vector2(j.pos)
                llamas.append(Llama(j.pos, tiempo))
        llamas[:] = [ll for ll in llamas if ll.vive(tiempo)]
        if llamas:
            lista_en = [en for en in enemigos]
            rects_en = [en.rect for en in lista_en]
            for ll in llamas:
                for i in ll.rect.collidelistall(rects_en):
                    enemigo = lista_en[i]
                    if enemigo.alive() and tiempo >= getattr(enemigo, "quemado_hasta", 0):
                        enemigo.quemado_hasta = tiempo + Llama.DANO_CADA
                        enemigo.vida -= 1
                        if enemigo.vida <= 0:
                            eliminar(enemigo)

        vivos_ahora = [j for j in jugadores if not j.muerto]
        for cristal in list(cristales):
            cristal.caer(dt)
            cristal.actualizar(dt, vivos_ahora)
            if not cristal.alive():
                continue
            for j in vivos_ahora:
                if j.rect.colliderect(cristal.rect):
                    cristal.kill()
                    dar_xp(j, cristal.valor)
                    break

        for j in jugadores:
            if j.muerto or ahora < j.invencible_hasta:
                continue
            golpe = (next((en for en in enemigos if j.hitbox.colliderect(en.rect)), None)
                     or next((b for b in balas_enemigas if j.hitbox.colliderect(b.rect)), None))
            if golpe:
                if golpe in balas_enemigas:
                    golpe.kill()
                j.recibir_dano(ahora)
                AUDIO.reproducir("golpe")
                if j.muerto:
                    j.niveles_al_morir = dict(j.niveles_mejoras)  # se guarda ANTES de traspasarlas
                if j.muerto and dos_jugadores:
                    aliado = next((o for o in jugadores if o is not j and not o.muerto), None)
                    if aliado and j.niveles_mejoras:
                        traspasar_mejoras(j, aliado)
                        aviso_traspaso = f"P{jugadores.index(j) + 1} CAYÓ: SUS HABILIDADES PASAN A P{jugadores.index(aliado) + 1}"
                        aviso_traspaso_fin = tiempo + 3.5
        abrir_mejora_pendiente()

    while True:
        dt = min(RELOJ.tick(FPS) / 1000, 0.05)
        reloj_real = pygame.time.get_ticks() / 1000  # solo para animaciones que deben seguir moviéndose en los menús
        teclas = pygame.key.get_pressed()
        for e in eventos():
            if e.type == pygame.KEYDOWN:
                if pausa:
                    if e.key in (pygame.K_ESCAPE, pygame.K_p):
                        alternar_pausa()
                    elif e.key == pygame.K_c:
                        abrir_configuracion_en_pausa()
                    elif e.key == pygame.K_m:
                        return
                elif e.key == pygame.K_ESCAPE or (e.key == pygame.K_p and not opciones_mejora):
                    alternar_pausa()
                elif opciones_mejora:
                    if e.key in (pygame.K_1, pygame.K_2, pygame.K_3) and e.key - pygame.K_1 < len(opciones_mejora):
                        elegir_mejora(e.key - pygame.K_1)
                else:
                    for j, ctrl in zip(jugadores, ("controles1", "controles2")):
                        if e.key == CONFIG[ctrl]["dash"] and not j.muerto:
                            activar_dash(j, tiempo)
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if pausa:
                    if rect_continuar.collidepoint(e.pos):
                        alternar_pausa()
                    elif rect_config_pausa.collidepoint(e.pos):
                        abrir_configuracion_en_pausa()
                    elif rect_salir_pausa.collidepoint(e.pos):
                        return
                elif opciones_mejora:
                    for i, rect in enumerate(rects_mejora):
                        if rect.collidepoint(e.pos):
                            elegir_mejora(i)
                            break
            elif FOCO_PERDIDO is not None and e.type == FOCO_PERDIDO and not pausa:
                alternar_pausa()  # si la ventana pierde el foco (Alt-Tab) el juego se pausa solo

        if pausa:
            VENTANA.blit(pantalla_pausa, (0, 0))
            pygame.display.flip()
            continue

        if not opciones_mejora:
            pasos = max(1, math.ceil(dt / PASO_MAX))
            for _ in range(pasos):
                avanzar(dt / pasos, teclas)
                if opciones_mejora:
                    break
        ahora = tiempo

        fondo(lienzo)
        for ll in llamas:
            ll.dibujar(lienzo, tiempo)
        for grupo in (cristales, enemigos, balas, balas_enemigas):
            for ente in grupo:
                ente.dibujar(lienzo)
        for j in jugadores:
            if not j.muerto:
                j.dibujar(lienzo, ahora, CONFIG["vibracion"])

        reloj = f"{int(tiempo // 60):02}:{int(tiempo % 60):02}"
        pygame.draw.rect(lienzo, (12, 16, 35), (0, 0, ANCHO, 64))
        for i, j in enumerate(jugadores):
            texto(lienzo, f"P{i + 1}  VIDAS {j.vidas}/{j.vidas_max}  NIV {j.nivel}  XP {j.xp}/{j.xp_siguiente}",
                  15 if i == 0 else 510, 10, FUENTE_CHICA, j.color, False, 470)
        if conjuntos < CONJUNTOS_POR_OLEADA:
            info = f"OLEADA {oleada} (Conjunto {conjuntos + 1}/{CONJUNTOS_POR_OLEADA})"
        elif jefe is None:
            info = f"OLEADA {oleada} · Elimina enemigos para invocar al jefe: {min(eliminados, necesarios)}/{necesarios}"
        else:
            info = f"OLEADA {oleada} · JEFE"
        texto(lienzo, info, ANCHO // 2, 46, FUENTE_CHICA, AMARILLO, True, 600)
        texto(lienzo, f"TIEMPO {reloj}", ANCHO - 175, 39, FUENTE_CHICA, BLANCO, False, 160)
        if jefe and jefe.pos.y >= 135:
            pygame.draw.rect(lienzo, (70, 20, 40), (ANCHO // 2 - 140, 70, 280, 12))
            pygame.draw.rect(lienzo, jefe.color, (ANCHO // 2 - 140, 70, int(280 * max(0, jefe.vida) / jefe.vida_max), 12))
            texto(lienzo, f"JEFE {jefe.nombre} · NIVEL {jefe.nivel}", ANCHO // 2, 94, FUENTE_CHICA, jefe.color, True)
        if aviso_jefe:
            dibujar_aviso_jefe(lienzo, aviso_fin - tiempo, oleada, ahora)
        if tiempo < aviso_traspaso_fin:
            texto(lienzo, aviso_traspaso, ANCHO // 2, 125 if jefe else 105, FUENTE, DORADO, True, 900)
        if opciones_mejora:
            escena = lienzo.copy()
            rects_mejora = dibujar_mejoras(lienzo, opciones_mejora, jugador_mejora, dos_jugadores)
            if dos_jugadores:
                pygame.draw.circle(lienzo, jugador_mejora.color, jugador_mejora.rect.center,
                                   30 + round(4 * math.sin(reloj_real * 8)), 3)

        dx = dy = 0
        if CONFIG["vibracion"] and not opciones_mejora:
            intensidad = max([2.2 if aviso_jefe else 0.0] + [6.0 * max(0.0, j.golpe_hasta - ahora) / DURACION_GOLPE for j in jugadores])
            if intensidad > 0:
                dx, dy = round(random.uniform(-intensidad, intensidad)), round(random.uniform(-intensidad, intensidad))
        VENTANA.fill(NEGRO)
        VENTANA.blit(lienzo, (dx, dy))

        if all(j.muerto for j in jugadores):
            puntaje = int(tiempo * 10 + puntos_enemigos + jefes_derrotados * 500)
            mejoras = [dict(j.niveles_al_morir if j.niveles_al_morir is not None else j.niveles_mejoras) for j in jugadores]
            entra = califica(puntaje, dos_jugadores)
            nombre = pantalla_fin(oleada, reloj, puntaje, entra)
            if entra:
                guardar_record(puntaje, reloj, mejoras, nombre or "---", dos_jugadores)
                if nombre and nombre != "---":
                    CONFIG["iniciales"] = limpiar_iniciales(nombre) or CONFIG["iniciales"]
                    guardar_configuracion()
            return
        pygame.display.flip()


def main():
    guardar_configuracion()  # comprueba desde el inicio si la carpeta data es escribible (si no, el menú avisa)
    while True:
        jugar(menu())


if __name__ == "__main__":
    main()
