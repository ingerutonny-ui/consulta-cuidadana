import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'consulta_ciudadana_2026'

# Limpieza de caché
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response

uri = os.environ.get('DATABASE_URL')
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    partidos = Partido.query.filter_by(ciudad=ciudad.upper()).all()
    return render_template('votar.html', ciudad=ciudad.upper(), partidos=partidos)

@app.route('/confirmar_voto', methods=['POST'])
def confirmar_voto():
    # FORZADO DE MAYÚSCULAS DESDE EL SERVIDOR
    ci = request.form.get('ci', '').strip().upper()
    nombres = request.form.get('nombres', '').strip().upper()
    apellido = request.form.get('apellido', '').strip().upper()
    
    # VALIDACIÓN DE DUPLICADOS ANTES DE GUARDAR
    existe = Voto.query.filter_by(ci=ci).first()
    if existe:
        return render_template('index.html', msg_type="error", ci_votante=ci)

    try:
        nuevo = Voto(
            ci=ci, nombres=nombres, apellido=apellido,
            celular=request.form.get('celular'),
            genero=request.form.get('genero').upper(),
            edad=request.form.get('edad'),
            partido_id=request.form.get('partido_id')
        )
        db.session.add(nuevo)
        db.session.commit()
        return render_template('index.html', msg_type="success", ci_votante=ci)
    except Exception:
        db.session.rollback()
        # Si falla por integridad (duplicado no detectado antes), mostramos error
        return render_template('index.html', msg_type="error", ci_votante=ci)

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
