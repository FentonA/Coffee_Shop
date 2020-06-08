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
        return json.dumps({
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
def get_drink_details(payload):
    try:
        menu_drinks = Drink.query.all()
        drink_details = [drink_detail.long() for drink_detail in menu_drinks]
        return json.dumps({
            'success': True,
            'drinks': [drink_detail.long() for drink_detail in menu_drinks]
        })
    except:
        abort(400)

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
def drinks(f):
    body = request.get_json()
    new_drinks = Drink(title=body.get('title'),
                  recipe=body.get('recipe') if type(body.get('recipe')) == str
                  else json.dumps(body.get('recipe')))
    try:
        new_drinks.insert()

        return json.dumps({
            'success': True,
            "drinks": [drink.long() for drink in Drink.query.all()]
        }), 200
    except: 
          return json.dumps({
            'success': False,
            'error': "An error occurred"
        }), 500

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
    update_title = body.get('title')
    update_recipe = body.get('recipe')

    updated_drinks = Drink.query.filter(Drink.id == drink_id).one_or_none()
        
    if update_title:
        updated_drinks.title = update_title
    if update_recipe:
        updated_drinks.recipe = update_recipe
    updated_drinks.update()

    return json.dumps({
        'success': True,
        'drinks': [updated_drinks.long()]
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
        del_drinks = Drink.query.filter(Drink.id == drink_id).one_or_none()
        del_drinks.delete()
        return json.dumps({
            'success': True,
            'drink': del_drinks.id,
        }), 200

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
def handle_auth_error(ex):

    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
      }), 400