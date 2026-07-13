from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = "PATIENT", "Пациент"
        DOCTOR = "DOCTOR", "Врач"
        ADMIN = "ADMIN", "Администратор"

    role = models.CharField("Роль", max_length=20, choices=Role.choices, default=Role.PATIENT)

    @property
    def is_doctor(self) -> bool:
        return self.role == self.Role.DOCTOR
    
    @property
    def is_patient(self) -> bool:
        return self.role == self.Role.PATIENT
    
    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN