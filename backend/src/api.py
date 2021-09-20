import os
# shahad 
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

#db_drop_and_create_all()

## ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    })


@app.route("/drinks-detail")
@requires_auth('get:drinks-detail')
def get_drink_detail(jwt):
    try:
        drinks = Drink.query.all()

        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        })
    except:
        abort(404)
        

@app.route("/drinks", methods=['POST'])
@requires_auth('post:drinks')
def post_drink_detail(jwt):
    body = request.get_json()
    if not ('title' in body and 'recipe' in body):
        abort(422)
    else:
        title = body['title']
        recipe = body['recipe']
        try:
            drink = Drink()
            drink.title = title
            drink.recipe = json.dumps(recipe) 
            drink.insert()
            return jsonify({
                'success': True,
                'drinks': [drink.long()]
            })
        except:
            abort(404)


@app.route("/drinks/<id>", methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(jwt, id):
    drink = Drink.query.get(id)
    if drink:
        try:
            body = request.get_json()
            title = body.get('title')
            recipe = body.get('recipe')
            if title:
                drink.title = title
            if recipe:
                drink.recipe = json.dumps(recipe) 
            drink.update()
            return jsonify({
                'success': True,
                'drinks': [drink.long()]
            })
        except:
            abort(400)
    else:
        abort(404)


@app.route("/drinks/<id>", methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt ,id):
    drink = Drink.query.get(id)
    if drink:
        try:
            drink.delete()
            return jsonify({
                'success': True,
                'drinks': id
            })
        except:
            abort(422)
    else:
        abort(404)


## Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

#error handler for AuthError
@app.errorhandler(AuthError)
def handle_auth_error(e):
    return jsonify({
                    "success": False,
                    "error": e.status_code,
                    'message': e.error
                    }), 401
