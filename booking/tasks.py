from celery import shared_task
from django.db import transaction

from .models import Appointment, Slot


@shared_task
def expire_appointment_if_unpaid(appointment_id):
    with transaction.atomic():
        appointment = Appointment.objects.select_related("slot").select_for_update().get(id=appointment_id)

        if appointment.status != "PENDING_PAYMENT":
            return
        else:
            appointment.status = "EXPIRED"
            appointment.save()
            appointment.slot.status = "FREE"
            appointment.slot.save()