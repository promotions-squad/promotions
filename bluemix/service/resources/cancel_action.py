"""
This module contains routes without Resources
"""
from flask import abort
from flask_api import status
from flask_restful import Resource
from service.models import Promotion

######################################################################
# CANCEL A PROMOTION
######################################################################
class CancelAction(Resource):
    """ Resource to Cancel a Promotion """
    def put(self, promotion_id):
        """ Cancel a Promotion """
        promotion = Promotion.find(promotion_id)

        if not promotion:
            abort(status.HTTP_404_NOT_FOUND, "Promotion with id '{}' was not found.".format(promotion_id))

        promotion.available = False

        promotion.save()

        return promotion.serialize(), status.HTTP_200_OK
