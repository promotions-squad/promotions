######################################################################
# Copyright 2016, 2017 John Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################
"""
Promotion Model that uses Redis

You must initlaize this class before use by calling inititlize().
This class looks for an environment variable called VCAP_SERVICES
to get it's database credentials from. If it cannot find one, it
tries to connect to Redis on the localhost. If that fails it looks
for a server name 'redis' to connect to.
"""

import os
import json
import logging
import pickle
from cerberus import Validator
from redis import Redis
from redis.exceptions import ConnectionError
from app.custom_exceptions import DataValidationError

######################################################################
# Promotion Model for database
#   This class must be initialized with use_db(redis) before using
#   where redis is a value connection to a Redis database
######################################################################
class Promotion(object):
    """ Promotion interface to database """

    logger = logging.getLogger(__name__)
    redis = None
    schema = {
        'id': {'type': 'integer'},
        'productid': {'type': 'string', 'required': True},
        'category': {'type': 'string', 'required': True},
        'available': {'type': 'boolean', 'required': True},
        'discount': {'type': 'string', 'required': True}
        }
    __validator = Validator(schema)

    def __init__(self, id=0, productid=None, category=None, available=True, discount=None):
        """ Constructor """
        self.id = int(id)
        self.productid = productid
        self.category = category
        self.available = available
        self.discount = discount

    def save(self):
        """ Saves a Promotion in the database """
        if self.productid is None:   # productid is the only required field
            raise DataValidationError('productid attribute is not set')
        if self.id == 0:
            self.id = Promotion.__next_index()
        Promotion.redis.set(self.id, pickle.dumps(self.serialize()))

    def delete(self):
        """ Deletes a Promotion from the database """
        Promotion.redis.delete(self.id)

    def serialize(self):
        """ serializes a Promotion into a dictionary """
        return {
            "id": self.id,
            "productid": self.productid,
            "category": self.category,
            "available": self.available,
            "discount": self.discount
        }

    def deserialize(self, data):
        """ deserializes a Promotion my marshalling the data """
        if isinstance(data, dict) and Promotion.__validator.validate(data):
            self.productid = data['productid']
            self.category = data['category']
            self.available = data['available']
            self.discount = data['discount']
        else:
            raise DataValidationError('Invalid promotion data: ' + str(Promotion.__validator.errors))
        return self


######################################################################
#  S T A T I C   D A T A B S E   M E T H O D S
######################################################################

    @staticmethod
    def __next_index():
        """ Increments the index and returns it """
        return Promotion.redis.incr('index')

    # @staticmethod
    # def use_db(redis):
    #     Promotion.__redis = redis

    @staticmethod
    def remove_all():
        """ Removes all Promotions from the database """
        Promotion.redis.flushall()

    @staticmethod
    def all():
        """ Query that returns all Promotions """
        # results = [Promotion.from_dict(redis.hgetall(key)) for key in redis.keys() if key != 'index']
        results = []
        for key in Promotion.redis.keys():
            if key != 'index':  # filer out our id index
                data = pickle.loads(Promotion.redis.get(key))
                promotion = Promotion(data['id']).deserialize(data)
                results.append(promotion)
        return results

######################################################################
#  F I N D E R   M E T H O D S
######################################################################

    @staticmethod
    def find(promotion_id):
        """ Query that finds Promotions by their id """
        if Promotion.redis.exists(promotion_id):
            data = pickle.loads(Promotion.redis.get(promotion_id))
            promotion = Promotion(data['id']).deserialize(data)
            return promotion
        return None

    @staticmethod
    def __find_by(attribute, value):
        """ Generic Query that finds a key with a specific value """
        # return [promotion for promotion in Promotion.__data if promotion.category == category]
        Promotion.logger.info('Processing %s query for %s', attribute, value)
        if isinstance(value, str):
            search_criteria = value.lower() # make case insensitive
        else:
            search_criteria = value
        results = []
        for key in Promotion.redis.keys():
            if key != 'index':  # filer out our id index
                data = pickle.loads(Promotion.redis.get(key))
                # perform case insensitive search on strings
                if isinstance(data[attribute], str):
                    test_value = data[attribute].lower()
                else:
                    test_value = data[attribute]
                if test_value == search_criteria:
                    results.append(Promotion(data['id']).deserialize(data))
        return results

    @staticmethod
    def find_by_productid(productid):
        """ Query that finds Promotions by their productid """
        return Promotion.__find_by('productid', productid)

    @staticmethod
    def find_by_category(category):
        """ Query that finds Promotions by their category """
        return Promotion.__find_by('category', category)

    @staticmethod
    def find_by_availability(available=True):
        """ Query that finds Promotions by their availability """
        return Promotion.__find_by('available', available)

    @staticmethod
    def find_by_discount(discount):
        """ Query that finds Promotions by their availability """
        return Promotion.__find_by('discount', discount)

######################################################################
#  R E D I S   D A T A B A S E   C O N N E C T I O N   M E T H O D S
######################################################################

    @staticmethod
    def connect_to_redis(hostname, port, password):
        """ Connects to Redis and tests the connection """
        Promotion.logger.info("Testing Connection to: %s:%s", hostname, port)
        Promotion.redis = Redis(host=hostname, port=port, password=password)
        try:
            Promotion.redis.ping()
            Promotion.logger.info("Connection established")
        except ConnectionError:
            Promotion.logger.info("Connection Error from: %s:%s", hostname, port)
            Promotion.redis = None
        return Promotion.redis

    @staticmethod
    def init_db(redis=None):
        """
        Initialized Redis database connection

        This method will work in the following conditions:
          1) In Bluemix with Redis bound through VCAP_SERVICES
          2) With Redis running on the local server as with Travis CI
          3) With Redis --link in a Docker container called 'redis'
          4) Passing in your own Redis connection object

        Exception:
        ----------
          redis.ConnectionError - if ping() test fails
        """
        if redis:
            Promotion.logger.info("Using client connection...")
            Promotion.redis = redis
            try:
                Promotion.redis.ping()
                Promotion.logger.info("Connection established")
            except ConnectionError:
                Promotion.logger.error("Client Connection Error!")
                Promotion.redis = None
                raise ConnectionError('Could not connect to the Redis Service')
            return
        # Get the credentials from the Bluemix environment
        if 'VCAP_SERVICES' in os.environ:
            Promotion.logger.info("Using VCAP_SERVICES...")
            vcap_services = os.environ['VCAP_SERVICES']
            services = json.loads(vcap_services)
            creds = services['rediscloud'][0]['credentials']
            Promotion.logger.info("Conecting to Redis on host %s port %s",
                            creds['hostname'], creds['port'])
            Promotion.connect_to_redis(creds['hostname'], creds['port'], creds['password'])
        else:
            Promotion.logger.info("VCAP_SERVICES not found, checking localhost for Redis")
            Promotion.connect_to_redis('127.0.0.1', 6379, None)
            if not Promotion.redis:
                Promotion.logger.info("No Redis on localhost, looking for redis host")
                Promotion.connect_to_redis('redis', 6379, None)
        if not Promotion.redis:
            # if you end up here, redis instance is down.
            Promotion.logger.fatal('*** FATAL ERROR: Could not connect to the Redis Service')
            raise ConnectionError('Could not connect to the Redis Service')
