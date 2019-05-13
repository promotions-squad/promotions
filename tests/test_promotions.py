# Copyright 2016, 2017 John J. Rofrano. All Rights Reserved.
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
Promotion Test Suite

Test cases can be run with the following:
nosetests -v --with-spec --spec-color
"""

import unittest
#import os
#import json
from mock import MagicMock, patch
from requests import HTTPError, ConnectionError
#from redis import Redis, ConnectionError
#from werkzeug.exceptions import NotFound
from app.models import Promotion, DataValidationError
#from app.custom_exceptions import DataValidationError
#from app import server  # to get Redis

VCAP_SERVICES = {
    'cloudantNoSQLDB': [
        {'credentials': {
            'username': 'admin',
            'password': 'pass',
            'host': 'localhost',
            'port': 5984,
            'url': 'http://admin:pass@localhost:5984'
            }
        }
    ]
}
#VCAP_SERVICES = os.getenv('VCAP_SERVICES', None)
#if not VCAP_SERVICES:
#    VCAP_SERVICES = '{"rediscloud": [{"credentials": {' \
#        '"password": "", "hostname": "127.0.0.1", "port": "6379"}}]}'


######################################################################
#  T E S T   C A S E S
######################################################################
class TestPromotions(unittest.TestCase):
    """ Test Cases for Promotion Model """

    def setUp(self):
        """ Initialize the Cloudant database """
        Promotion.init_db("test_promotion")
        Promotion.remove_all()

    def test_create_a_promotion(self):
        """ Create a promotion and assert that it exists """
        promotion = Promotion("A1234", "BOGO", False, "20")
        self.assertNotEqual(promotion, None)
        self.assertEqual(promotion.id, None)
        self.assertEqual(promotion.productid, "A1234")
        self.assertEqual(promotion.category, "BOGO")
        self.assertEqual(promotion.available, False)
        self.assertEqual(promotion.discount, "20")

    def test_add_a_promotion(self):
        """ Create a promotion and add it to the database """
        promotions = Promotion.all()
        self.assertEqual(promotions, [])
        promotion = Promotion("A1234", "BOGO", True, "20")
        self.assertNotEqual(promotion, None)
        self.assertEqual(promotion.id, None)
        promotion.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertNotEqual(promotion.id, None)
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 1)
        self.assertEqual(promotions[0].productid, "A1234")
        self.assertEqual(promotions[0].category, "BOGO")
        self.assertEqual(promotions[0].available, True)
        self.assertEqual(promotions[0].discount, "20")

    def test_update_a_promotion(self):
        """ Update a Promotion """
        promotion = Promotion("A1234", "BOGO", True, "20")
        promotion.save()
        self.assertNotEqual(promotion.id, None)
        # Change it an save it
        promotion.category = "Percentage"
        promotion.save()
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 1)
        self.assertEqual(promotions[0].category, "Percentage")
        self.assertEqual(promotions[0].productid, "A1234")

    def test_delete_a_promotion(self):
        """ Delete a Promotion """
        promotion = Promotion("A1234", "BOGO", False, "20")
        promotion.save()
        self.assertEqual(len(Promotion.all()), 1)
        # delete the promotion and make sure it isn't in the database
        promotion.delete()
        self.assertEqual(len(Promotion.all()), 0)

    def test_serialize_a_promotion(self):
        """ Serialize a Promotion """
        promotion = Promotion("A1234", "BOGO", True, "20")
        data = promotion.serialize()
        self.assertNotEqual(data, None)
        self.assertNotIn('_id', data)
        self.assertIn('productid', data)
        self.assertEqual(data['productid'], "A1234")
        self.assertIn('category', data)
        self.assertEqual(data['category'], "BOGO")
        self.assertIn('available', data)
        self.assertEqual(data['available'], True)
        self.assertIn('discount', data)
        self.assertEqual(data['discount'], "20")

    def test_deserialize_a_promotion(self):
        """ Deserialize a Promotion """
        data = {"productid": "B4321", "category": "dollar", "available": True, "discount": "5"}
        promotion = Promotion()
        promotion.deserialize(data)
        self.assertNotEqual(promotion, None)
        self.assertEqual(promotion.id, None)
        self.assertEqual(promotion.productid, "B4321")
        self.assertEqual(promotion.category, "dollar")
        self.assertEqual(promotion.available, True)
        self.assertEqual(promotion.discount, "5")

    def test_deserialize_with_no_productid(self):
        """ Deserialize a Promotion that has no productid """
        data = {"id":0, "category": "dollar"}
        promotion = Promotion()
        self.assertRaises(DataValidationError, promotion.deserialize, data)

    def test_deserialize_with_no_data(self):
        """ Deserialize a Promotion that has no data """
        promotion = Promotion()
        self.assertRaises(DataValidationError, promotion.deserialize, None)

    def test_deserialize_with_bad_data(self):
        """ Deserialize a Promotion that has bad data """
        promotion = Promotion()
        self.assertRaises(DataValidationError, promotion.deserialize, "string data")

    def test_save_a_promotion_with_no_productid(self):
        """ Save a Promotion with no productid """
        promotion = Promotion(None, "dollar",True,"5")
        self.assertRaises(DataValidationError, promotion.save)

    def test_create_a_promotion_with_no_productid(self):
        """ Save a Promotion with no productid """
        promotion = Promotion(None, "dollar",True,"5")
        self.assertRaises(DataValidationError, promotion.create)

    def test_find_promotion(self):
        """ Find a Promotion by id """
        Promotion("A1234", "BOGO", True, "20").save()
        saved_promotion = Promotion("B4321", "dollar", False, "5")
        saved_promotion.save()
        promotion = Promotion.find(saved_promotion.id)
        self.assertIsNot(promotion, None)
        self.assertEqual(promotion.id, saved_promotion.id)
        self.assertEqual(promotion.productid, "B4321")

    def test_find_with_no_promotions(self):
        """ Find a Promotion with empty database """
        promotion = Promotion.find("1")
        self.assertIs(promotion, None)

    def test_promotion_not_found(self):
        """ Find a Promotion that doesnt exist """
        Promotion("A1234", "BOGO", True, "20").save()
        promotion = Promotion.find("2")
        self.assertIs(promotion, None)

    def test_find_by_productid(self):
        """ Find a Promotion by Productid """
        Promotion("A1234", "BOGO", True, "20").save()
        Promotion("B4321", "dollar", False, "5").save()
        promotions = Promotion.find_by_productid("A1234")
        self.assertNotEqual(len(promotions), 0)
        self.assertEqual(promotions[0].category, "BOGO")
        self.assertEqual(promotions[0].productid, "A1234")

    def test_find_by_category(self):
        """ Find a Promotion by Category """
        Promotion("A1234", "BOGO", True, "20").save()
        Promotion("B4321", "dollar", False, "5").save()
        promotions = Promotion.find_by_category("dollar")
        self.assertNotEqual(len(promotions), 0)
        self.assertEqual(promotions[0].category, "dollar")
        self.assertEqual(promotions[0].productid, "B4321")

    def test_find_by_availability(self):
        """ Find a Promotion by Availability """
        Promotion("A1234", "BOGO", True, "20").save()
        Promotion("B4321", "dollar", False, "5").save()
        promotions = Promotion.find_by_availability(True)
        self.assertEqual(len(promotions), 1)
        self.assertEqual(promotions[0].productid, "A1234")

    def test_find_by_discount(self):
        """ Find a Promotion by Discount """
        Promotion("A1234", "BOGO", True, "20").save()
        Promotion("B4321", "dollar", False, "5").save()
        promotions = Promotion.find_by_discount("20")
        self.assertEqual(len(promotions), 1)
        self.assertEqual(promotions[0].productid, "A1234")

    def test_create_query_index(self):
        """ Test create query index """
        Promotion("A1234", "BOGO", True, "20").save()
        Promotion("B4321", "dollar", False, "5").save()
        Promotion.create_query_index('category')

    def test_disconnect(self):
        """ Test Disconnet """
        Promotion.disconnect()
        promotion = Promotion("A1234", "BOGO", True, "20")
        self.assertRaises(AttributeError, promotion.save)

    @patch('cloudant.database.CloudantDatabase.create_document')
    def test_http_error(self, bad_mock):
        """ Test a Bad Create with HTTP error """
        bad_mock.side_effect = HTTPError()
        promotion = Promotion("A1234", "BOGO", True, "20")
        promotion.create()
        self.assertIsNone(promotion.id)

    @patch('cloudant.document.Document.exists')
    def test_document_not_exist(self, bad_mock):
        """ Test a Bad Document Exists """
        bad_mock.return_value = False
        promotion = Promotion("A1234", "BOGO", True, "20")
        promotion.create()
        self.assertIsNone(promotion.id)

    @patch('cloudant.database.CloudantDatabase.__getitem__')
    def test_key_error_on_update(self, bad_mock):
        """ Test KeyError on update """
        bad_mock.side_effect = KeyError()
        promotion = Promotion("A1234", "BOGO", True, "20")
        promotion.save()
        promotion.productid = 'B4321'
        promotion.update()
        #self.assertEqual(promotion.name, 'fido')

    @patch('cloudant.database.CloudantDatabase.__getitem__')
    def test_key_error_on_delete(self, bad_mock):
        """ Test KeyError on delete """
        bad_mock.side_effect = KeyError()
        promotion = Promotion("A1234", "BOGO", True, "20")
        promotion.create()
        promotion.delete()

    @patch('cloudant.client.Cloudant.__init__')
    def test_connection_error(self, bad_mock):
        """ Test Connection error handler """
        bad_mock.side_effect = ConnectionError()
        self.assertRaises(AssertionError, Promotion.init_db, 'test_promotion')


        
##    @patch.dict(os.environ, {'VCAP_SERVICES': json.dumps(VCAP_SERVICES).encode('utf8')})
#    @patch.dict(os.environ, {'VCAP_SERVICES': VCAP_SERVICES})
#    def test_vcap_services(self):
#        """ Test if VCAP_SERVICES works """
#        Promotion.init_db()
#        self.assertIsNotNone(Promotion.redis)

#    @patch('redis.Redis.ping')
#    def test_redis_connection_error(self, ping_error_mock):
#        """ Test a Bad Redis connection """
#        ping_error_mock.side_effect = ConnectionError()
#        self.assertRaises(ConnectionError, Promotion.init_db)
#        self.assertIsNone(Promotion.redis)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPromotions)
    unittest.TextTestRunner(verbosity=2).run(suite)
