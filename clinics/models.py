from django.db import models
from django.conf import settings


class Clinic(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()

    class Meta:
        verbose_name = "Клиника"
        verbose_name_plural = "Клиники"
    
    def __str__(self) -> str:
        return self.name


class Specialization(models.Model):
    name = models.CharField(max_length=30, unique=True)

    class Meta:
        verbose_name = "Специализация"
        verbose_name_plural = "Специализации"
    
    def __str__(self) -> str:
        return self.name


class DoctorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctor_profile", verbose_name="Пользователь")
    clinic = models.ForeignKey(Clinic, on_delete=models.PROTECT, related_name="doctors", verbose_name="Клиника")
    specialization = models.ForeignKey(Specialization, on_delete=models.PROTECT, related_name="doctors", verbose_name="Специализация")
    slot_duration_minutes = models.PositiveSmallIntegerField("Длительность приёма (мин)", default=30)
    price = models.DecimalField("Стоимость приёма", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Профиль врача"
        verbose_name_plural = "Профили"
    
    def __str__(self) -> str:
        return f"{self.user} - {self.specialization}"