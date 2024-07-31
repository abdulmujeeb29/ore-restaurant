from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


# Create your models here.
class User(AbstractUser):
    is_staff_member = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        Group, related_name="oreapp_user_set", related_query_name="oreapp_user"
    )
    user_permissions = models.ManyToManyField(
        Permission, related_name="oreapp_user_set", related_query_name="oreapp_user"
    )

class Menu(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_discounted = models.BooleanField(default=False)
    is_drink = models.BooleanField(default=False)


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    menu_items = models.ManyToManyField(Menu)
    created_at = models.DateTimeField(auto_now_add=True)
