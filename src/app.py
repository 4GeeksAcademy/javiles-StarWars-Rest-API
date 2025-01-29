
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, People, FavoritePlanet, FavoritePeople


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

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200 


@app.route("/users", methods=['POST'])
def sign_up():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    if None in [name, email, password]:
        return jsonify ({
            "message": "Debes completar todos los campos."
        }), 400
    user_already_exist = db.session.execute(db.select(User).filter_by(email=email)).one_or_none()
    if user_already_exist:
        return jsonify({
            "message": "No puedes registrarte con ese correo. Intenta con otro."
        }), 400
    print(user_already_exist)
    new_user = User(name, email, password)
    if not isinstance(new_user, User):
        return jsonify({
            "message": "Error de servidor. Intenta de nuevo."
        }), 500
    try:
        db.session.add(new_user)
        db.session.commit()
    except:
        return jsonify({
            "message": "Error en la base de datos. Trata de nuevo más tarde."
        }), 500
    user_serialized = new_user.serialize()
    return jsonify (user_serialized), 200


@app.route('/planet', methods=['POST'])
def create_planet():
    data = request.get_json()
    name = data.get("name")
    if None in [name]:
        return jsonify({"message": "El planeta debe tener un nombre."}), 400
    planet_already_exist = db.session.execute(db.select(Planet).filter_by(name=name)).one_or_none()
    if planet_already_exist:
        return jsonify({
            "message": "Lo sentimos, al parecer algún otro ser pensó igual que tú al establecer su propio planeta. Intenta con otro nombre."
        }), 400
    new_planet = Planet(name)
    if not isinstance(new_planet, Planet):
        return jsonify({
            "message": "Error de servidor. Intenta de nuevo."
        }), 500
    try:
        db.session.add(new_planet)
        db.session.commit()
    except:
        return jsonify({
            "message": "Error en la base de datos. Intenta más tarde."
        }), 500
    planet_serialized = new_planet.serialize()
    return jsonify (planet_serialized), 200

# POST Add favorite planet (-------------Funciona------------)
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_email = request.args.get("email")
    if not user_email:
        return jsonify({"message": "El correo del usuario es necesario"}), 400
    
    user = db.session.execute(db.select(User).filter_by(email=user_email)).scalar_one_or_none()
    if user is None:
        return jsonify({"message": "Usuario no encontrado"}), 400
    
    planet = db.session.execute(db.select(Planet).filter_by(id=planet_id)).scalar_one_or_none()
    if planet is None:
        return jsonify({"message": "Planeta no encontrado"}), 400
    
    existing_favorite = db.session.execute(db.select(FavoritePlanet).filter_by(user_id=user.id, planet_id=planet.id)).scalar_one_or_none()
    if existing_favorite:
        return jsonify({"message": "Este planeta ya es uno de tus favoritos"}), 400
    
    new_favorite = FavoritePlanet(user_id=user.id, planet_id=planet.id)
    db.session.add(new_favorite)
    db.session.commit()
    
    return jsonify(new_favorite.serialize()), 200

# POST People (---------------------Funciona----------------)
@app.route('/people', methods=['POST'])
def create_people():
    data = request.get_json()
    name = data.get("name")
    gender = data.get("gender")
    age = data.get("age")
    if None in [name, gender, age]:
        return jsonify({"message": "Todos los campos (name, gender, age) son obligatorios."}), 400
    
    person_already_exist = db.session.execute(db.select(People).filter_by(name=name)).one_or_none()
    if person_already_exist:
        return jsonify({"message": "Ya existe una persona con ese nombre."}), 400
    
    new_person = People(name, gender, age)
    if not isinstance(new_person, People):
        return jsonify({"message": "Error de servidor. Intenta de nuevo."}), 500
    
    try:
        db.session.add(new_person)
        db.session.commit()
    except:
        return jsonify({"message": "Error en la base de datos. Intenta más tarde."}), 500
    
    person_serialized = new_person.serialize()
    return jsonify(person_serialized), 200

# POST Add favorite people (----------------Funciona---------------)
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user_email = request.args.get("email")
    if not user_email:
        return jsonify({"message": "El correo del usuario es necesario"}), 400
    
    user = db.session.execute(db.select(User).filter_by(email=user_email)).scalar_one_or_none()
    if user is None:
        return jsonify({"message": "Usuario no encontrado"}), 400
    
    person = db.session.execute(db.select(People).filter_by(id=people_id)).scalar_one_or_none()
    if person is None:
        return jsonify({"message": "Persona no encontrada"}), 400
    
    existing_favorite = db.session.execute(db.select(FavoritePeople).filter_by(user_id=user.id, people_id=person.id)).scalar_one_or_none()
    if existing_favorite:
        return jsonify({"message": "Esta persona ya es uno de tus favoritos"}), 400
    
    new_favorite = FavoritePeople(user_id=user.id, people_id=person.id)
    db.session.add(new_favorite)
    db.session.commit()
    
    favorite_serialized = new_favorite.serialize()
    favorite_serialized['person'] = person.serialize()
    return jsonify(favorite_serialized), 200


# GET Users (---------------Funciona----------------)
@app.route("/users", methods=['GET'])
def get_all_users():
    users_result = db.session.execute(db.select(User)).all()
    users = []
    for user_tuple in users_result:
        users.append(user_tuple[0])
    users_serialized = []
    for user in users:
        users_serialized.append(user.serialize())
    return jsonify(users_serialized), 200

# GET Just one user (-------------Funciona-------------)
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "Usuario no encontrado"}), 404
    return jsonify(user.serialize()), 200

# GET Planets (--------------------Funciona-----------------)
@app.route('/planets', methods=['GET'])
def get_planets():
    planets_result = db.session.execute(db.select(Planet)).all()
    planets = []
    for planet_tuple in planets_result:
        planets.append(planet_tuple[0])
    planets_serialized = []
    for planet in planets:
        planets_serialized.append(planet.serialize())
    return jsonify(planets_serialized), 200

# GET Just one planet (----------------Funciona----------------)
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    planet = db.session.execute(db.select(Planet).filter_by(id=planet_id)).scalar_one_or_none()
    if planet is None:
        return jsonify({"message": "Planeta no encontrado"}), 404
    return jsonify(planet.serialize()), 200

# GET People (------------------Funciona--------------------)
@app.route('/people', methods=['GET'])
def get_people():
    people_result = db.session.execute(db.select(People)).all()
    people = []
    for people_tuple in people_result:
        people.append(people_tuple[0])
    people_serialized = []
    for person in people:
        people_serialized.append(person.serialize())
    return jsonify(people_serialized), 200

# GET Just one person (-------------------Funciona-------------)
@app.route('/people/<int:people_id>', methods=['GET'])
def get_single_person(people_id):
    person = db.session.execute(db.select(People).filter_by(id=people_id)).scalar_one_or_none()
    if person is None:
        return jsonify({"message": "Persona no encontrada"}), 404
    return jsonify(person.serialize()), 200

# GET Favorites (-----------------Funciona------------------)
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_email = request.args.get("email")
    if not user_email:
        return jsonify({"message": "El correo del usuario es necesario"}), 400

    user = db.session.execute(db.select(User).filter_by(email=user_email)).scalar_one_or_none()
    if user is None:
        return jsonify({"message": "Usuario no encontrado"}), 404

    favorite_planets = db.session.execute(db.select(Planet).join(FavoritePlanet).filter(FavoritePlanet.user_id == user.id)).scalars().all()

    favorite_people = db.session.execute(db.select(People).join(FavoritePeople).filter(FavoritePeople.user_id == user.id)).scalars().all()

    favorite_planets_data = [planet.serialize() for planet in favorite_planets]
    favorite_people_data = [person.serialize() for person in favorite_people]

    return jsonify({
        "favorite_planets": favorite_planets_data,
        "favorite_people": favorite_people_data
    }), 200

# DELETE Deletes favorite planet (------------------Funciona-------------)
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def remove_favorite_planet(planet_id):
    user_email = request.args.get("email")
    if not user_email:
        return jsonify({"message": "El correo del usuario es necesario"}), 400
    
    user = db.session.execute(db.select(User).filter_by(email=user_email)).scalar_one_or_none()
    if user is None:
        return jsonify({"message": "Usuario no encontrado"}), 400
    
    favorite = db.session.execute(db.select(FavoritePlanet).filter_by(user_id=user.id, planet_id=planet_id)).scalar_one_or_none()
    if favorite is None:
        return jsonify({"message": "Este planeta no es uno de tus favoritos"}), 400
    
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({"message": "Planeta eliminado de tus favoritos"}), 200

# DELETE Deletes favorite people (-----------------Funciona-----------------)
@app.route('/favorite/people/<int:people_id>', methods=['DELETE']) 
def remove_favorite_people(people_id):
    user_email = request.args.get("email")
    if not user_email:
        return jsonify({"message": "El correo del usuario es necesario"}), 400
    
    user = db.session.execute(db.select(User).filter_by(email=user_email)).scalar_one_or_none()
    if user is None:
        return jsonify({"message": "Usuario no encontrado"}), 400
    
    favorite = db.session.execute(db.select(FavoritePeople).filter_by(user_id=user.id, people_id=people_id)).scalar_one_or_none()
    if favorite is None:
        return jsonify({"message": "Esta persona no es uno de tus favoritos"}), 400
    
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({"message": "Persona eliminada de tus favoritos"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)