import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

#https://fsnd-44-2.auth0.com/authorize?audience=drinks&response_type=token&client_id=INSERT_CLIENT_ID&redirect_uri=https://127.0.0.1:8080/login-results

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
NOTE: Uncomment to initialize the database
'''
#db_drop_and_create_all()

## ROUTES
# Returns list of available drinks
@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        available_drinks = Drink.query.all()
        drinks = [drink.short() for drink in available_drinks]

        return jsonify({
            'success':True,
            'drinks':drinks
        })

    except:
        abort(422)

# Returns details about a drink. Auth required.
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    try:
        all_drinks = Drink.query.all()
        drinks = [drink.long() for drink in all_drinks]
    
        return jsonify({
            'success':True,
            'drinks': drinks
        })

    except:
        abort(422)

# Adds new drink. Auth required.
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink():
    body = request.get_json()
    req_title = body.get('title',None)
    req_recipe= body.get('recipe',None)

    if req_title is None:
        abort(422)
    if req_recipe is None:
        abort(422)
    
    try:
        # Add new drink to db
        new_drink = Drink(title=req_title, recipe=json.dumps(req_recipe))
        new_drink.insert()

        # Fetch new list of drinks
        available_drinks = Drink.query.all()
        drinks = [drink.short() for drink in available_drinks]
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        abort(422)

# Edits existing drink info. Auth required.
@app.route('/drinks/<int:drink_id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(drink_id):
    selected_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    
    if selected_drink is None:
        abort(404)
    
    body = request.get_json()
    req_title = body.get('title',None)
    req_recipe= body.get('recipe',None)
    if req_title is not None:
        selected_drink.title = req_title
    if req_recipe is not None:
        #JSON dumps ensures "" are stored
        selected_drink.recipe = json.dumps(req_recipe)
    
    selected_drink.update()

    # Get updated list of drinks
    available_drinks = Drink.query.all()
    drinks = [drink.long() for drink in available_drinks]

    return jsonify({
        'success':True,
        'drinks':drinks
    })

# Removes drink. Auth required.
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id):
    selected_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if selected_drink is None:
        abort(404)
    
    selected_drink.delete()

    return jsonify({
        'success':True,
        'delete': drink_id
    })


# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(AuthError)
def authorization_error(error):
    return jsonify({
        "success": False, 
        "error": error.status_code,
        "message": error.error['code']
    }), error.status_code
