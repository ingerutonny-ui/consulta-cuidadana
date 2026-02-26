import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def get_db_connection():
    # Conexión persistente a PostgreSQL en Render usando la variable de entorno
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    return conn

def init_db():
    # Esta función crea la tabla 'votos' si no existe, solucionando el Error Crítico
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS votos (
            id SERIAL PRIMARY KEY,
            ci VARCHAR(20) UNIQUE NOT NULL,
            nombres VARCHAR(100) NOT NULL,
            apellido VARCHAR(100) NOT NULL,
            edad INTEGER NOT NULL,
            genero VARCHAR(20) NOT NULL,
            celular VARCHAR(20) NOT NULL,
            partido_id INTEGER NOT NULL
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

# LISTA DE CANDIDATOS - ORURO
partidos_oruro = [
    {"id": 1, "nombre": "MTS", "alcalde": "OLIVER OSCAR POMA CARTAGENA"},
    {"id": 2, "nombre": "PATRIA ORURO", "alcalde": "RAFAEL VARGAS VILLEGAS"},
    {"id": 3, "nombre": "LIBRE", "alcalde": "RENE BENJAMIN GUZMAN VARGAS"},
    {"id": 4, "nombre": "PP", "alcalde": "CARLOS AGUILAR"},
    {"id": 5, "nombre": "SOMOS ORURO", "alcalde": "MARCELO CORTEZ GUTIERREZ"},
    {"id": 6, "nombre": "JACHA", "alcalde": "MARCELO FERNANDO MEDINA CENTELLAS"},
    {"id": 7, "nombre": "SOL.BO", "alcalde": "MARCELO MEDINA"},
    {"id": 8, "nombre": "UN", "alcalde": "SAMUEL DORIA MEDINA"},
    {"id": 9, "nombre": "MAS-IPSP", "alcalde": "ADHEMAR WILCARANI"},
    {"id": 10, "nombre": "PBCP", "alcalde": "LIZETH TITO"},
    {"id": 11, "nombre": "UCS", "alcalde": "JORGE CALLE"},
    {"id": 12, "nombre": "PAN-BOL", "alcalde": "MILTON GOMEZ"},
    {"id": 13, "nombre": "AS", "alcalde": "ALVARO CASTELLON"},
    {"id": 14, "nombre": "FPV", "alcalde": "JAVIER CALIZAYA"},
    {"id": 15, "nombre": "BST", "alcalde": "FREDDY CANAVIRI"},
    {"id": 16, "nombre": "LIDER", "alcalde": "CARMEN ROSA QUISPE"},
    {"id": 17, "nombre": "UNSOL", "alcalde": "ESTEBAN MAMANI"}
]

# LISTA DE CANDIDATOS - LA PAZ
partidos_lapaz = [
    {"id": 101, "nombre": "SOBERANÍA", "alcalde": "FELIPE QUISPE"},
    {"id": 102, "nombre": "SOL.BO", "alcalde": "ALVARO BLONDEL"},
    {"id": 103, "nombre": "PAN-BOL", "alcalde": "AMILCAR BARRAL"},
    {"id": 104, "nombre": "MAS-IPSP", "alcalde": "CESAR DOCKWEILER"},
    {"id": 105, "nombre": "UCS", "alcalde": "PETER MALDONADO"},
    {"id": 106, "nombre": "MTS", "alcalde": "RONALD ESCOBAR"},
    {"id": 107, "nombre": "JALLALLA", "alcalde": "DAVID CASTRO"},
    {"id": 108, "nombre": "PBCP", "alcalde": "LOURDES CHUMACERO"},
    {"id": 109, "nombre": "FICO", "alcalde": "LUIS LARREA"},
    {"id": 110, "nombre": "ASP", "alcalde": "RAMIRO BURGOS"},
    {"id": 111, "nombre": "VENCEREMOS", "alcalde": "OSCAR HEREDIA"},
    {"id": 112, "nombre": "UN", "alcalde": "WALDO ALBARRACIN"},
    {"id": 113, "nombre": "FPV", "alcalde": "FRANKLIN FLORES"},
    {"id": 114, "nombre": "C-A", "alcalde": "JOSE LUIS BEDREGAL"},
    {"id": 115, "nombre": "MDS", "alcalde": "IVAN ARIAS"},
    {"id": 116, "nombre": "MNR", "alcalde": "REINALDO GARCIA"},
    {"id": 117, "nombre": "PDC", "alcalde": "ANA MARÍA FLORES"}
]

@app.route('/')
def index():
    # Captura parámetros para mostrar overlays azul/rojo en index.html
    msg_type = request.args.get('msg_type')
    ci_votante = request.args.get('ci')
    return render_template('index.html', msg_type=msg_type, ci_votante=ci_votante)

@app.route('/votar/<ciudad>')
def votar(ciudad):
    ciudad_upper = ciudad.upper().replace("_", " ")
    lista = partidos_oruro if "ORURO" in ciudad_upper else partidos_lapaz
    return render_template('votar.html', ciudad=ciudad_upper, partidos=lista)

@app.route('/confirmar_voto', methods=['POST'])
def confirmar_voto():
    ci = request.form.get('ci')
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Validar si el CI ya existe en la BD real
        cur.execute('SELECT ci FROM votos WHERE ci = %s', (ci,))
        if cur.fetchone():
            cur.close()
            conn.close()
            # Si existe, manda al index con ventana roja
            return redirect(url_for('index', msg_type='error', ci=ci))
        
        # Inserción con todos los campos P1, P2 y P3 mapeados
        cur.execute('''INSERT INTO votos (ci, nombres, apellido, edad, genero, celular, partido_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)''', (
            ci, 
            request.form.get('nombres').upper(), 
            request.form.get('apellido').upper(), 
            request.form.get('edad'), 
            request.form.get('genero'),
            request.form.get('celular'), 
            request.form.get('partido_id')
        ))
        conn.commit()
        cur.close()
        conn.close()
        # Si tiene éxito, manda al index con ventana azul
        return redirect(url_for('index', msg_type='success', ci=ci))
    except Exception as e:
        return f"Error Crítico: {str(e)}", 500

@app.route('/reporte')
def reporte():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT partido_id, COUNT(*) FROM votos GROUP BY partido_id')
        conteos = dict(cur.fetchall())
        cur.close()
        conn.close()

        # Asignar conteos a las listas originales
        for p in partidos_oruro: p['votos'] = conteos.get(p['id'], 0)
        for p in partidos_lapaz: p['votos'] = conteos.get(p['id'], 0)

        # Estructura de diccionario para el bucle en reporte.html
        resultados = {
            "ORURO": partidos_oruro,
            "LA PAZ": partidos_lapaz
        }
        return render_template('reporte.html', resultados=resultados)
    except Exception as e:
        return f"Error en Reporte: {str(e)}", 500

if __name__ == '__main__':
    init_db() # Crea la tabla al arrancar el servidor
    app.run()
