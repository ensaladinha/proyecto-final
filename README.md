> **Sobrevive a la oleada. Mejora tu nave. Rompe tu propio récord.**
> Un juego arcade de supervivencia hecho en **Python + Pygame**.

- **Nombre:** Lorenzo Brodsky
- **Curso / Materia:** 3°I Programación
- **Proyecto:** Proyecto Final de Python

---

## 📑 Índice

1. [¿De qué trata?](#-1-de-qué-trata)
2. [Cómo se juega](#-2-cómo-se-juega)
3. [Enemigos, oleadas y jefes](#-3-enemigos-oleadas-y-jefes)
4. [Mejoras, calidades y niveles](#-4-mejoras-calidades-y-niveles)
5. [Modo cooperativo](#-5-modo-cooperativo-2-jugadores)
6. [Menús: pausa, configuración y récords](#-6-menús-pausa-configuración-y-récords)
7. [Gráficos y sonido](#-7-gráficos-y-sonido)
8. [Tecnologías y librerías](#-8-tecnologías-y-librerías)
9. [Estructura del proyecto y datos guardados](#-9-estructura-del-proyecto-y-datos-guardados)
10. [Cómo está pensado el código](#-10-cómo-está-pensado-el-código)
11. [Instalación y ejecución (y cómo crear el .exe)](#-11-instalación-y-ejecución)
12. [Propuesta original vs. juego final](#-12-propuesta-original-vs-juego-final)
13. [Plan de trabajo](#-13-plan-de-trabajo)
14. [Uso de Inteligencia Artificial](#-14-uso-de-inteligencia-artificial-en-el-proyecto)
15. [Ideas a futuro](#-15-ideas-a-futuro)

---

## 📌 1. ¿De qué trata?

**Glitch Survivor** es un juego arcade en vista superior (top-down) con estética neón/retro. Controlás una pequeña nave en la parte baja de la pantalla y tenés que **sobrevivir el mayor tiempo posible** mientras oleadas de enemigos bajan hacia vos, cada tanto aparece un **jefe** y todo se vuelve más difícil.

Tu nave **dispara automáticamente**: lo único que tenés que hacer es **moverte, esquivar y elegir bien tus mejoras**. Cada enemigo derrotado suelta un cristal de experiencia; al juntar suficientes **subís de nivel** y podés elegir 1 de 3 mejoras al azar entre 17 posibles (más velocidad, disparo doble, escudo, estela de fuego, disparos críticos...). Dos partidas nunca son iguales.

### 🎯 ¿Por qué lo hice?

| Ingrediente | Qué lo hace adictivo |
|---|---|
| **Partidas cortas (3–8 min)** | Ideal para "una más y listo" entre clases o con amigos. |
| **Progresión constante** | Subís de nivel varias veces por partida: siempre sentís que mejorás. |
| **Builds aleatorias** | 17 mejoras de 4 calidades: cada partida combinás cosas distintas. |
| **Récords con historial de build** | El ranking guarda las 10 mejores partidas **y las habilidades que usaste en cada una**. |
| **Modo 2 jugadores local** | Un jugador usa WASD y el otro las flechas, en la misma pantalla, y se pasan las habilidades si uno cae. |
| **Estética neón + efectos de sonido** | Sprites de pixel art, vibración de pantalla y sonidos generados por código. |
| **Dificultad que escala** | Cada oleada es más rápida y más grande; los jefes ganan vida y velocidad de ataque. |

---

## 🎮 2. Cómo se juega

### Controles

| Acción | Jugador 1 | Jugador 2 (modo cooperativo) |
|---|---|---|
| Moverse | `W` `A` `S` `D` | `↑` `←` `↓` `→` |
| Dash (esquive rápido) | `Espacio` | `Enter` |
| Pausa | `Esc` o `P` | `Esc` o `P` |
| Elegir mejora | `1` `2` `3` o clic del mouse | `1` `2` `3` o clic del mouse |

Más controles:

- **Menú principal:** `1` = un jugador, `2` = cooperativo, o hacer clic en los botones. `Esc` cierra el juego.
- **Pausa:** `Esc`/`P` continúa, `C` abre la configuración y `M` vuelve al menú principal.
- **Los controles de movimiento y dash se pueden cambiar** desde **Configuración** (la tecla `P` está reservada para pausar).

### Reglas básicas

1. La nave **dispara sola hacia arriba**. Con la mejora *Disparo Doble* los proyectiles salen en abanico.
2. Empezás con **3 vidas**. Si te toca un enemigo o una bala enemiga, perdés **1 vida** (o 1 carga de escudo, si tenés).
3. Después de un golpe sos **invencible durante 1,2 segundos** (la nave parpadea) y la pantalla vibra un instante (se puede desactivar).
4. Solo recibís daño en una **hitbox pequeña de 10×10 px en el centro de la nave** (la nave mide unos 32 px), así que se pueden "rozar" las balas.
5. Cada **dash** te mueve a 2,6 veces tu velocidad durante 0,22 s; después hay que esperar **1,3 s** para volver a usarlo.
6. Cada enemigo derrotado suelta un **cristal** 💎. Pasá cerca para recogerlo: la nave tiene un radio de atracción (el *Imán* lo agranda).
7. Cada cristal da **1 punto de experiencia (XP)**. La primera subida de nivel pide 5 XP; cada nivel siguiente pide un 35 % más (5 → 8 → 12 → 18 → 26 → ...).
8. Al subir de nivel el juego se detiene y elegís 1 de 3 mejoras.
9. La partida termina cuando **todos los jugadores se quedan sin vidas**.

### Puntaje

```
puntaje = tiempo sobrevivido (en segundos) × 10
        + 5 por cada cristal que quedó sin recoger en pantalla
        + 500 por cada jefe derrotado
```

### Pantalla de juego (HUD)

- **Arriba a la izquierda (jugador 1) y en el centro-derecha (jugador 2):** vidas, nivel y XP de cada jugador.
- **Centro:** la **oleada actual** y el **conjunto** en curso (por ejemplo "Conjunto 3/8"). Cuando ya salieron los 8 conjuntos aparece un contador: *"Elimina enemigos para invocar al jefe: 40/55"*.
- **Arriba a la derecha:** el tiempo de la partida.
- **Debajo de cada nave:** una barra de vida. Además, **cuanta más vida pierde tu nave, más roja se pone**.
- **Con un jefe en pantalla:** barra de vida del jefe con su nombre y nivel.

---

## 👾 3. Enemigos, oleadas y jefes

### Tipos de enemigos

| Enemigo | Vida | Velocidad | Comportamiento | Aparece desde |
|---|---|---|---|---|
| 🟣 **Constante (zombi)** | 1 | 95 | Baja en línea recta. | Oleada 1 |
| 🔴 **Rápido** | 1 | 160 | Pequeño y veloz, con poca vida. | Oleada 2 |
| 🟠 **Tanque** | 3 | 55 | Grande, lento y resistente. | Oleada 3 |
| 🟢 **Tirador** | 2 | 85 | Se frena arriba, se mueve de lado a lado y **dispara una bala apuntada cada 2 s**. A los 10 s se retira. | Oleada 4 |

- Algunos enemigos (**35 % de los conjuntos**, uno por conjunto) llevan un **punto amarillo**: esos disparan una bala hacia abajo cada 2,2 s.
- En cada oleada la velocidad de los enemigos aumenta un 8 % (hasta un 50 % más) y los conjuntos son más grandes.
- Si un enemigo sale por abajo, **reaparece arriba**; solo desaparecen de verdad cuando los matás o salen por un costado.

### Oleadas y conjuntos

Una **oleada** se compone de **8 conjuntos** de enemigos. Cada conjunto (un grupo de hasta 11 enemigos del mismo tipo) aparece **cada 4,5 segundos** con uno de estos **7 patrones de formación**: fila, uve, columna, serpiente, diagonal, bloque o lateral.

Después del octavo conjunto, **el jefe no aparece hasta que hayas eliminado el 85 % de los enemigos generados en la oleada** (o hasta que no quede ninguno en pantalla). Ahí suena una **alerta animada de 1,5 s** con parpadeo rojo y el nombre del jefe, y recién entonces entra el jefe. Al derrotarlo empieza una **nueva oleada** (con un número más).

### Los 8 jefes

El jefe de la oleada *n* es el número *n* de esta lista (después del 8.º vuelve a empezar, con más nivel y otro color):

| N.º | Jefe | Patrón de ataque |
|---|---|---|
| 1 | **Espiral** | Doble espiral de balas, en ráfagas. |
| 2 | **Cazador** | Te persigue en horizontal, lanza abanicos de 5 balas apuntadas y embiste hacia abajo. |
| 3 | **Pulsar** | Anillos de 18 balas que giran en cada pulso y rachas de disparos apuntados. |
| 4 | **Invocador** | Lluvia de balas desde arriba e invoca refuerzos (zombis y rápidos). |
| 5 | **Barrido** | Dos chorros de balas que barren la pantalla en cruz y tríos apuntados. |
| 6 | **Muralla** | Muros de balas con un hueco por donde escapar, más disparos apuntados. |
| 7 | **Enjambre** | Manda grupos de 4 enemigos rápidos desde los costados y tríos de balas. |
| 8 | **Singularidad** | **Te atrae** hacia él (hay un círculo que marca la zona), órbitas de balas lentas y lluvia de meteoros. |

Dificultad progresiva de los jefes: su **vida** es `28 + 12 × (nivel − 1)` y su **ritmo de ataque** sube un 10 % por nivel (hasta el doble). Derrotar a un jefe da **500 puntos** y **25 XP** a cada jugador vivo. Los jefes apuntan al jugador más cercano.

---

## ⬆️ 4. Mejoras, calidades y niveles

### Cómo funcionan

Al subir de nivel aparecen **3 mejoras distintas** para elegir. Si elegís una que ya tenías, **su nivel sube en 1** y su efecto se hace más fuerte. Cada mejora tiene un **nivel máximo** (5 en casi todas). Cuando una mejora llega a su máximo, **deja de aparecer** en esa partida.

### Calidades

La **calidad** indica cuán rara es una mejora. Cada mejora tiene un *peso* y las 3 opciones se sortean con esos pesos:

| Calidad | Peso | Mejoras | Prob. aprox. de la 1.ª tarjeta* |
|---|---|---|---|
| **Normal** | 60 | 3 | 52,8 % |
| **Raro** | 30 | 4 | 35,2 % |
| **Épico** | 8 | 4 | 9,4 % |
| **Legendario** | 1,5 | 6 | 2,6 % |

\*Con las 17 mejoras disponibles. Al elegir una **legendaria** se muestra una animación de ondas doradas que se expanden desde la nave.

### Las 17 mejoras

| Mejora | Calidad | Nivel máx. | Qué hace |
|---|---|---|---|
| **Turbo** | Normal | 5 | +15 % de velocidad por nivel. |
| **Cadencia** | Normal | 5 | Dispara más rápido: el tiempo entre ráfagas baja un 20 % por nivel (0,70 s → 0,23 s). |
| **Imán** | Normal | 5 | +80 px de radio de atracción de cristales por nivel (base 90 px). |
| **Disparo Doble** | Raro | 4 | +1 proyectil por ráfaga (hasta 5, en abanico). |
| **Escudo** | Raro | 5 | +1 carga de escudo; cada carga absorbe un golpe. |
| **Corazón Extra** | Raro | 5 | +1 vida máxima y +1 vida. |
| **Dash Mejorado** | Raro | 5 | El dash se recarga un 18 % más rápido por nivel. |
| **Nanobots** | Épico | 5 | Regenera 1 vida cada 25 / 20 / 15 / 10 / 7 s (según el nivel) si te falta vida. |
| **Campo Distorsión** | Épico | 5 | Las balas enemigas van un 10 % más lentas por nivel (hasta la mitad de velocidad). |
| **Hipercargador** | Épico | 5 | +20 % de XP por nivel (hasta el doble). |
| **Misiles Perforantes** | Épico | 5 | Las balas atraviesan enemigos (nivel + 1 enemigos). En el nivel 5 atraviesan a todos. Cada bala daña **una sola vez** a cada enemigo. |
| **Propulsión Térmica** | Legendario | 1 | Durante el dash dejás una **estela de llamas** que quema a los enemigos (1 de daño cada 0,3 s). Las llamas pasan de amarillo brillante a brasa y duran unos 2 s. |
| **Escudo Espejo** | Legendario | 5 | 15 % de probabilidad por nivel (máx. 75 %) de anular por completo un golpe. |
| **Núcleo Sobrecarga** | Legendario | 1 | Dos disparos diagonales extra en cada ráfaga. |
| **Ancla Gravitacional** | Legendario | 1 | Atrae suavemente a los enemigos Constante y Rápido que estén a menos de 250 px. |
| **Condensador Plasma** | Legendario | 5 | 7 % de probabilidad por nivel (máx. 35 %) de ráfaga crítica: balas amarillas con el doble de daño. |
| **Estabilizador** | Legendario | 5 | El cooldown del dash se multiplica por 0,60 por nivel (mínimo 0,15 s). |

> Para ver **el efecto exacto de cada nivel**, mirá el PDF `Habilidades_Glitch_Survivor.pdf`.

---

## 🤝 5. Modo cooperativo (2 jugadores)

- Los dos jugadores comparten pantalla: el **jugador 1** (nave azul) con `WASD` + `Espacio`, y el **jugador 2** (nave roja) con las flechas + `Enter`.
- Cada jugador tiene **sus propias vidas, XP, nivel y habilidades**. Los enemigos van tras el jugador vivo más cercano.
- **¿Para quién es la mejora?** Al subir de nivel, el título dice qué jugador sube (*"¡JUGADOR 2 SUBIÓ DE NIVEL!"*), el panel toma el color de ese jugador y aparece un anillo pulsante sobre su nave.
- **Traspaso de habilidades:** si un jugador muere y el otro sigue vivo, el sobreviviente **recibe sus habilidades**. Los niveles se **suman** (si uno tenía Cadencia 2 y el otro Cadencia 1, el que sigue vivo queda con Cadencia 3), sin pasar del nivel máximo. Aparece un aviso dorado en pantalla.
- La partida termina cuando **los dos** se quedaron sin vidas.
- En el menú de pausa y en los récords se ven las habilidades **de ambos jugadores**.

---

## 🗂️ 6. Menús: pausa, configuración y récords

### Menú principal

Botones: **Jugar**, **Configuración**, **Récords** y **Salir**. También muestra tus teclas actuales y recuerda cuándo aparece el jefe.

### Menú de pausa

Se abre con `Esc` o `P` y congela la partida (también mientras elegís una mejora). Ofrece **Continuar**, **Configuración** y **Menú principal**, y muestra **las habilidades que elegiste** con su nivel y color de calidad (en cooperativo, las de los dos jugadores).

### Configuración

- **Reasignar teclas** de movimiento y dash de ambos jugadores (clic en una acción y pulsás la tecla nueva; `Esc` cancela). Si la tecla ya estaba usada por otra acción del mismo jugador, **se intercambian**.
- **Volumen** (barra, botones − / + o clic en la barra).
- **Vibración de pantalla** activada / desactivada.
- **Restablecer** los valores predeterminados.
- Todo se **guarda automáticamente** en `data/settings.json`.

### Récords

- Guarda los **10 mejores puntajes** (`data/scores.json`) con puntaje, tiempo y **habilidades de cada jugador en esa partida**.
- La lista se recorre con la **rueda del mouse**, la barra lateral o las flechas.
- Al hacer clic en un récord se ve el detalle: **un icono de pixel art por cada habilidad, con el nombre debajo y el nivel alcanzado al lado** (por ejemplo `Disparo Doble  NV.2`).
- En cooperativo, el jugador que murió primero muestra las habilidades **que tenía antes de morir**.
- Los récords viejos, de antes de que se guardaran las habilidades, lo indican en pantalla.

---

## 🎨 7. Gráficos y sonido

- **Sprites de pixel art dibujados por código:** la nave de cada jugador, los enemigos (rápido, constante, tirador, tanque) y los 8 jefes (con una segunda variante de color cuando se repite el ciclo). Los diseños vienen de archivos HTML de diseño y se guardan como "mapas" de letras dentro de `main.py`, así que **no hace falta ningún archivo de imagen**.
- **Nave dañada:** el sprite se tiñe de rojo a medida que pierde vida.
- **Estela de fuego:** 4 formas de llama y 3 etapas de color (recién creada → mitad de vida → brasa).
- **Iconos de habilidades:** 17 iconos de 16×16 con un marco del color de la calidad (gris, azul, violeta y dorado).
- **Ícono de la aplicación:** un avioncito, dibujado también por código (y en `icono.ico` para el `.exe`).
- **Sonido:** los **8 efectos** (click, dash, golpe, explosión, alerta, jefe, mejora y legendario) se **sintetizan con ondas senoidales** usando `array` y `math`; no se usan archivos de audio.
- **Vibración de pantalla** al recibir un golpe (opcional) y **alerta animada** antes de cada jefe.

---

## 🧰 8. Tecnologías y librerías

> **Objetivo de la consigna:** comprender el uso de librerías en Python. Cada librería de esta tabla se explica y se justifica.

| Librería | Tipo | ¿Para qué se usa en el juego? |
|---|---|---|
| **`pygame`** | Externa (`pip install pygame`) | Ventana, dibujo de sprites y formas, teclado y mouse, sonido, reloj de FPS y colisiones. Es el "motor" del juego. |
| **`random`** | Estándar | Tipo y formación de enemigos, qué 3 mejoras se ofrecen (con `random.choices` y pesos), aleatoriedad de los patrones de jefes. |
| **`math`** | Estándar | Distancias, ángulos y trayectorias de balas (`atan2`, `sin`, `cos`), ondas de los sonidos. |
| **`json`** | Estándar | Guardar y leer el **ranking** (`scores.json`) y la **configuración** (`settings.json`). |
| **`os`** | Estándar | Armar las rutas a la carpeta `data` sin errores según el sistema operativo. |
| **`sys`** | Estándar | Cerrar el programa de forma limpia y detectar si se ejecuta como `.exe`. |
| **`array`** | Estándar | Guardar las muestras de audio al sintetizar los sonidos. |
| **`PyInstaller`** | Externa (solo para crear el `.exe`) | Empaquetar el juego en un único archivo ejecutable. |

**Lenguaje principal:** Python 3.10 o superior. **Nota:** con Python 3.14 se usa `pygame-ce` (compatible con `import pygame`), porque `pygame` todavía no tiene versión lista para esa versión.

---

## 🗂️ 9. Estructura del proyecto y datos guardados

```
GlitchSurvivor/
│
├── main.py                ← Todo el juego (clases, menús y bucle principal)
├── requirements.txt       ← Dependencias (pygame)
├── README.md              ← Este archivo
├── icono.ico              ← Ícono del .exe (avioncito)
├── build_exe.bat          ← Crea el .exe con un doble clic
├── GlitchSurvivor.exe     ← Aparece después de ejecutar build_exe.bat
├── Habilidades_Glitch_Survivor.pdf  ← Guía de habilidades, calidades y niveles
│
└── data/                  ← Se crea solo la primera vez
    ├── scores.json        ← Ranking (top 10) con las habilidades de cada partida
    └── settings.json      ← Volumen, vibración y teclas
```

**Ejemplo de `data/scores.json`:**

```json
{
  "high_scores": [
    { "name": "JUGADOR", "score": 1346, "time": "01:18",
      "mejoras": [ { "cadencia": 1, "espejo": 1, "doble": 2, "termica": 1 } ] }
  ]
}
```

`mejoras` tiene un diccionario por jugador (`habilidad: nivel`).

---

## 🧠 10. Cómo está pensado el código

El juego sigue el patrón clásico del **game loop**, que se repite 60 veces por segundo:

```
┌───────────────────────────────────────────────────────┐
│ 1. EVENTOS    → ¿qué tecla o clic hubo?               │
│ 2. ACTUALIZAR → mover, disparar, chocar, subir de nivel│
│ 3. DIBUJAR    → pintar todo en pantalla               │
│ 4. RELOJ      → esperar para mantener 60 FPS          │
└───────────────────────────────────────────────────────┘
```

El movimiento usa **`dt`** (el tiempo que pasó desde el cuadro anterior), así que el juego va igual de rápido aunque la PC sea lenta o rápida.

### Bloques de código y qué hace cada uno

| Bloque (en `main.py`) | Idea principal | Concepto de Python que se practica |
|---|---|---|
| **Constantes e inicialización** | Abre la ventana, define colores, fuentes y rutas. | Importar librerías, constantes. |
| **`GestorAudio`** | Crea los 8 sonidos sumando ondas y los reproduce con el volumen elegido. | POO, `array`, matemática. |
| **Sprites (`construir_sprite`, `sprite`, `destello`)** | Convierten mapas de letras en imágenes, con un caché para no recalcular. | Diccionarios, listas por comprensión, caché. |
| **Clase `Jugador`** | Posición, vidas, XP, hitbox, dash, mejoras y dibujo de la nave. | Programación orientada a objetos (POO). |
| **Clases `Enemigo` y `Jefe`** | `Jefe` **hereda** de `Enemigo` y cambia su ataque según el tipo. | **Herencia** y **polimorfismo** (`dibujar`, `actualizar`). |
| **`crear_oleada`** | Genera un conjunto de enemigos con una formación al azar. | Funciones, `random`, listas de diccionarios. |
| **Clases `Bala`, `Cristal`, `Llama`** | Proyectiles, experiencia y estela de fuego. | Clases, `pygame.sprite.Group`. |
| **Colisiones** | Balas contra enemigos, enemigos contra la hitbox, cristales contra la nave. | Rectángulos (`Rect`), condicionales. |
| **Sistema de mejoras** | `obtener_opciones_con_calidad` sortea 3 mejoras con pesos y `aplicar_mejora` cambia las estadísticas. | `random.choices`, diccionarios, funciones. |
| **`traspasar_mejoras`** | Suma los niveles del jugador caído al compañero sin pasar el máximo. | Bucles, `min`, diccionarios. |
| **Menús (`menu`, `menu_configuracion`, `ver_records`)** | Pantallas con botones, reasignación de teclas, lista con scroll. | Eventos, bucles, estados. |
| **Persistencia (`leer_json`, `escribir_json`)** | Guarda y carga ranking y ajustes. | Archivos, JSON, manejo de errores (`try/except`). |
| **`jugar()`** | Bucle principal: oleadas, jefes, pausa, mejoras y fin de partida. | Funciones anidadas, `nonlocal`, variables de estado. |

### Detalles técnicos que vale la pena explicar

- **Hitbox reducida:** el jugador tiene dos rectángulos: uno de 28×28 px para recoger cristales y otro de 10×10 px para recibir daño.
- **Sorteo con pesos:** `random.choices(..., pesos)` hace que las mejoras raras salgan menos; cada mejora elegida se saca del grupo para no repetirse en la misma tarjeta.
- **Nivel máximo:** el sorteo solo incluye mejoras cuyo nivel actual es menor al máximo.
- **Balas perforantes:** cada bala guarda un conjunto (`set`) de los enemigos que ya golpeó para dañarlos una sola vez.
- **Jefe condicionado:** el juego cuenta `generados` y `eliminados`; el jefe entra cuando `eliminados >= 85 % de generados`.
- **Cooperativo:** cada `Jugador` tiene su propio diccionario `niveles_mejoras`; al morir, se guarda una copia (`niveles_al_morir`) para los récords **antes** de traspasarlas.
- **Rutas seguras:** `CARPETA` apunta a la carpeta del `.exe` (o de `main.py`), así los datos se guardan siempre junto al juego.

---

## ▶️ 11. Instalación y ejecución

### Ejecutar con Python

```bash
# 1. (Opcional) Crear un entorno virtual
python -m venv venv
# Windows:  venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt     # con Python 3.14: pip install pygame-ce

# 3. Jugar
python main.py
```

**requirements.txt**
```
pygame>=2.5
```

### Crear el archivo .exe (Windows)

1. Instalá Python 3.10 o superior (marcá "Add Python to PATH").
2. Hacé doble clic en `build_exe.bat`. Instala pygame-ce y PyInstaller, comprueba que el audio funcione y arma el ejecutable.
3. Al terminar aparece **`GlitchSurvivor.exe`** en la misma carpeta. Es un solo archivo: se puede copiar a otra carpeta o PC **sin instalar Python**.

Lo temporal de PyInstaller se hace en la carpeta TEMP de Windows y se borra al terminar, así que no quedan carpetas `build` ni `dist`. Al abrir el juego por primera vez se crea la carpeta `data` junto al `.exe`.

---

## 🔄 12. Propuesta original vs. juego final

El juego creció y cambió respecto a la idea del 22/10. Estas son las diferencias principales:

| Idea original | Juego final |
|---|---|
| La nave dispara "hacia el enemigo más cercano". | Dispara **hacia arriba** de forma automática (abanico con Disparo Doble). |
| Jefe cada 60 segundos. | Jefe tras **8 conjuntos** de enemigos y eliminando el **85 %** de ellos. |
| Un jefe "Glitch" con 3 patrones. | **8 jefes** distintos, cada uno con su propio patrón y sprite. |
| 8 mejoras simples, sin calidades. | **17 mejoras**, 4 calidades (Normal, Raro, Épico, Legendario) y niveles del 1 al 5. |
| Power-ups temporales (tiempo lento, invencible, bomba) y cofre de mejora especial. | No se implementaron; la variedad viene de las **mejoras épicas y legendarias**. |
| Mejora "Explosión" y Escudo que se recarga cada 20 s. | No se implementaron; el Escudo funciona con **cargas** que se acumulan. |
| Puntaje por tiempo + enemigos + jefes. | Puntaje por **tiempo + cristales sin recoger + jefes**. |
| Ranking de los 5 mejores. | **Top 10**, con las **habilidades** de cada partida y scroll con el mouse. |
| Estructura en carpetas (`game/`, `assets/`...). | **Un solo `main.py`**; no hay archivos de imagen ni de audio porque se generan por código. |
| Música de fondo y partículas. | Efectos de sonido sintetizados, vibración de pantalla y animaciones propias. |
| — | Nuevo: **modo cooperativo** con traspaso de habilidades, pausa con habilidades, configuración de teclas, ícono, sprites de pixel art y `.exe`. |

---

## 🗓️ 13. Plan de trabajo

| Fecha | Etapa | Entregable |
|---|---|---|
| **22/10/2026** | Definir la idea, escribir el README y subirlo al repositorio. | ✅ README en el repositorio **"ProyectoFinal"** |
| 23/10 – 25/10 | Instalar Python y pygame. Abrir la ventana y mover la nave con WASD. | Nave que se mueve |
| 26/10 – 29/10 | Disparo automático, enemigos básicos y colisiones. Sistema de vidas. | Primer nivel jugable |
| 30/10 – 01/11 | Cristales, experiencia, subida de nivel y menú de mejoras. | Progresión completa |
| 02/11 – 03/11 | Jefes, sonidos, efectos y ranking en JSON. | Juego terminado |
| 04/11 | Pruebas con compañeros, corrección de errores, ensayo de la exposición. | Versión final |
| **05/11/2026** | **Exposición oral (5 min):** demo del juego + explicación de qué hace cada bloque de código. | 🎤 Presentación |

---

## 🤖 14. Uso de Inteligencia Artificial en el proyecto

Según la consigna, la IA se usa **como medio para aprender a crear e interpretar código**, no para copiar sin entender. La forma de trabajo es:

1. **Pedir la idea o el esqueleto** de cada módulo a la IA.
2. **Leer y comprender cada línea:** si algo no se entiende, se le pide a la IA que lo explique "como si tuviera 15 años".
3. **Modificar el código a mano** (cambiar velocidades, colores, vidas) para comprobar que se entiende qué hace cada parte.
4. **Probar, romper y arreglar:** los errores se analizan junto con la IA para aprender a depurar (por ejemplo, el error de las balas perforantes que dañaban varias veces al mismo enemigo).
5. **Documentar** con comentarios en el código lo que se aprendió, para la exposición oral.

---

## 🚀 15. Ideas a futuro

- 🕹️ **Control físico con Arduino:** conectar un joystick y un botón de dash usando la librería `pyserial`.
- 🌐 **Pantalla de récords en HTML** generada desde `scores.json`.
- 🎨 **Skins desbloqueables** para la nave según el puntaje.
- 🗺️ **Nuevos escenarios** (espacio, ciudad cyberpunk, laboratorio).
- 🏆 **Logros** ("Derrotá 3 jefes", "Sobreviví 5 minutos sin recibir daño").
- 🎵 **Música de fondo** y partículas al destruir enemigos.
- ⏱️ **Power-ups temporales** (tiempo lento, invencibilidad, bomba), que estaban en la idea original.
- ✍️ **Nombre del jugador** en los récords (hoy todos se guardan como "JUGADOR").
