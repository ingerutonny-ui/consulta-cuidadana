import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'consulta_ciudadana_secret'

# --- CONFIGURACIÓN DE BASE DE DATOS Y COMPATIBILIDAD ---
uri = os.environ.get('DATABASE_URL')
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# sslmode=prefer para que tu tableta Samsung antigua no dé error de certificado
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"connect_args": {"sslmode": "prefer"}}

db = SQLAlchemy(app)

# --- MODELOS ---
class Votante(db.Model):
    ci = db.Column(db.String(20), primary_key=True)
    ya_voto = db.Column(db.Boolean, default=False)

class Partido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    alcalde = db.Column(db.String(100))
    ciudad = db.Column(db.String(50))

# --- RUTA RAÍZ: REINICIO Y CARGA DE DATOS ---
@app.route('/')
def index():
    try:
        db.drop_all()
        db.create_all()
        
        # AQUÍ CAMBIAS LOS NOMBRES FÁCILMENTE
        datos_oruro = [
            ["FRI", "Rene Roberto Mamani Llave"], ["LEAL", "Adhemar Willcarani Morales"],
            ["NGP", "Iván Quispe Gutiérrez"], ["AORA", "Santiago Condori Apaza"],
            ["UN", "Enrique Fernando Urquidi Daza"], ["AUPP", "Juan Carlos Choque Zubieta"],
            ["UCS", "Lino Marcos Main Adrián"], ["BST", "Edgar Rafael Bazán Ortega"],
            ["SUMATE", "Oscar Miguel Toco Choque"], ["MTS", "Oliver Oscar Poma Cartagena"],
            ["PATRIA", "Rafael Vargas Villegas"], ["LIBRE", "Rene Benjamin Guzman Vargas"],
            ["PP", "Carlos Aguilar"], ["SOMOS ORURO", "Marcelo Cortez Gutiérrez"],
            ["JACHA", "Marcelo Fernando Medina Centellas"]
        ]

        datos_lapaz = [
            ["Jallalla", "Jhonny Plata"], ["ASP", "Xavier Iturralde"],
            ["Venceremos", "Waldo Albarracín"], ["Somos La Paz", "Miguel Roca"],
            ["UPC", "Luis Eduardo Siles"], ["Libre", "Carlos Palenque"],
            ["A-UPP", "Isaac Fernández"], ["Innovación Humana", "César Dockweiler"],
            ["VIDA", "Fernando Valencia"], ["FRI", "Raúl Daza"],
            ["PDC", "Mario Silva"], ["MTS", "Jorge Dulon"],
            ["NGP", "Hernán Rodrigo Rivera"], ["MPS", "Ricardo Cuevas"],
            ["APB-Súmate", "Óscar Sogliano"], ["Alianza Patria", "Carlos Nemo Rivera"],
            ["Suma por el Bien Común", "Iván Arias"]
        ]

        objetos = []
        for d in datos_oruro: objetos.append(Partido(nombre=d[0], alcalde=d[1], ciudad="ORURO"))
        for d in datos_lapaz: objetos.append(Partido(nombre=d[0], alcalde=d[1], ciudad="LA PAZ"))
        
        db.session.bulk_save_objects(objetos)
        db.session.commit()
        return render_template('index.html', mensaje="SISTEMA LISTO Y CARGADO")
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/votar/<ciudad>')
def votar(ciudad):
    partidos = Partido.query.filter_by(ciudad=ciudad).order_by(Partido.id).all()
    prefijo = "OR" if ciudad == "ORURO" else "LP"
    return render_template('votar.html', ciudad=ciudad, partidos=partidos, prefijo=prefijo)

@app.route('/confirmar_voto', methods=['POST'])
def confirmar_voto():
    p = Partido.query.get(request.form.get('partido_id'))
    return render_template('confirmar.html', partido=p, ciudad=request.form.get('ciudad'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
