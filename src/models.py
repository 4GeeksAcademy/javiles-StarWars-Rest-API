from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    name = db.Column(db.String(250), nullable=False)
    favorite_planets = db.relationship("FavoritePlanet", back_populates="user")
    favorite_people = db.relationship("FavoritePeople", back_populates="user")

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
        self.is_active = True


    def __repr__(self):
        return '<User %r>' % self.email 

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "is_active": self.is_active
            
        }

class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    favorited_by = db.relationship("FavoritePlanet", back_populates="planet")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Planet %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }
    
class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    favorited_by = db.relationship("FavoritePeople", back_populates="person")

    def __init__(self, name, gender, age):
        self.name = name
        self.gender = gender
        self.age = age

    def __repr__(self):
        return '<People %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "age": self.age,
        }
    
class FavoritePlanet(db.Model):
    __tablename__ = 'favorite_planet'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'), nullable=False)
    user = db.relationship('User', back_populates='favorite_planets')
    planet = db.relationship('Planet', back_populates='favorited_by')

    def __init__(self, user_id, planet_id):
        self.user_id = user_id
        self.planet_id = planet_id

    def __repr__(self):
        return '<FavoritePlanet User:%r Planet:%r>' % (self.user_id, self.planet_id)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
        }

class FavoritePeople(db.Model):
    __tablename__ = 'favorite_people'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    user = db.relationship('User', back_populates='favorite_people')
    person = db.relationship('People', back_populates='favorited_by')

    def __init__(self, user_id, people_id):
        self.user_id = user_id
        self.people_id = people_id

    def __repr__(self):
        return '<FavoritePeople User:%r Person:%r>' % (self.user_id, self.people_id)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "people_id": self.people_id,
        }