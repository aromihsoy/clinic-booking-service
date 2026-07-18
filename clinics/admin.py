from django.contrib import admin

from .models import DoctorProfile, Clinic, Specialization
from booking.models import WorkSchedule


class WorkScheduleInline(admin.TabularInline):
    model = WorkSchedule
    extra = 1
    fields = ("weekday", "start_time", "end_time")


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "clinic", "specialization", "slot_duration_minutes", "price")
    list_select_related = ("user", "clinic", "specialization")

    inlines = [WorkScheduleInline]


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "address")
    search_fields = ("name",)


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)