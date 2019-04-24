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

# import os
# import json
import unittest
from mock import MagicMock, patch
from requests import HTTPError, ConnectionError
from service.models import Promotion, DataValidationError

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

######################################################################
#  T E S T   C A S E S
######################################################################
class TestPromotions(unittest.TestCase):
    """ Test Cases for Promotion Model """

    def setUp(self):
        """ Initialize the Cloudant database """
        Promotion.init_db("test")
        Promotion.remove_all()

    def test_create_a_promotion(self):
        """ Create a promotion and assert that it exists """
        promotion = Promotion("A002", "BOGO", True, 10)
        self.assertNotEqual(promotion, None)
        #self.assertEqual(promotion.id, None)
        self.assertEqual(promotion.productid, "A002")
        self.assertEqual(promotion.category, "BOGO")
        self.assertEqual(promotion.available, True)
        self.assertEqual(promotion.discount, 10)

    def test_add_a_promotion(self):
        """ Create a promotion and add it to the database """
        promotions = Promotion.all()
        self.assertEqual(promotions, [])
        promotion = Promotion("A002", "BOGO", True, 10)
        self.assertNotEqual(promotion, None)
        self.assertEqual(promotion.id, None)
        promotion.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertNotEqual(promotion.id, None)
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 1)
        self.assertEqual(promotions[0].productid, "A002")
        self.assertEqual(promotions[0].category, "BOGO")
        self.assertEqual(promotions[0].available, True)
        self.assertEqual(promotions[0].discount, 10)

    def test_update_a_promotion(self):
        """ Update a Promotion """
        promotion = Promotion("A002", "dog", True)
        promotion.save()
        self.assertNotEqual(promotion.id, None)
        # Change it an save it
        promotion.category = "k9"
        promotion.save()
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 1)
        self.assertEqual(promotions[0].category, "k9")
        self.assertEqual(promotions[0].productid, "A002")

    def test_delete_a_promotion(self):
        """ Delete a Promotion """
        promotion = Promotion("A002", "dog")
        promotion.save()
        self.assertEqual(len(Promotion.all()), 1)
        # delete the promotion and make sure it isn't in the database
        promotion.delete()
        self.assertEqual(len(Promotion.all()), 0)

    def test_serialize_a_promotion(self):
        """ Serialize a Promotion """
        promotion = Promotion("A002", "dog", False)
        data = promotion.serialize()
        self.assertNotEqual(data, None)
        self.assertNotIn('_id', data)
        self.assertIn('productid', data)
        self.assertEqual(data['productid'], "A002")
        self.assertIn('category', data)
        self.assertEqual(data['category'], "dog")
        self.assertIn('available', data)
        self.assertEqual(data['available'], False)

    def test_deserialize_a_promotion(self):
        """ Deserialize a Promotion """
        data = {"productid": "A002", "category": "BOGO", "available": True, "discount": 10 }
        promotion = Promotion()
        promotion.deserialize(data)
        self.assertNotEqual(promotion, None)
        #self.assertEqual(promotion.id, None)
        self.assertEqual(promotion.productid, "A002")
        self.assertEqual(promotion.category, "BOGO")
        self.assertEqual(promotion.available, True)
        self.assertEqual(promotion.discount, 10)

    def test_deserialize_with_no_name(self):
        """ Deserialize a Promotion that has no name """
        data = {"id":0, "category": "cat"}
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

    def test_save_a_promotion_with_no_name(self):
        """ Save a Promotion with no name """
        promotion = Promotion(None, "cat")
        self.assertRaises(DataValidationError, promotion.save)

    def test_create_a_promotion_with_no_name(self):
        """ Create a Promotion with no name """
        promotion = Promotion(None, "cat")
        self.assertRaises(DataValidationError, promotion.create)

    def test_find_promotion(self):
        """ Find a Promotion by id """
        Promotion("A002", "dog").save()
        # saved_promotion = Promotion("kitty", "cat").save()
        saved_promotion = Promotion("kitty", "cat")
        saved_promotion.save()
        promotion = Promotion.find(saved_promotion.id)
        self.assertIsNot(promotion, None)
        self.assertEqual(promotion.id, saved_promotion.id)
        self.assertEqual(promotion.productid, "kitty")

    def test_find_with_no_promotions(self):
        """ Find a Promotion with empty database """
        promotion = Promotion.find("1")
        self.assertIs(promotion, None)

    def test_promotion_not_found(self):
        """ Find a Promotion that doesnt exist """
        Promotion("A002", "dog").save()
        promotion = Promotion.find("2")
        self.assertIs(promotion, None)

    #def test_find_by_name(self):
    #    """ Find a Promotion by Name """
    #    Promotion("A002", "BOGO").save()
    #    Promotion("A002", "BOGO").save()
    #    promotions = Promotion.find_by_name("A002")
    #    self.assertNotEqual(len(promotions), 0)
    #    self.assertEqual(promotions[0].category, "BOGO")
    #    self.assertEqual(promotions[0].productid, "A002")

    def test_find_by_category(self):
        """ Find a Promotion by Category """
        Promotion("A002", "dog").save()
        Promotion("kitty", "cat").save()
        promotions = Promotion.find_by_category("cat")
        self.assertNotEqual(len(promotions), 0)
        self.assertEqual(promotions[0].category, "cat")
        self.assertEqual(promotions[0].productid, "kitty")

    def test_find_by_availability(self):
        """ Find a Promotion by Availability """
        Promotion("A002", "dog", False).save()
        Promotion("kitty", "cat", True).save()
        promotions = Promotion.find_by_availability(True)
        self.assertEqual(len(promotions), 1)
        self.assertEqual(promotions[0].productid, "kitty")

    def test_create_query_index(self):
        """ Test create query index """
        Promotion("A002", "dog", False).save()
        Promotion("kitty", "cat", True).save()
        Promotion.create_query_index('category')

    def test_disconnect(self):
        """ Test Disconnet """
        Promotion.disconnect()
        promotion = Promotion("A002", "dog", False)
        self.assertRaises(AttributeError, promotion.save)

    @patch('cloudant.database.CloudantDatabase.create_document')
    def test_http_error(self, bad_mock):
        """ Test a Bad Create with HTTP error """
        bad_mock.side_effect = HTTPError()
        promotion = Promotion("A002", "dog", False)
        promotion.create()
        self.assertIsNone(promotion.id)

    @patch('cloudant.document.Document.exists')
    def test_document_not_exist(self, bad_mock):
        """ Test a Bad Document Exists """
        bad_mock.return_value = False
        promotion = Promotion("A002", "dog", False)
        promotion.create()
        self.assertIsNone(promotion.id)

    @patch('cloudant.database.CloudantDatabase.__getitem__')
    def test_key_error_on_update(self, bad_mock):
        """ Test KeyError on update """
        bad_mock.side_effect = KeyError()
        promotion = Promotion("A002", "dog", False)
        promotion.save()
        promotion.productid = 'Fifi'
        promotion.update()
        #self.assertEqual(promotion.name, 'A002')

    @patch('cloudant.database.CloudantDatabase.__getitem__')
    def test_key_error_on_delete(self, bad_mock):
        """ Test KeyError on delete """
        bad_mock.side_effect = KeyError()
        promotion = Promotion("A002", "dog", False)
        promotion.create()
        promotion.delete()

    @patch('cloudant.client.Cloudant.__init__')
    def test_connection_error(self, bad_mock):
        """ Test Connection error handler """
        bad_mock.side_effect = ConnectionError()
        self.assertRaises(AssertionError, Promotion.init_db, 'test')


#     def test_http_error(self):
    # @patch.dict(os.environ, {'VCAP_SERVICES': json.dumps(VCAP_SERVICES)})
    # def test_vcap_services(self):
    #     """ Test if VCAP_SERVICES works """
    #     Promotion.init_db()
    #     self.assertIsNotNone(Promotion.client)
    #     Promotion("A002", "dog", True).save()
    #     promotions = Promotion.find_by_name("A002")
    #     self.assertNotEqual(len(promotions), 0)
    #     self.assertEqual(promotions[0].name, "A002")


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPromotions)
    unittest.TextTestRunner(verbosity=2).run(suite)
