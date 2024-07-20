from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Car)
admin.site.register(UserCar)
admin.site.register(RegistrationHistory)
admin.site.register(Inspection)
admin.site.register(Fine)
admin.site.register(VehicleLimits)
admin.site.register(Accident)