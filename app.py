import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuración con corrección de protocolo para Render
uri = os.environ.get('DATABASE_URL')
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODELOS
class Votante(db.Model):
    ci = db.Column(db.String(20), primary_key=True)
    ya_voto = db.Column(db.Boolean, default=False)
    fecha_voto = db.Column(db.DateTime, default=datetime.utcnow)

class Partido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    alcalde = db.Column(db.String(100), nullable=False)
    concejal = db.Column(db.String(100), nullable=False)
    votos_alcalde = db.Column(db.Integer, default=0)
    votos_concejal = db.Column(db.Integer, default=0)

@app.route('/')
def index():
    try:
        db.create_all()
        # Verificar si ya hay partidos para no duplicar datos
        if Partido.query.count() == 0:
            partidos_lista = [
                Partido(nombre="PARTIDO 1", alcalde="Alcalde 1", concejal="Concejal 1"),
                Partido(nombre="PARTIDO 2", alcalde="Alcalde 2", concejal="Concejal 2"),
                Partido(nombre="PARTIDO 3", alcalde="Alcalde 3", concejal="Concejal 3"),
                Partido(nombre="PARTIDO 4", alcalde="Alcalde 4", concejal="Concejal 4"),
                Partido(nombre="PARTIDO 5", alcalde="Alcalde 5", concejal="Concejal 5"),
                Partido(nombre="PARTIDO 6", alcalde="Alcalde 6", concejal="Concejal 6"),
                Partido(nombre="PARTIDO 7", alcalde="Alcalde 7", concejal="Concejal 7"),
                Partido(nombre="PARTIDO 8", alcalde="Alcalde 8", concejal="Concejal 8"),
                Partido(nombre="PARTIDO 9", alcalde="Alcalde 9", concejal="Concejal 9"),
                Partido(nombre="PARTIDO 10", alcalde="Alcalde 10", concejal="Concejal 10"),
                Partido(nombre="PARTIDO 11", alcalde="Alcalde 11", concejal="Concejal 11"),
                Partido(nombre="PARTIDO 12", alcalde="Alcalde 12", concejal="Concejal 12"),
                Partido(nombre="PARTIDO 13", alcalde="Alcalde 13", concejal="Concejal 13"),
                Partido(nombre="PARTIDO 14", alcalde="Alcalde 14", concejal="Concejal 14"),
                Partido(nombre="PARTIDO 15", alcalde="Alcalde 15", concejal="Concejal 15")
            ]
            db.session.bulk_save_objects(partidos_lista)
            db.session.commit()
            return "BASE DE DATOS LISTA: Tablas creadas y 15 partidos cargados."
        return "SISTEMA OPERATIVO: Los datos ya existen en la base de datos."
    except Exception as e:
        return f"Error en el sistema: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
