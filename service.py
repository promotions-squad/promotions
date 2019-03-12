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
from models import Pet, DataValidationError

# Import Flask application
from . import app

#Get Index
@app.route('/')
def index():
    """ Root URL response """
    return jsonify(name='promotions Demo REST API Service',
                   version='1.0',
                   paths=url_for('list_promotions', _external=True)
                  ), status.HTTP_200_OK

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
