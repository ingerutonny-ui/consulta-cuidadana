import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

def init_db():
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

# Inicialización en la nube (Render)
init_db()

# LISTA OFICIAL DE 15 PARTIDOS - ORDEN ESTRICTO
partidos_oruro = [
    {"id": 1, "nombre": "FRI", "alcalde": "CANDIDATO FRI"},
    {"id": 2, "nombre": "LODEL", "alcalde": "CANDIDATO LODEL"},
    {"id": 3, "nombre": "NGP", "alcalde": "CANDIDATO NGP"},
    {"id": 4, "nombre": "AORA", "alcalde": "CANDIDATO AORA"},
    {"id": 5, "nombre": "UN", "alcalde": "SAMUEL DORIA MEDINA"},
    {"id": 6, "nombre": "ALIANZA", "alcalde": "CANDIDATO ALIANZA"},
    {"id": 7, "nombre": "AESA", "alcalde": "CANDIDATO AESA"},
    {"id": 8, "nombre": "SÚMATE", "alcalde": "CANDIDATO SÚMATE"},
    {"id": 9, "nombre": "MTS", "alcalde": "OLIVER OSCAR POMA CARTAGENA"},
    {"id": 10, "nombre": "JALLALLA", "alcalde": "DAVID CASTRO"},
    {"id": 11, "nombre": "LIBRE", "alcalde": "RENE BENJAMIN GUZMAN VARGAS"},
    {"id": 12, "nombre": "PP", "alcalde": "CARLOS AGUILAR"},
    {"id": 13, "nombre": "SOMOS PUEBLO", "alcalde": "MARCELO CORTEZ GUTIERREZ"},
    {"id": 14, "nombre": "JA-HA", "alcalde": "MARCELO FERNANDO MEDINA CENTELLAS"},
    {"id": 15, "nombre": "PDC", "alcalde": "ANA MARÍA FLORES"}
]

partidos_lapaz = [
    {"id": 101, "nombre": "FRI", "alcalde": "CANDIDATO FRI"},
    {"id": 102, "nombre": "LODEL", "alcalde": "CANDIDATO LODEL"},
    {"id": 103, "nombre": "NGP", "alcalde": "CANDIDATO NGP"},
    {"id": 104, "nombre": "AORA", "alcalde": "CANDIDATO AORA"},
    {"id": 105, "nombre": "UN", "alcalde": "WALDO ALBARRACIN"},
    {"id": 106, "nombre": "ALIANZA", "alcalde": "CANDIDATO ALIANZA"},
    {"id": 107, "nombre": "AESA", "alcalde": "CANDIDATO AESA"},
    {"id": 108, "nombre": "SÚMATE", "alcalde": "CANDIDATO SÚMATE"},
    {"id": 109, "nombre": "MTS", "alcalde": "RONALD ESCOBAR"},
    {"id": 110, "nombre": "JALLALLA", "alcalde": "DAVID CASTRO"},
    {"id": 111, "nombre": "LIBRE", "alcalde": "FRANKLIN FLORES"},
    {"id": 112, "nombre": "PP", "alcalde": "AMILCAR BARRAL"},
    {"id": 113, "nombre": "SOMOS PUEBLO", "alcalde": "IVAN ARIAS"},
    {"id": 114, "nombre": "JA-HA", "alcalde": "CANDIDATO JA-HA"},
    {"id": 115, "nombre": "PDC", "alcalde": "ANA MARÍA FLORES"}
]

@app.route('/')
def index():
    msg_type = request.args.get('msg_type')
    ci_votante = request.args.get('ci')
    return render_template('index.html', msg_type=msg_type, ci_votante=ci_votante)

@app.route('/votar/<ciudad>')
def votar(ciudad):
    ciudad_upper = ciudad.upper().replace("_", " ")
    # Selección de lista basada en ciudad [cite: 2026-02-04]
    lista = partidos_oruro if "ORURO" in ciudad_upper else partidos_lapaz
    return render_template('votar.html', ciudad=ciudad_upper, partidos=lista)

@app.route('/confirmar_voto', methods=['POST'])
def confirmar_voto():
    ci = request.form.get('ci')
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT ci FROM votos WHERE ci = %s', (ci,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return redirect(url_for('index', msg_type='error', ci=ci))
        
        cur.execute('''INSERT INTO votos (ci, nombres, apellido, edad, genero, celular, partido_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)''', (
            ci,
            request.form.get('nombres').upper(), request.form.get('apellido').upper(), 
            request.form.get('edad'), request.form.get('genero'),
            request.form.get('celular'), request.form.get('partido_id')
        ))
        conn.commit()
        cur.close()
        conn.close()
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

        # Mapeo de votos respetando el orden oficial [cite: 2026-02-11]
        for p in partidos_oruro: p['votos'] = conteos.get(p['id'], 0)
        for p in partidos_lapaz: p['votos'] = conteos.get(p['id'], 0)

        resultados = {"ORURO": partidos_oruro, "LA PAZ": partidos_lapaz}
        return render_template('reporte.html', resultados=resultados)
    except Exception as e:
        return f"Error en Reporte: {str(e)}", 500

if __name__ == '__main__':
    app.run()
