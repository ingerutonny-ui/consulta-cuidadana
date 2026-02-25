import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'consulta_ciudadana_secret'

# --- CONFIGURACIÓN DE BASE DE DATOS ---
uri = os.environ.get('DATABASE_URL')
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CORRECCIÓN PARA TABLETA: Cambiamos 'require' por 'prefer' para permitir navegadores antiguos
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "connect_args": {
        "sslmode": "prefer"
    }
}

db = SQLAlchemy(app)

# --- MODELOS ---
class Votante(db.Model):
    ci = db.Column(db.String(20), primary_key=True)
    ciudad = db.Column(db.String(50))
    ya_voto = db.Column(db.Boolean, default=False)
    fecha_voto = db.Column(db.DateTime, default=datetime.utcnow)

class Partido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    alcalde = db.Column(db.String(100), nullable=False)
    concejal = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(50), nullable=False)
    votos_alcalde = db.Column(db.Integer, default=0)
    votos_concejal = db.Column(db.Integer, default=0)

# --- RUTAS ---
@app.route('/')
def index():
    try:
        db.create_all()
        if not Partido.query.first():
            partidos_lista = []
            ciudades = ["ORURO", "LA PAZ"]
            for ciudad in ciudades:
                for i in range(1, 16):
                    partidos_lista.append(Partido(
                        nombre=f"PARTIDO {i}", 
                        alcalde=f"Candidato {i}", 
                        concejal=f"Concejal {i}", 
                        ciudad=ciudad
                    ))
            db.session.bulk_save_objects(partidos_lista)
            db.session.commit()
        
        return render_template('index.html', mensaje="SISTEMA INICIALIZADO - ELIJA SU CIUDAD")
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/votar/<ciudad>')
def votar(ciudad):
    partidos = Partido.query.filter_by(ciudad=ciudad).all()
    return render_template('votar.html', ciudad=ciudad, partidos=partidos)

@app.route('/confirmar_voto', methods=['POST'])
def confirmar_voto():
    partido_id = request.form.get('partido_id')
    ciudad = request.form.get('ciudad')
    partido = Partido.query.get(partido_id)
    return render_template('confirmar.html', partido=partido, ciudad=ciudad)

@app.route('/registrar_voto', methods=['POST'])
def registrar_voto():
    ci = request.form.get('ci')
    partido_id = request.form.get('partido_id')
    
    votante = Votante.query.get(ci)
    if votante and votante.ya_voto:
        return render_template('error.html', mensaje="Usted ya emitió su voto.")
    
    if not votante:
        votante = Votante(ci=ci, ya_voto=True)
        db.session.add(votante)
    else:
        votante.ya_voto = True
        
    partido = Partido.query.get(partido_id)
    partido.votos_alcalde += 1
    partido.votos_concejal += 1
    
    db.session.commit()
    return render_template('exito.html')

if __name__ == '__main__':
    # Configuración de puerto dinámica para Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
