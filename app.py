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
    
    # 1. INICIALIZACIÓN: Aseguramos que esta variable exista siempre.
    folio_generado = "Se generará automáticamente" 
    
    if request.method == 'POST':
        try:
            # 1. Recuperar datos del formulario, incluyendo Lat/Lon de JavaScript
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

            # Generar datos complementarios
            encuestador = "ENCUESTADOR MUNICIPAL"
            
            # =======================================================
            # LÓGICA DE SUBIDA DE FOTO (request.files)
            # =======================================================
            foto_archivo = request.files.get('foto_predio')
            foto_blob = None
            
            if foto_archivo and foto_archivo.filename != '':
                try:
                    foto_blob = foto_archivo.read()
                except Exception as file_err:
                    print(f"Error al leer el archivo de la foto: {file_err}")

            # 2. Guardar en Base de Datos
            conn = get_connection()
            if not conn:
                raise Exception("Error de conexión a la base de datos.")
                
            cursor = conn.cursor()
            
            # NOTA CLAVE: No se incluye 'id' en el INSERT porque es AUTO_INCREMENT.
            # 'folio' se establece a NULL (o vacío) como se solicitó.
            sql = """
                INSERT INTO ENCUESTAS_TELCHAC (
                    folio, fecha, nombre, direccion, colonia, telefono, problema_agua, problema_basura, 
                    frecuencia_recoleccion, servicio_agua, tiene_construccion, tipo_construccion, niveles, 
                    material_predominante, estado_construccion, observacion_construccion, uso_predio, 
                    tiene_contrato_agua, numero_contrato_agua, tiene_contrato_basura, numero_contrato_basura, 
                    latitud, longitud, foto, encuestador
                )
                VALUES (
                    %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """

            folio_valor_db = None # Inserta NULL en la columna 'folio' (VARCHAR/TEXT)

            cursor.execute(sql, (
                folio_valor_db,
                nombre, direccion, colonia, telefono, agua, basura, frec, serv_agua,
                tiene_const, tipo_const, niveles, material, estado, obs, uso,
                cont_agua, num_cont_agua, cont_basura, num_cont_basura,
                latitud, longitud, foto_blob, encuestador
            ))

            # 3. Recuperamos el ID consecutivo generado (el valor de la columna 'id')
            folio_generado = cursor.lastrowid

            conn.commit()
            conn.close()

            # 4. Redireccionar al éxito
            return redirect(url_for('exito', folio=folio_generado))

        except Exception as err:
            # Si hay error (DB, conexión, etc.), mostramos el mensaje de error.
            print(f"Error al guardar: {err}")
            # Usamos el valor inicializado de 'folio_generado' (Se generará automáticamente)
            return render_template('encuesta.html', error=f"Error al guardar: {err}", folio=folio_generado)

    # 5. LÓGICA GET: Si se accede a la ruta directamente (sin POST)
    return render_template('encuesta.html', folio=folio_generado)

@app.route('/exito')
def exito():
    folio = request.args.get('folio', 'N/A')
    return render_template('exito.html', folio=folio)


if __name__ == '__main__':
    # 'host=0.0.0.0' hace que la aplicación sea accesible desde cualquier IP.
    app.run(debug=True, host='0.0.0.0', port=5000)