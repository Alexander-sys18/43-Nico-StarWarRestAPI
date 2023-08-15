import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planeta, Personaje, Favorito 
from sqlalchemy.exc import IntegrityError

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
    current_user_id = 1

    user_favorites = Favorito.query.filter_by(user_id=current_user_id).all()

    favorites_serialized = []
    for favorite in user_favorites:
        favorite_data = {
            "id": favorite.id,
            "user_id": favorite.user_id,
            "planet": favorite.planeta.serialize() if favorite.planeta else None,
            "personaje": favorite.personaje.serialize() if favorite.personaje else None
        }
        favorites_serialized.append(favorite_data)

    return jsonify({"favorites": favorites_serialized})

def get_current_user():

    user = {
        "id": 1,
        "username": "usuario_ejemplo"
    }
    return user

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    try:
        current_user = get_current_user()

        if current_user and "id" in current_user:
            has_favorite = Favorito.query.filter_by(user_id=current_user["id"], planet_id=planet_id).first()

            if has_favorite:
                return jsonify({'message': 'Planet is already a favorite'}), 200

            new_favorite = Favorito(user_id=current_user["id"], planet_id=planet_id)
            db.session.add(new_favorite)
            db.session.commit()

            return jsonify({'message': 'Planet added to favorites'}), 201
        else:
            return jsonify({'error': 'User not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    try:
        current_user = get_current_user()

        if current_user:
            has_favorite = Favorito.query.filter_by(user_id=current_user.id, people_id=people_id).first()

            if has_favorite:
                return jsonify({'message': 'Person is already a favorite'}), 200

            new_favorite = Favorito(user_id=current_user.id, people_id=people_id)
            db.session.add(new_favorite)
            db.session.commit()

            return jsonify({'message': 'Person added to favorites'}), 201
        else:
            return jsonify({'error': 'User not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def remove_favorite_planet(planet_id):
    try:
        current_user = get_current_user()

        if current_user:
            favorite = Favorito.query.filter_by(user_id=current_user['id'], planet_id=planet_id).first()

            if favorite:
                db.session.delete(favorite)
                db.session.commit()
                return jsonify({'message': 'Favorite planet removed'}), 200
            else:
                return jsonify({'message': 'Favorite planet not found'}), 404
        else:
            return jsonify({'error': 'User not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/favorito/people/<int:people_id>', methods=['DELETE'])
def remove_favorite_people(people_id):
    try:
        current_user = get_current_user()

        if current_user:
            favorite = Favorito.query.filter_by(user_id=current_user['id'], people_id=people_id).first()

            if favorite:
                db.session.delete(favorite)
                db.session.commit()
                return jsonify({'message': 'Favorite people removed'}), 200
            else:
                return jsonify({'message': 'Favorite people not found'}), 404
        else:
            return jsonify({'error': 'User not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
