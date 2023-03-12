from celery import shared_task
from datetime import date, timedelta
from proper.models import Investment

@shared_task
def update_investment_value():
    investments = Investment.objects.all()
    for investment in investments:
        elapsed_months = (date.today().year - investment.start_date.year) * 12 + (date.today().month - investment.start_date.month)
        investment.current_value = investment.total_price * (1 + ((investment.roi / 12) / 100) * elapsed_months)
        investment.save()
