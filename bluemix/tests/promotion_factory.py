"""
Test Factory to make fake objects for testing
"""
import factory
#import datetime
#import factory.fuzzy as ff
from factory.fuzzy import FuzzyChoice
from factory.fuzzy import FuzzyFloat
from factory.fuzzy import FuzzyText
from factory.fuzzy import FuzzyInteger
from app.models import Promotion

class PromotionFactory(factory.Factory):
    """ Creates fake promotions that you don't have to feed """
    class Meta:
        model = Promotion
    id = factory.Sequence(lambda n: n)
    productid = FuzzyInteger(0,9999)
    category = FuzzyChoice(choices=['dollar', 'percentage', 'BOGO', 'BOHO'])
    available = FuzzyChoice(choices=[True, False])
    discount = FuzzyFloat(50)
#    startdate = ff.FuzzyDate(datetime.date.today()-datetime.timedelta(days=10),
#                              datetime.date.today())
#    enddate = ff.FuzzyDate(datetime.date.today(),
#                            datetime.date.today()+datetime.timedelta(days=10))

if __name__ == '__main__':
    for _ in range(10):
        promotion = PromotionFactory()
        print(promotion.serialize())
