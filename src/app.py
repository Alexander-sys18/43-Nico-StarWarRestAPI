import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planeta, Personaje, Favorito 

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/people', methods=['GET'])
def listar_personajes():
    personajes = Personaje.query.all()
    personajes_serializados = [p.serialize() for p in personajes]
    return jsonify(personajes_serializados), 200

@app.route('/people/<int:personaje_id>', methods=['GET'])
def obtener_personaje(personaje_id):
    personaje = Personaje.query.get(personaje_id)
    if personaje is None:
        return jsonify({"message": "Personaje no encontrado"}), 404
    return jsonify(personaje.serialize()), 200

@app.route('/planets', methods=['GET'])
def listar_planetas():
    planetas = Planeta.query.all()
    planetas_serializados = [p.serialize() for p in planetas]
    return jsonify(planetas_serializados), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def obtener_planeta(planet_id):
    planeta = Planeta.query.get(planet_id)
    if planeta is None:
        return jsonify({"message": "Planeta no encontrado"}), 404
    return jsonify(planeta.serialize()), 200

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_serialized = [{"id": user.id, "username": user.username} for user in users]
    return jsonify(users_serialized)

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    
    return jsonify({"favorites": []})  # Debes implementar esta lógica

# @app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
# def add_favorite_planet(planet_id):
#     
#     return jsonify({"message": "Favorite planet added"})

# @app.route('/favorite/people/<int:people_id>', methods=['POST'])
# def add_favorite_people(people_id):
#  
#     return jsonify({"message": "Favorite people added"})

# @app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
# def remove_favorite_planet(planet_id):
#     
#     return jsonify({"message": "Favorite planet removed"})

# @app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
# def remove_favorite_people(people_id):
#   
#     return jsonify({"message": "Favorite people removed"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
