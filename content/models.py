from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.db.models import Sum,Q
# Create your models here.


class Current_manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    active_status = models.IntegerField(default=0)
    start_date =  models.DateField(default = now)
    end_date =  models.DateField(default = now)
    safe = models.ForeignKey('Safe_Month',on_delete=models.SET_NULL, blank=True ,null = True)
    def __str__(self):
        return self.user.first_name

class Point_User(models.Model):
    active_status = models.IntegerField(default = 0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    start_date =  models.DateField(default = now)
    end_date =  models.DateField(default = now)
    point = models.ForeignKey('Point',on_delete = models.SET_NULL,blank= True,null = True)
    def __str__(self):
        return self.user.first_name

## فواتير النقاط
class Point_User_Payment(models.Model):
    g_user = models.ForeignKey('Point', on_delete=models.SET_NULL , null=True)
    t_user = models.ForeignKey('Current_manager', on_delete=models.SET_NULL , null=True)
    date = models.DateTimeField(default = now)
    amount= models.FloatField(default=0.0)

    def __str__(self):
        return self.g_user.name

## لسماء النقاط
class Point(models.Model):
    name = models.CharField(max_length = 264)

    ## no need will be deleted
    given_money =models.FloatField(default=0.0)
    @property
    def remaining_money(self):
        return self.total_money_sell - self.total_money_buy


    ## this property calculates products buying cost in points
    @property
    def total_money_buy(self):

        return round(sum(product.current_quantity_cost_buy for product in self.all_point_products) , 2)

    @property
    def total_money_sell(self):
        return round(sum(product.current_quantity_cost_sell for product in self.all_point_products) , 2)

    @property
    def all_point_products(self):
        return Point_Product.objects.filter(Point = self.id)

    def __str__(self):
        return self.name

## بضائع النقاط create point new bills
class Point_Product(models.Model):

    objects = models.Manager()
    total_quantity_fixed = models.IntegerField(default = 0)
    date = models.DateTimeField(default=now, null=True)
    quantity = models.IntegerField(default = 0)
    quantity_packet = models.IntegerField(default = 0)
    unit_sell_price = models.FloatField(default = 0)


    restored_store_quantity = models.IntegerField(default = 0)

    given_status =  models.IntegerField(default = 0)
    notes = models.TextField(default="", null=True)
    ## refercing trader product data
    # product_image = models.FileField(upload_to="canteen_products_pic/%Y/%m/%d" , null=True)
    # production_date  = models.DateTimeField(default=now, null=True)
    # expiration_date = models.DateTimeField(default=now, null=True)

    trader_product = models.ForeignKey('Trader_Product', on_delete = models.SET_NULL , null=True)
    Point = models.ForeignKey('Point', on_delete = models.SET_NULL, null=True)




    def __str__(self):
        return self.trader_product.product.name +  "  --  trader name :-> " + self.Point.name


    @property
    def total_money_quantity_buy(self):
            return    round(self.total_quantity * self.unit_buy_price , 2)


    @property
    def quantity_per_packet(self):
            return    self.trader_product.quantity_per_packet

    @property
    def unit_buy_price(self):
            return    self.trader_product.unit_buy_price

    @property
    def unit_buy_price_ad(self):
            return    self.trader_product.unit_buy_price_ad

    @property
    def remaining_quantity(self):
        return    self.total_quantity

    @property
    def total_quantity(self):
        return   ( self.quantity  + (self.quantity_per_packet * self.quantity_packet )) -  self.restored_store_quantity


    @property
    def current_quantity_cost_buy(self):
        cost =  self.remaining_quantity   * self.unit_buy_price_ad
        return round(cost , 2)

    @property
    def current_quantity_cost_sell(self):
        cost =  self.remaining_quantity   * self.unit_sell_price
        return round(cost , 2)

    def normailze_product(self):
        ## normalize product
        if self.quantity_per_packet :
            quo , rem = divmod(self.quantity , self.quantity_per_packet)
            self.quantity = rem
            self.quantity_packet += quo
        self.save()


    def subtract_from_product(self, nq, nqp):

        quo, rem = divmod(nq, self.quantity_per_packet)
        nq = rem
        nqp += quo

        if nq > self.quantity:
            self.quantity += self.quantity_per_packet
            self.quantity_packet -= 1

        ##subtract from product
        self.quantity -= nq
        self.quantity_packet -= nqp
        self.save()
        self.normailze_product()

    def add_to_product(self, nq, nqp):


        self.quantity += nq
        self.quantity_packet += nqp

        self.save()
        self.normailze_product()


    def calculate_cost(self , nq, nqp):
        total =    (nq * self.unit_buy_price)  + ( nqp * self.packet_price)
        return round(total , 2)

## this table will be used in three cases
## 1. store to point  -> line_type = 0
## 2. point to store  -> line_type = 1
## 3. point to point  -> line_type = 2
class Store_To_Point_Product(models.Model):
        quantity = models.IntegerField(default = 0)
        quantity_packet = models.IntegerField(default = 0)
        date = models.DateTimeField(default=now)
        unit_sell_price =  models.FloatField(default = 0)
        ## line type 0 for given and 1 for restored
        line_type = models.IntegerField(default = 0)
        ## must be 1 for assertion
        given_status = models.IntegerField(default = 0)

        # point_product = models.ForeignKey('Point_Product', on_delete = models.CASCADE, null = True)
        point = models.ForeignKey('Point', on_delete = models.CASCADE, null = True, related_name ='Store_To_Point_Product' , blank = True )
        ## in case of restored only
        # point_product = models.ForeignKey('Point_Product', on_delete = models.CASCADE, null = True)
        to_point = models.ForeignKey(Point, on_delete = models.CASCADE, null = True,  related_name ='To_Point' , blank = True)
        ## in case of restored only
        trader_product =  models.ForeignKey('Trader_Product', on_delete = models.CASCADE, null = True, blank = True)

        def __str__(self):
            return "moving product : ->  "+ self.trader_product.product.name + "  from stroe to point :  ->  " + self.point.name

        @property
        def total_quantity(self):
            re = self.quantity + (self.quantity_packet * self.trader_product.quantity_per_packet)
            return re
        @property
        def line_cost(self):
            return round(self.total_quantity * self.trader_product.unit_buy_price_ad  ,2)


## بضائع النقاط المباعة   === bill line
class Point_Product_Sellings(models.Model):
    objects = models.Manager()

    quantity = models.IntegerField(default = 0)
    quantity_packet = models.IntegerField(default = 0)

    unit_sell_price = models.FloatField(default = 0)
    discount_per_unit = models.FloatField(default = 0)
    date = models.DateTimeField(default=now)


    ## 0 for sold ,   1 for restored
    line_type = models.IntegerField(default = 0)
    taken_status =  models.IntegerField(default = 0)


    ## if restord any amount

    point_product = models.ForeignKey('Point_Product', on_delete = models.SET_NULL, null = True)
    Point = models.ForeignKey('Point', on_delete = models.SET_NULL, null = True)
    bill = models.ForeignKey('Customer_Bill', on_delete = models.CASCADE, null = True)
    come_from = models.ForeignKey('Point_Product_Sellings', on_delete = models.SET_NULL, null = True, blank = True)


    def __str__(self):
        # ttp = Total_Point_Product.objects.get(Point = self.Point , product = self.product)
        return self.point_product.trader_product.product.name +  "  --  trader name :-> " + self.Point.name

    ## same for both sold and restored
    @property
    def total_quantity_sold(self):
        return   int( self.quantity  + (self.point_product.quantity_per_packet * self.quantity_packet ))

    @property
    def unit_buy_price(self):
        return self.point_product.unit_buy_price_ad

    @property
    def line_discount(self):
        if self.line_type == 0:
            return round(self.total_quantity_sold * self.discount_per_unit , 1)
        else :
            return round(self.total_quantity_sold * self.come_from.discount_per_unit , 1)


    @property
    def line_cost_buy(self):
        return round(self.unit_buy_price * self.total_quantity_sold, 1)


    @property
    def line_cost_sell(self):
        if self.line_type == 0:
            return round(self.unit_sell_price * self.total_quantity_sold, 1)
        else :
            return round(self.come_from.unit_sell_price * self.total_quantity_sold, 1)

    @property
    def line_cost_sell_ad(self):
        return round(self.line_cost_sell - self.line_discount , 1)




    ### in case of restored product amount
    ## need that in many conditions
    ## need in accumulation for restored bills
    @property
    def restored_quantity(self):
            bills = Point_Product_Sellings.objects.filter(come_from =self.id, line_type = 1 )
            return sum(b.total_quantity_sold for b in bills)

    @property
    def restored_quantity_cost(self):
            return round(self.restored_quantity * (self.unit_sell_price_ad) , 1)

    @property
    def restored_quantity_cost_withoutd(self):

            return round(self.restored_quantity * (self.unit_sell_price) , 1)



    @property
    def unit_sell_price_ad(self):
        return self.unit_sell_price - self.discount_per_unit


    @property
    def quantity_per_packet(self):
        return self.point_product.quantity_per_packet


    def normailze_product(self):
        ## normalize product
        if self.quantity_per_packet :
            quo , rem = divmod(self.quantity , self.quantity_per_packet)
            self.quantity = rem
            self.quantity_packet += quo
        self.save()


    def subtract_from_product(self, nq, nqp):

        quo, rem = divmod(nq, self.quantity_per_packet)
        nq = rem
        nqp += quo

        if nq > self.quantity:
            self.quantity += self.quantity_per_packet
            self.quantity_packet -= 1

        ##subtract from product
        self.quantity -= nq
        self.quantity_packet -= nqp
        self.save()
        self.normailze_product()

    def add_to_product(self, nq, nqp):


        self.quantity += nq
        self.quantity_packet += nqp

        self.save()
        self.normailze_product()




## البضاعة
class Product(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length = 264)

    descreption = models.TextField(default = "")
    product_image = models.FileField(upload_to="canteen_products_pic/%Y/%m/%d" , null=True)
    trader = models.ManyToManyField('Trader', through ='Trader_Product',  blank=True)

    ##just accumelator
    @property
    def total_quantity(self):
        return sum(line.total_quantity_in_store for line in self.all_lines)

    @property
    def total_quantity_packets(self):
        return sum(line.quantity_packet for line in self.all_lines)

    @property
    def total_quantity_items(self):

        return sum(line.quantity for line in self.all_lines)

    ##just accumelator
    @property
    def total_cost(self):
        return sum( (line.total_quantity_in_store_cost)  for line in self.all_lines)


    '''
        total quantity in points
    '''
    @property
    def total_quantity_in_points(self):
        return sum(line.total_quantity for line in self.all_lines_in_points)

    @property
    def total_quantity_packets_in_points(self):
        return sum(line.quantity_packet for line in self.all_lines_in_points)

    @property
    def total_quantity_items_in_points(self):

        return sum(line.quantity for line in self.all_lines_in_points)

    ##just accumelator
    @property
    def total_cost_in_points_buy(self):
        return sum( (line.total_quantity_in_store_cost)  for line in self.all_lines)

    @property
    def total_cost_in_points_sell(self):
        return sum( (line.current_quantity_cost_sell)  for line in self.all_lines)

    ##just accumelator
    @property
    def all_lines(self):
        return Trader_Product.objects.filter(product = self.id)

    @property
    def all_lines_in_points(self):
        return Point_Product.objects.filter(trader_product__product = self.id)


    def __str__(self):
        return self.name



### in case of sellings products in parts of units Not in a complete one
### i.e selling in unit parts of parts
class Sub_Product(models.Model):
    product = models.OneToOneField('Product', on_delete = models.SET_NULL, null  =True)
    measurement_unit = models.ForeignKey('Measurement_Unit', on_delete = models.SET_NULL , null= True)

    quantity_per_unit = models.IntegerField(default = 0 )
    unit_sell_price = models.FloatField(default = 0 )

    def __str__(self):
        return  " اسم الصنف : " + self.product.name +",  سعر بيع ال " + self.measurement_unit.name +\
                " الواحد ب " + str(self.unit_sell_price * 10 ) +" قرش "



## names of measurement units ie kilogram - gram - liter and so on
class Measurement_Unit(models.Model):
    name = models.CharField(max_length = 64)

    def __str__(self):
        return self.name




## التجار
class Trader(models.Model):
    name = models.CharField(max_length = 264)
    address = models.CharField(max_length = 264)
    phone_number = models.CharField(max_length = 264, default = "")
    date = models.DateTimeField(default=now)

    given_money =models.FloatField(default=0.0)
    total_money = models.FloatField(default=0.0)

    def __str__(self):
        return self.name

    @property
    def remaining_money(self):
        return round(self.total_money - self.given_money , 1)

## trader bills
class Trader_Payment(models.Model):
    amount = models.FloatField(default=0.0)
    date = models.DateTimeField(default=now)
    sender = models.ForeignKey(Current_manager, on_delete =models.SET_NULL, null = True)
    reciever = models.ForeignKey('Trader', on_delete = models.SET_NULL, null = True)
    notes = models.TextField(default="")
    bill_file = models.FileField(upload_to="upload_to='canteen_bills/%Y/%m/%d'" , null=True)
    discount = models.FloatField(default = 0.0)
    previos_amount = models.FloatField(default = 0.0)
    current_amount = models.FloatField(default = 0.0)
    ## 0 for coming , 1 for restored products
    payment_type = models.IntegerField(default = 0)
    def __str__(self):
        return self.sender.user.first_name +  "  --  trader name :-> " + self.reciever.name + " -- date -> " + str(self.date) + " -- money: " + str(self.amount)



## بضائع التجار bills
class Trader_Product(models.Model):
    objects = models.Manager()
    total_quantity_fixed = models.IntegerField(default = 0)
    quantity = models.IntegerField(default = 0)
    quantity_packet = models.IntegerField(default = 0)
    quantity_per_packet = models.IntegerField(default = 0)
    packet_price = models.FloatField(default = 0)
    discount_per_packet = models.FloatField(default = 0.0)
    restored_quantity =  models.IntegerField(default = 0)


    date = models.DateTimeField(default=now)

    ## must be 1 for assertion
    given_status = models.IntegerField(default = 0)
    notes = models.TextField(default="", null=True)

    ## line type 0 for given and 1 for restored
    line_type = models.IntegerField(default = 0)

    product_image = models.FileField(upload_to="canteen_products_pic/%Y/%m/%d" , null=True)
    production_date  = models.DateTimeField(default=now, null=True)
    expiration_date = models.DateTimeField(default=now, null=True)

    product = models.ForeignKey(Product, on_delete = models.SET_NULL, null = True)
    trader = models.ForeignKey(Trader, on_delete = models.SET_NULL, null = True)
    trader_bill = models.ForeignKey('Trader_Bill', on_delete = models.CASCADE, null = True)
    ## in case of restored only
    come_from =  models.OneToOneField('Trader_Product', on_delete = models.CASCADE, null = True, blank = True)

    def __str__(self):
        if self.line_type == 0 :
            if self.product != None:
                return self.product.name +  "  --  trader name :-> " + self.trader.name
            else:
                return self.trader.name
        else :
            return ""

    @property
    def unit_buy_price(self):
        if self.quantity_per_packet > 0:
            return  round(  self.packet_price / self.quantity_per_packet , 3 )
        else:
            return 0
    @property
    def unit_buy_price_ad(self):
        return self.unit_buy_price - self.discount_per_unit
    @property
    def packet_price_ad(self):
        return self.packet_price - self.discount_per_packet


    @property
    def moved_to_point_quantity(self):
        pp = Point_Product.objects.filter(trader_product = self.id)
        quantity_in_points = sum(p.total_quantity for p in pp )
        return  quantity_in_points

    @property
    def sold_to_any_customer(self):
        pp =Point_Product_Sellings.objects.filter(point_product__trader_product = self.id, line_type = 0)

        return len(pp) ## if >  0 already sold


    @property
    def total_quantity_in_store(self):
        return  self.total_quantity


    @property
    def total_quantity_in_store_cost(self):
        return  round(self.total_quantity_in_store * ( self.unit_buy_price - self.discount_per_unit) , 2)


    @property
    def total_quantity(self):
        return  self.quantity + (self.quantity_packet * self.quantity_per_packet)

    @property
    def total_discount(self):
        if self.line_type == 0:
            r = round( ( ( self.total_quantity_fixed - self.restored_quantity ) / self.quantity_per_packet ) * self.discount_per_packet, 2)
        else :
            r = round(self.total_quantity * self.discount_per_unit , 2)
        return r
    @property
    def qp_original(self):
        try :
            return int(self.total_quantity_fixed / self.quantity_per_packet)
        except :
            return 0
    @property
    def qi_original(self):
        try :
            return int(self.total_quantity_fixed % self.quantity_per_packet)
        except :
            return 0
    @property
    def total_cost(self):
        if self.line_type == 0:
            r = round( (self.total_quantity_fixed - self.restored_quantity ) * self.unit_buy_price, 2)
        else :
            r = round( self.total_quantity * self.unit_buy_price , 2)
        return r

    @property
    def required_amount(self):
        return round(self.total_cost - self.total_discount , 1)

    @property
    def restored_amount_cost(self):
        return round(self.restored_quantity * self.unit_buy_price , 1)

    @property
    def restored_amount_cost_ad(self):
        return round(self.restored_amount_cost - (self.restored_quantity * self.discount_per_unit) , 1)


    @property
    def discount_per_unit(self):
        try :
            return round( self.discount_per_packet / self.quantity_per_packet , 3)
        except :
            return 0

    @property
    def total_discount_after_restore(self):
        r = round( ((self.total_quantity_fixed - self.restored_quantity) / self.quantity_per_packet ) * self.discount_per_packet, 2)
        return r



    def normailze_product(self):
        ## normalize product
        if self.quantity_per_packet :
            quo , rem = divmod(self.quantity , self.quantity_per_packet)
            self.quantity = rem
            self.quantity_packet += quo
        self.save()


    def subtract_from_product(self, nq, nqp):

        quo, rem = divmod(nq, self.quantity_per_packet)
        nq = rem
        nqp += quo

        if nq > self.quantity:
            self.quantity += self.quantity_per_packet
            self.quantity_packet -= 1

        ##subtract from product
        self.quantity -= nq
        self.quantity_packet -= nqp
        self.save()
        self.normailze_product()

    def add_to_product(self, nq, nqp):


        self.quantity += nq
        self.quantity_packet += nqp

        self.save()
        self.normailze_product()


    def calculate_cost(self , nq, nqp):
        total =    (nq * self.unit_buy_price)  + ( nqp * self.packet_price)
        return round(total , 2)


## بضائع التجار bills
class Trader_Bill(models.Model):
    date = models.DateTimeField(default=now)
    given_status = models.IntegerField(default = 0)
    paid_status = models.IntegerField(default = 0)
    ## 0 for delivered ,   1 for restored
    bill_type = models.IntegerField(default = 0)
    given_amount = models.FloatField(default=0.0)
    ## if we give customer more discounts in the upcoming bills
    discount = models.FloatField(default=0.0)

    bill_file = models.FileField(upload_to="canteen_bills/%Y/%m/%d" , null=True)

    trader = models.ForeignKey(Trader, on_delete = models.CASCADE, null = True)
    manager = models.ForeignKey(Current_manager, on_delete = models.CASCADE, null = True)
    notes = models.TextField(default="", null=True)
    def __str__(self):

        return  " رقم الفاتورة : " +str(self.id) + "   اسم التاجر  "+ self.trader.name


    # ## check bill in store
    @property
    def get_any_line(self):
        return Trader_Product.objects.filter(trader_bill = self.id).last()
    # ## check bill in store
    @property
    def has_any_quantity_in_store(self):
        for line in self.all_lines:
            if line.total_quantity_in_store > 0 :
                return True
                break

        return False

    # ## bill cost without any discount
    @property
    def total_bill_cost(self):
        # bill_lines = self.all_lines
        total_bill_cost = round( sum(b.total_cost for b in self.all_lines), 2)
        return total_bill_cost
    #
    ## bill cost without any discount after restoring to trader
    @property
    def total_bill_cost_ar(self):
        return round(self.total_bill_cost - self.restored_amount_cost , 1)

    @property
    def restored_amount_cost(self):
        # bill_lines = self.all_lines
        total = round( sum(b.restored_amount_cost for b in self.all_lines ), 2)
        return  total


    @property
    def total_discount(self):
        return     self.main_discount + self.discount

    ## disount for the sold amount only =>   total_sold - total_restored
    @property
    def main_discount(self):
        if self.bill_type == 0:
            total_discount =  round( sum( (b.total_discount_after_restore  for b in self.all_lines ) ) , 2)
        else :
            total_discount =  round( sum( (b.total_quantity * b.discount_per_unit  for b in self.all_lines ) ) , 2)
        return total_discount

    # ## bill cost without with all discounts
    @property
    def required_amount(self):
        return round(self.total_bill_cost -  self.total_discount , 1) #- self.restored_amount_cost



    @property
    def remaining_amount(self):
        return round(self.required_amount -  self.given_amount , 1)



    # cost of the restored amount removing from it the discount per packet
    @property
    def restored_amount_cost_ad(self):
        # bill_lines = self.all_lines
        total = round( sum(b.restored_amount_cost_ad for b in self.all_lines ), 2)
        return  total

    #

    #
    @property
    def all_lines(self):
        bill_lines = Trader_Product.objects.filter(trader_bill = self.id)
        return bill_lines




    @property
    def remaining_amount(self):
        return round( self.total_bill_cost - self.given_amount - self.discount )








### بيانات الخزنة
class Safe_data(models.Model):
    objects = models.Manager()
    day =  models.DateTimeField(default = now)
    money_amount = models.FloatField(default=0.0)
    given_person = models.ForeignKey(Current_manager, on_delete = models.CASCADE, null = True)
    notes = models.TextField(default = "")
    ### status takes values fom 1 - 6
    ### 1- withdraw money    2- point_product_bill  3. trader_products_bill  4. sandwiches cost
    ## 5. sandwich sellings    6. generics ,   7. customer payment   8. trader payment
    safe_line_status = models.IntegerField(default = 0)
    def __str__(self):
        return self.notes


## safe montly
class Safe_Month(models.Model):
    name = models.CharField(max_length = 264 , default="")
    money = models.FloatField(default= 0.0)

    def __str__(self):
        return self.name

## النثريات
class withdrawings(models.Model):

    descreption =  models.TextField(default = "")
    day =  models.DateTimeField(default = now)
    money_amount =models.FloatField(default=0.0)
    ## 1. store product
    ##2. safe money withdraw
    status = models.IntegerField(default = 0)

    def __str__(self):
        return self.descreption





## بضائع التجار  realtion between product and trader will be deleted
class Trader_Product_Data(models.Model):
    objects = models.Manager()
    price_per_packet = models.IntegerField(default = 0)
    product = models.ForeignKey(Product, on_delete = models.CASCADE, null = True)
    trader = models.ForeignKey(Trader, on_delete = models.CASCADE, null = True)
    def __str__(self):
        return self.product.name +  "  --  trader name :-> " + self.trader.name




#############################################################
### customers tables
############################################################

### first

## التجار
class Customer(models.Model):
    name = models.CharField(max_length = 264)
    address = models.CharField(max_length = 264)
    phone_number = models.CharField(max_length = 264, default = "")
    date = models.DateTimeField(default=now)

    ## in case of customer pay any amount under calculations
    pre_amount = models.FloatField(default = 0.0)

    @property
    def remaining_money(self):
        bought_bills =  round(sum(b.remaining_amount for b in self.customer_unpaid_bill), 2)
        restored_bills =  round(sum(b.remaining_amount for b in self.customer_unpaid_bill_restored), 2)
        return  round(bought_bills - self.pre_amount , 2)
        # return  round(bought_bills - restored_bills , 2)



    @property
    def customer_unpaid_bill(self):
        return Customer_Bill.objects.filter(customer = self.id , paid_status = 0,  bill_type = 0).order_by("-id")


    @property
    def customer_unpaid_bills_ids(self):
        ids  = []
        for bill in self.customer_unpaid_bill() :
            ids.append(bill.id)
        return ids

    @property
    def customer_unpaid_bill_restored(self):
        return Customer_Bill.objects.filter(customer = self.id , paid_status = 0, bill_type = 1 )




    def __str__(self):
        return self.name


class Customer_Bill(models.Model):
    date = models.DateTimeField(default=now)
    given_status = models.IntegerField(default = 0)
    paid_status = models.IntegerField(default = 0)
    ## 0 for sold ,   1 for restored
    bill_type = models.IntegerField(default = 0)
    given_amount = models.FloatField(default=0.0)
    ## if we give customer more discounts in the upcoming bills
    discount = models.FloatField(default=0.0)


    customer  = models.ForeignKey('Customer', on_delete = models.SET_NULL, null = True)
    manager  = models.ForeignKey('Current_manager', on_delete = models.SET_NULL, null = True)



    @property
    def total_bill_cost(self):
        bill_lines = self.all_lines
        total_bill_cost = round( sum(b.line_cost_sell for b in bill_lines), 2)
        return total_bill_cost

    ## bill cost without any discount
    @property
    def total_bill_cost_ar(self):
        bill_lines = self.all_lines
        total_bill_cost = round( sum(b.line_cost_sell_ad for b in bill_lines), 2)
        return total_bill_cost

    @property
    def remaining_amount(self):
        return self.required_amount -  self.given_amount

    @property
    def total_discount(self):
        return     self.main_discount + self.discount

    ## disount for the sold amount only =>   total_sold - total_restored
    @property
    def main_discount(self):
        bill_lines = self.all_lines
        total_discount =  round( sum( (b.line_discount  for b in bill_lines ) ) , 2)
        return total_discount

    ## bill cost without with all discounts
    @property
    def required_amount(self):
        return self.total_bill_cost_ar - self.discount


    @property
    def restored_amount_cost_ad(self):
        bill_lines = self.all_lines
        total = round( sum(b.restored_quantity_cost for b in bill_lines ), 2)
        return  total

    @property
    def restored_amount_cost_withoutd(self):
        bill_lines = self.all_lines
        total = round( sum(b.restored_quantity_cost_withoutd for b in bill_lines ), 2)
        return  total



    @property
    def all_lines(self):
        bill_lines = Point_Product_Sellings.objects.filter(bill = self.id)
        return bill_lines

    @property
    def point(self):
        bill_line = Point_Product_Sellings.objects.filter(bill = self.id).first()
        try:
            return bill_line.Point
        except:
            return None



    def __str__(self):
        return  "   فاتورة رقم :  " +  str(self.id) + " ---- " + "  اسم العميل :  " +  self.customer.name




## فواتير العملاء
class Customer_Payment(models.Model):
    g_user = models.ForeignKey('Customer', on_delete=models.SET_NULL, null=True)
    t_user = models.ForeignKey('Current_manager', on_delete=models.SET_NULL , null=True)
    date = models.DateTimeField(default = now)
    amount= models.FloatField(default=0.0)
    previos_amount= models.FloatField(default=0.0)
    current_amount= models.FloatField(default=0.0)
    discount= models.FloatField(default=0.0)
    ## 0 from customer to company
    ## 1 opposite to 0
    payment_type  =  models.IntegerField(default = 0)

    def __str__(self):
        try :
            return self.g_user.name + " مدفوعة ل  " + self.t_user.user.first_name
        except :
            return "  "

##################################################################################################







##################### define models for the sandwich itself

## اسماء السنتدوتشات
class Sandwich(models.Model):
    objects = models.Manager()
    # name = models.CharField(default="", max_length=64)
    sandwich_type = models.ForeignKey('Sandwich_Type' , on_delete = models.SET_NULL, null =True)
    katchab = models.ForeignKey('Katchab' , on_delete = models.SET_NULL, null =True)
    bread = models.ForeignKey('Bread_Type' , on_delete = models.SET_NULL, null =True)
    packet = models.ForeignKey('Packet' , on_delete = models.SET_NULL, null =True)
    unit_sell_price = models.FloatField(default = 0.0)

    @property
    def unit_cost_price(self):
        stup = kup = bup = pup = 0
        if self.sandwich_type != None:
            stup = self.sandwich_type.old_unit_buy_price if self.sandwich_type.amount_old != 0 else self.sandwich_type.new_unit_buy_price

        if self.katchab != None:
            kup = self.katchab.old_unit_buy_price if self.katchab.amount_old != 0 else self.katchab.new_unit_buy_price

        if self.bread != None:
            bup = self.bread.old_unit_buy_price if self.bread.amount_old != 0 else self.bread.new_unit_buy_price

        if self.packet != None:
            pup = self.packet.old_unit_buy_price if self.packet.amount_old != 0 else self.packet.new_unit_buy_price

        return  round(( stup + kup + bup + pup) , 3)




    def __str__(self):
        if self.sandwich_type != None:
            return self.sandwich_type.name

## السنتدوتشات اليومية
class DaySandwich(models.Model):
    objects = models.Manager()
    number = models.IntegerField()
    total_cost = models.FloatField(default=0.0)
    total_return = models.FloatField(default=0.0)
    profit = models.FloatField(default=0.0)
    date = models.DateTimeField(default = now)
    sandwich = models.ForeignKey('Sandwich' , on_delete = models.SET_NULL, null =True)


    def __str__(self):
        return  self.sandwich.sandwich_type.name + " -- " + str(self.number) +" -- date: " +str(self.date)



### 1. bread type
class Bread_Type(models.Model):
    name = models.CharField(max_length = 264)


    new_packet_cost = models.IntegerField(default = 0.0)
    new_quantity_per_packet = models.IntegerField(default = 0.0)
    new_unit_buy_price = models.FloatField(default = 0)


    old_packet_cost = models.IntegerField(default = 0.0)
    old_quantity_per_packet = models.IntegerField(default = 0.0)
    old_unit_buy_price = models.FloatField(default = 0)
    amount_new = models.IntegerField(default=0)
    amount_old = models.IntegerField(default=0)


    @property
    def total_cost(self):
        if self.total_quantity > 0:
            return   ( self.amount_new * self.new_unit_buy_price)  +  ( self.amount_old * self.old_unit_buy_price)
        else:
            return 0


    @property
    def total_quantity(self):
        return  self.amount_old + self.amount_new

    def subtract(self, amount):
        r = 0
        ## check enough amount :
        if self.total_quantity >= amount :
            if self.amount_old >= amount:
                self.amount_old -= amount
                amount = 0
            elif self.amount_old != 0 :
                self.amount_old -=0
                amount = amount-r
            else:
                self.amount_new -= amount
                amount = 0
            if amount !=0 :
                self.amount_new -= amount
            self.save()

            return True
        else :
            return False

    def __str__(self):
        return self.name



### 2. packet type
class Packet(models.Model):
    name = models.CharField(max_length = 264)

    new_packet_cost = models.IntegerField(default = 0.0)
    new_quantity_per_packet = models.IntegerField(default = 0.0)
    new_unit_buy_price = models.FloatField(default = 0)


    old_packet_cost = models.IntegerField(default = 0.0)
    old_quantity_per_packet = models.IntegerField(default = 0.0)
    old_unit_buy_price = models.FloatField(default = 0)
    amount_new = models.IntegerField(default=0)
    amount_old = models.IntegerField(default=0)


    @property
    def total_cost(self):
        if self.total_quantity > 0:
            return   ( self.amount_new * self.new_unit_buy_price)  +  ( self.amount_old * self.old_unit_buy_price)
        else:
            return 0



    @property
    def total_quantity(self):
        return  self.amount_old + self.amount_new

    def subtract(self, amount):
        r = 0
        if self.total_quantity >= amount :
            if self.amount_old >= amount:
                self.amount_old -= amount
                amount = 0
            elif self.amount_old != 0 :
                self.amount_old -=0
                amount = amount-r
            else:
                self.amount_new -= amount
                amount = 0
            if amount !=0 :
                self.amount_new -= amount
            self.save()

            ##success
            return True
        else:
            return False

    def __str__(self):
        return self.name


### 3. sandwich type -  name
class Sandwich_Type(models.Model):
    name = models.CharField(max_length = 264)

    new_packet_cost = models.IntegerField(default = 0.0)
    new_quantity_per_packet = models.IntegerField(default = 0.0)
    new_unit_buy_price = models.FloatField(default = 0)


    old_packet_cost = models.IntegerField(default = 0.0)
    old_quantity_per_packet = models.IntegerField(default = 0.0)
    old_unit_buy_price = models.FloatField(default = 0)
    amount_new = models.IntegerField(default=0)
    amount_old = models.IntegerField(default=0)


    @property
    def total_cost(self):
        if self.total_quantity > 0:
            return   ( self.amount_new * self.new_unit_buy_price)  +  ( self.amount_old * self.old_unit_buy_price)
        else:
            return 0



    @property
    def total_quantity(self):
        return  self.amount_old + self.amount_new

    def subtract(self, amount):
        r = 0
        ## check enough amount :
        if self.total_quantity >= amount :
            if self.amount_old >= amount:
                self.amount_old -= amount
                amount = 0
            elif self.amount_old != 0 :
                self.amount_old -=0
                amount = amount-r
            else:
                self.amount_new -= amount
                amount = 0
            if amount !=0 :
                self.amount_new -= amount
            self.save()
            return True
        else :
            return False


    def __str__(self):

        return self.name


### 4. katchab type
class Katchab(models.Model):
    name = models.CharField(max_length = 264)

    new_packet_cost = models.IntegerField(default = 0.0)
    new_quantity_per_packet = models.IntegerField(default = 0.0)
    new_unit_buy_price = models.FloatField(default = 0)


    old_packet_cost = models.IntegerField(default = 0.0)
    old_quantity_per_packet = models.IntegerField(default = 0.0)
    old_unit_buy_price = models.FloatField(default = 0)
    amount_new = models.IntegerField(default=0)
    amount_old = models.IntegerField(default=0)


    @property
    def total_cost(self):
        if self.total_quantity > 0:
            return   ( self.amount_new * self.new_unit_buy_price)  +  ( self.amount_old * self.old_unit_buy_price)
        else:
            return 0



    @property
    def total_quantity(self):
        return  self.amount_old + self.amount_new



    def subtract(self, amount):
        r = 0
        ## check enough amount :
        if self.total_quantity >= amount :
            if self.amount_old >= amount:
                self.amount_old -= amount
                amount = 0
            elif self.amount_old != 0 :
                self.amount_old -=0
                amount = amount-r
            else:
                self.amount_new -= amount
                amount = 0
            if amount !=0 :
                self.amount_new -= amount
            self.save()
            return True
        else :
            return False

    def __str__(self):
        return self.name
