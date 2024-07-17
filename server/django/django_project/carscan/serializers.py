from rest_framework import serializers
from .models import UserCar, User, RegistrationHistory, VehicleLimits, Inspection, Accident, Fine, Car


class UserCarSerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = UserCar
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    """"""
    user_info = UserCarSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "user_type", "subscription_expired_date", "registration_date", "password", "user_info")


class RegistrationHistorySerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = RegistrationHistory
        fields = ("id", "car", "period", "description")


class VehicleLimitSerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = VehicleLimits
        fields = "__all__"


class InspectionSerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = Inspection
        fields = "__all__"


class AccidentSerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = Accident
        fields = "__all__"


class FineSerializer(serializers.ModelSerializer):
    """"""

    class Meta:
        model = Fine
        fields = "__all__"


class CarSerializer(serializers.ModelSerializer):
    """"""
    reg_history = RegistrationHistorySerializer(many=True, read_only=True)
    limits = VehicleLimitSerializer(many=True, read_only=True)
    inspections = InspectionSerializer(many=True, read_only=True)
    accidents = AccidentSerializer(many=True, read_only=True)
    fines = FineSerializer(many=True, read_only=True)
    car_info = UserCarSerializer(many=True, read_only=True)

    class Meta:
        model = Car
        fields = (
            "id", "vin_number", "body_number", "chassis_number", "license_number", "license_region", "model", "brand",
            "manufacture_year", "vehicle_category", "vehicle_category_tr", "min_weight", "max_weight", "power_hp",
            "fuel_type", "brake_system", "document_type_sts", "document_series", "document_number", "document_date",
            "document_maker", "color", "vehicle_type", "engine_capacity", "engine_number", "pts_series_number",
            "pts_maker", "pts_owner", "hijacking", "reg_history", "limits",
            "inspections", "accidents", "fines", "car_info"
        )
