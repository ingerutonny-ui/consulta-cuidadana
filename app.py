import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuración de la base de datos desde la variable de entorno
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de prueba para verificar la conexión
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)

@app.route('/')
def home():
    try:
        # Intenta crear las tablas si no existen para probar conexión
        db.create_all()
        return "Servidor VOTO ONLINE activo y conectado a PostgreSQL."
    except Exception as e:
        return f"Error de conexión: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
