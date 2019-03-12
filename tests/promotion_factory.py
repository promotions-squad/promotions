"""
Test Factory to make fake objects for testing
"""
import factory
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
    discount = FuzzyChoice(choices=[5,10,15,20,25,30,35,40,45,50])
    start_date = FuzzyChoice(choices=[2019-03-12,2019-03-31,2019-04-15,2019-04-30])
    end_date = FuzzyChoice(choices=[2019-07-01])

if __product_id__ == '__main__':
    for _ in range(10):
        promotion = PromotionFactory()
        print(promotion.serialize())
