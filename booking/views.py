from django.db import transaction, DatabaseError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


from booking.models import Slot, Appointment


class CreateAppointmentView(APIView):
    def post(self, request):
        slot_id = request.data.get("slot_id")
        user = request.user

        with transaction.atomic():
            try:
                try:
                    slot = Slot.objects.select_for_update(nowait=True).get(id=slot_id)
                    if slot.status == "FREE":
                        slot.status = "BOOKED"
                        slot.save()
                        
                        appointment = Appointment.objects.create(patient=user, slot=slot, status="PENDING_PAYMENT")
                        transaction.on_commit(lambda: expire_appointment_if_unpaid.delay(appointment.id))
                        
                        return Response({"message": "Слот забронирован"}, status=status.HTTP_201_CREATED)

                except DatabaseError:
                    return Response({"error": "Слот уже бронируется другим"}, status=status.HTTP_409_CONFLICT)

            except Slot.DoesNotExist:
                return Response({"error": "Слот не найден"}, status=status.HTTP_404_NOT_FOUND)