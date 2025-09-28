from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from pms.models import Rent
from api.twilio_util.sms import send_sms
from api.rent import RENT_ACTIVE,RENT_TERMINATED,RENT_MONTHLY_CYCLE,RENT_QUARTERLY_CYCLE,RENT_WEEKLY_CYCLE,RENT_YEARLY_CYCLE

class Command(BaseCommand):
    help = "send rent reminders to users before due date "

    def handle(self, *args, **options):
        today = timezone.now().date()
        reminder_target_day = today+timedelta(days=3)
        rents = Rent.objects.filter(status=RENT_ACTIVE)

        for rent in rents:
            if not rent.start_date:
                continue
            next_due = self.get_next_due_date(rent.start_date.date(),rent.payment_cycle,today)

            if next_due == reminder_target_day:
                send_sms(rent.user_id.phone_number,
                    f"Reminder: Your rent is due on {next_due.strftime('%Y-%m-%d')} with an outstanding amount of {rent.rent_amount}. Please make the payment.")
    
    def get_next_due(self,start_date,cycle,today):
        cycle = cycle.lower()
        interval = timedelta(days=30) #default monthly
        if cycle == RENT_WEEKLY_CYCLE:
            interval = timedelta(weeks=1)
        elif cycle == RENT_MONTHLY_CYCLE:
            interval = timedelta(days=30)
        elif cycle == RENT_QUARTERLY_CYCLE:
            interval = timedelta(days=90)
        elif cycle == RENT_YEARLY_CYCLE:
            interval = timedelta(days=365)

        next_due = start_date
        while next_due <= today:
            next_due+=interval
        return next_due
