import os
from flask import Flask, render_template, request, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text

app = Flask(__name__)

app.secret_key = 'consulta_ciudadana_2026'

# --- LÓGICA DE COMPATIBILIDAD PARA TABLETAS ANTIGUAS ---
@app.after_request
def add_header(response):
    # Obliga al navegador (especialmente en tablets viejas) a no usar cache
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Configuración de Base de Datos para Render
uri = os.environ.get('DATABASE_URL')
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "connect_args": {"sslmode": "prefer"} if uri else {}
}

db = SQLAlchemy(app)

# MODELOS
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
    partido_rel = db.relationship('Partido', backref='votos_recibidos')

# RUTAS
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/votar/<ciudad>')
def votar(ciudad):
    # Forzar creación de tablas y nuevas columnas al entrar a la papeleta
    with app.app_context():
        db.create_all()
        actualizar_schema()
        seed_data()
    partidos = Partido.query.filter_by(ciudad=ciudad.upper()).all()
    return render_template('votar.html', ciudad=ciudad.upper(), partidos=partidos)

@app.route('/confirmar_voto', methods=['POST'])
def confirmar_voto():
    try:
        p_id = request.form.get('partido_id')
        nombres = request.form.get('nombres', '').strip().upper()
        apellido = request.form.get('apellido', '').strip().upper()
        ci = request.form.get('ci', '').strip().upper()
        celular = request.form.get('celular', '').strip()
        genero = request.form.get('genero')
        edad = request.form.get('edad')

        if Voto.query.filter_by(ci=ci).first():
            return render_template('index.html', mensaje=f"EL CI {ci} YA VOTO Y GRACIAS")

        nuevo_voto = Voto(
            ci=ci, nombres=nombres, apellido=apellido, 
            celular=celular, genero=genero, edad=edad, 
            partido_id=p_id
        )
        db.session.add(nuevo_voto)
        db.session.commit()
        return render_template('index.html', mensaje="VOTO REGISTRADO EXITOSAMENTE")
    except Exception as e:
        db.session.rollback()
        # Imprime el error en la consola de Render para monitoreo
        print(f"Error en registro: {str(e)}")
        return render_template('index.html', mensaje="ERROR EN EL REGISTRO")

@app.route('/reporte')
def reporte():
    total = Voto.query.count()
    votos_query = db.session.query(
        Partido.nombre, Partido.ciudad, func.count(Voto.id).label('t')
    ).join(Voto).group_by(Partido.id).all()
    
    resultados = [{
        'nombre': r.nombre, 
        'ciudad': r.ciudad, 
        'total': r.t,
        'porcentaje': round((r.t/total*100), 2) if total > 0 else 0
    } for r in votos_query]
    
    return render_template('reporte.html', resultados=resultados, total_global=total)

def actualizar_schema():
    """Agrega columnas faltantes si la DB ya existía"""
    try:
        # Intentamos añadir las columnas por si la DB es antigua
        db.session.execute(text('ALTER TABLE voto ADD COLUMN nombres VARCHAR(50)'))
        db.session.execute(text('ALTER TABLE voto ADD COLUMN celular VARCHAR(15)'))
        db.session.commit()
    except:
        db.session.rollback()

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
        for d in datos:
            db.session.add(Partido(nombre=d[0], alcalde=d[1], ciudad=d[2]))
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
