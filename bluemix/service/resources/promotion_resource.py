"""
This module contains all of Resources for the Promotion Shop API
"""
from flask import abort, request
from flask_restful import Resource
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import BadRequest
from service import app, api
from service.models import Promotion, DataValidationError

######################################################################
#  PATH: /promotions/{id}
######################################################################
class PromotionResource(Resource):
    """
    PromotionResource class

    Allows the manipulation of a single Promotion
    GET /promotions/{id} - Returns a Promotion with the id
    PUT /promotions/{id} - Update a Promotion with the id
    DELETE /promotions/{id} -  Deletes a Promotion with the id
    """

    def get(self, promotion_id):
        """
        Retrieve a single Promotion

        This endpoint will return a Promotion based on it's id
        """
        app.logger.info("Request to Retrieve a promotion with id [%s]", promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(status.HTTP_404_NOT_FOUND, "Promotion with id '{}' was not found.".format(promotion_id))
        return promotion.serialize(), status.HTTP_200_OK


    def put(self, promotion_id):
        """
        Update a Promotion

        This endpoint will update a Promotion based the body that is posted
        """
        app.logger.info('Request to Update a promotion with id [%s]', promotion_id)
        #check_content_type('application/json')
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(status.HTTP_404_NOT_FOUND, "Promotion with id '{}' was not found.".format(promotion_id))

        payload = request.get_json()
        try:
            promotion.deserialize(payload)
        except DataValidationError as error:
            raise BadRequest(str(error))

        promotion.id = promotion_id
        promotion.save()
        return promotion.serialize(), status.HTTP_200_OK

    def delete(self, promotion_id):
        """
        Delete a Promotion

        This endpoint will delete a Promotion based the id specified in the path
        """
        app.logger.info('Request to Delete a promotion with id [%s]', promotion_id)
        promotion = Promotion.find(promotion_id)
        if promotion:
            promotion.delete()
        return '', status.HTTP_204_NO_CONTENT
