
"""
Test cases for Promotion Model
Test cases can be run with:
  nosetests
  coverage report -m
"""
import datetime
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

    def test_create_a_promotion(self):
        """ Create a promotion and assert that it exists """
        promotion = Promotion(productid="1234",
                              category="dollar",
                              available=True,
                              discount=5.0)
#                              startdate=datetime.date.today(),
#                              enddate=datetime.date.today()+datetime.timedelta(days=10))
        self.assertTrue(promotion != None)
        self.assertEqual(promotion.id, None)
        self.assertEqual(promotion.productid, "1234")
        self.assertEqual(promotion.category, "dollar")
        self.assertEqual(promotion.available, True)
        self.assertEqual(promotion.discount, 5.0)
#        self.assertEqual(promotion.startdate, datetime.date.today())
#        self.assertEqual(promotion.enddate, datetime.date.today()+datetime.timedelta(days=10))

    def test_add_a_promotion(self):
        """ Create a promotion and add it to the database """
        promotions = Promotion.all()
        self.assertEqual(promotions, [])
        promotion = Promotion(productid="1234",
                              category="dollar",
                              available=True,
                              discount=5.0)
#                              startdate=datetime.date.today(),
#                              enddate=datetime.date.today()+datetime.timedelta(days=10))
        self.assertTrue(promotion != None)
        self.assertEqual(promotion.id, None)
        promotion.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(promotion.id, 1)
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 1)

    def test_update_a_promotion(self):
        """ Update a Promotion """
        promotion = Promotion(productid="1234",
                              category="dollar",
                              available=True,
                              discount=5.0)
#                              startdate=datetime.date.today(),
#                              enddate=datetime.date.today()+datetime.timedelta(days=10))
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


    def test_delete_a_promotion(self):
        """ Delete a Pet """
        promotion = Promotion(productid="1234",
                              category="dollar",
                              available=True,
                              discount=5.0)
#                              startdate=datetime.date.today(),
#                              enddate=datetime.date.today()+datetime.timedelta(days=10))
        promotion.save()
        self.assertEqual(len(Promotion.all()), 1)
        # delete the promotion and make sure it isn't in the database
        promotion.delete()
        self.assertEqual(len(Promotion.all()), 0)

    def test_serialize_a_promotion(self):
        """ Test serialization of a Promotion """
        promotion = Promotion(productid="1234",
                              category="dollar",
                              available=True,
                              discount=5.0)
#                              startdate=datetime.date.today(),
#                              enddate=datetime.date.today()+datetime.timedelta(days=10))
        data = promotion.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], None)
        self.assertIn('productid', data)
        self.assertEqual(data['productid'], "1234")
        self.assertIn('category', data)
        self.assertEqual(data['category'], "dollar")
        self.assertIn('available', data)
        self.assertEqual(data['available'], True)
        self.assertIn('discount', data)
        self.assertEqual(data['discount'], 5.0)
#        self.assertIn('startdate', data)
#        self.assertEqual(data['startdate'], datetime.date.today())
#        self.assertIn('enddate', data)
#        self.assertEqual(data['enddate'], datetime.date.today()+datetime.timedelta(days=10))



    def test_deserialize_a_promotion(self):
        """ Test deserialization of a Promotion """
        data = {"id": 1,
                "productid": "4321",
                "category": "percentage",
                "available": True,
                "discount":5.0}
#                "startdate": datetime.date.today(),
#                "enddate": datetime.date.today()+datetime.timedelta(days=10)
#        }
        promotion = Promotion()
        promotion.deserialize(data)
        self.assertNotEqual(promotion, None)
        self.assertEqual(promotion.id, None)
        self.assertEqual(promotion.productid, "4321")
        self.assertEqual(promotion.category, "percentage")
        self.assertEqual(promotion.available, True)
        self.assertEqual(promotion.discount, 5.0)
#        self.assertEqual(promotion.startdate, datetime.date.today())
#        self.assertEqual(promotion.enddate, datetime.date.today()+datetime.timedelta(days=10))


    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        promotion = Promotion()
        self.assertRaises(DataValidationError, promotion.deserialize, data)

    def test_find_promotion(self):
        """ Find a Promotion by ID """
        Promotion(productid="1234",
                  category="dollar",
                  available=True,
                  discount=5.0)
#                  startdate=datetime.date.today(),
#                  enddate=datetime.date.today()+datetime.timedelta(days=10)).save()
        promo = Promotion(productid="4321",
                          category="percentage",
                          available=False,
                          discount = 20.0)
#                          startdate = datetime.date.today(),
#                          enddate = datetime.date.today()+datetime.timedelta(days=10)
        promo.save()
        promotion = Promotion.find_or_404(promo.id)
        self.assertIsNot(promotion, None)
        self.assertEqual(promotion.id, promo.id)
        self.assertEqual(promotion.productid, "4321")
        self.assertEqual(promotion.category, "percentage")
        self.assertEqual(promotion.available, False)
        self.assertEqual(promotion.discount, 20.0)
#        self.assertEqual(promotion.startdate, datetime.date.today())
#        self.assertEqual(promotion.enddate, datetime.date.today()+datetime.timedelta(days=10))


    def test_find_by_category(self):
        """ Find Promotions by Category """
        Promotion(productid="1234",
                  category="dollar",
                  available=True,
                  discount=5.0)
#                  startdate=datetime.date.today(),
#                  enddate=datetime.date.today()+datetime.timedelta(days=10)).save()
        Promotion(productid="4321",
                  category="percentage",
                  available=False,
                  discount=20.0,
#                  startdate=datetime.date.today(),
#                  enddate=datetime.date.today()+datetime.timedelta(days=10)).save()
        promotions = Promotion.find_by_category("percentage")
        self.assertEqual(promotions[0].category, "percentage")
        self.assertEqual(promotions[0].productid, "4321")
        self.assertEqual(promotions[0].available, False)
        self.assertEqual(promotions[0].discount, 20.0)
#        self.assertEqual(promotions[0].startdate, datetime.date.today())
#        self.assertEqual(promotions[0].enddate, datetime.date.today()+datetime.timedelta(days=10))

    def test_find_by_product(self):
        """ Find a Promotion by productid """
        Promotion(productid="1234",
                  category="dollar",
                  available=True,
                  discount=5.0)
#                  startdate=datetime.date.today(),
#                  enddate=datetime.date.today()+datetime.timedelta(days=10)).save()
        Promotion(productid="4321",
                  category="percentage",
                  available=False,
                  discount=20.0)
#                  startdate=datetime.date.today(),
#                  enddate=datetime.date.today()+datetime.timedelta(days=10)).save()
        promotions = Promotion.find_by_product("4321")
        self.assertEqual(promotions[0].category, "percentage")
        self.assertEqual(promotions[0].productid, "4321")
        self.assertEqual(promotions[0].available, False)
        self.assertEqual(promotions[0].discount, 20.0)
#        self.assertEqual(promotions[0].startdate, datetime.date.today())
#        self.assertEqual(promotions[0].enddate, datetime.date.today()+datetime.timedelta(days=10))

    def test_find_by_availability(self):
        """ Find a Promotion by availability """
        Promotion(productid="1234",
                  category="dollar",
                  available=True,
                  discount=5.0)
#                  startdate=datetime.date.today(),
#                  enddate=datetime.date.today()+datetime.timedelta(days=10)).save()
        Promotion(productid="4321",
                  category="percentage",
                  available=False,
                  discount=20.0)
#                  startdate=datetime.date.today(),
#                  enddate=datetime.date.today()+datetime.timedelta(days=10)).save()
        promotions = Promotion.find_by_availability(False)
        self.assertEqual(promotions[0].category, "percentage")
        self.assertEqual(promotions[0].productid, "4321")
        self.assertEqual(promotions[0].available, False)
        self.assertEqual(promotions[0].discount, 20.0)
#        self.assertEqual(promotions[0].startdate, datetime.date.today())
#        self.assertEqual(promotions[0].enddate, datetime.date.today()+datetime.timedelta(days=10))


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
