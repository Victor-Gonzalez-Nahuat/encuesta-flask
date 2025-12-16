import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

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

def extraer_foto_por_folio(folio_a_buscar):

    conn = get_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    try:
        cursor = conn.cursor()
        
        sql = "SELECT folio, foto FROM ENCUESTAS_TELCHAC WHERE folio = %s"
        cursor.execute(sql, (folio_a_buscar,))
        
        resultado = cursor.fetchone()
        
        if resultado:
            folio, foto_blob = resultado
            
            if foto_blob:
                nombre_archivo = f"foto_verificacion_{folio}.jpg"
                
                with open(nombre_archivo, 'wb') as file:
                    file.write(foto_blob)
                
                print(f"✅ ¡Éxito! Foto extraída para el folio {folio}.")
                print(f"Guarda como: {nombre_archivo}")
                print("Puedes abrir este archivo para ver la imagen.")
            else:
                print(f"El folio {folio_a_buscar} se encontró, pero no tiene foto guardada.")
        else:
            print(f"❌ Error: No se encontró ninguna encuesta con el folio {folio_a_buscar}.")

    except Exception as err:
        print(f"Error al extraer la foto: {err}")
    finally:
        conn.close()


FOLIO_DE_PRUEBA = "TP-20251216-020456" 

if __name__ == '__main__':
    print(f"Intentando extraer foto para el folio: {FOLIO_DE_PRUEBA}")
    extraer_foto_por_folio(FOLIO_DE_PRUEBA)