import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text

app = Flask(__name__)
app.secret_key = 'consulta_ciudadana_2026'

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response

uri = os.environ.get('DATABASE_URL')
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}

db = SQLAlchemy(app)

class Partido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    alcalde = db.Column(db.String(100))
    ciudad = db.Column(db.String(50))

class Voto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ci = db.Column(db.String(15), unique=True, nullable=False)
    nombres = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    celular = db.Column(db.String(15), nullable=False)
    genero = db.Column(db.String(15), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    partido_id = db.Column(db.Integer, db.ForeignKey('partido.id'), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/votar/<ciudad>')
def votar(ciudad):
    with app.app_context():
        db.create_all()
        seed_data()
    partidos = Partido.query.filter_by(ciudad=ciudad.upper()).all()
    return render_template('votar.html', ciudad=ciudad.upper(), partidos=partidos)

@app.route('/confirmar_voto', methods=['POST'])
def confirmar_voto():
    ci = request.form.get('ci', '').strip().upper()
    nombres = request.form.get('nombres', '').strip().upper()
    
    existe = Voto.query.filter_by(ci=ci).first()
    if existe:
        return render_template('index.html', msg_type="error", ci_votante=ci)

    try:
        nuevo = Voto(
            ci=ci, nombres=nombres, 
            apellido=request.form.get('apellido', '').upper(),
            celular=request.form.get('celular'),
            genero=request.form.get('genero'),
            edad=request.form.get('edad'),
            partido_id=request.form.get('partido_id')
        )
        db.session.add(nuevo)
        db.session.commit()
        return render_template('index.html', msg_type="success", ci_votante=ci)
    except Exception as e:
        db.session.rollback()
        return render_template('index.html', mensaje="ERROR AL PROCESAR")

def seed_data():
    if not Partido.query.first():
        datos = [
            ["FRI", "Rene Roberto Mamani", "ORURO"], ["LEAL", "Ademar Willcarani", "ORURO"],
            ["NGP", "Iván Quispe", "ORURO"], ["AORA", "Santiago Condori", "ORURO"],
            ["UN", "Enrique Urquidi", "ORURO"], ["AUPP", "Juan Carlos Choque", "ORURO"],
            ["UCS", "Lino Marcos Main", "ORURO"], ["BST", "Edgar Rafael Bazán", "ORURO"],
            ["SUMATE", "Oscar Miguel Toco", "ORURO"], ["MTS", "Oliver Oscar Poma", "ORURO"],
            ["PATRIA", "Rafael Vargas", "ORURO"], ["LIBRE", "Rene Benjamin Guzman", "ORURO"],
            ["PP", "Carlos Aguilar", "ORURO"], ["SOMOS ORURO", "Marcelo Cortez", "ORURO"],
            ["JACHA", "Marcelo Medina", "ORURO"],
            ["Jallalla", "Jhonny Plata", "LA PAZ"], ["ASP", "Xavier Iturralde", "LA PAZ"],
            ["Venceremos", "Waldo Albarracín", "LA PAZ"], ["Somos La Paz", "Miguel Roca", "LA PAZ"],
            ["UPC", "Luis Eduardo Siles", "LA PAZ"], ["Libre", "Carlos Palenque", "LA PAZ"],
            ["A-UPP", "Isaac Fernández", "LA PAZ"], ["Innovación Humana", "César Dockweiler", "LA PAZ"],
            ["VIDA", "Fernando Valencia", "LA PAZ"], ["FRI", "Raúl Daza", "LA PAZ"],
            ["PDC", "Mario Silva", "LA PAZ"], ["MTS", "Jorge Dulon", "LA PAZ"],
            ["NGP", "Hernán Rivera", "LA PAZ"], ["MPS", "Ricardo Cuevas", "LA PAZ"],
            ["APB-Súmate", "Óscar Sogliano", "LA PAZ"], ["Alianza Patria", "Carlos Rivera", "LA PAZ"],
            ["Suma por el Bien Común", "Iván Arias", "LA PAZ"]
        ]
        for d in datos: db.session.add(Partido(nombre=d[0], alcalde=d[1], ciudad=d[2]))
        db.session.commit()

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
