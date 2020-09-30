import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from database.models import db_drop_and_create_all, setup_db, Drink
from auth.auth import AuthError, requires_auth
print("Sahba")
app = Flask(__name__)
setup_db(app)
CORS(app)


db_drop_and_create_all()

@app.route('/drinks')
def get_drink():
    drinks = Drink.query.all()
    drink_short = [drink.short() for drink in drinks]

    if drinks is None:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': drink_short
    })



@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinkDetail(token):
    drinks = Drink.query.all()
    drink_long = [drink.long() for drink in drinks]

    if drinks is None:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': drink_long
    })



@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(token):
    body = request.get_json()

    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)

    try:
        drink = Drink(title=new_title, recipe=new_recipe)
        drink.insert()
        drinks = Drink.query.all()
        drink_long = [drink.long() for drink in drinks]

        return jsonify({
            'success': True,
            'drinks': drink_long
        })
    except:
        abort(422) 



@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(token, drink_id):
    body = request.get_json()
    drink = Drink.query.filter(Drink.id == drink_id)
    if drink is None:
        abort(404)
    if 'title' in body:
        drink.title = body.get('title')
    if 'recipe' in body:
        drink.recipe = body.get('recipe')
    drink.update()
    drinks = Drink.query.all()
    drink_long = [drink.long() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': drink_long
    })
    


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id)
        if drink is None:
            abort(404)
        drink.delete()
        
        return jsonify({
            'success': True,
            'deleted': drink_id
        })
    except:
        abort(422)

        
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
        }), 422

@app.errorhandler(404)
def notFound(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "unprocessable"
    }), 404

@app.errorhandler(AuthError)
def handleAuthError(exception):
    response = jsonify(exception.error)
    response.status_code = exception.status_code
    return response
