# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import random
from base_de_preguntas import BASE_DE_PREGUNTAS

# Constantes de la aplicación
NUM_PREGUNTAS_EXAMEN = 15
DIFICULTADES = {
    'facil': {'vidas': 3, 'nombre': 'Fácil'},
    'intermedio': {'vidas': 2, 'nombre': 'Intermedio'},
    'dificil': {'vidas': 1, 'nombre': 'Difícil'},
    'dios': {'vidas': 0, 'nombre': 'Modo Dios'},
    'todos': {'vidas': 2, 'nombre': 'Todas las Dificultades'}
}
CLAVE_SECRETA = 'clave_secreta_super_segura_para_desarrollo_cambiar_en_prod' # ¡IMPORTANTE! Cambia esto en producción

app = Flask(__name__)
app.secret_key = CLAVE_SECRETA


class Examen:
    """Clase para manejar la lógica y el estado de un examen."""
    def __init__(self, dificultad_id):
        if dificultad_id not in DIFICULTADES:
            raise ValueError("Dificultad no válida")

        self.dificultad_id = dificultad_id
        self.dificultad_info = DIFICULTADES[dificultad_id]
        self.preguntas = self._preparar_preguntas()
        self.vidas_iniciales = self.dificultad_info['vidas']
        self.vidas_actuales = self.vidas_iniciales
        self.respuestas_usuario = []
        self.indice_pregunta_actual = 0
        self.examen_terminado = False

    def _preparar_preguntas(self):
        """Filtra y selecciona las preguntas para el examen según la dificultad."""
        if self.dificultad_id == 'todos':
            preguntas_filtradas = BASE_DE_PREGUNTAS[:]
        else:
            preguntas_filtradas = [p for p in BASE_DE_PREGUNTAS if p.get('dificultad') == self.dificultad_id]

        if not preguntas_filtradas:
            # Considerar lanzar una excepción o manejar de otra forma si no hay preguntas
            return []

        random.shuffle(preguntas_filtradas)
        return preguntas_filtradas[:min(NUM_PREGUNTAS_EXAMEN, len(preguntas_filtradas))]

    def obtener_pregunta_actual(self):
        """Devuelve la pregunta actual o None si el examen terminó."""
        if not self.examen_terminado and self.indice_pregunta_actual < len(self.preguntas):
            pregunta = self.preguntas[self.indice_pregunta_actual]
            opciones_desordenadas = pregunta['opciones'][:]
            random.shuffle(opciones_desordenadas)
            return {
                'numero': self.indice_pregunta_actual + 1,
                'total_preguntas': len(self.preguntas),
                'texto_pregunta': pregunta['pregunta'],
                'opciones': opciones_desordenadas,
                'tema': pregunta['tema']
            }
        return None

    def procesar_respuesta(self, seleccion_usuario):
        """Procesa la respuesta del usuario, actualiza vidas y puntaje."""
        if self.examen_terminado:
            return False # No procesar si el examen ya terminó

        pregunta_actual_obj = self.preguntas[self.indice_pregunta_actual]
        respuesta_correcta_texto = pregunta_actual_obj['opciones'][pregunta_actual_obj['respuesta_correcta']]

        es_correcta = (seleccion_usuario == respuesta_correcta_texto)

        if not es_correcta:
            self.vidas_actuales -= 1
            flash(f'¡Incorrecto! La respuesta correcta era: {respuesta_correcta_texto}', 'error')
        else:
            flash('¡Correcto!', 'success')

        self.respuestas_usuario.append({
            'pregunta': pregunta_actual_obj['pregunta'],
            'seleccion': seleccion_usuario,
            'correcta': respuesta_correcta_texto,
            'tema': pregunta_actual_obj['tema'],
            'acertada': es_correcta
        })

        self._avanzar_pregunta()
        return es_correcta

    def _avanzar_pregunta(self):
        """Avanza a la siguiente pregunta o marca el examen como terminado."""
        self.indice_pregunta_actual += 1
        if self.vidas_actuales < 0 or self.indice_pregunta_actual >= len(self.preguntas):
            self.examen_terminado = True
            # En modo Dios, una falla (-1 vidas) termina el examen inmediatamente
            if self.dificultad_id == 'dios' and self.vidas_actuales < self.vidas_iniciales : # vidas_iniciales es 0 para modo dios
                 self.examen_terminado = True


    def obtener_resultados(self):
        """Calcula y devuelve los resultados del examen."""
        total_preguntas_respondidas = len(self.respuestas_usuario)
        correctas = sum(1 for r in self.respuestas_usuario if r['acertada'])
        temas_a_repasar = sorted(list(set(r['tema'] for r in self.respuestas_usuario if not r['acertada'])))
        porcentaje = (correctas / total_preguntas_respondidas) * 100 if total_preguntas_respondidas > 0 else 0

        mensaje_especial = None
        if self.dificultad_id == 'dios':
            if correctas == len(self.preguntas) and total_preguntas_respondidas == len(self.preguntas) and self.vidas_actuales >= 0 :
                mensaje_especial = "¡HAS CONQUISTADO EL MODO DIOS! Eres imparable. 🎉"
                temas_a_repasar = [] # No hay temas a repasar si se ganó el Modo Dios
            else:
                mensaje_especial = "El Modo Dios requiere perfección. Sigue estudiando. 😢"

        return {
            'correctas': correctas,
            'total_preguntas_examen': len(self.preguntas), # Total de preguntas que tenía el examen
            'total_respondidas': total_preguntas_respondidas, # Total que el usuario llegó a responder
            'vidas_finales': self.vidas_actuales,
            'vidas_iniciales': self.vidas_iniciales,
            'porcentaje': porcentaje,
            'temas_a_repasar': temas_a_repasar,
            'mensaje_especial': mensaje_especial,
            'dificultad_nombre': self.dificultad_info['nombre']
        }

    def debe_continuar_examen(self):
        """Verifica si el examen debe continuar."""
        if self.examen_terminado:
            return False

        # Lógica específica para Modo Dios y primera pregunta
        if self.dificultad_id == 'dios' and self.vidas_actuales < self.vidas_iniciales and self.indice_pregunta_actual > 0:
             self.examen_terminado = True
             return False

        if self.vidas_actuales < 0: # Para cualquier modo, si se acaban las vidas (llega a negativo)
            self.examen_terminado = True
            return False

        if self.indice_pregunta_actual >= len(self.preguntas): # Si ya no hay más preguntas
            self.examen_terminado = True
            return False

        return True


@app.route('/')
def inicio():
    """Ruta para la página de inicio, donde se selecciona la dificultad."""
    session.pop('examen_actual', None) # Limpiar examen anterior si existe
    return render_template('inicio.html', dificultades=DIFICULTADES)

@app.route('/iniciar_examen', methods=['POST'])
def iniciar_examen():
    """Inicia un nuevo examen y redirige a la primera pregunta."""
    dificultad_seleccionada = request.form.get('dificultad')
    if not dificultad_seleccionada or dificultad_seleccionada not in DIFICULTADES:
        flash('Por favor, selecciona una dificultad válida.', 'warning')
        return redirect(url_for('inicio'))

    try:
        examen_obj = Examen(dificultad_seleccionada)
        if not examen_obj.preguntas:
            flash(f"No hay preguntas disponibles para la dificultad '{DIFICULTADES[dificultad_seleccionada]['nombre']}'. Por favor, intenta con otra.", "warning")
            return redirect(url_for('inicio'))
        session['examen_actual'] = examen_obj.__dict__ # Guardar el estado del examen en sesión
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('inicio'))

    return redirect(url_for('mostrar_pregunta_ruta'))


@app.route('/pregunta', methods=['GET', 'POST'])
def mostrar_pregunta_ruta():
    """Muestra la pregunta actual o procesa la respuesta."""
    examen_data = session.get('examen_actual')
    if not examen_data:
        flash('El examen no se ha iniciado correctamente o la sesión ha expirado.', 'warning')
        return redirect(url_for('inicio'))

    # Recrear el objeto Examen desde los datos de la sesión
    examen_obj = Examen(examen_data['dificultad_id'])
    examen_obj.__dict__.update(examen_data)

    if not examen_obj.debe_continuar_examen():
        session['examen_actual'] = examen_obj.__dict__ # Guardar estado antes de redirigir
        return redirect(url_for('resultado_ruta'))

    if request.method == 'POST':
        seleccion = request.form.get('opcion')
        if seleccion is None:
            flash('Por favor, selecciona una opción antes de responder.', 'warning')
            # No redirigir, simplemente re-renderizar la misma pregunta
            pregunta_actual_render = examen_obj.obtener_pregunta_actual()
            return render_template('examen.html',
                                   pregunta_data=pregunta_actual_render,
                                   vidas_actuales=examen_obj.vidas_actuales,
                                   vidas_iniciales=examen_obj.vidas_iniciales,
                                   dificultad_id=examen_obj.dificultad_id,
                                   dificultad_nombre=examen_obj.dificultad_info['nombre'])

        examen_obj.procesar_respuesta(seleccion)
        session['examen_actual'] = examen_obj.__dict__ # Actualizar sesión después de procesar

        if not examen_obj.debe_continuar_examen():
            return redirect(url_for('resultado_ruta'))
        else:
            # Redirigir a GET para mostrar la siguiente pregunta y evitar reenvío de formulario
            return redirect(url_for('mostrar_pregunta_ruta'))

    # Método GET: Mostrar la pregunta actual
    pregunta_actual_render = examen_obj.obtener_pregunta_actual()
    if not pregunta_actual_render: # Si por alguna razón no hay pregunta (ej. fin de examen no detectado antes)
        return redirect(url_for('resultado_ruta'))

    return render_template('examen.html',
                           pregunta_data=pregunta_actual_render,
                           vidas_actuales=examen_obj.vidas_actuales,
                           vidas_iniciales=examen_obj.vidas_iniciales,
                           dificultad_id=examen_obj.dificultad_id,
                           dificultad_nombre=examen_obj.dificultad_info['nombre'])


@app.route('/resultado')
def resultado_ruta():
    """Muestra los resultados finales del examen."""
    examen_data = session.get('examen_actual')
    if not examen_data:
        flash('No hay resultados para mostrar o la sesión ha expirado.', 'warning')
        return redirect(url_for('inicio'))

    examen_obj = Examen(examen_data['dificultad_id'])
    examen_obj.__dict__.update(examen_data)

    resultados = examen_obj.obtener_resultados()

    # Limpiar el examen de la sesión después de mostrar los resultados
    session.pop('examen_actual', None)

    return render_template('resultado.html', **resultados)

if __name__ == '__main__':
    app.run(debug=True)