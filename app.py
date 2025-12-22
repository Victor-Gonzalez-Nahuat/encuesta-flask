# app.py
from flask import Flask, render_template, request, redirect, url_for
import pymysql
from datetime import datetime
import os
from dotenv import load_dotenv
from flask import session
from functools import wraps



load_dotenv()
app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# --- Conexión a la Base de Datos (sin cambios) ---
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

def login_requerido(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorador


# --- Rutas de la Aplicación ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')

        conn = get_connection()
        if not conn:
            return render_template(
                'login.html',
                error="No se pudo conectar a la base de datos"
            )

        cursor = conn.cursor()
        sql = "SELECT usuario FROM ENCUESTADORES_TELCHAC WHERE usuario=%s AND password=%s"
        cursor.execute(sql, (usuario, password))
        result = cursor.fetchone()
        conn.close()

        if result:
            session['usuario'] = usuario
            return redirect(url_for('encuesta'))
        else:
            return render_template('login.html', error="Credenciales incorrectas")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
@login_requerido
def encuesta():
    
    folio_generado = "Se generará automáticamente" 
    
    if request.method == 'POST':
        try:
            # ----------------------------------------------------
            # 1. Recuperación de datos (sin cambios)
            # ----------------------------------------------------
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

            encuestador = session.get('usuario')
            
            # --- GENERAR FECHA EN PYTHON PARA EL VARCHAR(20) ---
            fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # LÓGICA DE SUBIDA DE FOTO (sin cambios)
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
            
            # --- CAMBIO 1: EL SQL AHORA USA %s PARA LA FECHA ---
            sql = """
                INSERT INTO ENCUESTAS_TELCHAC (
                    folio, fecha, nombre, direccion, colonia, telefono, problema_agua, problema_basura, 
                    frecuencia_recoleccion, servicio_agua, tiene_construccion, tipo_construccion, niveles, 
                    material_predominante, estado_construccion, observacion_construccion, uso_predio, 
                    tiene_contrato_agua, numero_contrato_agua, tiene_contrato_basura, numero_contrato_basura, 
                    latitud, longitud, foto, encuestador
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """

            folio_valor_db = None 
            
            # --- CAMBIO 2: AGREGAMOS fecha_actual a la tupla (TOTAL 25 parámetros) ---
            parametros = (
                # 1. Columna 'folio'
                folio_valor_db, 
                
                # 2. Columna 'fecha' (NUEVO)
                fecha_actual,

                # 3. Datos de Identificación
                nombre, 
                direccion, 
                colonia, 
                telefono, 

                # 4. Servicios 
                agua, 
                basura, 
                frec, 
                serv_agua, 

                # 5. Construcción 
                tiene_const, 
                tipo_const, 
                niveles, 
                material, 
                estado, 

                # 6. Observaciones y Uso
                obs, 
                uso, 

                # 7. Contratos 
                cont_agua, 
                num_cont_agua, 
                cont_basura, 
                num_cont_basura, 

                # 8. GPS y Archivos
                latitud, 
                longitud, 
                foto_blob, 
                encuestador
            )
            # -------------------------------------------------------------------
            
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