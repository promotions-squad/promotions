# Copyright 2019 John J. Rofrano, Scott Halperin, Chaoyun Bao, Eliza-Eve Leas, Dhruv Sharma. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Promotion Service

Paths:
------
GET /promotions - Returns a list all of the Promotions
GET /promotions/{id} - Returns the Promotion with a given id number
POST /promotions - creates a new promotion record in the database
PUT /promotions/{id} - updates a promotion record in the database
DELETE /promotions/{id} - deletes a promotion record in the database
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound

from flask_sqlalchemy import SQLAlchemy
from models import Promotion, DataValidationError

# Import Flask application
from . import app
import json

######################################################################
# Custom Exceptions
######################################################################
class DataValidationError(ValueError):
    pass

######################################################################
# ERROR Handling
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = error.message or str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_400_BAD_REQUEST,
                   error='Bad Request',
                   message=message), status.HTTP_400_BAD_REQUEST

@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = error.message or str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_404_NOT_FOUND,
                   error='Not Found',
                   message=message), status.HTTP_404_NOT_FOUND

@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = error.message or str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_405_METHOD_NOT_ALLOWED,
                   error='Method not Allowed',
                   message=message), status.HTTP_405_METHOD_NOT_ALLOWED

@app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    message = error.message or str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                   error='Unsupported media type',
                   message=message), status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = error.message or str(error)
    app.logger.error(message)
    return jsonify(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                   error='Internal Server Error',
                   message=message), status.HTTP_500_INTERNAL_SERVER_ERROR

#Get Index
@app.route('/')
def index():
    """ Root URL response """
    return jsonify(name='Promotions Demo REST API Service',
                   version='1.0',
                   paths=url_for('list_promotions', _external=True)
                  ), status.HTTP_200_OK

######################################################################
# LIST ALL PROMOTIONS
######################################################################

@app.route('/promotions', methods=['GET'])
def list_promotions():
    """ Returns all of the Promotions """
    app.logger.info('Request for promotion list')
    promotions = []
    productid = request.args.get('productid')
    category = request.args.get('category')
    available = request.args.get('available')
    if productid:
        promotions = Promotion.find_by_product(productid)
    elif category:
        promotions = Promotion.find_by_category(category)
    elif available:
        promotions = Promotion.find_by_availability(eval(available))
    else:
        promotions = Promotion.all()

    results = [promotion.serialize() for promotion in promotions]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
#ADD A NEW PROMOTION
######################################################################
@app.route('/promotions', methods=['POST'])
def create_promotions():
    """
    Creates a Promotion
    This endpoint will create a promotion based the data in the body that is posted
    """
    app.logger.info('Request to create a promotion')
    check_content_type('application/json')
    promotion = Promotion()
    promotion.deserialize(request.get_json())
    promotion.save()
    message = promotion.serialize()
    location_url = url_for('get_promotions', promotion_id=promotion.id, _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {
                             'Location': location_url
                         })

######################################################################
# RETRIEVE A PROMOTION BASED ON PROMOTION ID
######################################################################
@app.route('/promotions/<int:promotion_id>', methods=['GET'])
def get_promotions(promotion_id):
    """
    Retrieve promotions that apply to a product

    This endpoint will return a promotion based on the product id associated with the promotion
    """
    app.logger.info('Request for promotion with product id: %s', promotion_id)
    promotion = Promotion.find(promotion_id)
    if not promotion:
        raise NotFound("Promotion with id '{}' was not found.".format(promotion_id))
    return make_response(jsonify(promotion.serialize()), status.HTTP_200_OK)


######################################################################
# CANCEL A PROMOTION
######################################################################

@app.route('/promotions/<int:promotion_id>/cancel', methods=['PUT'])
def cancel_promotions(promotion_id):
    """
    Update a Promotion
    This endpoint will update a Promotion based the body that is posted
    """
    app.logger.info('Request to cancel promotion with id: %s', promotion_id)
    check_content_type('application/json')
    promotion = Promotion.find(promotion_id)
    if not promotion:
        raise NotFound("Promotion with id '{}' was not found.".format(promotion_id))
    promotion.deserialize(request.get_json())
    promotion.available = False
    promotion.save()
    return make_response(jsonify(promotion.serialize()), status.HTTP_200_OK)



######################################################################
# DELETE A PROMOTION
######################################################################
@app.route('/promotions/<int:promotion_id>', methods=['DELETE'])
def delete_promotions(promotion_id):
    """
    Delete a Promotion
    This endpoint will delete a Promotion based the id specified in the path
    """
    app.logger.info('Request to delete promotion with id: %s', promotion_id)
    promotion = Promotion.find(promotion_id)
    if promotion:
        promotion.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
# UPDATE AN EXISTING PROMOTION
######################################################################
@app.route('/promotions/<int:promotion_id>', methods=['PUT'])
def update_promotions(promotion_id):
    """
    Update a Promotion
    This endpoint will update a Promotion based the body that is posted
    """
    app.logger.info('Request to update promotion with id: %s', promotion_id)
    check_content_type('application/json')
    promotion = Promotion.find(promotion_id)
    if not promotion:
        raise NotFound("Promotion with id '{}' was not found.".format(promotion_id))
    promotion.deserialize(request.get_json())
    promotion.id = promotion_id
    promotion.save()
    return make_response(jsonify(promotion.serialize()), status.HTTP_200_OK)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Promotion.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s', request.headers['Content-Type'])
    abort(415, 'Content-Type must be {}'.format(content_type))

def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print 'Setting up logging...'
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.info('Logging handler established')
