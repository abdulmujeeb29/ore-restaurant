from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    MenuViewSet,
    OrderViewSet,
    RegisterCustomerAPIView,
    RegisterStaffAPIView,
)

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"menus", MenuViewSet)
router.register(r"orders", OrderViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "register/customer/",
        RegisterCustomerAPIView.as_view(),
        name="register_customer",
    ),
    path("register/staff/", RegisterStaffAPIView.as_view(), name="register_staff"),
]
