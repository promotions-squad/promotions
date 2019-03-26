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
product_id (string) - the product_id the promotion applies to
category (string) - the category the promotion belongs to (i.e., percentage, dollar amount off)
available (boolean) - True for promotions that are enabled for a product_id
discount (float) - the amount of the promotional discount (for percentage will be a decimal, for dollar will be a number)
start_date (datetime) - starting date of promotion
end_date (datetime) - ending date of promotion
"""
import logging
from flask_sqlalchemy import SQLAlchemy

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
    product_id = db.Column(db.String(63))
    category = db.Column(db.String(63))
    available = db.Column(db.Boolean())
    discount = db.Column(db.Float())
    start_date = db.Column(db.datetime())
    end_date = db.Column(db.datetime())

    def __repr__(self):
        return '<Promotion %r>' % (self.proudct_id)

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
                "product_id": self.product_id,
                "category": self.category,
                "available": self.available,
		"discount": self.discount,
		"start_date": self.start_date,
		"end_date": self.end_date}

    def deserialize(self, data):
        """
        Deserializes a Promotion from a dictionary
        Args:
            data (dict): A dictionary containing the Promotion data
        """
        try:
            self.product_id = data['product_id']
            self.category = data['category']
            self.available = data['available']
	    self.discount = data['discount']
	    self.start_date = data['start_date']
	    self.end_date = data['end_date']
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
    def find_or_404(cls, id):
        """ Find a Promotion by it's id """
        cls.logger.info('Processing lookup or 404 for id %s ...', id)
        return cls.query.get_or_404(id)

    @classmethod
    def find_by_product(cls, product_id):
        """ Returns all Promotions for a specific product
        Args:
            available (string): product_id
        """
        cls.logger.info('Processing product_id query for %s ...', product_id)
        return cls.query.filter(cls.product_id == product_id)

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
