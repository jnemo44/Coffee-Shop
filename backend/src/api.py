import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

#https://fsnd-44-2.auth0.com/authorize?audience=drinks&response_type=token&client_id=NoXHRkYPNKc4K0pEO7sU0LGhVR4U0Hmg&redirect_uri=https://127.0.0.1:8080/login-results

#JWT - Manager
#eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkR2WFFWOXNwZEFOQ2V1SUVpZ1dJaSJ9.eyJpc3MiOiJodHRwczovL2ZzbmQtNDQtMi5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWViYWUyZjI5M2NiMzkwYzZlNGU0ZWM2IiwiYXVkIjoiZHJpbmtzIiwiaWF0IjoxNTg5NDg1Mzc1LCJleHAiOjE1ODk0OTI1NzUsImF6cCI6Ik5vWEhSa1lQTktjNEswcEVPN3NVMExHaFZSNFUwSG1nIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6ZHJpbmtzIiwiZ2V0OmRyaW5rcy1kZXRhaWwiLCJwYXRjaDpkcmlua3MiLCJwb3N0OmRyaW5rcyJdfQ.5qX_RWPMzPXMTnx88FqnTW7_7WGMu582lqU13Khm6cb8uQZFQ7vPfNLH0gVPDqgDjopWTidOGsY7ynrtDUjuW_cvc-B8C1z2c7tw8624m6E6girNBGZ7Wbn9XBi_GJZ0PJbHdvhkLfzTcAjbnze1PR7ai0NH0AjHyZ4aOgRIxzVvAXAjNUdZybTZtv41okWKZtQjgIT8YJMtVH7deiGCCG7npfllU7Z5X4MQUX81RX4Do64MzxzZrR_NGollXSdRwVkegOe-_0kPq2TxEBXLt4wUoN1NnBgKImGWj2I02ro84loMFNllsIbsjjje2B0I2WOmq6dlvZC7lU3TwnSwog

#JWT - Barista
#eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkR2WFFWOXNwZEFOQ2V1SUVpZ1dJaSJ9.eyJpc3MiOiJodHRwczovL2ZzbmQtNDQtMi5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWViYWUyZjI5M2NiMzkwYzZlNGU0ZWM2IiwiYXVkIjoiZHJpbmtzIiwiaWF0IjoxNTg5NDg1NTEyLCJleHAiOjE1ODk0OTI3MTIsImF6cCI6Ik5vWEhSa1lQTktjNEswcEVPN3NVMExHaFZSNFUwSG1nIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJnZXQ6ZHJpbmtzLWRldGFpbCJdfQ.2T4N5k6FNSgQ03KE2h56dtgFuAhIoaLpTaI7w_3Bn85L3AKfPVUuPz5qAd7wEBMzQsq_PbfZ3uVS4ZsVSByiI027EKcWPK_4wsUPe5iRT4g4kWfQpoC1IhFNZDSOcuzodmBe_5daXxD8XqWnUwTNVMUNbY-mqBWqnGbqLP7nXf0dmKYaOn2pkFZHfpw_y1g8tUfcLXp8KVa4ktSSud2bNTNRkfwno7jLkSrD0GxrNIeJF9IT0ZR8ThLiecsa0C7aNRxWC1ixZVT1nrmLGa9qnzBYZk3gQvBevMPQwrUvBSq1Khg7_HJsUlO5VlnM5a-3pem12nX9AQ7rzHa8Xn60hQ

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    all_drinks = Drink.query.all()
    drinks = [drink.short() for drink in all_drinks]

    return jsonify({
        'success':True,
        'drinks':drinks
    })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    all_drinks = Drink.query.all()
    drinks = []
    for drink in all_drinks:
        drinks.append(drink.long())
    
    return jsonify({
        'success':True,
        'drinks': drinks
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
def add_drink():
    body = request.get_json()
    req_title = body.get('title',None)
    req_recipe = body.get('recipe',None)

    if req_title is None:
        print('here1')
        abort(422)
    if req_recipe is None:
        print('here2')
        abort(422)
    
    try:
        # Add new drink to db
        drink = Drink(title=req_title, recipe=req_recipe)
        print('here3')
        drink.insert()
        print('here4')
    
        # Fetch new list of drinks
        available_drinks = Drink.query.all()
        drinks = [drink.short() for drink in available_drinks]
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        return jsonify({
            'success': False,
            'message': "The drink is not formatted correctly and can't be shown"
        })

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
