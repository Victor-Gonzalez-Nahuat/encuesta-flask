# app.py
from flask import Flask, render_template, request, redirect, url_for
import pymysql
from datetime import datetime
import os
from dotenv import load_dotenv



load_dotenv()
app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui' # Necesario para sesiones/mensajes flash


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


@app.route('/', methods=['GET', 'POST'])
def encuesta():
    
    folio_generado = "Se generará automáticamente" 
    
    if request.method == 'POST':
        try:

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
            
            latitud = request.form.get('latitud_gps')
            longitud = request.form.get('longitud_gps')

            encuestador = "ENCUESTADOR MUNICIPAL"
            
            foto_archivo = request.files.get('foto_predio')
            foto_blob = None
            
            if foto_archivo and foto_archivo.filename != '':
                try:
                    foto_blob = foto_archivo.read()
                except Exception as file_err:
                    print(f"Error al leer el archivo de la foto: {file_err}")

            conn = get_connection()
            if not conn:
                raise Exception("Error de conexión a la base de datos.")
                
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
                    %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """

            folio_valor_db = None 
            
            # --- TUPLA DE PARÁMETROS ORDENADA Y COMPLETA (24 valores) ---
            parametros = (
                # 1. Columna 'folio'
                folio_valor_db, 

                # 2. Datos de Identificación
                nombre, 
                direccion, 
                colonia, 
                telefono, 

                # 3. Servicios 
                agua, 
                basura, 
                frec, 
                serv_agua, 

                # 4. Construcción 
                tiene_const, 
                tipo_const, 
                niveles, 
                material, 
                estado, 

                # 5. Observaciones y Uso
                obs, 
                uso, 

                # 6. Contratos 
                cont_agua, 
                num_cont_agua, 
                cont_basura, 
                num_cont_basura, 

                # 7. GPS y Archivos
                latitud, 
                longitud, 
                foto_blob, 
                encuestador
            )
            
            cursor.execute(sql, parametros)

            folio_generado = cursor.lastrowid

            conn.commit()
            conn.close()

            return redirect(url_for('exito', folio=folio_generado))

        except Exception as err:
            print(f"Error al guardar: {err}")
            return render_template('encuesta.html', error=f"Error al guardar: {err}", folio=folio_generado)

    return render_template('encuesta.html', folio=folio_generado)

@app.route('/exito')
def exito():
    folio = request.args.get('folio', 'N/A')
    return render_template('exito.html', folio=folio)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)