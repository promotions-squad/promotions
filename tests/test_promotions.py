
"""
Test cases for Promotion Model
Test cases can be run with:
  nosetests
  coverage report -m
"""

import unittest
import os
from app.models import Promotion, DataValidationError, db
from app import app

DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')

######################################################################
#  T E S T   C A S E S
######################################################################
class TestPromotions(unittest.TestCase):
    """ Test Cases for Promotions """

    @classmethod
    def setUpClass(cls):
        """ These run once per Test suite """
        app.debug = False
        # Set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        Promotion.init_db(app)
        db.drop_all()    # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_update_a_promotion(self):
        """ Update a Promotion """
        promotion = Promotion(product_id="1234", category="dollar", available=True, discount="5", start_date=factory.LazyFunction(datetime.date.today),factory.LazyFunction(datetime.date.today+datetime.timedelta(days=10)))
        promotion.save()
        self.assertEqual(promotion.id, 1)
        # Change it an save it
        promotion.category = "percentage"
        promotion.save()
        self.assertEqual(promotion.id, 1)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 1)
        self.assertEqual(promotions[0].category, "percentage")

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
