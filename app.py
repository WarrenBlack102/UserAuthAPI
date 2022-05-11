from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_bcrypt import Bcrypt

import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')


db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
CORS(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable = False, unique = True)
    password = db.Column(db.String, nullable = False)
    email = db.Column(db.String, unique = True)

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "password", "email")

user_schema = UserSchema()
multi_user_schema = UserSchema(many=True)


@app.route("/user/add", methods=["POST"])
def add_user():
    if request.content_type != "application/json":
        return jsonify("ERROR: JSON needed here")

    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")
    email = post_data.get("email")

    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
    new_record = User(username, pw_hash, email)
    db.session.add(new_record)
    db.session.commit()

    return jsonify(user_schema.dump(new_record))


@app.route("/user/verification", methods=["POST"])
def verification():
    if request.content_type != "application/json":
        return jsonify("User could not be Verfied!")

    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")

    user = db.session.query(User).filter(User.username == username).first()

    if user is None:
        return jsonify("User could not be Verfied!")

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify("User could not be Verfied!")

    return jsonify("User Verified")


@app.route("/user/get", methods=["GET"])
def get_users():
    users = db.session.query(User).all()
    return jsonify(multi_user_schema.dump(users))


@app.route("/user/delete/<id>", methods=["DELETE"])
def user_delete(id):
    delete_user = db.session.query(User).filter(User.id == id).first()
    db.session.delete(delete_user)
    db.session.commit()
    return jsonify("You are sooooooo Deleted")


@app.route("/user/update/<id>", methods=["PUT"])
def update_usermail(id):
    if request.content_type != 'appilcation/json':
        return jsonify("Data must be JSON!")

    put_data = request.get_json()
    username = put_data.get("username")
    email = put_data.get("email")
    
    usermail_update = db.session.query(User).filter(User.id == id).first()

    if username != None:
        usermail_update.username = username
    if email != None:
        usermail_update.email = email

    db.session.commit()
    return jsonify(user_schema.dump(usermail_update))


@app.route("/user/pw/<id>", methods=["PUT"])
def pw_update(id):
    if request.content_type != "application/json":
        return jsonify("Error: Data must be JSON")

    password = request.get_json().get("password")
    user = db.session.query(User).filter(User.id == id).first()
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    user.password = pw_hash

    db.session.commit()

    return jsonify(user_schema.dump(user))






if __name__ == '__main__':
	app.run(debug=True)