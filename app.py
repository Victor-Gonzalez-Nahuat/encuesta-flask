# app.py
from flask import Flask, render_template, request, redirect, url_for
import pymysql
from datetime import datetime
import os
from dotenv import load_dotenv

# Nota: La función obtener_gps() ya no es necesaria, 
# ya que la ubicación se obtendrá directamente del navegador con JavaScript.

load_dotenv()
app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui' # Necesario para sesiones/mensajes flash

# --- Conexión a la Base de Datos ---

def get_connection():
    DB_HOST = os.getenv('DB_HOST')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')
    DB_PORT = 51558
    try:
        return pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )
    except Exception as e:
        print(f"Error de conexión a DB: {e}")
        return None

# --- Rutas de la Aplicación ---

@app.route('/', methods=['GET', 'POST'])
def encuesta():
    """Maneja la visualización del formulario y el envío de datos."""
    
    if request.method == 'POST':
        # 1. Recuperar datos del formulario, incluyendo Lat/Lon de JavaScript
        try:
            # Los datos vienen de la solicitud POST
            nombre = request.form.get('nombre')
            direccion = request.form.get('direccion')
            colonia = request.form.get('colonia')
            telefono = request.form.get('telefono')
            agua = request.form.get('cmb_agua')
            basura = request.form.get('cmb_basura')
            frec = request.form.get('cmb_frec')
            serv_agua = request.form.get('cmb_servicio_agua')
            tiene_const = request.form.get('cmb_tiene_const')
            tipo_const = request.form.get('cmb_tipo_const')
            niveles = request.form.get('cmb_niveles')
            material = request.form.get('cmb_material')
            estado = request.form.get('cmb_estado')
            obs = request.form.get('tx_obs_const')
            uso = request.form.get('cmb_uso')
            cont_agua = request.form.get('cmb_cont_agua')
            num_cont_agua = request.form.get('tx_num_cont_agua')
            cont_basura = request.form.get('cmb_cont_basura')
            num_cont_basura = request.form.get('tx_num_cont_basura')
            
            # ¡Las variables clave con GPS preciso!
            latitud = request.form.get('latitud_gps')
            longitud = request.form.get('longitud_gps')

            # Generar Folio y otros datos
            folio = f"TP-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            encuestador = "ENCUESTADOR MUNICIPAL"
            
            # Nota: La lógica de la foto se ha omitido por simplicidad en la migración.
            # Los archivos (fotos) se manejan de manera diferente en Flask (request.files).
            foto_blob = None 

            # 2. Guardar en Base de Datos (Lógica de tu función guardar_encuesta)
            conn = get_connection()
            if not conn:
                return "Error de conexión a la base de datos.", 500
                
            cursor = conn.cursor()
            
            sql = """
                INSERT INTO ENCUESTAS_TELCHAC (
                    folio, fecha, nombre, direccion, colonia, telefono, problema_agua, problema_basura, 
                    frecuencia_recoleccion, servicio_agua, tiene_construccion, tipo_construccion, niveles, 
                    material_predominante, estado_construccion, observacion_construccion, uso_predio, 
                    tiene_contrato_agua, numero_contrato_agua, tiene_contrato_basura, numero_contrato_basura, 
                    latitud, longitud, foto, encuestador
                )
                VALUES (
                    %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """

            cursor.execute(sql, (
                folio,
                nombre, direccion, colonia, telefono, agua, basura, frec, serv_agua,
                tiene_const, tipo_const, niveles, material, estado, obs, uso,
                cont_agua, num_cont_agua, cont_basura, num_cont_basura,
                latitud, longitud, foto_blob, encuestador
            ))

            conn.commit()
            conn.close()

            # 3. Redireccionar al éxito
            return redirect(url_for('exito', folio=folio))

        except Exception as err:
            print(f"Error al guardar: {err}")
            # En Flask, puedes usar "flash" para mostrar mensajes de error
            return render_template('encuesta.html', error=f"Error al guardar: {err}")

    # Si es GET, mostrar el formulario
    return render_template('encuesta.html', folio=f"TP-{datetime.now().strftime('%Y%m%d-%H%M%S')}")

@app.route('/exito')
def exito():
    folio = request.args.get('folio', 'N/A')
    return render_template('exito.html', folio=folio)


if __name__ == '__main__':
    # 'host=0.0.0.0' hace que la aplicación sea accesible desde cualquier IP, 
    # incluyendo tu red local.
    app.run(debug=True, host='0.0.0.0', port=5000)