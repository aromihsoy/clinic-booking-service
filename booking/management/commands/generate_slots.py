from datetime import datetime, date, time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from clinics.models import DoctorProfile
from booking.models import Slot, WorkSchedule



class Command(BaseCommand):
    help = "..."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=14)
    
    def handle(self, *args, **options):
        slots_to_create = []
        days_count = options['days']

        today_date = timezone.now().date()

        doctors = DoctorProfile.objects.prefetch_related('schedules')

        for i in range(0, days_count):
            target_date = today_date + timedelta(days=i)
        

            for doctor in doctors:
                for sch in doctor.schedules.all():
                    if sch.weekday == target_date.weekday():
                        start_dt = datetime.combine(target_date, sch.start_at)
                        end_dt = datetime.combine(target_date, sch.end_at)
                        while start_dt < end_dt:
                            aware_dt = timezone.make_aware(start_dt)
                            
                            slot = Slot(doctor=doctor, start_at=aware_dt)
                            slots_to_create.append(slot)
                            
                            start_dt += timedelta(minutes=doctor.slot_duration_minutes)
        Slot.objects.bulk_create(slots_to_create, ignore_conflicts=True)

