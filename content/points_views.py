from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Sandwich, DaySandwich, Product, Safe_data, withdrawings,Current_manager,Trader, Trader_Product, Trader_Payment
from .models import Point, Point_User, Point_Product, Point_User_Payment, Safe_Month,Point_Product_Sellings
from .models import Customer, Customer_Bill, Customer_Payment, Store_To_Point_Product

from django.utils import timezone
from django.db.models import Sum,Q


@login_required
def points(request):
    points = Point.objects.all().order_by("name")
    total_points_buy = round( sum(p.total_money_buy for p in points) , 1)
    total_points_sell = round(sum(p.total_money_sell for p in points), 1)

    context = {
        'points':points,
        'total_points_buy':total_points_buy,
        'total_points_sell':total_points_sell,

    }
    return render(request, 'content/points.html',context)

@login_required
def add_new_point(request):
    if request.method == "POST":
        try:
            name = request.POST['point_name']
            point = Point.objects.get(name = name)
            ## if success failed = 1
            failed = 1
            print("existing point")

        except :
            failed = 0
            Point.objects.create(name = name)
            print("new point")
    return redirect('content:points')

@login_required
def point_page(request, point_id):
    from_date = to_date =  timezone.now().date()
    if request.method == "POST":
        from_date = request.POST['from_date']
        to_date = request.POST['to_date']
    date = timezone.now().date()
    point = Point.objects.get(id = point_id)
    today_date = timezone.now().date()

    bills = Customer_Bill.objects.filter(point_product_sellings__Point = point,given_status = 1 , date__date = today_date , bill_type = 0)
    total_bills = 0.0
    if bills != None:
        total_bills_cost =  round( sum((bill.required_amount)  for bill in bills) , 1)
        total_bills_given =  round( sum((bill.given_amount)  for bill in bills) , 1)
        total_bills_remaining =  round( sum((bill.remaining_amount)  for bill in bills) , 1)


    # restored_bills = Point_Product_Sellings.objects.filter(Point = point,taken_status = 1 , date__date = today_date , line_type = 1)
    # restored_total_bills = 0.0
    # if restored_bills != None:
    #     restored_total_bills_sell =  round( sum((bill.restored_amount_cost_ad)  for bill in bills) , 1)
    #     restored_total_bills_buy =  round( sum((bill.restored_amount_cost_buy)  for bill in bills) , 1)

    ## withdrawing goods on this day
    today_point_products = Store_To_Point_Product.objects.filter(date__date__gte = from_date,date__date__lte = to_date, point = point, line_type = 0).order_by('-date')
    today_dept = 0
    if today_point_products != None:
        today_dept = round(sum(tpp.line_cost  for tpp in today_point_products) , 1)


    all_products = Point_Product.objects.filter(Point = point).order_by("trader_product__product__name")
    all_products_count =len( all_products )
    total_dept = 0
    if all_products != None:
        total_dept = round(sum(p.current_quantity_cost_buy for p in all_products) , 1)

    # ## current_manager date
    # today_date =  timezone.now().date()
    # user = Current_manager.objects.filter(user = request.user).first()
    # all_bills = Point_User_Payment.objects.filter(g_user = point,date__date__gte = user.start_date ,date__date__lte = user.end_date).order_by('-date')
    # bills_amount = 0
    # if all_bills != None:
    #     bills_amount  = round(sum(p.amount for p in all_bills) , 1)
    context = {

        'bills':bills,
        # 'restored_bills':restored_bills,

        'total_bills_selling_cost':total_bills_cost,
        'total_bills_selling_given':total_bills_given,
        'total_bills_selling_remain':total_bills_remaining,
        # 'restored_total_bills_sell':restored_total_bills_sell,
        # 'restored_total_bills_buy':restored_total_bills_buy,

        'point':point,
        'today_point_products':today_point_products,
        'today_dept':today_dept,
        'all_products':all_products,
        'all_products_count':all_products_count,
        'total_dept':total_dept,
        # 'all_bills':all_bills,
        # 'bills_amount':bills_amount,

    }
    return render(request, 'content/point_page.html',context)


@login_required
def point_total_product(request, tpp):

    return render(request, 'content/point_total_product.html')


@login_required
def point_trader_page(request, point_trader_id):

    return render(request, 'content/point_trader_page.html')

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def add_new_point_bill(request):

    failed = success = 0

    today_date = timezone.now().date()
    if request.method == "POST":
        # date = request.POST['date']

        create_new_point_bill(request)

    products = Product.objects.all()
    points = Point.objects.all()
    products_in_store = []
    for product in products :
        product_in_store = Trader_Product.objects.filter(~Q(quantity = 0, quantity_packet = 0)).filter(product = product).order_by('-production_date')
        products_in_store.append(product_in_store)


    ##  get current lines
    current_lines = Store_To_Point_Product.objects.filter(line_type = 0 , given_status = 0)
    total_buy = round(sum(c.total_quantity * c.trader_product.unit_buy_price_ad for c in current_lines) , 2)
    total_sell = round(sum(c.total_quantity * c.unit_sell_price for c in current_lines) , 2)
    context = {
        'failed':failed,
        'success':success,
        'products':products,
        'points':points,
        'products_in_store':products_in_store,

        'current_lines':current_lines,
        'total_buy':total_buy,
        'total_sell':total_sell,

    }
    return render(request, 'content/add_new_point_bill.html', context)



def create_new_point_bill(request):
    ##get come from trader_product
    trader_product = Trader_Product.objects.get(id = int(request.POST['bill_id']) )
    point = Point.objects.get(id = int(request.POST['point_id']))




    ## 3. check amount
    quantity = int(request.POST['quantity'])
    quantity_packet = int(request.POST['quantity_packet'])
    total_q = quantity + (quantity_packet * trader_product.quantity_per_packet)
    if total_q <= trader_product.total_quantity_in_store :
        ##3.1 subtract from original line
        trader_product.subtract_from_product(quantity, quantity_packet)
        ## create new point bill line
        ## . create point product realted to it or create new one
        q,r = divmod(quantity ,trader_product.quantity_per_packet )

        quantity = r
        quantity_packet += q

        unit_sell_price = float(request.POST['selling_price'])
        Store_To_Point_Product.objects.create(trader_product = trader_product , point= point, unit_sell_price = unit_sell_price,
                                quantity = quantity , quantity_packet = quantity_packet )



    return redirect("content:add_new_point_bill")

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def delete_point_bill_line(request, line_id):
    line = Store_To_Point_Product.objects.get(id = line_id)
    ## restore amount to trader_product line
    line.trader_product.add_to_product(line.quantity, line.quantity_packet)
    line.delete()

    return redirect('content:add_new_point_bill')

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def edit_point_bill_line(request, line_id):
    # print(request.POST) ## this is a restored line
    line = Store_To_Point_Product.objects.get(id = line_id)
    new_quantity =  int(request.POST['quantity'])
    new_quantity_packet = int(request.POST['quantity_packet'])

    total_new_q = new_quantity + (new_quantity_packet * line.trader_product.quantity_per_packet)

    l_quantity_old = line.total_quantity
    temp_diff = total_new_q - l_quantity_old

    if temp_diff <= line.trader_product.total_quantity_in_store :
        line.quantity =new_quantity
        line.quantity_packet =new_quantity_packet
        line.unit_sell_price = float(request.POST['unit_sell_price'])
        line.point = Point.objects.get(id = int(request.POST['point_id']))
        line.save()

        ## edit origanl come from line
        if temp_diff < 0 :
            line.trader_product.add_to_product(abs(temp_diff), 0)

        elif temp_diff > 0 :
            line.trader_product.subtract_from_product((temp_diff), 0)




    return redirect('content:add_new_point_bill')


@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def confirm_add_point_bill(request, bill_id):
    ##  get current lines
    current_lines = Store_To_Point_Product.objects.filter(line_type = 0 , given_status = 0)
    for line in current_lines :
        ##get relevant point product row  or create a new one
        try :
            point_product = Point_Product.objects.get(trader_product = line.trader_product , Point = line.point)

        except :
            ## create a new one
            Point_Product.objects.create(trader_product = line.trader_product , Point = line.point)
            point_product = Point_Product.objects.get(trader_product = line.trader_product , Point = line.point)

        ## move data from line to point product
        point_product.total_quantity_fixed += line.total_quantity
        point_product.date = line.date
        point_product.unit_sell_price = line.unit_sell_price
        point_product.save()

        point_product.add_to_product(line.quantity, line.quantity_packet)


    ## update lines to be given
    current_lines.update(given_status = 1)
    return redirect('content:add_new_point_bill')



## update point payments
@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def add_new_point_sellings(request, point_id):
    failed = success = 0
    point = Point.objects.get(id = point_id)

    selected_customer = None
    if request.method == "POST":
        create_new_customer_point_bill(request)
        selected_customer = Customer.objects.get(id = int(request.POST['customer_id']))



    products = Product.objects.all()

    products_in_point = []
    products_in_point_2 = []
    for product in products :
        product_in_point = Point_Product.objects.filter(~Q(quantity = 0, quantity_packet = 0)).filter(trader_product__product = product, Point = point).order_by('-trader_product__production_date')
        if len(product_in_point) > 0 :
            products_in_point.append(product_in_point)
            products_in_point_2.append(product_in_point.first().trader_product.product)


    customers = Customer.objects.all().order_by("name")
    current_bill = Customer_Bill.objects.filter(point_product_sellings__Point = point, customer = selected_customer, given_status = 0).distinct().last()
    if current_bill == None :
        current_bill = Customer_Bill.objects.filter( given_status = 0, bill_type = 0, point_product_sellings__Point = point).last()
    context = {
        'point':point,
        'failed':failed,
        'success':success,
        # 'products':products,
        'products':products_in_point_2,
        'products_in_point':products_in_point,
        'customers':customers,
        'selected_customer':selected_customer,
        'current_bill':current_bill,



    }
    return render(request, 'content/add_new_point_sellings.html', context)


def create_new_customer_point_bill(request):
    ##1. get come from trader_product
    point_product = Point_Product.objects.get(id = int(request.POST['bill_id']) )
    point = point_product.Point
    selected_customer = Customer.objects.get(id = int(request.POST['customer_id']))
    manager = Current_manager.objects.get(user = request.user)
    ##2. create new customer bill or get existing one
    try :
        current_bill = Customer_Bill.objects.get( customer = selected_customer, given_status = 0, bill_type = 0)

    except:
        Customer_Bill.objects.create( manager = manager, customer = selected_customer, given_status = 0, bill_type = 0)
        current_bill = Customer_Bill.objects.filter(customer = selected_customer, given_status = 0, bill_type = 0).last()


    ## 3. check amount
    quantity = int(request.POST['quantity'])
    quantity_packet = int(request.POST['quantity_packet'])
    total_q = quantity + (quantity_packet * point_product.quantity_per_packet)

    ## create new point product selling line
    if total_q <= point_product.total_quantity :
        ##3.1 subtract from original line
        point_product.subtract_from_product(quantity, quantity_packet)
        ## create new point bill line
        ## . create point product realted to it or create new one
        q,r = divmod(quantity ,point_product.quantity_per_packet )

        quantity = r
        quantity_packet += q
        unit_sell_price = float(request.POST['selling_price'])
        discount_per_unit = float(request.POST['discount_per_unit'])

        Point_Product_Sellings.objects.create(point_product = point_product , Point= point,bill = current_bill,
                                                quantity = quantity , quantity_packet = quantity_packet, unit_sell_price = unit_sell_price ,
                                                discount_per_unit = discount_per_unit)



    return redirect("content:add_new_point_sellings", point.id)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def delete_customer_point_bill_line(request, line_id):
    line = Point_Product_Sellings.objects.get(id = line_id)
    ## restore amount to trader_product line
    point_product = Point_Product.objects.get(point_product_sellings = line ,Point = line.Point )
    point_product.add_to_product(line.quantity, line.quantity_packet)
    line.delete()

    return redirect('content:add_new_point_sellings',point_product.Point.id)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def edit_customer_point_bill_line(request, line_id):
    # print(request.POST) ## this is a restored line
    line = Point_Product_Sellings.objects.get(id = line_id)
    point_product = Point_Product.objects.get(point_product_sellings = line ,Point = line.Point )

    new_quantity =  int(request.POST['quantity'])
    new_quantity_packet = int(request.POST['quantity_packet'])

    total_new_q = new_quantity + (new_quantity_packet * point_product.quantity_per_packet)

    l_quantity_old = line.total_quantity_sold
    temp_diff = total_new_q - l_quantity_old

    # print("temp_diff %d  pp_tq %d" %(temp_diff ,point_product.total_quantity ))
    if temp_diff <= point_product.total_quantity :
        line.quantity =new_quantity
        line.quantity_packet =new_quantity_packet
        line.save()

        ## edit origanl come from line
        if temp_diff < 0 :
            point_product.add_to_product(abs(temp_diff), 0)

        elif temp_diff > 0 :
            point_product.subtract_from_product((temp_diff), 0)




    return redirect('content:add_new_point_sellings', line.Point.id)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def confirm_customer_point_bill(request, bill_id):
    ## 1. if discount > 0 remove it from bills
    discount = float(request.POST['discount'])
    given_money_amount = float(request.POST['given_money_amount'])
    customer = Customer.objects.get(id = int(request.POST['customer_id']))
    current_bill = Customer_Bill.objects.get(id = bill_id)
    point = current_bill.point


    if ( discount +  given_money_amount ) <= customer.remaining_money :
        if discount > 0:
            remove_discount_from_bills(request , discount, customer)

        if given_money_amount > 0:
            add_amount_to_bills(request , given_money_amount, customer)

            ## create new customer payment and map it to safe
            add_payment(request, customer,given_money_amount , discount , point)

        current_bill.given_status = 1
        current_bill.save()
        ## update lines to be given
        current_bill.all_lines.update(taken_status = 1)

    return redirect('content:add_new_point_sellings',point.id)


def remove_discount_from_bills(request, discount,customer):

    bills = Customer_Bill.objects.filter(customer = customer, paid_status = 0)
    for bill in bills :
        print("find bills for discount")
        if discount >= bill.remaining_amount:
            discount -=  bill.remaining_amount
            bill.discount += bill.remaining_amount
            bill.paid_status = 1
            bill.save()
        ## amount < bill.cost or amount = 0
        ## create new bill with the remaing money and make old given =1
        elif discount != 0:
            ## create new one
            # Trader_Product.objects.create(product = bill.product ,manager =bill.manager ,trader = trader, total_cost = amount_loop, total_cost_old = amount_loop, date=date,given_status =1)
            bill.discount += discount
            bill.save()
            discount = 0
            break

def add_amount_to_bills(request, amount, customer):
    bills = Customer_Bill.objects.filter(customer = customer, paid_status = 0)
    for bill in bills :
        print("find bills for amount")
        if amount >= bill.remaining_amount:
            amount -=  bill.remaining_amount
            bill.given_amount += bill.remaining_amount
            bill.paid_status = 1
            bill.save()
        ## amount < bill.cost or amount = 0
        ## create new bill with the remaing money and make old given =1
        elif amount != 0:
            ## create new one
            # Trader_Product.objects.create(product = bill.product ,manager =bill.manager ,trader = trader, total_cost = amount_loop, total_cost_old = amount_loop, date=date,given_status =1)
            bill.given_amount += amount
            bill.save()
            amount = 0
            break

def add_payment(request, customer, amount , discount, point):
    ## update customer given - remaining_money
    ## create customer payment
    print("creating new payment bills ")
    manager = Current_manager.objects.get(user = request.user)
    Customer_Payment.objects.create(g_user = customer, t_user=manager, date= timezone.now(), amount = amount
                    ,discount = discount, previos_amount = customer.remaining_money + discount + amount , current_amount = customer.remaining_money   , payment_type = 0)



    m_safe = Safe_Month.objects.last()
    ## m_safe
    m_safe.money += amount
    m_safe.save()

    ## create new bill given
    Point_User_Payment.objects.create(g_user = point, t_user=manager, date= timezone.now(), amount = amount )
    ## 2. safe_date
    notes = " مبيعات نقطة " + point.name
    Safe_data.objects.create(day = timezone.now(), money_amount = amount, given_person =manager, notes=notes , safe_line_status = 6 )





@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def add_new_point_payments(request,point_id):
    failed = success = 0
    point = Point.objects.get(id = point_id)
    today_date = timezone.now()
    ## get all bills give status = 0 and relate to this point
    bills = Customer_Bill.objects.filter(point_product_sellings__Point = point,given_status = 0).distinct()

    if request.method == "POST":
        amount = float(request.POST['total_money'])
        customer = Customer.objects.get(id = int(request.POST['customer_id']))
        # amount_loop = amount
        if amount <= customer.remaining_money and amount >= 0 :
            bill = Customer_Bill.objects.get(id = int(request.POST['bill_id']) )
            ## update bill lines
            bill.all_lines.update(taken_status = 1)

            if bill.required_amount == amount  or (bill.required_amount - amount) <= .01:
                bill.paid_status = 1

            bill.given_amount += amount
            ##3. update all bills taken status = 1
            bill.given_status = 1
            bill.save()


            ## update customer given - remaining_money
            ## create customer payment
            manager = Current_manager.objects.get(user = request.user)
            Customer_Payment.objects.create(g_user = customer, t_user=manager, date= timezone.now(), amount = amount
                            ,discount = bill.main_discount, previos_amount = customer.remaining_money + bill.main_discount , current_amount = customer.remaining_money - amount  , payment_type = 0)

            m_safe = Safe_Month.objects.last()


            ## m_safe
            m_safe.money +=amount


            ## create new bill given
            Point_User_Payment.objects.create(g_user = point, t_user=manager, date= today_date, amount = amount )
            ## 2. safe_date
            notes = " مبيعات نقطة " + point.name
            Safe_data.objects.create(day = today_date, money_amount = amount, given_person =manager, notes=notes , safe_line_status = 6 )




            m_safe.save()
            success = 1

        else :
            failed =1


    managers = Current_manager.objects.filter(end_date__gte = today_date.date() )

    context = {
        'failed':failed,
        'success':success,
        'managers':managers,
        'point':point,

        'bills':bills,
        # 'total':total,
    }
    return render(request, 'content/add_new_point_payments.html',context)


@login_required
def add_new_point_seller(request):

    return render(request, 'content/add_new_point_seller.html')



@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def restore_point_bill_sell(request, bill_id):
    bill = Point_Product_Sellings.objects.get(id =bill_id )
    point = bill.Point
    cust_bill = Customer_Bill.objects.filter(point_product_sellings__Point = point,given_status = 0).first()
    customer = cust_bill.customer

    ###
    customer.total_money -= bill.required_amount
    customer.save()
    customer.normalize()


    ## remove this wrong bill
    bill.delete()
    current_ulr = str((request.META['HTTP_REFERER']))
    if 'add_new_point_sellings' in current_ulr :
        return redirect('content:add_new_point_sellings',point.id)
    else :
        return redirect('content:add_new_point_payments',point.id)



@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def restore_point_product_store(request , point_id):
    point = Point.objects.get(id = point_id)
    success = failed = old_quantity = new_quantity =  0
    point = Point.objects.get(id = point_id)

    if request.method == "POST":
        create_new_restored_point_bill(request)



    products = Product.objects.all()

    products_in_point = []
    products_in_point_2 = []
    for product in products :
        product_in_point = Point_Product.objects.filter(~Q(quantity = 0, quantity_packet = 0)).filter(trader_product__product = product, Point = point).order_by('-trader_product__production_date')
        if len(product_in_point) > 0 :
            products_in_point.append(product_in_point)
            products_in_point_2.append(product_in_point.first().trader_product.product)


    ##  get current lines
    current_lines = Store_To_Point_Product.objects.filter(line_type = 1 , given_status = 0, point=point)
    total_buy = round(sum(c.total_quantity * c.trader_product.unit_buy_price_ad for c in current_lines) , 2)
    total_sell = round(sum(c.total_quantity * c.unit_sell_price for c in current_lines) , 2)

    context = {
        'point':point,
        'failed':failed,
        'success':success,
        'products':products_in_point_2,

        'products_in_point':products_in_point,

        'current_lines':current_lines,
        'total_buy' : total_buy,
        'total_sell' : total_sell,


    }
    return render(request, 'content/restore_point_product_store.html', context)


def create_new_restored_point_bill(request):
    ##get come from trader_product
    point_product = Point_Product.objects.get(id = int(request.POST['bill_id']) )
    point = point_product.Point




    ## 3. check amount
    quantity = int(request.POST['quantity'])
    quantity_packet = int(request.POST['quantity_packet'])
    total_q = quantity + (quantity_packet * point_product.quantity_per_packet)
    if total_q <= point_product.total_quantity :
        ##3.1 subtract from original line
        point_product.subtract_from_product(quantity, quantity_packet)
        ## create new point bill line
        ## . create point product realted to it or create new one
        q,r = divmod(quantity ,point_product.quantity_per_packet )

        quantity = r
        quantity_packet += q


        Store_To_Point_Product.objects.create(trader_product = point_product.trader_product , point= point,
                                quantity = quantity , quantity_packet = quantity_packet, line_type=1  )



    return redirect("content:restore_point_product_store", point.id)



@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def delete_restored_point_bill_line(request, line_id):
    line = Store_To_Point_Product.objects.get(id = line_id)
    ## restore amount to trader_product line
    point_product = Point_Product.objects.get(trader_product = line.trader_product ,Point = line.point )
    point_product.add_to_product(line.quantity, line.quantity_packet)
    line.delete()

    return redirect('content:restore_point_product_store',point_product.Point.id)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def edit_restored_point_bill_line(request, line_id):
    # print(request.POST) ## this is a restored line
    line = Store_To_Point_Product.objects.get(id = line_id)
    new_quantity =  int(request.POST['quantity'])
    new_quantity_packet = int(request.POST['quantity_packet'])

    total_new_q = new_quantity + (new_quantity_packet * line.trader_product.quantity_per_packet)

    l_quantity_old = line.total_quantity
    temp_diff = total_new_q - l_quantity_old

    point_product = Point_Product.objects.get(trader_product = line.trader_product ,Point = line.point )
    # print("temp_diff %d  pp_tq %d" %(temp_diff ,point_product.total_quantity ))
    if temp_diff <= point_product.total_quantity :
        line.quantity =new_quantity
        line.quantity_packet =new_quantity_packet
        line.save()

        ## edit origanl come from line
        if temp_diff < 0 :
            point_product.add_to_product(abs(temp_diff), 0)

        elif temp_diff > 0 :
            point_product.subtract_from_product((temp_diff), 0)




    return redirect('content:restore_point_product_store', line.point.id)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def confirm_restored_point_bill(request, point_id):
    ##  get current lines
    current_lines = Store_To_Point_Product.objects.filter(line_type = 1 , given_status = 0, point = point_id)

    for line in current_lines :
        line.trader_product.add_to_product(line.quantity, line.quantity_packet)


    ## update lines to be given
    current_lines.update(given_status = 1)
    return redirect('content:restore_point_product_store',point_id)






@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def point_to_point_product(request , point_id):
    point = Point.objects.get(id = point_id)
    success = failed = old_quantity = new_quantity =  0

    if request.method == "POST":
        create_new_point_to_point_bill(request)



    products = Product.objects.all()

    products_in_point = []
    products_in_point_2 = []
    for product in products :
        product_in_point = Point_Product.objects.filter(~Q(quantity = 0, quantity_packet = 0)).filter(trader_product__product = product, Point = point).order_by('-trader_product__production_date')
        if len(product_in_point) > 0 :
            products_in_point.append(product_in_point)
            products_in_point_2.append(product_in_point.first().trader_product.product)


    ##  get current lines
    current_lines = Store_To_Point_Product.objects.filter(line_type = 2 , given_status = 0, point=point)
    total_buy = round(sum(c.total_quantity * c.trader_product.unit_buy_price_ad for c in current_lines) , 2)
    total_sell = round(sum(c.total_quantity * c.unit_sell_price for c in current_lines) , 2)

    points = Point.objects.all().exclude(id = point.id).exclude(name__in = ['manager' , 'stuff'])
    context = {
        'point':point,
        'points':points,
        'failed':failed,
        'success':success,
        'products':products_in_point_2,

        'products_in_point':products_in_point,
        'current_lines':current_lines,
        'total_buy' : total_buy,
        'total_sell' : total_sell,

    }
    return render(request, 'content/point_to_point_product.html', context)



def create_new_point_to_point_bill(request):
    ##get come from trader_product
    point_product = Point_Product.objects.get(id = int(request.POST['bill_id']) )
    point = point_product.Point
    to_point = Point.objects.get(id = int(request.POST['point_id']))



    ## 3. check amount
    quantity = int(request.POST['quantity'])
    quantity_packet = int(request.POST['quantity_packet'])
    total_q = quantity + (quantity_packet * point_product.quantity_per_packet)
    if total_q <= point_product.total_quantity :
        ##3.1 subtract from original line
        point_product.subtract_from_product(quantity, quantity_packet)
        ## create new point bill line
        ## . create point product realted to it or create new one
        q,r = divmod(quantity ,point_product.quantity_per_packet )

        quantity = r
        quantity_packet += q

        unit_sell_price = float(request.POST['selling_price'])
        Store_To_Point_Product.objects.create(trader_product = point_product.trader_product ,point = point,  to_point= to_point , unit_sell_price = unit_sell_price
                                ,quantity = quantity , quantity_packet = quantity_packet, line_type = 2  )



    return redirect("content:point_to_point_product", point.id)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def delete_point_to_point_bill_line(request, line_id):
    line = Store_To_Point_Product.objects.get(id = line_id)
    ## restore amount to trader_product line
    point_product = Point_Product.objects.get(trader_product = line.trader_product ,Point = line.point )
    point_product.add_to_product(line.quantity, line.quantity_packet)
    line.delete()

    return redirect('content:point_to_point_product',point_product.Point.id)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def edit_point_to_point_bill_line(request, line_id):
    # print(request.POST) ## this is a restored line
    line = Store_To_Point_Product.objects.get(id = line_id)
    new_quantity =  int(request.POST['quantity'])
    new_quantity_packet = int(request.POST['quantity_packet'])

    total_new_q = new_quantity + (new_quantity_packet * line.trader_product.quantity_per_packet)

    l_quantity_old = line.total_quantity
    temp_diff = total_new_q - l_quantity_old

    point_product = Point_Product.objects.get(trader_product = line.trader_product ,Point = line.point )
    # print("temp_diff %d  pp_tq %d" %(temp_diff ,point_product.total_quantity ))
    if temp_diff <= point_product.total_quantity :
        line.quantity =new_quantity
        line.quantity_packet =new_quantity_packet
        line.unit_sell_price = float(request.POST['selling_price'])
        line.to_point = Point.objects.get(id = int(request.POST['point_id']))
        line.save()

        ## edit origanl come from line
        if temp_diff < 0 :
            point_product.add_to_product(abs(temp_diff), 0)

        elif temp_diff > 0 :
            point_product.subtract_from_product((temp_diff), 0)




    return redirect('content:point_to_point_product', line.point.id)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def confirm_point_to_point_bill(request, point_id):
    ##  get current lines
    current_lines = Store_To_Point_Product.objects.filter(line_type = 2 , given_status = 0, point = point_id)

    for line in current_lines :
        ##get relevant point product row  or create a new one
        try :
            point_product = Point_Product.objects.get(trader_product = line.trader_product , Point = line.to_point)

        except :
            ## create a new one
            Point_Product.objects.create(trader_product = line.trader_product , Point = line.to_point)
            point_product = Point_Product.objects.get(trader_product = line.trader_product , Point = line.to_point)

        ## move data from line to point product
        point_product.total_quantity_fixed += line.total_quantity
        point_product.date = line.date
        point_product.unit_sell_price = line.unit_sell_price
        point_product.save()

        point_product.add_to_product(line.quantity, line.quantity_packet)


    ## update lines to be given
    current_lines.update(given_status = 1)
    return redirect('content:point_to_point_product',point_id)





@login_required
def all_discount_bills(request):
    bills_with_discount = get_all_bills_with_discount(request)

    total_discounts = sum(b.total_discount for b in bills_with_discount )
    context= {
        'bills':bills_with_discount,
        'total_discounts':total_discounts,

    }
    return render(request, 'content/all_discount_bills.html', context)

def get_all_bills_with_discount(request):
    cur_m = Current_manager.objects.get(user = request.user)
    bills_with_discount = Customer_Bill.objects.filter(given_status = 1, bill_type = 0, date__date__gte = cur_m.start_date, date__date__lte = cur_m.end_date)

    result = []
    # result.append(bill for bill in un_paid_bills if bill.remaining_amount < 0 )
    for bill in bills_with_discount:
        if bill.total_discount > 0:
            result.append(bill)

    return result

def normalize_product_v(product, old_q , new_q):
    ## normalize product
    lq,lqp,nq,nqp = (0,0,0,0)
    if product.quantity_per_packet :
        nqp , nq = divmod(new_q , product.quantity_per_packet)

    if product.last_quantity_per_packet :
        lqp , lq = divmod(old_q , product.last_quantity_per_packet)


    return (lq, lqp, nq, nqp)
