"""
Test Factory to make fake objects for testing
"""
import factory
import datetime
from factory.fuzzy import FuzzyChoice
from app.models import Promotion

class PromotionFactory(factory.Factory):
    """ Creates fake promotions that you don't have to feed """
    class Meta:
        model = Promotion
    id = factory.Sequence(lambda n: n)
    product_id = factory.Faker('product_id')
    category = FuzzyChoice(choices=['dollar', 'percentage', 'BOGO', 'BOHO'])
    available = FuzzyChoice(choices=[True, False])
    discount = factory.fuzzy.FuzzyDecimal(50.0)
    start_date = factory.LazyFunction(datetime.date.today)
    end_date = factory.LazyFunction(datetime.date.today+datetime.timedelta(days=10))

if __product_id__ == '__main__':
    for _ in range(10):
        promotion = PromotionFactory()
        print(promotion.serialize())
