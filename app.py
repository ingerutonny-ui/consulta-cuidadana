import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'consulta_ciudadana_2026'

# Configuración de Base de Datos para Render
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

@app.route('/')
def index():
    try:
        db.drop_all()
        db.create_all()
        
        # 15 CANDIDATOS ORURO
        oruro = [
            ["FRI", "Rene Roberto Mamani"], ["LEAL", "Ademar Willcarani"], ["NGP", "Iván Quispe"],
            ["AORA", "Santiago Condori"], ["UN", "Enrique Urquidi"], ["AUPP", "Juan Carlos Choque"],
            ["UCS", "Lino Marcos Main"], ["BST", "Edgar Rafael Bazán"], ["SUMATE", "Oscar Miguel Toco"],
            ["MTS", "Oliver Oscar Poma"], ["PATRIA", "Rafael Vargas"], ["LIBRE", "Rene Benjamin Guzman"],
            ["PP", "Carlos Aguilar"], ["SOMOS ORURO", "Marcelo Cortez"], ["JACHA", "Marcelo Medina"]
        ]
        
        # 17 CANDIDATOS LA PAZ
        lapaz = [
            ["Jallalla", "Jhonny Plata"], ["ASP", "Xavier Iturralde"], ["Venceremos", "Waldo Albarracín"],
            ["Somos La Paz", "Miguel Roca"], ["UPC", "Luis Eduardo Siles"], ["Libre", "Carlos Palenque"],
            ["A-UPP", "Isaac Fernández"], ["Innovación Humana", "César Dockweiler"], ["VIDA", "Fernando Valencia"],
            ["FRI", "Raúl Daza"], ["PDC", "Mario Silva"], ["MTS", "Jorge Dulon"], ["NGP", "Hernán Rivera"],
            ["MPS", "Ricardo Cuevas"], ["APB-Súmate", "Óscar Sogliano"], ["Alianza Patria", "Carlos Rivera"],
            ["Suma por el Bien Común", "Iván Arias"]
        ]

        objetos = []
        for d in oruro: objetos.append(Partido(nombre=d[0], alcalde=d[1], ciudad="ORURO"))
        for d in lapaz: objetos.append(Partido(nombre=d[0], alcalde=d[1], ciudad="LA PAZ"))
        
        db.session.bulk_save_objects(objetos)
        db.session.commit()
        return render_template('index.html')
    except Exception as e:
        return f"Error Crítico: {str(e)}"

@app.route('/votar/<ciudad>')
def votar(ciudad):
    ciudad_upper = ciudad.upper()
    partidos = Partido.query.filter_by(ciudad=ciudad_upper).all()
    # Prefijo para las imágenes (OR o LP)
    prefijo = "OR" if ciudad_upper == "ORURO" else "LP"
    return render_template('votar.html', ciudad=ciudad_upper, partidos=partidos, prefijo=prefijo)

@app.route('/confirmar_voto', methods=['POST'])
def confirmar_voto():
    p_id = request.form.get('partido_id')
    partido = Partido.query.get(p_id)
    return render_template('confirmar.html', partido=partido)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
