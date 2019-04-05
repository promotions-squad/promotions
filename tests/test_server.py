"""
Promotion API Service Test Suite
Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN
"""

import unittest
import os
import logging
from flask_api import status    # HTTP Status Codes
#from mock import MagicMock, patch
from app.models import Promotion, DataValidationError, db
from .promotion_factory import PromotionFactory
import app.service as service
import json

DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')

######################################################################
#  T E S T   C A S E S
######################################################################
class TestPromotionServer(unittest.TestCase):
    """ Promotion Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        service.app.debug = False
        service.initialize_logging(logging.INFO)
        # Set up the test database
        service.app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        """ Runs before each test """
        service.init_db()
        db.drop_all()    # clean up the last tests
        db.create_all()  # create new tables
        self.app = service.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def _create_promotions(self, count):
        """ Factory method to create promotions in bulk """
        promotions = []
        for _ in range(count):
            test_promotion = PromotionFactory()
            resp = self.app.post('/promotions',
                                 json=json.dumps(test_promotion.serialize(),default=str),
                                 content_type='application/json')
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED, 'Could not create test promotion')
            new_promotion = resp.get_json()
            test_promotion.id = new_promotion['id']
            promotions.append(test_promotion)
        return promotions

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['name'], 'Promotions Demo REST API Service')

    def test_create_promotion(self):
        """ Create a new Promotion """
        test_promotion = PromotionFactory()
        resp = self.app.post('/promotions',
                             json=json.dumps(test_promotion.serialize(),default=str),
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertTrue(location != None)
        # Check the data is correct
        new_promotion = resp.get_json()
        self.assertEqual(new_promotion['productid'], test_promotion.productid, "Product ID does not match")
        self.assertEqual(new_promotion['category'], test_promotion.category, "Categories do not match")
        self.assertEqual(new_promotion['available'], test_promotion.available, "Availability does not match")
        self.assertEqual(new_promotion['discount'], test_promotion.discount, "Discount does not match")
        self.assertEqual(new_promotion['startdate'], test_promotion.startdate, "Start Date does not match")
        self.assertEqual(new_promotion['enddate'], test_promotion.enddate, "End Date does not match")

        # Check that the location header was correct
        resp = self.app.get(location,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_promotion = resp.get_json()
        self.assertEqual(new_promotion['productid'], test_promotion.productid, "Product ID does not match")
        self.assertEqual(new_promotion['category'], test_promotion.category, "Categories do not match")
        self.assertEqual(new_promotion['available'], test_promotion.available, "Availability does not match")
        self.assertEqual(new_promotion['discount'], test_promotion.discount, "Discount does not match")
        self.assertEqual(new_promotion['startdate'], test_promotion.startdate, "Start Date does not match")
        self.assertEqual(new_promotion['enddate'], test_promotion.enddate, "End Date does not match")

    def test_update_promotion(self):
        """ Update an existing Promotion """
        # create a promotion to update
        test_promotion = PromotionFactory()
        resp = self.app.post('/promotions',
                             json=json.dumps(test_promotion.serialize(),default=str),
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the promotion
        new_promotion = resp.get_json()
        new_promotion['category'] = 'unknown'
        resp = self.app.put('/promotions/{}'.format(new_promotion['id']),
                            json=new_promotion,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_promotion = resp.get_json()
        self.assertEqual(updated_promotion['category'], 'unknown')


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
