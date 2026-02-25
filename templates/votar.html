import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'consulta_ciudadana_secret'

# --- CONFIGURACIÓN DB ---
uri = os.environ.get('DATABASE_URL')
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"connect_args": {"sslmode": "prefer"}}

db = SQLAlchemy(app)

# --- MODELOS ---
class Votante(db.Model):
    ci = db.Column(db.String(20), primary_key=True)
    ciudad = db.Column(db.String(50))
    ya_voto = db.Column(db.Boolean, default=False)

class Partido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    alcalde = db.Column(db.String(100), nullable=False)
    concejal = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(50), nullable=False)
    votos_alcalde = db.Column(db.Integer, default=0)

@app.route('/')
def index():
    try:
        db.create_all()
        # Aquí ya están cargados los 15 de Oruro y 17 de La Paz según los chats anteriores
        return render_template('index.html', mensaje="SISTEMA LISTO")
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/votar/<ciudad>')
def votar(ciudad):
    partidos = Partido.query.filter_by(ciudad=ciudad).order_by(Partido.id).all()
    # PREFIJO AUTOMÁTICO: OR para Oruro, LP para La Paz
    prefijo = "OR" if ciudad == "ORURO" else "LP"
    return render_template('votar.html', ciudad=ciudad, partidos=partidos, prefijo=prefijo)

@app.route('/confirmar_voto', methods=['POST'])
def confirmar_voto():
    p = Partido.query.get(request.form.get('partido_id'))
    return render_template('confirmar.html', partido=p, ciudad=request.form.get('ciudad'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
