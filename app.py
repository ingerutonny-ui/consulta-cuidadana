import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuración con corrección de protocolo y SSL forzado para Render
uri = os.environ.get('DATABASE_URL')
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración de argumentos de conexión para evitar el cierre de SSL
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "connect_args": {
        "sslmode": "require"
    }
}

db = SQLAlchemy(app)

# MODELOS
class Votante(db.Model):
    ci = db.Column(db.String(20), primary_key=True)
    ciudad = db.Column(db.String(50))
    ya_voto = db.Column(db.Boolean, default=False)
    fecha_voto = db.Column(db.DateTime, default=datetime.utcnow)

class Partido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    alcalde = db.Column(db.String(100), nullable=False)
    concejal = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(50), nullable=False)
    votos_alcalde = db.Column(db.Integer, default=0)
    votos_concejal = db.Column(db.Integer, default=0)

@app.route('/')
def index():
    try:
        # Lógica de base de datos
        db.drop_all() 
        db.create_all()
        
        partidos_lista = []
        ciudades = ["ORURO", "LA PAZ"]
        
        for ciudad in ciudades:
            for i in range(1, 16):
                partidos_lista.append(
                    Partido(
                        nombre=f"PARTIDO {i}", 
                        alcalde=f"Candidato {i}", 
                        concejal=f"Concejal {i}",
                        ciudad=ciudad
                    )
                )
        
        db.session.bulk_save_objects(partidos_lista)
        db.session.commit()
        
        # Parámetros para el Frontend
        github_user = "ingerutonny-ui"
        mensaje = "Base de datos reseteada y partidos cargados correctamente."
        
        return render_template('index.html', mensaje=mensaje, github_user=github_user)
        
    except Exception as e:
        return f"Error en el sistema: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
