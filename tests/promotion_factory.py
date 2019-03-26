"""
Test Factory to make fake objects for testing
"""
import factory
import datetime
from factory.fuzzy import FuzzyChoice
from app.models import Promotion


class PromotionFactory(factory.Factory):
    """ Creates fake promotions that you don't have to maintain """
    class Meta:
        model = Promotion
    id = factory.Sequence(lambda n: n)
    product_id = factory.Faker('tshirt001')
    category = FuzzyChoice(choices=['DollarDiscount', 'PercentDiscount'])
    available = FuzzyChoice(choices=[True, False])
    discount = FuzzyDecimal(50.0)
    start_date = factory.LazyFunction(datetime.date.today)
    end_date = factory.LadyFunction(datetime.date.today+datetime.timedelta(days=10))

if __name__ == '__main__':
    for _ in range(10):
        promotion = PromotionFactory()
        print(promotion.serialize())
