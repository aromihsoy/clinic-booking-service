from django.db import transaction, DatabaseError, IntegrityError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


from .models import Slot, Appointment, PaymentWebhookEvent, Payment
from .tasks import expire_appointment_if_unpaid


class CreateAppointmentView(APIView):
    def post(self, request):
        slot_id = request.data.get("slot_id")
        user = request.user

        with transaction.atomic():
            try:
                slot = Slot.objects.select_for_update(nowait=True).get(id=slot_id)
                if slot.status == "FREE":
                    slot.status = "BOOKED"
                    slot.save()
                    
                    appointment = Appointment.objects.create(patient=user, slot=slot, status="PENDING_PAYMENT")
                    transaction.on_commit(lambda: expire_appointment_if_unpaid.delay(appointment.id)) # type: ignore
                    
                    return Response({"message": "Слот забронирован"}, status=status.HTTP_201_CREATED)

            except DatabaseError:
                return Response({"error": "Слот уже бронируется другим"}, status=status.HTTP_409_CONFLICT)

            except Slot.DoesNotExist:
                return Response({"error": "Слот не найден"}, status=status.HTTP_404_NOT_FOUND)
            

class PaymentWebhookView(APIView):
    def post(self, request):
        event_id = request.data.get("event_id")
        appointment_id = request.data.get("appointment_id")
        try:
            PaymentWebhookEvent.objects.create(event_id=event_id)
        except IntegrityError:
            return Response({"Error": "Запись уже существует"}, status=status.HTTP_200_OK)
        
        with transaction.atomic():
            try:
                appointment = Appointment.objects.select_for_update().get(id=appointment_id)

                if appointment.status != "PENDING_PAYMENT":
                    return Response({"Message": "Неверный статус брони для оплаты"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    appointment.status = "PAID"
                    appointment.save()
                    Payment.objects.create(appointment=appointment)

                    return Response({"Message": "Бронь оплачена"}, status=status.HTTP_200_OK)
            except Appointment.DoesNotExist:
                return Response({"Error": "Неверный ID брони"}, status=status.HTTP_404_NOT_FOUND)