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

    def test_get_promotion_list(self):
        """Get a list of Promotions"""
        self._create_promotions(5)
        resp = self.app.get('/promotions')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_promotion(self):
        """ Get a single Promotion """
        # get the id of a promotion
        test_promotion = self._create_promotions(1)[0]
        resp = self.app.get('/promotions/{}'.format(test_promotion.id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['name'], test_promotion.name)

    def test_get_promotion_not_found(self):
        """ Get a Promotion thats not found """
        resp = self.app.get('/promotions/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


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

    def test_delete_promotion(self):
        """ Delete a Promotion """
        test_promotion = self._create_promotions(1)[0]
        resp = self.app.delete('/Promotions/{}'.format(test_promotion.id),
                               content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get('/promotions/{}'.format(test_promotion.id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_promotion_list_by_category(self):
        """ Query Promotions by Category """
        promotions = self._create_promotions(10)
        test_category = promotions[0].category
        category_promotions = [promotion for promotion in promotions if promotion.category == test_category]
        resp = self.app.get('/promotions',
                            query_string='category={}'.format(test_category))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(category_promotions))
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(promotion['category'], test_category)

    def test_query_promotion_list_by_availability(self):
        """ Query Promotions by Availability """
        promotions = self._create_promotions(10)
        test_availability = promotions[0].available
        available_promotions = [promotion for promotion in promotions if promotion.available == test_availability]
        resp = self.app.get('/promotions',
                            query_string='available={}'.format(test_availability))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(available_promotions))
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(promotion['available'], test_availability)


    @patch('app.service.Promotion.find_by_name')
    def test_bad_request(self, bad_request_mock):
         """ Test a Bad Request error from Find By Name """
         bad_request_mock.side_effect = DataValidationError()
         resp = self.app.get('/promotions', query_string='productid=1234')
         self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('app.service.Promotion.find_by_name')
    def test_mock_search_data(self, promotion_find_mock):
         """ Test showing how to mock data """
         promotion_find_mock.return_value = [MagicMock(serialize=lambda: {'productid': '1234'})]
         resp = self.app.get('/promotions', query_string='productid=1234')
         self.assertEqual(resp.status_code, status.HTTP_200_OK)

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
