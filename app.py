import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'consulta_ciudadana_2026'

uri = os.environ.get('DATABASE_URL')
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"connect_args": {"sslmode": "prefer"}}

db = SQLAlchemy(app)

class Partido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    alcalde = db.Column(db.String(100))
    ciudad = db.Column(db.String(50))

# EJECUCIÓN ÚNICA AL ARRANCAR PARA EVITAR TIMEOUT
with app.app_context():
    db.create_all()
    if not Partido.query.first():
        datos = [
            ["FRI", "Rene Roberto Mamani", "ORURO"], ["LEAL", "Ademar Willcarani", "ORURO"],
            ["NGP", "Iván Quispe", "ORURO"], ["AORA", "Santiago Condori", "ORURO"],
            ["UN", "Enrique Urquidi", "ORURO"], ["AUPP", "Juan Carlos Choque", "ORURO"],
            ["UCS", "Lino Marcos Main", "ORURO"], ["BST", "Edgar Rafael Bazán", "ORURO"],
            ["SUMATE", "Oscar Miguel Toco", "ORURO"], ["MTS", "Oliver Oscar Poma", "ORURO"],
            ["PATRIA", "Rafael Vargas", "ORURO"], ["LIBRE", "Rene Benjamin Guzman", "ORURO"],
            ["PP", "Carlos Aguilar", "ORURO"], ["SOMOS ORURO", "Marcelo Cortez", "ORURO"],
            ["JACHA", "Marcelo Medina", "ORURO"], ["Jallalla", "Jhonny Plata", "LA PAZ"],
            ["ASP", "Xavier Iturralde", "LA PAZ"], ["Venceremos", "Waldo Albarracín", "LA PAZ"],
            ["Somos La Paz", "Miguel Roca", "LA PAZ"], ["UPC", "Luis Eduardo Siles", "LA PAZ"],
            ["Libre", "Carlos Palenque", "LA PAZ"], ["A-UPP", "Isaac Fernández", "LA PAZ"],
            ["Innovación Humana", "César Dockweiler", "LA PAZ"], ["VIDA", "Fernando Valencia", "LA PAZ"],
            ["FRI", "Raúl Daza", "LA PAZ"], ["PDC", "Mario Silva", "LA PAZ"],
            ["MTS", "Jorge Dulon", "LA PAZ"], ["NGP", "Hernán Rivera", "LA PAZ"],
            ["MPS", "Ricardo Cuevas", "LA PAZ"], ["APB-Súmate", "Óscar Sogliano", "LA PAZ"],
            ["Alianza Patria", "Carlos Rivera", "LA PAZ"], ["Suma por el Bien Común", "Iván Arias", "LA PAZ"]
        ]
        for d in datos:
            db.session.add(Partido(nombre=d[0], alcalde=d[1], ciudad=d[2]))
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html', mensaje="SISTEMA LISTO")

@app.route('/votar/<ciudad>')
def votar(ciudad):
    partidos = Partido.query.filter_by(ciudad=ciudad.upper()).all()
    return render_template('votar.html', ciudad=ciudad.upper(), partidos=partidos)

@app.route('/confirmar_voto', methods=['POST'])
def confirmar_voto():
    p_id = request.form.get('partido_id')
    partido = Partido.query.get(p_id)
    return f"VOTO REGISTRADO: {partido.nombre}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
