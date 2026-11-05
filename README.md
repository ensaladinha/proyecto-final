# Glitch Survivor — Proyecto Final de Python

Juego arcade de supervivencia en vista superior hecho con Python y Pygame. La nave dispara automáticamente y el jugador debe esquivar enemigos, recoger cristales, subir de nivel y elegir mejoras.

## Requisitos
- Python 3.10 o superior
- Pygame 2.5 o superior

## Instalación y ejecución
Abre una terminal en esta carpeta y ejecuta:

```bash
python -m pip install -r requirements.txt
python main.py
```

## Crear el archivo .exe (Windows)
1. Instala Python 3.10 o superior (marca "Add Python to PATH").
2. Haz doble clic en `build_exe.bat`. Instala pygame-ce (equivalente a Pygame, ya compilado para Python 3.14) y PyInstaller. Si falla con tu versión de Python, usa Python 3.12 o 3.13.
3. Al terminar aparece `GlitchSurvivor.exe` en esta misma carpeta. Es un solo archivo: puedes copiarlo a otra carpeta o PC sin instalar Python.

El proceso no deja carpetas sobrantes: lo temporal de PyInstaller se hace en la carpeta TEMP de Windows y se borra al terminar. Al abrir el juego por primera vez se crea la carpeta `data` junto al `.exe` con el ranking (`scores.json`) y la configuración (`settings.json`).

## Estructura de la carpeta
```
GlitchSurvivor/
  main.py            (el juego)
  fondos_data.py     (los fondos de la nebulosa y del circuito, incrustados)
  requirements.txt
  README.md
  icono.ico          (ícono del .exe)
  build_exe.bat      (crea el .exe)
  GlitchSurvivor.exe (aparece al ejecutar build_exe.bat)
  data/              (puntajes y configuración)
```

## Controles
- Jugador 1: WASD para moverse, Espacio para dash.
- Jugador 2 (modo cooperativo): flechas para moverse, Enter para dash.
- Esc o P: abre el menú de pausa (Continuar, Configuración, Menú principal) y muestra las habilidades de cada jugador con su icono, nombre y nivel (NV.actual/máximo); dentro, C abre la configuración y M vuelve al menú.
- 1, 2 o 3 / clic: elegir una mejora.

Los controles de movimiento y dash de ambos jugadores se pueden reasignar desde **Configuración**. Haz clic en una acción y pulsa la nueva tecla; Esc cancela la reasignación. Si la tecla ya estaba asignada a otra acción del mismo jugador, ambas se intercambian.

En el menú principal, pulsa Jugar para un jugador o usa las teclas 1/2 para elegir el modo. El ranking guarda los diez mejores puntajes de un jugador y los diez de cooperativo, por separado, en `data/scores.json`. Si tu puntaje entra al top 10 se piden 3 iniciales (letras o números; Enter guarda, Esc guarda sin nombre). En la pantalla de récords, TAB o las pestañas cambian entre las dos listas.

**Puntaje:** `tiempo × 10` + puntos de cada enemigo eliminado (zombi 10, rápido 15, tirador 25, tanque 30) + 500 por jefe derrotado. Los cristales sin recoger ya no suman.

## Oleadas y jefes
- La oleada actual aparece permanentemente en la parte superior de la pantalla.
- Cada oleada tiene 8 conjuntos de enemigos. Cuando salió el último, el jefe solo aparece si ya eliminaste el 85% de los enemigos de todos los conjuntos (el contador se ve arriba). Su nivel y su vida aumentan en cada encuentro.
- Hay dieciocho jefes, cada uno con un patrón de ataque propio. Los ocho primeros rotan en este orden: **Espiral** (doble espiral de balas), **Cazador** (abanicos apuntados y embestidas), **Pulsar** (anillos de balas que giran y rachas apuntadas), **Invocador** (lluvia de balas y refuerzos), **Barrido** (dos chorros de balas que cruzan la pantalla), **Muralla** (muros de balas con un hueco para escapar), **Enjambre** (oleadas de enemigos rápidos desde los costados) y **Singularidad** (atrae a la nave, órbitas de balas y meteoros). Los diez nuevos (oleadas 9 a 18): **Bastión** (tres cañones apuntados y anillo de escudo), **Lanza** (lanzadas en fila y agujas a los costados), **Medusa** (abanicos con huecos alternados y crías), **Cruzado** (cuatro brazos giratorios), **Escorpión** (pinzas y aguijón rápido), **Polilla** (polvo de alas y ráfagas laterales), **Calavera** (ojos que apuntan, mandíbula y furia con poca vida), **Cristal** (anillos en forma de diamante y esquirlas), **Sierra** (discos grandes y chispas giratorias) y **Ojo** (mirada veloz e iris giratorio).
- **Orden y dificultad:** de la oleada 1 a la 18 aparece un jefe de cada tipo en orden; desde la 19 se elige al azar entre los 18 (sin repetir el anterior y con cualquiera de sus dos colores). Con cada oleada el jefe tiene más vida, ataca más rápido (hasta el doble) y sus balas van más rápido (hasta +30%). Además su vida crece con el nivel medio de los jugadores (+3% por nivel) y en cooperativo (×1,35).
- **Fondos:** oleadas 1-10 cuadrícula base; 11-18 nebulosa; desde la 19 circuito. Los menús usan el fondo base.
- Un segundo y medio antes de la entrada del jefe se muestra una alerta animada con parpadeo rojo, nombre del jefe, cuenta regresiva, sonido y vibración opcional.
- Las oleadas normales se reanudan después de derrotar al jefe.

## Modo beta (panel secreto)
Durante una partida (sin pausa ni menú de mejoras abierto) escribe **hola3ro** en el teclado, como un código Konami. Se abre un panel de pruebas y el juego queda detenido mientras esté abierto:
- **Jefe:** elige cualquiera de los 18, su color (1 o 2) y su nivel (que es también la oleada: define su vida, su ritmo de ataque y el fondo). Con **Invocar jefe** aparece al instante; con **Ir a oleada** saltas a esa oleada con enemigos normales. La rueda del ratón sube/baja el nivel.
- **Habilidades:** clic izquierdo sube un nivel y clic derecho lo baja, en las 17 habilidades (en cooperativo hay una pestaña por jugador). También hay **Todas al máx.** y **Quitar todas**. Cada cambio recalcula los efectos desde cero y devuelve la vida completa.
- **Invencible:** alterna si la nave recibe daño.
- Esc cierra el panel y la partida sigue. En la parte superior aparece **MODO BETA** y esa partida **no se guarda en el ranking**.

## Configuración
El menú permite cambiar controles, volumen y vibración de pantalla. También incluye un botón para restablecer los valores predeterminados. Los ajustes se guardan automáticamente en `data/settings.json` y se conservan al cerrar el juego.

## Qué incluye
- Bucle de juego con límite de 60 FPS, movimiento basado en `dt` y simulación en pasos de máximo 20 ms (con FPS bajos las balas no atraviesan enemigos).
- Un único reloj de juego: dash, invencibilidad, cadencia, disparos enemigos y ataques de jefes se detienen en la pausa y en el menú de mejoras. La pausa se activa sola si la ventana pierde el foco (Alt-Tab).
- Clases para jugadores, enemigos, jefe, balas y cristales.
- Enemigos básicos, rápidos, tanques y tiradores.
- Dieciocho jefes con patrones de ataque distintos y dificultad progresiva, y tres fondos que cambian con la oleada.
- Disparo automático hacia arriba.
- Hitbox reducida: solo recibes daño en un cuadrado pequeño en el centro de la nave.
- La nave se vuelve más roja a medida que pierde vida.
- Cristales de experiencia: desaparecen a los 20 segundos si no se recogen (parpadean en los últimos 4). En cooperativo el imán atrae cada cristal hacia el jugador más cercano. Si un enemigo muere fuera de la vista por arriba (detrás del panel superior), su cristal baja solo hasta la zona visible para que se note dónde quedó la experiencia.
- Si una ganancia de experiencia cruza varios umbrales se sube más de un nivel: las mejoras se ofrecen una tras otra. Si ya tienes todas las habilidades al máximo se avisa en pantalla.
- Los enemigos que se van por un costado cuentan como resueltos para el 85% que pide el jefe.
- Un `scores.json` editado o dañado ya no rompe el ranking (los registros inválidos se ignoran), y si no se puede escribir en la carpeta `data` el menú avisa.
- Experiencia, niveles y mejoras aleatorias por rareza (las épicas y legendarias son poco frecuentes). Al elegir una legendaria, ondas doradas se expanden desde la nave por toda la pantalla.
- Propulsión Térmica: el dash deja una estela de llamas (sprites de pixel art) que quema a los enemigos que la tocan. Las llamas son dinámicas: parpadean cambiando entre sus 4 formas, suben un poco y pasan de recién creadas a brasa hasta apagarse.
- Ranking local en JSON. Cada récord guarda las habilidades que elegiste en esa partida; haz clic en un récord para verlas, con el icono de cada habilidad, su nombre y el nivel que alcanzó (en cooperativo, también las del jugador que murió, tal como las tenía antes de caer). La lista de récords (top 10) se recorre con la rueda del ratón.
- Sprites de pixel art: nave del jugador 1 (azul) y del jugador 2 (roja), enemigos (rápido, constante, tirador y tanque) y los dieciocho jefes. La nave se tiñe de rojo a medida que pierde vida. Cada jefe tiene una segunda variante de color (se usa desde la oleada 19, al azar).
- Modo cooperativo local para dos jugadores: al subir de nivel se indica a qué jugador pertenece la mejora (título, color del panel y un anillo sobre su nave), y si uno cae sus habilidades pasan al compañero (sin superar el nivel máximo de cada una).
- Efectos de sonido sintetizados y vibración visual configurable.
- Modo beta con panel de pruebas (código `hola3ro`) para elegir jefe, nivel y habilidades.
- Optimización: balas y sprites con imagen en caché, menos objetos temporales por fotograma, colisiones del jugador por lista de rectángulos, sin rellenado redundante de pantalla y precarga del fondo de la oleada siguiente.

Las naves y los jefes usan sprites de pixel art (diseñados en `sprites_naves_pixel_art.html` y `jefes_pixel_art_variaciones.html`) que están dentro de `main.py` (los fondos, en `fondos_data.py`), y los sonidos se generan por código, así que no hace falta descargar imágenes ni archivos de audio externos.
