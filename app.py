import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# CONEXIÓN A POSTGRESQL EN LA NUBE (RENDER)
def get_db_connection():
    # Render proporciona la DATABASE_URL automáticamente
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    return conn

# LISTA REAL DE CANDIDATOS (IGUAL QUE EL ANTERIOR)
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
    conn = get_db_connection()
    cur = conn.cursor()
    
    # VERIFICACIÓN EN LA BASE DE DATOS REAL
    cur.execute('SELECT ci FROM votos WHERE ci = %s', (ci,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return redirect(url_for('index', msg_type='error', ci=ci))
    
    # INSERCIÓN PERMANENTE (P1, P2, P3 mapeados)
    cur.execute('''
        INSERT INTO votos (ci, nombres, apellido, edad, genero, celular, partido_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (
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
    
    return redirect(url_for('index', msg_type='success', ci=ci))

if __name__ == '__main__':
    app.run(debug=True)
