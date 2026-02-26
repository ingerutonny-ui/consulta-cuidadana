from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# BASE DE DATOS COMPLETA SIN ERRORES
partidos = [
    # CANDIDATOS ORURO
    {"id": 1, "nombre": "MTS", "alcalde": "OLIVER OSCAR POMA CARTAGENA", "ciudad": "ORURO", "votos": 0},
    {"id": 2, "nombre": "PATRIA ORURO", "alcalde": "RAFAEL VARGAS VILLEGAS", "ciudad": "ORURO", "votos": 0},
    {"id": 3, "nombre": "LIBRE", "alcalde": "RENE BENJAMIN GUZMAN VARGAS", "ciudad": "ORURO", "votos": 0},
    {"id": 4, "nombre": "PP", "alcalde": "CARLOS AGUILAR", "ciudad": "ORURO", "votos": 0},
    {"id": 5, "nombre": "SOMOS ORURO", "alcalde": "MARCELO CORTEZ GUTIERREZ", "ciudad": "ORURO", "votos": 0},
    {"id": 6, "nombre": "JACHA", "alcalde": "MARCELO FERNANDO MEDINA CENTELLAS", "ciudad": "ORURO", "votos": 0},
    {"id": 7, "nombre": "SOL.BO", "alcalde": "MARCELO MEDINA", "ciudad": "ORURO", "votos": 0},
    
    # CANDIDATOS LA PAZ
    {"id": 8, "nombre": "UN", "alcalde": "SAMUEL DORIA MEDINA", "ciudad": "LA PAZ", "votos": 0},
    {"id": 9, "nombre": "MAS-IPSP", "alcalde": "CESAR DOCKWEILER", "ciudad": "LA PAZ", "votos": 0},
    {"id": 10, "nombre": "PBCP", "alcalde": "IVAN ARIAS", "ciudad": "LA PAZ", "votos": 0},
    {"id": 11, "nombre": "SOL.BO", "alcalde": "ALVARO BLONDEL", "ciudad": "LA PAZ", "votos": 0},
    {"id": 12, "nombre": "PAN-BOL", "alcalde": "AMILCAR BARAL", "ciudad": "LA PAZ", "votos": 0}
]

votos_registrados = []

@app.route('/')
def index():
    msg_type = request.args.get('msg_type')
    ci = request.args.get('ci')
    return render_template('index.html', msg_type=msg_type, ci_votante=ci)

@app.route('/votar/<ciudad>')
def votar(ciudad):
    p_ciudad = [p for p in partidos if p['ciudad'] == ciudad]
    return render_template('votar.html', ciudad=ciudad, partidos=p_ciudad)

@app.route('/confirmar_voto', methods=['POST'])
def confirmar_voto():
    ci = request.form.get('ci').strip()
    p_id = int(request.form.get('partido_id'))
    if any(v['ci'] == ci for v in votos_registrados):
        return redirect(url_for('index', msg_type='error', ci=ci))
    votos_registrados.append({'ci': ci, 'partido_id': p_id})
    for p in partidos:
        if p['id'] == p_id:
            p['votos'] += 1
            break
    return redirect(url_for('index', msg_type='success', ci=ci))

@app.route('/reporte')
def reporte():
    resultados = {}
    ciudades = sorted(list(set(p['ciudad'] for p in partidos)))
    for c in ciudades:
        resultados[c] = sorted([p for p in partidos if p['ciudad'] == c], key=lambda x: x['votos'], reverse=True)
    return render_template('reporte.html', resultados=resultados)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
