"""
This module contains the Promotion Collection Resource
"""
from flask import request, abort
from flask_restful import Resource
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import BadRequest
from service import app, api
from service.models import Promotion, DataValidationError
from . import PromotionResource

class PromotionCollection(Resource):
    """ Handles all interactions with collections of Promotions """

    def get(self):
        """ Returns all of the Promotions """
        app.logger.info('Request to list Promotions...')
        promotions = []
        category = request.args.get('category')
        name = request.args.get('name')
        available = request.args.get('available')
        if category:
            app.logger.info('Filtering by category: %s', category)
            promotions = Promotion.find_by_category(category)
        elif name:
            app.logger.info('Filtering by name:%s', name)
            promotions = Promotion.find_by_name(name)
        elif available:
            app.logger.info('Filtering by available: %s', available)
            is_available = available.lower() in ['yes', 'y', 'true', 't', '1']
            promotions = Promotion.find_by_availability(is_available)
        else:
            promotions = Promotion.all()

        app.logger.info('[%s] Promotions returned', len(promotions))
        results = [promotion.serialize() for promotion in promotions]
        return results, status.HTTP_200_OK

    def post(self):
        """
        Creates a Promotion

        This endpoint will create a Promotion based the data in the body that is posted
        or data that is sent via an html form post.
        """
        app.logger.info('Request to Create a Promotion')
        content_type = request.headers.get('Content-Type')
        if not content_type:
            abort(status.HTTP_400_BAD_REQUEST, "No Content-Type set")

        data = {}
        # Check for form submission data
        if content_type == 'application/x-www-form-urlencoded':
            app.logger.info('Processing FORM data')
            app.logger.info(type(request.form))
            app.logger.info(request.form)
            data = {
                'productid': request.form['productid'],
                'category': request.form['category'],
                'available': request.form['available'].lower() in ['yes', 'y', 'true', 't', '1'],
                'discount': request.form['discount']
            }
        elif content_type == 'application/json':
            app.logger.info('Processing JSON data')
            data = request.get_json()
        else:
            message = 'Unsupported Content-Type: {}'.format(content_type)
            app.logger.info(message)
            abort(status.HTTP_400_BAD_REQUEST, message)

        promotion = Promotion()
        try:
            promotion.deserialize(data)
        except DataValidationError as error:
            raise BadRequest(str(error))
        promotion.save()
        app.logger.info('Promotion with new id [%s] saved!', promotion.id)
        location_url = api.url_for(PromotionResource, promotion_id=promotion.id, _external=True)
        return promotion.serialize(), status.HTTP_201_CREATED, {'Location': location_url}
