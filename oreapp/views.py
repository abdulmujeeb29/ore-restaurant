from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.contrib.auth import get_user_model
from .models import Menu, Order
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from .serializers import (
    UserSerializer,
    MenuSerializer,
    OrderSerializer,
    RegisterSerializer,
)

User = get_user_model()


class IsStaffMember(permissions.BasePermission):
    """
    Custom permission to only allow staff members to access certain actions.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class MenuViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing the Menu. Allows staff to create, update, and delete menus.
    Customers can view the list of menus and retrieve individual menu items.
    """

    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Override get_permissions to set custom permissions for different actions.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            # Only staff members can create, update, or delete menu items
            self.permission_classes = [permissions.IsAuthenticated, IsStaffMember]
        elif self.action in ["list", "retrieve", "discounted", "drinks"]:
            # Customers  can view the list of menus, retrieve specific items, view discounted and drink menus
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    @action(detail=False, methods=["get"])
    def discounted(self, request):
        """
        Custom action for customers  to retrieve menus that are on discount.
        """
        discounted_menus = Menu.objects.filter(is_discounted=True)
        serializer = self.get_serializer(discounted_menus, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def drinks(self, request):
        """
        Custom action for customers  to retrieve menus that are drinks.
        """
        drink_menus = Menu.objects.filter(is_drink=True)
        serializer = self.get_serializer(drink_menus, many=True)
        return Response(serializer.data)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing Users. Allows staff to view the list of registered users and retrieve individual users.
    Authenticated users can view their own profile.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Override get_permissions to set custom permissions for different actions.
        """
        if self.action in ["list", "retrieve"]:
            # Only staff members can view the list of users or retrieve individual users
            self.permission_classes = [IsStaffMember]
        else:
            # Authenticated users can view their own profile
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    @action(
        detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def profile(self, request):
        """
        Custom action to retrieve the profile information of the authenticated user.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsStaffMember])
    def registered_customers(self, request):
        """
        Custom action to retrieve the number of registered customers.
        Only staff members can access this.
        """
        customers_count = User.objects.filter(is_staff=False).count()
        return Response({"registered_customers": customers_count})


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Orders. Customers can place orders and staff can view all orders.
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Override to provide different permissions for staff and customers.
        """
        if self.action in ["list", "retrieve"]:
            # Staff can view all orders
            self.permission_classes = [permissions.IsAuthenticated, IsStaffMember]
        elif self.action in ["create"]:
            # Customers can place orders
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        """
        Override perform_create to associate the order with the authenticated customer.
        """
        serializer.save(customer=self.request.user)

    @action(detail=False, methods=["get"])
    def customer_orders(self, request):
        """
        Custom action to get orders for the authenticated customer.
        """
        if not request.user.is_staff:
            # If not a staff member, only allow access to their own orders
            queryset = Order.objects.filter(customer=request.user)
        else:
            # Staff can see all orders
            queryset = self.queryset
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RegisterCustomerAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: RegisterSerializer, 400: "Bad Request"},
    )
    def post(self, request, *args, **kwargs):
        """
        Register a new customer.
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_staff = False  # Ensure the user is not marked as staff
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterStaffAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: RegisterSerializer, 400: "Bad Request"},
    )
    def post(self, request, *args, **kwargs):
        """
        Register a new staff member.
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_staff = True  # Ensure the user is marked as staff
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
