from django.db import models
from django.db.models import Q
from django.conf import settings


class WorkSchedule(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Понедельник"
        TUESDAY = 1, "Вторник"
        WEDNESDAY = 2, "Среда"
        THURSDAY = 3, "Четверг"
        FRIDAY = 4, "Пятница"
        SATURDAY = 5, "Суббота"
        SUNDAY = 6, "Воскресенье"

    doctor = models.ForeignKey(
        "clinics.DoctorProfile",
        on_delete=models.CASCADE,
        related_name="schedules",
        verbose_name="Врач"
    )

    weekday = models.PositiveSmallIntegerField("День недели", choices=Weekday.choices)
    start_time = models.TimeField("Начало приёма")
    end_time = models.TimeField("Конец приёма")

    class Meta:
        verbose_name = "Расписание"
        verbose_name_plural = "Расписания"
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "weekday"],
                name="unique_schedule_per_doctor_weekday",
            ),
        ]
    
    def __str__(self) -> str:
        return f"{self.doctor} - {self.get_weekday_display()}"


class Slot(models.Model):
    class Status(models.TextChoices):
        FREE = "FREE", "Свободно"
        BOOKED = "BOOKED", "Забронировано"

    doctor = models.ForeignKey(
        "clinics.DoctorProfile",
        on_delete=models.CASCADE,
        related_name="slots",
        verbose_name="Врач"
    )
    start_at = models.DateTimeField("Начало приёма")
    end_at = models.DateTimeField("Конец приёма")
    status = models.CharField(
        "Статус",
        max_length=10,
        choices=Status.choices,
        default=Status.FREE,
    )

    class Meta:
        verbose_name = "Слот"
        verbose_name_plural = "Слоты"
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "start_at"],
                name="unique_slot_per_doctor_start",
            ),
        ]
        
    
    def __str__(self) -> str:
        return f"{self.doctor} - {self.get_status_display()}"


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING_PAYMENT = "PENDING_PAYMENT", "Ожидание оплаты"
        PAID = "PAID", "Оплачено"
        EXPIRED = "EXPIRED", "Истёк"
        CANCELLED_BY_PATIENT = "CANCELLED_BY_PATIENT", "Отменено пациентом"
        CANCELLED_BY_CLINIC = "CANCELLED_BY_CLINIC", "Отменено клиникой"
        COMPLETED = "COMPLETED", "Завершена"
        NO_SHOW = "NO_SHOW", "Неявка"

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="appointments", verbose_name="Пациент")
    slot = models.ForeignKey(Slot, on_delete=models.PROTECT, related_name="appointments", verbose_name="Слот")
    status = models.CharField(max_length=30, choices=Status.choices, verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField("Истекает")
    cancelled_at = models.DateTimeField(null=True)

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"
        constraints = [
            models.UniqueConstraint(
                fields=["slot"],
                condition=Q(status__in=["PENDING_PAYMENT", "PAID"]),
                name="one_active_appointment_per_slot",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.patient} - {self.get_status_display()}"    


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Ожидание"
        SUCCEEDED = "SUCCEEDED", "Выполнено"
        FAILED = "FAILED", "Неудалось"

    appointment = models.OneToOneField(Appointment, on_delete=models.PROTECT, related_name="payment")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    paid_at = models.DateTimeField(null=True)

    class Meta:
        verbose_name = "Оплата"
        verbose_name_plural = "Оплаты"
    
    def __str__(self) -> str:
        return f"{self.appointment} - {self.get_status_display()}"


class PaymentWebhookEvent(models.Model):
    event_id = models.CharField(max_length=255, unique=True)
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True)

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"
    
    def __str__(self) -> str:
        return f"{self.event_id}"