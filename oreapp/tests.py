from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from oreapp.models import Menu, Order
from oreapp.serializers import OrderSerializer

User = get_user_model()


class UserViewSetTests(APITestCase):

    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="staff", password="password", is_staff=True
        )
        self.customer_user = User.objects.create_user(
            username="customer", password="password"
        )

    def test_staff_can_list_all_users(self):
        self.client.login(username="staff", password="password")
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_customer_cannot_list_all_users(self):
        self.client.login(username="customer", password="password")
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_retrieve_specific_user(self):
        self.client.login(username="staff", password="password")
        response = self.client.get(f"/api/users/{self.customer_user.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "customer")

    def test_customer_cannot_retrieve_specific_user(self):
        self.client.login(username="customer", password="password")
        response = self.client.get(f"/api/users/{self.staff_user.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_retrieve_registered_customers_count(self):
        self.client.login(username="staff", password="password")
        response = self.client.get("/api/users/registered_customers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["registered_customers"], 1)


class MenuViewSetTests(APITestCase):

    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="staff", password="password", is_staff=True
        )
        self.customer_user = User.objects.create_user(
            username="customer", password="password"
        )
        self.menu = Menu.objects.create(
            name="Pizza",
            description="A cheesy pizza with lots of toppings.",
            price=10.00,
            is_discounted=False,
            is_drink=False,
        )
        self.discounted_menu = Menu.objects.create(
            name="Burger",
            description="A juicy burger with lettuce and tomato.",
            price=5.00,
            is_discounted=True,
            is_drink=False,
        )
        self.drink_menu = Menu.objects.create(
            name="Coke",
            description="A refreshing cola drink.",
            price=2.00,
            is_discounted=False,
            is_drink=True,
        )

    def test_staff_can_create_menu(self):
        self.client.login(username="staff", password="password")
        data = {
            "name": "New Pizza",
            "description": "A delicious new pizza",
            "price": "15.00",  # Should be a string, but check serializer handling
            "is_discounted": False,
            "is_drink": False,
        }
        response = self.client.post("/api/menus/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Menu.objects.filter(name="New Pizza").exists())

    def test_staff_can_update_menu(self):
        self.client.login(username="staff", password="password")
        data = {
            "name": "Updated Pizza",
            "description": "An updated description for the pizza",
            "price": "12.00",  # Should be a string, but check serializer handling
            "is_discounted": True,
            "is_drink": False,
        }
        response = self.client.patch(f"/api/menus/{self.menu.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.menu.refresh_from_db()
        self.assertEqual(self.menu.name, "Updated Pizza")
        self.assertEqual(self.menu.description, "An updated description for the pizza")
        self.assertEqual(self.menu.price, 12.00)
        self.assertTrue(self.menu.is_discounted)

    def test_staff_can_delete_menu(self):
        self.client.login(username="staff", password="password")
        response = self.client.delete(f"/api/menus/{self.menu.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Menu.objects.filter(id=self.menu.id).exists())

    def test_customer_can_list_menus(self):
        self.client.login(username="customer", password="password")
        response = self.client.get("/api/menus/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        menu_names = [menu["name"] for menu in response.data]
        self.assertIn("Pizza", menu_names)
        self.assertIn("Burger", menu_names)
        self.assertIn("Coke", menu_names)

    def test_customer_can_retrieve_menu(self):
        self.client.login(username="customer", password="password")
        response = self.client.get(f"/api/menus/{self.menu.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Pizza")
        self.assertEqual(
            response.data["description"], "A cheesy pizza with lots of toppings."
        )
        self.assertEqual(
            response.data["price"], "10.00"
        )  # Ensure price is correctly formatted
        self.assertEqual(response.data["is_discounted"], False)
        self.assertEqual(response.data["is_drink"], False)

    def test_customer_can_view_discounted_menus(self):
        self.client.login(username="customer", password="password")
        response = self.client.get("/api/menus/discounted/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        discounted_menu_names = [menu["name"] for menu in response.data]
        self.assertIn("Burger", discounted_menu_names)
        self.assertNotIn("Pizza", discounted_menu_names)
        self.assertNotIn("Coke", discounted_menu_names)

    def test_customer_can_view_drinks(self):
        self.client.login(username="customer", password="password")
        response = self.client.get("/api/menus/drinks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        drink_menu_names = [menu["name"] for menu in response.data]
        self.assertIn("Coke", drink_menu_names)
        self.assertNotIn("Pizza", drink_menu_names)
        self.assertNotIn("Burger", drink_menu_names)


class OrderViewSetTests(APITestCase):

    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="staff", password="password", is_staff=True
        )
        self.customer_user = User.objects.create_user(
            username="customer", password="password"
        )
        self.menu_item1 = Menu.objects.create(
            name="Pizza",
            description="A cheesy pizza with lots of toppings.",
            price=10.00,
            is_discounted=False,
            is_drink=False,
        )
        self.menu_item2 = Menu.objects.create(
            name="Pasta",
            description="A delicious pasta with creamy sauce.",
            price=12.00,
            is_discounted=False,
            is_drink=False,
        )
        self.order = Order.objects.create(customer=self.customer_user)
        self.order.menu_items.set([self.menu_item1, self.menu_item2])

    # def test_customer_can_place_order(self):
    #     self.client.login(username="customer", password="password")
    #     data = {"menu_items": [self.menu_item1.id, self.menu_item2.id]}
    #     response = self.client.post("/api/orders/", data)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(Order.objects.count(), 2)
    #     new_order = Order.objects.latest("created_at")
    #     self.assertEqual(
    #         set(new_order.menu_items.values_list("id", flat=True)),
    #         {self.menu_item1.id, self.menu_item2.id},
    #     )

    def test_staff_can_view_all_orders(self):
        self.client.login(username="staff", password="password")
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        order_ids = [order["id"] for order in response.data]
        self.assertIn(self.order.id, order_ids)

    def test_customer_can_only_view_own_orders(self):
        self.client.login(username="customer", password="password")
        response = self.client.get("/api/orders/customer_orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        order_ids = [order["id"] for order in response.data]
        self.assertIn(self.order.id, order_ids)

    def test_staff_can_retrieve_order_details(self):
        self.client.login(username="staff", password="password")
        response = self.client.get(f"/api/orders/{self.order.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["customer"], self.customer_user.id)
        self.assertEqual(
            set(response.data["menu_items"]), {self.menu_item1.id, self.menu_item2.id}
        )


# class RegistrationTests(APITestCase):

#     def test_register_customer(self):
#         data = {
#             "username": "new_customer",
#             "password": "password",
#             "password2": "password",
#         }
#         response = self.client.post("/api/register/customer/", data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertTrue(User.objects.filter(username="new_customer").exists())
#         user = User.objects.get(username="new_customer")
#         self.assertFalse(user.is_staff)

#     def test_register_staff(self):
#         data = {
#             "username": "new_staff",
#             "password": "password",
#             "password2": "password",
#         }
#         response = self.client.post("/api/register/staff/", data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertTrue(User.objects.filter(username="new_staff").exists())
#         user = User.objects.get(username="new_staff")
#         self.assertTrue(user.is_staff)

#     def test_register_customer_password_mismatch(self):
#         data = {
#             "username": "new_customer",
#             "password": "password",
#             "password2": "different_password",
#         }
#         response = self.client.post("/api/register/customer/", data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_register_staff_password_mismatch(self):
#         data = {
#             "username": "new_staff",
#             "password": "password",
#             "password2": "different_password",
#         }
#         response = self.client.post("/api/register/staff/", data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
