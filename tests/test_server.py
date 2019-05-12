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
Pet API Service Test Suite

Test cases can be run with the following:
nosetests -v --with-spec --spec-color
"""

import unittest
import logging
from werkzeug.datastructures import MultiDict, ImmutableMultiDict
#import json
from app import server

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
HTTP_409_CONFLICT = 409
HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415

######################################################################
#  T E S T   C A S E S
######################################################################
class TestPromotionServer(unittest.TestCase):
    """ Promotion Service tests """

    def setUp(self):
        self.app = server.app.test_client()
        server.initialize_logging(logging.INFO)
        server.init_db()
        server.data_reset()
        server.data_load({"productid": "A1234", "category": "BOGO", "available": True, "discount": "20"})
        server.data_load({"productid": "B4321", "category": "Percentage", "available": True, "discount": "50"})

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
        promotion = self.get_promotion('B4321')[0] # returns a list
        resp = self.app.get('/promotions/{}'.format(promotion['_id']))
        #resp = self.app.get('/promotions/2')
        #print 'resp_data: ' + resp.data
        self.assertEqual(resp.status_code, HTTP_200_OK)
        data = resp.get_json()
        #data = json.loads(resp.data)
        self.assertEqual(data['productid'], 'B4321')

    def test_get_promotion_not_found(self):
        """ Get a Promotion that doesn't exist """
        resp = self.app.get('/promotions/0')
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)
        data = resp.get_json()
        #data = json.loads(resp.data)
        self.assertIn('was not found', data['message'])

    def test_create_promotion(self):
        """ Create a new Promotion """
        # save the current number of promotions for later comparrison
        promotion_count = self.get_promotion_count()
        # add a new promotion
        new_promotion = {'productid': 'C1111', 'category': 'Dollar', 'available': True, 'discount': "5"}
        #data = json.dumps(new_promotion)
        #resp = self.app.post('/promotions', data=data, content_type='application/json')
        resp = self.app.post('/promotions', json=new_promotion, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertNotEqual(location, None)
        # Check the data is correct
        #new_json = json.loads(resp.data)
        new_json = resp.get_json()
        self.assertEqual(new_json['productid'], 'C1111')
        # check that count has gone up
        resp = self.app.get('/promotions')
        # print 'resp_data(2): ' + resp.data
        #data = json.loads(resp.data)
        data = resp.get_json()
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertEqual(len(data), promotion_count + 1)
        self.assertIn(new_json, data)

    def test_create_promotion_from_formdata(self):
        promotion_data = MultiDict()
        promotion_data.add('productid', 'D0003')
        promotion_data.add('category', 'Percentage')
        promotion_data.add('available', 'True')
        promotion_data.add('discount', '15')
        data = ImmutableMultiDict(promotion_data)
        resp = self.app.post('/promotions', data=data, content_type='application/x-www-form-urlencoded')
        self.assertEqual(resp.status_code, HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertNotEqual(location, None)
        # Check the data is correct
        new_json = resp.get_json()
        self.assertEqual(new_json['productid'], 'D0003')

    def test_update_promotion(self):
        """ Update a Promotion """
        promotion = self.get_promotion('B4321')[0] # returns a list
        self.assertEqual(promotion['category'], 'Percentage')
        promotion['category'] = 'Dollar'
        # make the call
        resp = self.app.put('/promotions/{}'.format(promotion['_id']), json=promotion,
                            content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        # go back and get it again
        resp = self.app.get('/promotions/{}'.format(promotion['_id']), content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        new_json = resp.get_json()
        self.assertEqual(new_json['category'], 'Dollar')

    def test_update_promotion_with_no_productid(self):
        """ Update a Promotion without assigning a productid """
        promotion = self.get_promotion('A1234')[0] # returns a list
        del promotion['productid']
        resp = self.app.put('/promotions/{}'.format(promotion['_id']), json=promotion,
                            content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_update_promotion_not_found(self):
        """ Update a Promotion that doesn't exist """
        new_promo = {"productid": "D0001", "category": "Percentage"}
        #data = json.dumps(new_promo)
        #resp = self.app.put('/promotions/0', data=data, content_type='application/json')
        resp = self.app.put('/promotions/0', json=new_promo, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)

    def test_delete_promotion(self):
        """ Delete a Promotion """
        promotion = self.get_promotion('A1234')[0] # returns a list
        # save the current number of promotions for later comparrison
        promotion_count = self.get_promotion_count()
        # delete a promotion
        resp = self.app.delete('/promotions/{}'.format(promotion['_id']), content_type='application/json')
#        resp = self.app.delete('/promotions/2', content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_promotion_count()
        self.assertEqual(new_count, promotion_count - 1)

    def test_create_promotion_with_no_productid(self):
        """ Create a Promotion without a productid """
        new_promotion = {'category': 'BOGO', 'available': True, 'Discount': '50'}
        #data = json.dumps(new_promotion)
        #resp = self.app.post('/promotions', data=data, content_type='application/json')
        resp = self.app.post('/promotions', json=new_promotion, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_create_promotion_no_content_type(self):
        """ Create a Promotion with no Content-Type """
        resp = self.app.post('/promotions', data="new_promotion")
        self.assertEqual(resp.status_code, HTTP_415_UNSUPPORTED_MEDIA_TYPE)

#        new_promotion = {'category': 'BOGO'}
#        data = json.dumps(new_promotion)
#        resp = self.app.post('/promotions', data=data)
#        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_get_nonexisting_promotion(self):
        """ Get a nonexisting Promotion """
        resp = self.app.get('/promotions/5')
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)

    def test_create_promotion_wrong_content_type(self):
        """ Create a Promotion with wrong Content-Type """
        data = "BOGO for productid E123"
        resp = self.app.post('/promotions', data=data, content_type='plain/text')
        self.assertEqual(resp.status_code, HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_call_create_with_an_id(self):
        """ Call create passing an id """
        new_promotion = {'productid': 'E0007', 'category': 'percentage'}
        #data = json.dumps(new_promotion)
        #resp = self.app.post('/promotions/1', data=data)
        resp = self.app.post('/promotions/1', json=new_promotion)
        self.assertEqual(resp.status_code, HTTP_405_METHOD_NOT_ALLOWED)

    def test_query_by_productid(self):
        """ Query Promotions by productid """
        resp = self.app.get('/promotions', query_string='productid=A1234')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)
        self.assertIn('A1234', resp.data)
        self.assertNotIn('B4321', resp.data)
        data = resp.get_json()
        query_item = data[0]
        self.assertEqual(query_item['productid'], 'A1234')

    def test_query_by_category(self):
        """ Query Promotions by category """
        resp = self.app.get('/promotions', query_string='category=BOGO')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)
        self.assertIn('A1234', resp.data)
        self.assertNotIn('B4321', resp.data)
        data = resp.get_json()
        query_item = data[0]
        self.assertEqual(query_item['category'], 'BOGO')

    def test_query_by_available(self):
        """ Query Promotions by availability """
        resp = self.app.get('/promotions', query_string='available=true')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)
        # self.assertIn('fido', resp.data)
        # self.assertNotIn('harry', resp.data)
        data = resp.get_json()
        query_item = data[0]
        self.assertEqual(query_item['available'], True)

    def test_cancel_a_promotion(self):
        """ Cancel a Promotion """
        promotion = self.get_promotion('A1234')[0] # returns a list
        resp = self.app.put('/promotions/{}/cancel'.format(promotion['_id']), content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        resp = self.app.get('/promotions/{}'.format(promotion['_id']), content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        promotion_data = resp.get_json()
        self.assertEqual(promotion_data['available'], False)

        #resp = self.app.put('/promotions/2/cancel', content_type='application/json')
        #self.assertEqual(resp.status_code, HTTP_200_OK)
        #resp = self.app.get('/promotions/2', content_type='application/json')
        #self.assertEqual(resp.status_code, HTTP_200_OK)
        #promotion_data = json.loads(resp.data)
        #self.assertEqual(promotion_data['available'], False)

    def test_cancel_not_available(self):
        """ Cancel a Promotion that does not exist """
        resp = self.app.put('/promotions/5/cancel', content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)
        #resp_json = json.loads(resp.get_data())
        resp_json = resp.get_json()
        self.assertIn('not found', resp_json['message'])

    def test_reset_promotion_data(self):
        resp = self.app.delete('/promotions/reset',content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_204_NO_CONTENT)


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
        data = resp.get_json()
        return data

    def get_promotion_count(self):
        """ save the current number of promotions """
        resp = self.app.get('/promotions')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        #data = json.loads(resp.data)
        data = resp.get_json()
        return len(data)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
