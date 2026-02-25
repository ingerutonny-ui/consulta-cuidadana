import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'consulta_ciudadana_nancy_2026'

# Configuración de Base de Datos para Render (PostgreSQL)
uri = os.environ.get('DATABASE_URL')
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELOS ---
class Partido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    alcalde = db.Column(db.String(100))
    ciudad = db.Column(db.String(50))

class Voto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ci = db.Column(db.String(20), unique=True, nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    celular = db.Column(db.String(20), nullable=False)
    genero = db.Column(db.String(20), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    partido_id = db.Column(db.Integer, db.ForeignKey('partido.id'), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/votar/<ciudad>')
def votar(ciudad):
    # Forzamos creación de tablas en cada entrada para asegurar sincronización en Render
    db.create_all()
    partidos = Partido.query.filter_by(ciudad=ciudad.upper()).all()
    return render_template('votar.html', ciudad=ciudad.upper(), partidos=partidos)

@app.route('/confirmar_voto', methods=['POST'])
def confirmar_voto():
    # RECOLECCIÓN Y FORZADO DE MAYÚSCULAS
    ci_input = request.form.get('ci', '').strip().upper()
    nom_input = request.form.get('nombres', '').strip().upper()
    ape_input = request.form.get('apellido', '').strip().upper()
    p_id = request.form.get('partido_id')

    # 1. Verificar si el CI ya existe (Evitar Error 500 por duplicado)
    existe = Voto.query.filter_by(ci=ci_input).first()
    if existe:
        return render_template('index.html', msg_type="error", ci_votante=ci_input)

    try:
        # 2. Intentar guardar el voto
        nuevo_voto = Voto(
            ci=ci_input,
            nombres=nom_input,
            apellido=ape_input,
            celular=request.form.get('celular'),
            genero=request.form.get('genero', '').upper(),
            edad=int(request.form.get('edad', 0)),
            partido_id=int(p_id)
        )
        db.session.add(nuevo_voto)
        db.session.commit()
        return render_template('index.html', msg_type="success", ci_votante=ci_input)
    
    except Exception as e:
        db.session.rollback()
        # Log del error para diagnóstico (se ve en los logs de Render)
        print(f"ERROR AL GUARDAR: {str(e)}")
        # Si algo falla, mostramos el mensaje de error en lugar del 500 del sistema
        return render_template('index.html', msg_type="error", ci_votante=ci_input)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
