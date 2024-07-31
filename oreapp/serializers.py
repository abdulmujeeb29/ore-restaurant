from rest_framework import serializers
from .models import User, Menu, Order
from django.contrib.auth import get_user_model


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "is_staff_member", "is_customer"]


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ["id", "name", "description", "price", "is_discounted", "is_drink"]


class OrderSerializer(serializers.ModelSerializer):
    menu_items = serializers.PrimaryKeyRelatedField(
        queryset=Menu.objects.all(), many=True
    )

    class Meta:
        model = Order
        fields = ["id", "customer", "menu_items", "created_at"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name"]

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user
