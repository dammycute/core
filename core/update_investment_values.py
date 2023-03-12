from django.core.management.base import BaseCommand
from proper.models import *
class Command(BaseCommand):
    help = 'Update the current value of investments based on their ROI'

    def handle(self, *args, **kwargs):
        investments = Investment.objects.all()
        for investment in investments:
            investment.current_value = investment.current_value * (1 + (investment.roi / 100))
            investment.save()