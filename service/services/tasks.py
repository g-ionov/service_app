from celery import shared_task
from django.db.models import F


@shared_task
def set_price(subscriptions_id):
    from services.models import Subscription
    subscription = Subscription.objects.filter(id=subscriptions_id).annotate(
        annotated_price=F('service__full_price') - F('service__full_price') * F('plan__discount_percent') / 100.00)[0]
    subscription.price = subscription.annotated_price
    subscription.save()