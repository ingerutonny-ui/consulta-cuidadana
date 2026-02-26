import os
import psycopg2
import requests
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

def enviar_whatsapp(numero, ci):
    url = "https://api.ultramsg.com/instance163345/messages/chat"
    mensaje = (
        f"✅ *VOTO REGISTRADO EXITOSAMENTE*\n\n"
        f"Se ha confirmado su participación con el CI: *{ci}*.\n"
        f"Gracias por ser parte de la Consulta Ciudadana."
    )
    payload = {
        "token": "rmcd9oavsczcgdg4",
        "to": f"+591{numero}",
        "body": mensaje
    }
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    try:
        requests.post(url, data=payload, headers=headers, timeout=5)
    except:
        pass

def obtener_partidos(ciudad):
    ciudad_upper = ciudad.upper()
    if "LA PAZ" in ciudad_upper:
        # LISTA CORREGIDA SEGÚN TABLA OFICIAL (image_515168.png)
        return [
            {"id": 101, "nombre": "JALLALLA", "alcalde": "JHONNY PLATA"},
            {"id": 102, "nombre": "ASP", "alcalde": "XAVIER ITURRALDE"},
            {"id": 103, "nombre": "VENCEREMOS", "alcalde": "WALDO ALBARRACÍN"},
            {"id": 104, "nombre": "SOMOS LA PAZ", "alcalde": "MIGUEL ROCA"},
            {"id": 105, "nombre": "UPC", "alcalde": "LUIS EDUARDO SILES"},
            {"id": 106, "nombre": "LIBRE", "alcalde": "CARLOS PALENQUE"},
            {"id": 107, "nombre": "A-UPP", "alcalde": "ISAAC FERNÁNDEZ"},
            {"id": 108, "nombre": "INNOVACIÓN HUMANA", "alcalde": "CÉSAR DOCKWEILER"},
            {"id": 109, "nombre": "VIDA", "alcalde": "FERNANDO VALENCIA"},
            {"id": 110, "nombre": "FRI", "alcalde": "RAÚL DAZA"},
            {"id": 111, "nombre": "PDC", "alcalde": "MARIO SILVA"},
            {"id": 112, "nombre": "MTS", "alcalde": "JORGE DULON"},
            {"id": 113, "nombre": "NGP", "alcalde": "HERNÁN RODRIGO RIVERA"},
            {"id": 114, "nombre": "MPS", "alcalde": "RICARDO CUEVAS"},
            {"id": 115, "nombre": "APB-SÚMATE", "alcalde": "ÓSCAR SOGLIANO"},
            {"id": 116, "nombre": "ALIANZA PATRIA", "alcalde": "CARLOS NEMO RIVERA"},
            {"id": 117, "nombre": "SUMA POR EL BIEN COMÚN", "alcalde": "IVÁN ARIAS"}
        ]
    else:
        # LISTA ORURO (MANTENIENDO INTEGRIDAD)
        return [
            {"id": 1, "nombre": "FRI", "alcalde": "RENE ROBERTO MAMANI LLAVE"},
            {"id": 2, "nombre": "LEAL", "alcalde": "ADEMAR WILLCARANI MORALES"},
            {"id": 3, "nombre": "NGP", "alcalde": "IVAN QUISPE GUTIERREZ"},
            {"id": 4, "nombre": "AORA", "alcalde": "SANTIAGO CONDORI APAZA"},
            {"id": 5, "nombre": "UN", "alcalde": "ENRIQUE FERNANDO"},
            {"id": 6, "nombre": "AUPP", "alcalde": "JUAN CARLOS CHOQUE ZUBIETA"},
            {"id": 7, "nombre": "UCS", "alcalde": "LINO MARCOS MAIN"},
            {"id": 9, "nombre": "SÚMATE", "alcalde": "OSCAR MIGUEL TOCO CHOQUE"},
            {"id": 10, "nombre": "MTS", "alcalde": "OLIVER OSCAR POMA CARTAGENA"},
            {"id": 11, "nombre": "ALIANZA PATRIA ORURO", "alcalde": "RAFAEL VARGAS VILLEGAS"},
            {"id": 12, "nombre": "LIBRE", "alcalde": "RENE BENJAMIN GUZMAN VARGAS"},
            {"id": 13, "nombre": "PP", "alcalde": "CARLOS AGUILAR"},
            {"id": 14, "nombre": "SOMOS ORURO", "alcalde": "MARCELO CORTEZ GUTIERREZ"},
            {"id": 15, "nombre": "JA-HA", "alcalde": "MARCELO FERNANDO MEDINA"}
        ]

@app.route('/')
def index():
    return render_template('index.html', msg_type=request.args.get('msg_type'), ci_votante=request.args.get('ci'))

@app.route('/votar/<ciudad>')
def votar(ciudad):
    c_nom = ciudad.upper().replace("_", " ")
    return render_template('votar.html', ciudad=c_nom, partidos=obtener_partidos(c_nom))

@app.route('/confirmar_voto', methods=['POST'])
def confirmar_voto():
    ci = request.form['ci']
    celular = request.form['celular']
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT ci FROM votos WHERE ci = %s", (ci,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return redirect(url_for('index', msg_type='error', ci=ci))
        
        cur.execute('''INSERT INTO votos (ci, nombres, apellido, edad, genero, celular, partido_id) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)''', 
                    (ci, request.form['nombres'].upper(), request.form['apellido'].upper(), 
                     request.form['edad'], request.form['genero'], celular, request.form['partido_id']))
        conn.commit()
        cur.close()
        conn.close()

        enviar_whatsapp(celular, ci)
        return redirect(url_for('index', msg_type='success', ci=ci))
    except:
        return redirect(url_for('index', msg_type='error', ci=ci))

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
        totales = {}
        for ciudad in ["ORURO", "LA PAZ"]:
            lista = obtener_partidos(ciudad)
            suma = 0
            for p in lista:
                p['votos'] = conteos.get(p['id'], 0)
                suma += p['votos']
            res[ciudad] = lista
            totales[ciudad] = suma
        return render_template('reporte.html', resultados=res, totales=totales)
    except:
        return "Error en reporte", 500

if __name__ == '__main__':
    app.run()
