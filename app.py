import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'consulta_ciudadana_nancy_2026'

uri = os.environ.get('DATABASE_URL')
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODELOS DEFINITIVOS
class Partido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    alcalde = db.Column(db.String(100))
    ciudad = db.Column(db.String(50))

class Voto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ci = db.Column(db.String(30), unique=True, nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    celular = db.Column(db.String(20), nullable=False)
    genero = db.Column(db.String(20), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    partido_id = db.Column(db.Integer, db.ForeignKey('partido.id'), nullable=False)

# ESTO ROMPE EL BUCLE: LIMPIEZA TOTAL AL ARRANCAR
with app.app_context():
    db.drop_all() 
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/votar/<ciudad>')
def votar(ciudad):
    partidos = Partido.query.filter_by(ciudad=ciudad.upper()).all()
    return render_template('votar.html', ciudad=ciudad.upper(), partidos=partidos)

@app.route('/confirmar_voto', methods=['POST'])
def confirmar_voto():
    try:
        ci_f = request.form.get('ci', '').strip().upper()
        # Verificar duplicado para no morir en el intento
        if Voto.query.filter_by(ci=ci_f).first():
            return render_template('index.html', msg_type="error", ci_votante=ci_f)

        nuevo = Voto(
            ci=ci_f,
            nombres=request.form.get('nombres', '').strip().upper(),
            apellido=request.form.get('apellido', '').strip().upper(),
            celular=request.form.get('celular'),
            genero=request.form.get('genero', '').upper(),
            edad=int(request.form.get('edad')),
            partido_id=int(request.form.get('partido_id'))
        )
        db.session.add(nuevo)
        db.session.commit()
        return render_template('index.html', msg_type="success", ci_votante=ci_f)
    except Exception as e:
        db.session.rollback()
        return render_template('index.html', msg_type="error", ci_votante="SISTEMA")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
