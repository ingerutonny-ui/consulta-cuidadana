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

init_db()

def obtener_partidos_oficiales(ciudad):
    es_lp = "LA PAZ" in ciudad.upper()
    offset = 100 if es_lp else 0
    # Candidatos según papeleta oficial
    return [
        {"id": 1 + offset, "nombre": "FRI", "alcalde": "CANDIDATO FRI"},
        {"id": 2 + offset, "nombre": "LODEL", "alcalde": "CANDIDATO LODEL"},
        {"id": 3 + offset, "nombre": "NGP", "alcalde": "CANDIDATO NGP"},
        {"id": 4 + offset, "nombre": "AORA", "alcalde": "CANDIDATO AORA"},
        {"id": 5 + offset, "nombre": "UN", "alcalde": "WALDO ALBARRACIN" if es_lp else "SAMUEL DORIA MEDINA"},
        {"id": 6 + offset, "nombre": "ALIANZA", "alcalde": "CANDIDATO ALIANZA"},
        {"id": 7 + offset, "nombre": "AESA", "alcalde": "CANDIDATO AESA"},
        {"id": 8 + offset, "nombre": "SÚMATE", "alcalde": "CANDIDATO SÚMATE"},
        {"id": 9 + offset, "nombre": "MTS", "alcalde": "RONALD ESCOBAR" if es_lp else "OLIVER OSCAR POMA CARTAGENA"},
        {"id": 10 + offset, "nombre": "JALLALLA", "alcalde": "DAVID CASTRO"},
        {"id": 11 + offset, "nombre": "LIBRE", "alcalde": "FRANKLIN FLORES" if es_lp else "RENE BENJAMIN GUZMAN VARGAS"},
        {"id": 12 + offset, "nombre": "PP", "alcalde": "AMILCAR BARRAL" if es_lp else "CARLOS AGUILAR"},
        {"id": 13 + offset, "nombre": "SOMOS PUEBLO", "alcalde": "IVAN ARIAS" if es_lp else "MARCELO CORTEZ GUTIERREZ"},
        {"id": 14 + offset, "nombre": "JA-HA", "alcalde": "MARCELO FERNANDO MEDINA CENTELLAS"},
        {"id": 15 + offset, "nombre": "PDC", "alcalde": "ANA MARÍA FLORES"}
    ]

@app.route('/')
def index():
    return render_template('index.html', msg_type=request.args.get('msg_type'), ci=request.args.get('ci'))

@app.route('/votar/<ciudad>')
def votar(ciudad):
    c_nom = ciudad.upper().replace("_", " ")
    return render_template('votar.html', ciudad=c_nom, partidos=obtener_partidos_oficiales(c_nom))

@app.route('/confirmar_voto', methods=['POST'])
def confirmar_voto():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO votos (ci, nombres, apellido, edad, genero, celular, partido_id) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)''', 
                    (request.form['ci'], request.form['nombres'].upper(), request.form['apellido'].upper(), 
                     request.form['edad'], request.form['genero'], request.form['celular'], request.form['partido_id']))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index', msg_type='success', ci=request.form['ci']))
    except:
        return redirect(url_for('index', msg_type='error', ci=request.form['ci']))

@app.route('/reporte')
def reporte():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT partido_id, COUNT(*) FROM votos GROUP BY partido_id')
        conteos = dict(cur.fetchall())
        cur.close()
        conn.close()
        res = {}
        for c in ["ORURO", "LA PAZ"]:
            lista = obtener_partidos_oficiales(c)
            for p in lista: p['votos'] = conteos.get(p['id'], 0)
            res[c] = lista
        return render_template('reporte.html', resultados=res)
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run()
