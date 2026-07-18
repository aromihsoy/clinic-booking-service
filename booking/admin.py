from django.contrib import admin

from .models import Appointment, Slot, WorkSchedule


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "get_slot_info", "status")

    list_select_related = ("patient", "slot")

    list_filter = ("status",)

    search_fields = ("patient__username",)

    @admin.display(description="Слот")
    def get_slot_info(self, obj):
        return f"Слот #{obj.slot.id}"
    

@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = ("id", "doctor", "get_weekday_display", "start_time", "end_time")
    list_select_related = ("doctor",)
    list_filter = ("weekday",)
    search_fields = ("doctor__user__username",)


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ("id", "doctor", "start_at", "end_at", "status")
    list_select_related = ("doctor",)
    list_filter = ("status",)