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
Promotion API Service Test Suite

Test cases can be run with the following:
nosetests -v --with-spec --spec-color
"""
import unittest
import json
from werkzeug.datastructures import MultiDict, ImmutableMultiDict
from service import app
from service.models import Promotion

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
HTTP_409_CONFLICT = 409

######################################################################
#  T E S T   C A S E S
######################################################################
class TestPromotionServer(unittest.TestCase):
    """ Promotion Service tests """

    def setUp(self):
        """ Initialize the Cloudant database """
        self.app = app.test_client()
        Promotion.init_db("tests")
        Promotion.remove_all()
        Promotion("A001", "BOGO", True, 10).save()
        Promotion("A002", "B2GO", True, 10).save()
        Promotion("A003", "B3GO", False, 10).save()

    def test_index(self):
        """ Test the index page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertIn('Promotion Demo REST API Service', resp.data)

    def test_get_promotion_list(self):
        """ Get a list of Promotions """
        resp = self.app.get('/promotions')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)

    def test_get_promotion(self):
        """ get a single Promotion """
        promotion = self.get_promotion('A002')[1] # returns a list
        resp = self.app.get('/promotions/{}'.format(promotion['_id']))
        self.assertEqual(resp.status_code, HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['productid'], 'A002')

    def test_get_promotion_not_found(self):
        """ Get a Promotion that doesn't exist """
        resp = self.app.get('/promotions/0')
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)
        data = json.loads(resp.data)
        self.assertIn('was not found', data['message'])

    def test_create_promotion(self):
        """ Create a new Promotion """
        # save the current number of promotions for later comparrison
        promotion_count = self.get_promotion_count()
        # add a new promotion
        new_promotion = {'productid': 'A001', 'category': 'BOGO', 'available': True, 'discount': 10}
        data = json.dumps(new_promotion)
        resp = self.app.post('/promotions', data=data, content_type='application/json')
        # if resp.status_code == 429: # rate limit exceeded
        #     sleep(1)                # wait for 1 second and try again
        #     resp = self.app.post('/promotions', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertNotEqual(location, None)
        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['productid'], 'A001')
        # check that count has gone up and includes sammy
        resp = self.app.get('/promotions')
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertEqual(len(data), promotion_count + 1)
        self.assertIn(new_json, data)

    def test_create_promotion_from_formdata(self):
        promotion_data = MultiDict()
        promotion_data.add('productid', 'A001')
        promotion_data.add('category', 'BOGO')
        promotion_data.add('available', 'True')
        promotion_data.add('discount', '10')
        data = ImmutableMultiDict(promotion_data)
        resp = self.app.post('/promotions', data=data, content_type='application/x-www-form-urlencoded')
        self.assertEqual(resp.status_code, HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertNotEqual(location, None)
        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['productid'], 'A001')

    def test_update_promotion(self):
        """ Update a Promotion """
        promotion = self.get_promotion('A002')[1] # returns a list
        self.assertEqual(promotion['category'], 'B2GO')
        promotion['category'] = 'B3GO'
        # make the call
        data = json.dumps(promotion)
        resp = self.app.put('/promotions/{}'.format(promotion['_id']), data=data,
                            content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        # go back and get it again
        resp = self.app.get('/promotions/{}'.format(promotion['_id']), content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['category'], 'B3GO')

    def test_update_promotion_with_no_name(self):
        """ Update a Promotion without assigning a productid """
        promotion = self.get_promotion('A001')[0] # returns a list
        del promotion['productid']
        data = json.dumps(promotion)
        resp = self.app.put('/promotions/{}'.format(promotion['_id']), data=data,
                            content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_update_promotion_not_found(self):
        """ Update a Promotion that doesn't exist """
        new_A002 = {"productid": "timothy", "category": "mouse"}
        data = json.dumps(new_A002)
        resp = self.app.put('/promotions/0', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)

    def test_delete_promotion(self):
        """ Delete a Promotion """
        promotion = self.get_promotion('A001')[0] # returns a list
        # save the current number of promotions for later comparrison
        promotion_count = self.get_promotion_count()
        # delete a promotion
        resp = self.app.delete('/promotions/{}'.format(promotion['_id']), content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_promotion_count()
        self.assertEqual(new_count, promotion_count - 1)

    def test_create_promotion_with_no_name(self):
        """ Create a Promotion without a productid """
        new_promotion = {'category': 'BOGO', 'available': True}
        data = json.dumps(new_promotion)
        resp = self.app.post('/promotions', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_create_promotion_no_content_type(self):
        """ Create a Promotion with no Content-Type """
        new_promotion = {'productid': 'sammy', 'category': 'snake', 'available': True}
        data = json.dumps(new_promotion)
        resp = self.app.post('/promotions', data=data)
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_create_promotion_wrong_content_type(self):
        """ Create a Promotion with wrong Content-Type """
        data = "jimmy the fish"
        resp = self.app.post('/promotions', data=data, content_type='plain/text')
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_call_create_with_an_id(self):
        """ Call create passing an id """
        new_promotion = {'productid': 'sammy', 'category': 'snake', 'available': True}
        data = json.dumps(new_promotion)
        resp = self.app.post('/promotions/1', data=data)
        self.assertEqual(resp.status_code, HTTP_405_METHOD_NOT_ALLOWED)

    def test_query_by_name(self):
        """ Query Promotions by productid """
        resp = self.app.get('/promotions', query_string='productid=A001')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)
        self.assertIn('A001', resp.data)
        #self.assertNotIn('A002', resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['productid'], 'A001')

    def test_query_by_category(self):
        """ Query Promotions by category """
        resp = self.app.get('/promotions', query_string='category=BOGO')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)
        self.assertIn('A001', resp.data)
        self.assertNotIn('A002', resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['category'], 'BOGO')

    def test_query_by_available(self):
        """ Query Promotions by availability """
        resp = self.app.get('/promotions', query_string='available=true')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)
        # self.assertIn('A001', resp.data)
        # self.assertNotIn('A003', resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['available'], True)
    """
    def test_purchase_a_promotion(self):
    Purchase a Promotion
        promotion = self.get_promotion('A001')[0] # returns a list
        resp = self.app.put('/promotions/{}/purchase'.format(promotion['_id']), content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        resp = self.app.get('/promotions/{}'.format(promotion['_id']), content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        promotion_data = json.loads(resp.data)
        self.assertEqual(promotion_data['available'], False)

    def test_purchase_not_available(self):
        Purchase a Promotion that is not available
        promotion = self.get_promotion('A003')[0]
        resp = self.app.put('/promotions/{}/purchase'.format(promotion['_id']), content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)
        resp_json = json.loads(resp.get_data())
        self.assertIn('not available', resp_json['message'])
     """

######################################################################
# Utility functions
######################################################################

    def get_promotion(self, productid):
        """ retrieves a promotion for use in other actions """
        resp = self.app.get('/promotions',
                            query_string='productid={}'.format(productid))
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertGreater(len(resp.data), 0)
        self.assertIn(productid, resp.data)
        data = json.loads(resp.data)
        return data

    def get_promotion_count(self):
        """ save the current number of promotions """
        resp = self.app.get('/promotions')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
