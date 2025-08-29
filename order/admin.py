from django.contrib import admin
from .models import Order, Ticket


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (TicketInline,)
    list_display = ("id", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__email",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("journey", "order", "cargo", "seat")
    list_filter = ("journey__route__source", "journey__route__destination")
