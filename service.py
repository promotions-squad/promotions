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
    message = str(error)
    app.logger.info(message)
    return jsonify(status=400, error='Bad Request', message=message), \
                   status.HTTP_400_BAD_REQUEST

@app.errorhandler(404)
def not_found(error):
    message = str(error)
    app.logger.info(message)
    return jsonify(status=404, error='Not Found', message=message), \
                   status.HTTP_404_NOT_FOUND

@app.errorhandler(400)
def bad_request(error):
    message = str(error)
    app.logger.info(message)
    return jsonify(status=400, error='Bad Request', message=message), \
                   status.HTTP_400_BAD_REQUEST

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify(status=405, error='Method not Allowed',
                   message='Your request method is not supported. Check your HTTP method and try again.'), \
                   status.HTTP_405_METHOD_NOT_ALLOWED

@app.errorhandler(500)
def internal_error(error):
    return jsonify(status=500, error='Internal Server Error',
                   message='Houston... we have a problem.'), \
                   status.HTTP_500_INTERNAL_SERVER_ERROR

#Get Index
@app.route('/')
def index():
    """ Root URL response """
    return jsonify(name='promotions Demo REST API Service',
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
    category = request.args.get('category')
    name = request.args.get('name')
    if category:
        promotions = Promotion.find_by_category(category)
    elif name:
        promotions = Promotion.find_by_name(name)
    else:
        promotions = Promotion.all()

    results = [promotion.serialize() for promotion in promotions]
    return make_response(jsonify(results), status.HTTP_200_OK)


#Add a new Promotion
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
    location_url = url_for('get_promotions', promotion_id=promotions.id, _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {
                             'Location': location_url
                         })

######################################################################
# RETRIEVE A PROMOTION BASED ON PRODUCT ID
######################################################################
@app.route('/promotions/product/<int:product_id>', methods=['GET'])
def get_promotions(product_id):
    """
    Retrieve promotions that apply to a product

    This endpoint will return a promotion based on the product id associated with the promotion
    """
    app.logger.info('Request for promotion with product_id: %s', product_id)
    promotion = Promotion.find_by_product(product_id)
    if not promotion:
        raise NotFound("Promotion for product with id '{}' was not found.".format(product_id))
    return make_response(jsonify(promotion.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE A PROMOTION
######################################################################
@app.route('/promotions/<int:promotion_id>', methods=['DELETE'])
def delete_promotions(promotion_id):
    app.logger.info('Request to delete Promotion with id: {}'.format(promotion_id))
    promotion = Promotion.find(promotion_id)
    if promotion:
        promotion.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)
