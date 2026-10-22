> **Sobrevive a la oleada. Mejora tu nave. Rompe tu propio récord.**
> Un juego arcade de supervivencia hecho en **Python + Pygame**.

---

## 📌 1. ¿de que trata? ##

 es un juego arcade en vista superior (top-down) con estética neón/retro. Controlás una pequeña nave en el centro de la pantalla y tenés que **sobrevivir el mayor tiempo posible** mientras oleadas de enemigos te persiguen desde todos los lados.

Tu nave **dispara automáticamente**: lo único que tenés que hacer es **moverte, esquivar y elegir bien tus mejoras**. Cada enemigo derrotado suelta cristales de experiencia; al juntar suficientes **subís de nivel** y podés elegir 1 de 3 mejoras al azar (más velocidad, disparo doble, escudo, imán de cristales, etc.). Dos partidas nunca son iguales.

Cada 60 segundos aparece un **jefe** (boss) con un patrón de ataque propio. Si lo derrotás, ganás una mejora especial y la dificultad sube.

### 🎯 ¿Por qué lo hice?

| Ingrediente | Qué lo hace adictivo |
|---|---|
| **Partidas cortas (3–8 min)** | Ideal para "una más y listo" entre clases o con amigos. |
| **Progresión constante** | Subís de nivel varias veces por partida: siempre sentís que mejorás. |
| **Builds aleatorias** | Cada partida combinás mejoras distintas: probás estrategias nuevas. |
| **Récords y ranking local** | Competís contra tu propio puntaje y contra el de tus amigos en la misma PC. |
| **Modo 2 jugadores local** | Un jugador usa WASD y el otro las flechas, en la misma pantalla. |
| **Estética neón + música** | Visuales llamativos, efectos de partículas y sonidos satisfactorios. |
| **Dificultad que escala** | Fácil de aprender, difícil de dominar. |

---

## 🎮 2. Cómo se juega

### Controles

| Acción | Jugador 1 | Jugador 2 (modo cooperativo) |
|---|---|---|
| Moverse | `W` `A` `S` `D` | `↑` `←` `↓` `→` |
| Dash (esquive rápido) | `Espacio` | `Enter` |
| Pausa | `P` | `P` |
| Elegir mejora | `1` `2` `3` o clic del mouse | `1` `2` `3` o clic del mouse |
| Salir al menú | `Esc` | `Esc` |

### Reglas básicas

1. La nave **dispara sola** hacia el enemigo más cercano.
2. Si un enemigo te toca, perdés **1 corazón** (empezás con 3).
3. Los enemigos derrotados sueltan **cristales** 💎. Recogelos pasando por encima.
4. Al llenar la barra de experiencia **subís de nivel** y elegís una mejora.
5. Cada **60 segundos** aparece un **jefe**. Derrotarlo da puntos extra y un cofre con mejora especial.
6. La partida termina cuando te quedás **sin corazones**.
7. Tu puntaje final se calcula con: tiempo sobrevivido + enemigos eliminados + jefes derrotados.

### Tipos de enemigos

| Enemigo | Comportamiento | Aparece desde |
|---|---|---|
| 🟣 **Zombi Pixel** | Camina lento directo hacia vos. | Minuto 0 |
| 🔴 **Rápido** | Pequeño y veloz, pero con poca vida. | Minuto 1 |
| 🟠 **Tanque** | Lento, mucha vida, te empuja al chocar. | Minuto 2 |
| 🟢 **Tirador** | Se queda a distancia y lanza proyectiles. | Minuto 3 |
| 👾 **Jefe "Glitch"** | Patrones: círculo de balas, embestida, invoca minions. | Cada 60 s |

### Mejoras disponibles (se eligen al subir de nivel)

- ⚡ **Turbo:** +15 % velocidad de movimiento.
- 🔫 **Disparo doble / triple:** más proyectiles por ráfaga.
- 🔥 **Cadencia:** disparás más rápido.
- 🛡️ **Escudo:** absorbe un golpe y se recarga cada 20 s.
- 🧲 **Imán:** atrae cristales desde más lejos.
- ❤️ **Corazón extra:** +1 vida máxima.
- 💥 **Explosión:** al matar a un enemigo, daña a los cercanos.
- 🌀 **Dash mejorado:** menos tiempo de espera entre esquives.

### Power-ups temporales (caen de enemigos al azar)

- ⏱️ **Tiempo lento:** todo se mueve más despacio por 5 s.
- 🌟 **Invencible:** inmunidad por 4 s.
- 💣 **Bomba:** elimina todos los enemigos en pantalla.

---

## 🧰 3. Tecnologías y librerías

> **Objetivo de la consigna:** comprender el uso de librerías en Python. Cada librería de esta tabla se explica y se justifica.

| Librería | Tipo | ¿Para qué se usa en el juego? |
|---|---|---|
| **`pygame`** | Externa (`pip install pygame`) | Ventana, dibujo de sprites y formas, control del teclado/mouse, sonido, reloj de FPS y detección de colisiones. Es el "motor" del juego. |
| **`random`** | Estándar | Posición y tipo de enemigos, mejoras aleatorias, drops de power-ups. |
| **`math`** | Estándar | Distancias, ángulos y trayectorias de balas (`sqrt`, `atan2`, `sin`, `cos`). |
| **`json`** | Estándar | Guardar y leer el **ranking de récords** en un archivo `scores.json`. |
| **`os`** / **`pathlib`** | Estándar | Rutas a imágenes, sonidos y al archivo de puntajes, sin errores según el sistema operativo. |
| **`time`** | Estándar | Medir el tiempo de supervivencia y los cooldowns (dash, escudo). |
| **`sys`** | Estándar | Cerrar el programa de forma limpia. |

**Lenguaje principal:** Python 3.10 o superior.

---

## 🗂️ 4. Estructura del proyecto

```
ProyectoFinal/
│
├── README.md              ← Este archivo
├── requirements.txt       ← Dependencias (pygame)
├── main.py                ← Punto de entrada: inicia el juego
│
├── game/
│   ├── settings.py        ← Constantes: tamaño de ventana, FPS, colores, vidas
│   ├── player.py          ← Clase Player: movimiento, disparo, dash, vida
│   ├── enemies.py         ← Clases de enemigos y jefe
│   ├── bullets.py         ← Proyectiles del jugador y de los enemigos
│   ├── items.py           ← Cristales y power-ups
│   ├── upgrades.py        ← Lista de mejoras y lógica de selección
│   ├── ui.py              ← Menú, HUD (vida, nivel, tiempo), pantalla Game Over
│   ├── effects.py         ← Partículas, temblor de pantalla, brillo neón
│   └── scores.py          ← Leer/guardar ranking en JSON
│
├── assets/
│   ├── images/            ← Sprites (o se dibujan con formas de pygame)
│   ├── sounds/            ← Efectos: disparo, golpe, subir de nivel
│   └── music/             ← Música de fondo (loop)
│
└── data/
    └── scores.json        ← Ranking local (se crea solo)
```

---

## 🧠 5. Cómo está pensado el código (clave para la exposición oral)

El juego sigue el patrón clásico del **game loop**, que se repite ~60 veces por segundo:

```
┌─────────────────────────────────────────┐
│ 1. EVENTOS   → ¿qué tecla se presionó?  │
│ 2. ACTUALIZAR → mover, disparar, chocar │
│ 3. DIBUJAR   → pintar todo en pantalla  │
│ 4. RELOJ     → esperar para mantener 60 FPS │
└─────────────────────────────────────────┘
```

### Bloques de código y qué hace cada uno

| Bloque | Idea principal | Concepto de Python que se practica |
|---|---|---|
| **Inicialización** | Abre la ventana y carga recursos. | Importar librerías, constantes. |
| **Clase `Player`** | Guarda posición, vida, velocidad y dispara. | Programación orientada a objetos (POO). |
| **Clases de enemigos** | Cada tipo hereda de una clase base `Enemy`. | Herencia y polimorfismo. |
| **Grupos de sprites** | Administran muchas balas/enemigos a la vez. | Listas, colecciones, bucles. |
| **Colisiones** | Detectan cuándo una bala toca a un enemigo. | Rectángulos (`Rect`), condicionales. |
| **Sistema de mejoras** | Elige 3 mejoras al azar sin repetir. | `random.sample`, diccionarios, funciones. |
| **Oleadas y dificultad** | Cada minuto aparecen más enemigos y más fuertes. | Variables, operadores, temporizadores. |
| **Ranking** | Guarda los mejores 5 puntajes. | Archivos, JSON, manejo de errores (`try/except`). |

---

## 🗓️ 6. Plan de trabajo

| Fecha | Etapa | Entregable |
|---|---|---|
| **22/10/2026** | Definir la idea, escribir este README y subirlo al repositorio. | ✅ README en el repositorio **"ProyectoFinal"** |
| 23/10 – 25/10 | Instalar Python y pygame. Abrir la ventana y mover la nave con WASD. | Nave que se mueve |
| 26/10 – 29/10 | Disparo automático, enemigos básicos y colisiones. Sistema de vidas. | Primer nivel jugable |
| 30/10 – 01/11 | Cristales, experiencia, subida de nivel y menú de mejoras. | Progresión completa |
| 02/11 – 03/11 | Jefe, power-ups, sonidos, partículas y ranking en JSON. | Juego terminado |
| 04/11 | Pruebas con compañeros, corrección de errores, ensayo de la exposición. | Versión final |
| **05/11/2026** | **Exposición oral (5 min):** demo del juego + explicación de qué hace cada bloque de código. | 🎤 Presentación |

---

## 🤖 7. Uso de Inteligencia Artificial en el proyecto

Según la consigna, la IA se usa **como medio para aprender a crear e interpretar código**, no para copiar sin entender. La forma de trabajo es:

1. **Pedir la idea o el esqueleto** de cada módulo a la IA.
2. **Leer y comprender cada línea:** si algo no se entiende, se le pide a la IA que lo explique "como si tuviera 15 años".
3. **Modificar el código a mano** (cambiar velocidades, colores, vidas) para comprobar que se entiende qué hace cada parte.
4. **Probar, romper y arreglar:** los errores se analizan junto con la IA para aprender a depurar.
5. **Documentar** con comentarios en el código lo que se aprendió, para la exposición oral.

---

## ▶️ 8. Instalación y ejecución

```bash
# 1. Clonar el repositorio
git clone <URL-del-repositorio>/ProyectoFinal.git
cd ProyectoFinal

# 2. (Opcional) Crear un entorno virtual
python -m venv venv
# Windows:  venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Jugar
python main.py
```

**requirements.txt**
```
pygame>=2.5
```

---

## 🚀 9. Ideas a futuro (extras opcionales)

- 🕹️ **Control físico con Arduino:** conectar un joystick y un botón de dash usando la librería `pyserial` (la consigna permite integrar electrónica).
- 🌐 **Pantalla de récords en HTML** generada desde `scores.json`.
- 🎨 **Skins desbloqueables** para la nave según el puntaje.
- 🗺️ **Nuevos escenarios** (espacio, ciudad cyberpunk, laboratorio).
- 🏆 **Logros** ("Derrotá 3 jefes", "Sobreviví 5 minutos sin recibir daño").

---

## 👤 10. Autor

- **Nombre:** _(completar)_
- **Curso / Materia:** _(completar)_
- **Proyecto:** Proyecto Final de Python
- **Año:** 2026

---

> *"Un buen juego no se mide por sus gráficos, sino por las ganas de volver a jugar."* 🎮
