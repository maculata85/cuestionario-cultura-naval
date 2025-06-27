# -*- coding: utf-8 -*-
"""
Este archivo contiene la lógica principal para el cuestionario de Cultura Naval
ejecutado en la consola.
"""
import random
import os
import time
import traceback

try:
    from base_de_preguntas import BASE_DE_PREGUNTAS
except ImportError:
    print("Error Fatal: No se encontró el archivo 'base_de_preguntas.py'.")
    print("Asegúrate de que ambos archivos ('cuestionario_final.py' y 'base_de_preguntas.py') estén en la misma carpeta.")
    input("Presiona Enter para salir.")
    exit()

# --- Constantes ---
NUM_PREGUNTAS_EXAMEN = 15
DIFICULTADES_CONSOLA = {
    '1': {"id": "facil", "nombre": "Fácil", "vidas": 3, "icono": "💚"},
    '2': {"id": "intermedio", "nombre": "Intermedio", "vidas": 2, "icono": "💛"},
    '3': {"id": "dificil", "nombre": "Difícil", "vidas": 1, "icono": "❤️"},
    '4': {"id": "dios", "nombre": "Dios", "vidas": 0, "icono": "☠️"},
    '5': {"id": "todos", "nombre": "Todos", "vidas": 2, "icono": "💛"}
}

# --- Arte ASCII para los resultados ---
ARTE_ASCII = {
    "excelente": """
      ___________
     '._==_==_=_.'
     .-\\:      /-.
    | (|:.     |) |
     '-|:.     |-'
       \\::.    /
        '::. .'
          ) (
        _.' '._
       `\"\"\"\"\"\"\"`
¡EXCELENTE! Eres un maestro en la materia.""",
    "regular": """
      .---.
     /     \\
     \\.@-@./
     /`\\_/`\\
    //  _  \\\\
   | \\     )|
  /`-_`>  <`_-\\
  \\___)=(___/
Estudia un poco más los temas señalados. ¡Vas por buen camino!""",
    "malo": """
     .-.
    (o.o)
     | |
     '-'
De plano estas bien perdido, ¡ponte a estudiar!""",
    "dios_conquistado": """
  _ .-') _  / _.-') _
 ( (  OO) )(  OO) )) )
  \\ \\(_)--\\/\\  _(`( (
  /  /    _/\ (_()_) )
  \\_)-/\  \ \  -')(_/
  (_.--\ ) .\(`_.)  __
  |\  `.'  /  /  __)(  \\
  | \\     /   \  `   /
  `--'   `     `--`--'
¡HAS CONQUISTADO EL MODO DIOS! Eres imparable. 🎉""",
    "dios_fallido": """
       .--.
      |o_o |
      |:_/ |
     //   \ \
    (|     | )
   /'\_   _/`\
   \___)-(___/
El Modo Dios requiere perfección. Sigue estudiando. 😢"""
}

def limpiar_pantalla():
    """Limpia la consola."""
    os.system('cls' if os.name == 'nt' else 'clear')

def seleccionar_dificultad_consola():
    """Permite al usuario seleccionar la dificultad del examen en la consola."""
    print("Elige un nivel de dificultad para tu examen:")
    for key, value in DIFICULTADES_CONSOLA.items():
        vidas_str = f"{value['vidas']} vida{'s' if value['vidas'] != 1 else ''}"
        if value['id'] == 'dios':
            vidas_str = "0 vidas ☠️ - Sin margen de error"
        else:
            vidas_str = f"{value['vidas']} vida{'s' if value['vidas'] != 1 else ''} {value['icono'] * value['vidas']}"
        print(f"{key}. {value['nombre']} ({vidas_str})")

    while True:
        eleccion = input(f"Ingresa el número de tu elección (1-{len(DIFICULTADES_CONSOLA)}): ")
        if eleccion in DIFICULTADES_CONSOLA:
            return DIFICULTADES_CONSOLA[eleccion]
        else:
            print(f"Opción no válida. Por favor, ingresa un número del 1 al {len(DIFICULTADES_CONSOLA)}.")


def preparar_examen_consola(dificultad_id, todas_las_preguntas):
    """Filtra y selecciona las preguntas para el examen de consola."""
    if not todas_las_preguntas:
        print("\n❌ Error: La base de datos de preguntas está vacía.")
        return None

    if dificultad_id == "todos":
        preguntas_filtradas = todas_las_preguntas[:]
    else:
        preguntas_filtradas = [p for p in todas_las_preguntas if p.get('dificultad') == dificultad_id]

    if not preguntas_filtradas:
        print(f"\n❌ Error: No se encontraron preguntas para el nivel '{dificultad_id}'.")
        return None

    if len(preguntas_filtradas) < NUM_PREGUNTAS_EXAMEN:
        print(f"\n⚠️ Advertencia: No hay suficientes preguntas ({len(preguntas_filtradas)}) para el nivel '{dificultad_id}'.")
        print(f"El examen se realizará con las {len(preguntas_filtradas)} preguntas disponibles.")

    num_a_seleccionar = min(NUM_PREGUNTAS_EXAMEN, len(preguntas_filtradas))
    random.shuffle(preguntas_filtradas)
    return preguntas_filtradas[:num_a_seleccionar]


def ejecutar_examen_consola(preguntas_examen, dificultad_info):
    """Lógica principal para correr el cuestionario en consola."""
    puntaje = 0
    vidas_actuales = dificultad_info['vidas']
    vidas_iniciales = dificultad_info['vidas']
    temas_a_repasar = set()
    examen_completado_normalmente = True # Asumimos que se completa, cambia si hay fallo en Modo Dios

    for i, pregunta_actual in enumerate(preguntas_examen):
        limpiar_pantalla()

        # Visualización de vidas
        if dificultad_info['id'] != 'dios':
            vida_iconos = dificultad_info['icono'] * vidas_actuales
            if vidas_iniciales > vidas_actuales:
                vida_iconos += "💔 " * (vidas_iniciales - vidas_actuales)
            print(f"--- Pregunta {i + 1} de {len(preguntas_examen)} --- | Vidas: {vida_iconos}")
        else:
            print(f"--- Pregunta {i + 1} de {len(preguntas_examen)} --- | Vidas: ☠️ (MODO DIOS)")

        print(f"Puntaje actual: {puntaje}\n")
        print(f"Tema: {pregunta_actual['tema']}\n")
        print(f"P: {pregunta_actual['pregunta']}\n")

        opciones_mostradas = list(pregunta_actual['opciones'])
        respuesta_correcta_texto = opciones_mostradas[pregunta_actual['respuesta_correcta']]
        random.shuffle(opciones_mostradas)

        for j, opcion_texto in enumerate(opciones_mostradas):
            print(f"  {chr(65 + j)}) {opcion_texto}")

        # Validar respuesta
        while True:
            respuesta_usuario_letra = input("\nTu respuesta (A, B, C...): ").upper()
            if respuesta_usuario_letra and respuesta_usuario_letra in [chr(65 + k) for k in range(len(opciones_mostradas))]:
                break
            else:
                print("Respuesta no válida. Inténtalo de nuevo.")

        opcion_seleccionada_texto = opciones_mostradas[ord(respuesta_usuario_letra) - 65]

        if opcion_seleccionada_texto == respuesta_correcta_texto:
            puntaje += 1
            print("\n¡Correcto! 👍")
        else:
            vidas_actuales -= 1
            temas_a_repasar.add(pregunta_actual['tema'])
            print("\n¡Incorrecto! 👎")
            print(f"La respuesta correcta era: {respuesta_correcta_texto}")

            if dificultad_info['id'] == 'dios': # En Modo Dios, cualquier fallo termina el examen
                print("\n¡Has cometido un error en Modo Dios! El examen ha terminado.")
                examen_completado_normalmente = False
                time.sleep(2)
                return puntaje, temas_a_repasar, vidas_actuales, examen_completado_normalmente
        
        if vidas_actuales < 0 and dificultad_info['id'] != 'dios': # Vidas agotadas en modos normales
            print("\n¡Te has quedado sin vidas! El examen ha terminado.")
            examen_completado_normalmente = False # No se completó por falta de vidas
            time.sleep(2)
            break # Salir del bucle de preguntas

        time.sleep(1.5)

    # Si el bucle termina sin interrupciones (ej. Modo Dios fallido o sin vidas)
    # y no se marcó como no completado, entonces se completó.
    # Esto es redundante si ya se maneja arriba, pero asegura el estado.
    if vidas_actuales >= 0 and (dificultad_info['id'] != 'dios' or puntaje == len(preguntas_examen)):
         examen_completado_normalmente = True


    return puntaje, temas_a_repasar, vidas_actuales, examen_completado_normalmente

def grafica_horizontal_consola(correctas, total):
    """Genera una barra gráfica de texto para el resultado en consola."""
    if total == 0: return ""
    porc_correctas = int((correctas / total) * 100)
    longitud_barra = 30 # Más corta para consola
    bloques_correctos = int(longitud_barra * (porc_correctas / 100))
    barra = "🟩" * bloques_correctos + "🟥" * (longitud_barra - bloques_correctos)
    return f"Rendimiento: [{barra}] {porc_correctas}%"

def mostrar_resultados_consola(puntaje, total_preguntas_examen, temas_repasar, vidas_finales, dificultad, examen_completado):
    """Muestra los resultados en la consola."""
    try:
        limpiar_pantalla()
        print("--- 🏁 Resultados Finales del Examen ---")

        calificacion = (puntaje / total_preguntas_examen) * 100 if total_preguntas_examen > 0 else 0.0

        print("\n" + grafica_horizontal_consola(puntaje, total_preguntas_examen))
        print("-------------------------------------------")
        print(f"Respuestas correctas: {puntaje} de {total_preguntas_examen}")

        if dificultad['id'] != 'dios':
            vidas_usadas = dificultad['vidas'] - max(0, vidas_finales) # Vidas iniciales de la dificultad
            print(f"Vidas utilizadas: {vidas_usadas} de {dificultad['vidas']}")

        print(f"Calificación: {calificacion:.2f} / 100.00")
        print("-------------------------------------------\n")

        if dificultad['id'] == 'dios':
            print(ARTE_ASCII["dios_conquistado"] if examen_completado and puntaje == total_preguntas_examen else ARTE_ASCII["dios_fallido"])
            if examen_completado and puntaje == total_preguntas_examen:
                temas_repasar.clear()
        elif calificacion >= 90:
            print(ARTE_ASCII["excelente"])
        elif calificacion >= 60:
            print(ARTE_ASCII["regular"])
        else:
            print(ARTE_ASCII["malo"])

        if temas_repasar:
            print("\n💡 Sugerencias de Estudio:")
            print("Se recomienda repasar los siguientes temas donde cometiste errores:")
            for i, tema in enumerate(sorted(list(temas_repasar))):
                print(f"  {i+1}. {tema}")
        elif dificultad['id'] != 'dios' and calificacion >= 90:
            print("\n¡Felicidades, no hay temas que repasar!")
        elif not temas_repasar and (dificultad['id'] == 'dios' and not (examen_completado and puntaje == total_preguntas_examen)):
             print("\nAunque no hay temas específicos por errores, el Modo Dios requiere perfección. ¡Sigue intentando!")


    except Exception:
        print("\n\n          ¡ERROR INESPERADO AL GENERAR EL DIAGNÓSTICO!          ")
        print("===================================================================")
        traceback.print_exc()
        print("-------------------------------------------------------------------")


def main_consola():
    """Función principal para la versión de consola."""
    limpiar_pantalla()
    print("======================================================")
    print("   Bienvenido al Cuestionario de Cultura Naval (Consola) ")
    print("======================================================")

    dificultad_seleccionada_info = seleccionar_dificultad_consola()
    preguntas_del_examen_actual = preparar_examen_consola(dificultad_seleccionada_info['id'], BASE_DE_PREGUNTAS)

    if preguntas_del_examen_actual:
        total_preguntas_actual = len(preguntas_del_examen_actual)
        print(f"\nIniciando examen nivel '{dificultad_seleccionada_info['nombre']}' con {total_preguntas_actual} preguntas.")
        input("Presiona Enter para comenzar...")

        puntaje_obtenido, temas_pendientes, vidas_restantes, completado_status = \
            ejecutar_examen_consola(preguntas_del_examen_actual, dificultad_seleccionada_info)

        mostrar_resultados_consola(puntaje_obtenido, total_preguntas_actual, temas_pendientes,
                                   vidas_restantes, dificultad_seleccionada_info, completado_status)
    else:
        print("\nNo se pudo iniciar el examen. Verifica la configuración.")

    input("\n\nEl diagnóstico ha finalizado. Presiona Enter para cerrar la ventana...")


if __name__ == "__main__":
    # Podrías añadir un argumento para elegir entre app.py y cuestionario_final.py si quisieras
    # Por ahora, esto solo correrá la versión de consola.
    main_consola()