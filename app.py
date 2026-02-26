import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'consulta_ciudadana_nancy_2026'

# Configuración para Render / PostgreSQL
uri = os.environ.get('DATABASE_URL')
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODELOS
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

def restaurar_datos():
    db.create_all()
    # Mapeo completo: 15 de Oruro y 17 de La Paz
    data = [
        # ORURO (Basado en PDF) [cite: 24, 25, 27, 30, 32, 33, 34, 35, 36, 37, 41, 42, 43, 46]
        {'n': 'FRI', 'a': 'RENE ROBERTO MAMANI LLAVE', 'c': 'ORURO'},
        {'n': 'LEAL', 'a': 'ADEMAR WILLCARANI MORALES', 'c': 'ORURO'},
        {'n': 'NGP', 'a': 'IVÁN QUISPE GUTIÉRREZ', 'c': 'ORURO'},
        {'n': 'AORA', 'a': 'SANTIAGO CONDORI APAZA', 'c': 'ORURO'},
        {'n': 'UN', 'a': 'ENRIQUE FERNANDO URQUIDI DAZA', 'c': 'ORURO'},
        {'n': 'AUPP', 'a': 'JUAN CARLOS CHOQUE ZUBIETA', 'c': 'ORURO'},
        {'n': 'UCS', 'a': 'LINO MARCOS MAIN ADRIÁN', 'c': 'ORURO'},
        {'n': 'SUMATE', 'a': 'OSCAR MIGUEL TOCO CHOQUE', 'c': 'ORURO'},
        {'n': 'MTS', 'a': 'OLIVER OSCAR POMA CARTAGENA', 'c': 'ORURO'},
        {'n': 'PATRIA ORURO', 'a': 'RAFAEL VARGAS VILLEGAS', 'c': 'ORURO'},
        {'n': 'LIBRE', 'a': 'RENE BENJAMIN GUZMAN VARGAS', 'c': 'ORURO'},
        {'n': 'PP', 'a': 'CARLOS AGUILAR', 'c': 'ORURO'},
        {'n': 'SOMOS ORURO', 'a': 'MARCELO CORTEZ GUTIÉRREZ', 'c': 'ORURO'},
        {'n': 'JACHA', 'a': 'MARCELO FERNANDO MEDINA CENTELLAS', 'c': 'ORURO'},
        {'n': 'SOL.BO', 'a': 'MARCELO MEDINA', 'c': 'ORURO'},

        # LA PAZ (17 Candidatos)
        {'n': 'JALLALLA', 'a': 'SANTOS QUISPE', 'c': 'LA PAZ'},
        {'n': 'ASP', 'a': 'XAVIER ITURRALDE', 'c': 'LA PAZ'},
        {'n': 'VENCEREMOS', 'a': 'WALDO ALBARRACIN', 'c': 'LA PAZ'},
        {'n': 'SOMOS LA PAZ', 'a': 'MIGUEL ROCA', 'c': 'LA PAZ'},
        {'n': 'UPC', 'a': 'LUIS EDUARDO SILES', 'c': 'LA PAZ'},
        {'n': 'LIBRE', 'a': 'CARLOS CORDERO', 'c': 'LA PAZ'},
        {'n': 'MTS', 'a': 'FELIX PATZI', 'c': 'LA PAZ'},
        {'n': 'PAN-BOL', 'a': 'AMILCAR BARRAL', 'c': 'LA PAZ'},
        {'n': 'SOL.BO', 'a': 'ALVARO BLONDEL', 'c': 'LA PAZ'},
        {'n': 'UNIDOS', 'a': 'PEDRO SUSZ', 'c': 'LA PAZ'},
        {'n': 'UCS', 'a': 'PETER MALDONADO', 'c': 'LA PAZ'},
        {'n': 'MAS-IPSP', 'a': 'CESAR DOCKWEILER', 'c': 'LA PAZ'},
        {'n': 'PBCSP', 'a': 'IVAN ARIAS', 'c': 'LA PAZ'},
        {'n': 'FPLP', 'a': 'FEDERICO ESCOBAR', 'c': 'LA PAZ'},
        {'n': 'CC-A', 'a': 'RONALD MACLEAN', 'c': 'LA PAZ'},
        {'n': 'MNR', 'a': 'JOSE MANUEL ENCINAS', 'c': 'LA PAZ'},
        {'n': 'APG', 'a': 'GUSTAVO BEJARANO', 'c': 'LA PAZ'}
    ]
    for p in data:
        if not Partido.query.filter_by(nombre=p['n'], ciudad=p['c']).first():
            db.session.add(Partido(nombre=p['n'], alcalde=p['a'], ciudad=p['c']))
    db.session.commit()

@app.route('/')
def index():
    restaurar_datos()
    return render_template('index.html')

@app.route('/votar/<ciudad>')
def votar(ciudad):
    restaurar_datos()
    partidos = Partido.query.filter_by(ciudad=ciudad.upper()).all()
    return render_template('votar.html', ciudad=ciudad.upper(), partidos=partidos)

@app.route('/confirmar_voto', methods=['POST'])
def confirmar_voto():
    ci_f = request.form.get('ci', '').strip().upper()
    if Voto.query.filter_by(ci=ci_f).first():
        return render_template('index.html', msg_type="error", ci_votante=ci_f)
    try:
        nuevo_voto = Voto(
            ci=ci_f,
            nombres=request.form.get('nombres', '').upper(),
            apellido=request.form.get('apellido', '').upper(),
            celular=request.form.get('celular'),
            genero=request.form.get('genero'),
            edad=int(request.form.get('edad')),
            partido_id=int(request.form.get('partido_id'))
        )
        db.session.add(nuevo_voto)
        db.session.commit()
        return render_template('index.html', msg_type="success", ci_votante=ci_f)
    except:
        db.session.rollback()
        return redirect(url_for('index'))

@app.route('/reporte')
def reporte():
    # Esta es la ruta correcta, no uses reporte.html en la URL
    resultados = db.session.query(
        Partido.nombre, 
        Partido.ciudad, 
        db.func.count(Voto.id).label('total')
    ).outerjoin(Voto).group_by(Partido.id).order_by(db.func.count(Voto.id).desc()).all()
    return render_template('reporte.html', resultados=resultados)

if __name__ == '__main__':
    with app.app_context():
        restaurar_datos()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
