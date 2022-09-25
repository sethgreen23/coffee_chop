import os
from tkinter.messagebox import NO
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks',methods=['GET'])
def get_public_drinks():
    try:
        drinks = Drink.query.all();

        return jsonify({
        'success':True,
        'drinks':[drink.short() for drink in drinks]
        })
    except:
        abort(404)
    

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
'''
Provide a long listing of the drinks and it is a restricted to
the manager role
'''
#get drink list with long data representation
#restricted permission to the Manager and Barista roles
@app.route('/drinks-detail',methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_with_permition(jwt):
    try:
        drinks = Drink.query.all()

        return jsonify({
            'success':True,
            'drinks':[drink.long() for drink in drinks]
        })
    except:
        abort(404)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
'''
create a drink
restrincted for usage for Manager role

'''
@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def add_drink(jwt):
    body = request.get_json()
    
    # we need to get the title and the recipe in the body of the request that we can preced to 
    # the creation of the drink
    if not('title' in body and 'recipe' in body):
        abort(422)

    title = body.get("title")
    recipe = body.get("recipe");
    try:
        # we store the python object in a string format in the database using dumps
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
        return jsonify({
            'success':True,
            'drinks':[drink.long()]
        })
    except:
        abort(422)

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
#update a drink
#restrincted for usage for Manager role
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt,id):
    
    drink = Drink.query.get(id)
    # we need to get a drink back from the query to precede to the update
    if drink is None:
        abort(404)
    try:

        body = request.get_json()

        # check every colone if it exist in the request body 
        # if so we precede to update the object with the new  values
        if 'title' in body:
            drink.title=body.get('title')
        if 'recipe' in body:
            drink.recipe = json.dumps(body.get('recipe'))

        drink.update()

        return jsonify({
            'success':True,
            'drinks':[drink.long()]
        })

    except:
     abort(422)

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
# delete a drink
#restrincted for usage for Manager role
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    drink = Drink.query.get(id)

    # we need to get a drink back from the query to precede to the deletion
    if drink is None:
        abort(404)

    try:
        drink.delete()
        
        return jsonify({
            'success':True,
            'delete':id
        })
    except:
        abort(422)


# Error Handling
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
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def manage_auth_error(auth_error):
    return jsonify({
        "success":False,
        "error":auth_error.status_code,
        "message":auth_error.error
    }),auth_error.status_code