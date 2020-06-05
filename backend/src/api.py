
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import jose

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods= ['GET'])
def get_drinks():
    try:
        menu_drinks = Drink.query.all()
        drinks = [drink.short() for drink in menu_drinks]
        if len(drinks) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        abort(400)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods =['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details():
    menu_drinks = Drink.query.all()
    drink_details = [drinks_details.long() for drinks_details in menu_drinks]
    if len(drink_details) == 0:
        abort(404)
    return jsonify({
        'success': True,
        'drink_details': drink_details
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def new_coffee(token):
    body = request.get_data()
    new_Drink = Drink(
        title = body['title'],
        recipe = body['recipe']
    )

    new_Drink.insert()
    drink_all = Drink.query.all()
    drink = [drink.long() for drink in drink_all]

    return jsonify({
        'success': True,
        "drinks": drink
    })

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, drink_id):

    
    body = request.get_json()
    update_title = body['title']
    update_recipe = body['recipe']

    updated_drinks = Drink.query.filter(Drink.id == drink_id).one_or_none()

    
    if updated_drinks is None:
        abort(404)
        
    if update_title:
        updated_drinks.title = update_title
    if update_recipe:
        updated_drinks.recipe = update_recipe
    updated_drinks.update()

    return jsonify({
        'success': True,
        'drinks': updated_drinks.long()
    })

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_da_drink(payload, drink_id):
    try:
        if drink_id is None:
            abort(404)
        del_drinks = Drink.query.filter(Drink.id == drink_id).one_or_none()
        del_drinks.delete()

        drinks = Drink.query.all()
        return jsonify({
            'success': True,
            'delete': id,
            'drinks': drinks
        }, 200)

    except:
        abort(422)


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


@app.errorhandler(404)
def page_not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "Page not found"
                    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def autherror(error):
    error_details = error.error
    error_status_code = error
    
    return jsonify({
        'success': False,
        'error': error_status_code,
        'message': error_details['description'] 
    }), error_status_code


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
      }), 400