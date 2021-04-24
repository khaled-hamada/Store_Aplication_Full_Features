from django.contrib import admin
from .models import Sandwich, DaySandwich, Product,  Safe_data, withdrawings,Current_manager, Trader, Trader_Product, Point_User, Point_Product, Point, Point_User_Payment,Trader_Payment
# Register your models here.
from .models import Safe_Month ,Point_Product_Sellings, Sandwich_Type,Bread_Type,Katchab,Packet
from .models import Customer,Customer_Bill,Customer_Payment, Sub_Product, Measurement_Unit , Trader_Bill , Store_To_Point_Product

admin.site.register(Sandwich)
admin.site.register(DaySandwich)
admin.site.register(Product)

admin.site.register(Safe_data)
admin.site.register(Safe_Month)
admin.site.register(withdrawings)
admin.site.register(Current_manager)
admin.site.register(Trader)
admin.site.register(Trader_Product)
admin.site.register(Point)
admin.site.register(Point_User)
admin.site.register(Point_Product)
admin.site.register(Point_User_Payment)

admin.site.register(Point_Product_Sellings)
admin.site.register(Trader_Payment)
admin.site.register(Trader_Bill)


admin.site.register(Sandwich_Type)
admin.site.register(Bread_Type)
admin.site.register(Katchab)
admin.site.register(Packet)


admin.site.register(Customer)
admin.site.register(Customer_Bill)
admin.site.register(Customer_Payment)
admin.site.register(Sub_Product)
admin.site.register(Measurement_Unit)
admin.site.register(Store_To_Point_Product)
