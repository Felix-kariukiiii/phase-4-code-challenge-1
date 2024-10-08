#!/usr/bin/env python3

import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower
from flask.json.provider import DefaultJSONProvider

# Setup database connection
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Initialize Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json_provider_class = DefaultJSONProvider
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Initialize migration
migrate = Migrate(app, db)
db.init_app(app)

# Define routes
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/heroes", methods=["GET"])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([hero.to_dict(rules=("-hero_powers",)) for hero in heroes]), 200

@app.route("/heroes/<int:id>", methods=["GET"])
def get_hero(id):
    hero = Hero.query.get(id)
    if not hero:
        return jsonify({"error": "Hero not found"}), 404
    return jsonify(hero.to_dict()), 200

@app.route("/powers", methods=["GET"])
def get_powers():
    powers = Power.query.all()
    return jsonify([power.to_dict(rules=("-hero_powers", "-heroes")) for power in powers]), 200

@app.route("/powers/<int:id>", methods=["GET"])
def get_power(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({"error": "Power not found"}), 404
    return jsonify(power.to_dict(rules=("-hero_powers", "-heroes"))), 200

@app.route("/powers/<int:id>", methods=["PATCH"])
def patch_power_by_id(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({"error": "Power not found"}), 404

    data = request.get_json()
    description = data.get("description", "")

    if len(description) < 20:
        return jsonify({"errors": ["validation errors"]}), 400

    power.description = description
    db.session.commit()
    return jsonify(power.to_dict()), 200


@app.route("/hero_powers", methods=["POST"])
def create_hero_power():
    data = request.get_json()
    strength = data.get("strength")
    hero_id = data.get("hero_id")
    power_id = data.get("power_id")

    if strength not in ["Strong", "Weak", "Average"]:
        return jsonify({"errors": ["validation errors"]}), 400

    hero = Hero.query.get(hero_id)
    power = Power.query.get(power_id)
    if not hero or not power:
        return jsonify({"error": "Hero or Power not found"}), 404

    hero_power = HeroPower(strength=strength, hero_id=hero_id, power_id=power_id)
    db.session.add(hero_power)
    db.session.commit()

    return jsonify(hero_power.to_dict()), 200
if __name__ == "__main__":
    app.run(port=5555, debug=True)