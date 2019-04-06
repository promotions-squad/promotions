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
"""
Models for Promotion Demo Service
All of the models are stored in this module
Models
------
Promotion - A Promotion used in the Store
Attributes:
-----------
productid (float) - the productid the promotion applies to
category (string) - the category the promotion belongs to (i.e., percentage, dollar amount off)
available (boolean) - True for promotions that are enabled for a productid
discount (float) - the amount of the promotional discount (for percentage will be a decimal, for dollar will be a number)
startdate (datetime) - starting date of promotion
enddate (datetime) - ending date of promotion
"""
import logging
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

class Promotion(db.Model):
    """
    Class that represents a Promotion
    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """
    logger = logging.getLogger(__name__)
    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    productid = db.Column(db.Float())
    category = db.Column(db.String(63))
    available = db.Column(db.Boolean())
    discount = db.Column(db.Float())
#    startdate = db.Column(db.Date())
#    enddate = db.Column(db.Date())

    def __repr__(self):
        return '<Promotion %r>' % (self.productid)

    def save(self):
        """
        Saves a Promotion to the data store
        """
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        """ Removes a Promotion from the data store """
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Promotion into a dictionary """
        return {"id": self.id,
                "productid": self.productid,
                "category": self.category,
                "available": self.available,
		"discount": self.discount}
#		"startdate": self.startdate,
#		"enddate": self.enddate}

    def deserialize(self, data):
        """
        Deserializes a Promotion from a dictionary
        Args:
            data (dict): A dictionary containing the Promotion data
        """
        try:
            self.productid = data['productid']
            self.category = data['category']
            self.available = data['available']
            self.discount = data['discount']
#	    self.startdate = data['startdate']
#	    self.enddate = data['enddate']
        except KeyError as error:
            raise DataValidationError('Invalid Promotion: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid Promotion: body of request contained' \
                                      'bad or no data')
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        cls.logger.info('Initializing database')
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Promotions in the database """
        cls.logger.info('Processing all Promotions')
        return cls.query.all()

    @classmethod
    def find(cls, id):
        """ Finds a Promotion by it's ID """
        cls.logger.info('Processing lookup for id %s ...', id)
        return cls.query.get(id)

    @classmethod
    def find_or_404(cls, promotion_id):
        """ Find a Promotion by it's id """
        cls.logger.info('Processing lookup or 404 for id %s ...', id)
        return cls.query.get_or_404(promotion_id)

    @classmethod
    def find_by_product(cls, productid):
        """ Returns all Promotions for a specific product
        Args:
            available (string): productid
        """
        cls.logger.info('Processing productid query for %s ...', productid)
        return cls.query.filter(cls.productid == productid)

    @classmethod
    def find_by_category(cls, category):
        """ Returns all of the Promotions in a category
        Args:
            category (string): the category of the Promotions you want to match
        """
        cls.logger.info('Processing category query for %s ...', category)
        return cls.query.filter(cls.category == category)

    @classmethod
    def find_by_availability(cls, available=True):
        """ Query that finds Promotions by their availability """
        """ Returns all Promotions by their availability
        Args:
            available (boolean): True for promotions that are available
        """
        cls.logger.info('Processing available query for %s ...', available)
        return cls.query.filter(cls.available == available)
