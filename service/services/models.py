from django.db import models
from django.core.validators import MaxValueValidator
from django.db.models.signals import post_delete

from services.receivers import delete_cache_total_sum
from services.tasks import set_price, set_comment


class Service(models.Model):
    name = models.CharField(max_length=50)
    full_price = models.PositiveIntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_price = self.full_price

    def save(self, *args, **kwargs):
        if self.__original_price != self.full_price:
            for subscription in self.subscriptions.all():
                set_comment.delay(subscription.id)
                set_price.delay(subscription.id)
        super().save(*args, **kwargs)


class Plan(models.Model):
    PLAN_TYPES = (
        ('full', 'Full'),
        ('student', 'Student'),
        ('discount', 'Discount'),
    )

    plan_type = models.CharField(max_length=10, choices=PLAN_TYPES)
    discount_percent = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_discount_percent = self.discount_percent

    def save(self, *args, **kwargs):
        if self.__original_discount_percent != self.discount_percent:
            for subscription in self.subscriptions.all():
                set_comment.delay(subscription.id)
                set_price.delay(subscription.id)
        super().save(*args, **kwargs)


class Subscription(models.Model):
    client = models.ForeignKey('clients.Client', on_delete=models.PROTECT, related_name='subscriptions')
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='subscriptions')
    price = models.PositiveIntegerField(default=0)
    comment = models.CharField(max_length=255, blank=True, null=True, default='')


    def save(self, *args, **kwargs):
        creating = not bool(self.id)
        result = super().save(*args, **kwargs)
        if creating:
            set_price.delay(self.id)
        return result


post_delete.connect(delete_cache_total_sum, sender=Subscription)
