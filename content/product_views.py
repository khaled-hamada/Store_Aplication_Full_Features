from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Sandwich, DaySandwich, Product, Safe_data, withdrawings,Current_manager,Trader, Trader_Product, Trader_Payment
from .models import Point, Point_User, Point_Product, Point_User_Payment, Safe_Month,Point_Product_Sellings
from .models import Trader_Bill, Measurement_Unit, Sub_Product

from django.utils import timezone
from django.db.models import Sum,Q


from getmac import get_mac_address as gma
Computer_Mac_Address = '5C:b9:01:43:f1:28'

@login_required
def product_page(request, product_id):
    product = Product.objects.get(id = product_id)

    if request.method == "POST":
        trader = Trader.objects.get(id = int(request.POST['trader_id']))
        try :
            product_trader =  Trader_Product.objects.filter(product = product, trader = trader)
            if len(product_trader) > 0 : ## ie this trader is already mapped to this product previously
                print("trader already exists")
            else :
                print("add a new trader")
                product.trader.add(trader)

        except :
            print("errors occurs")
    product_sellers = Trader_Product.objects.filter(product = product).values_list('trader').distinct()
    product_sellers_names = set()
    for tp in product_sellers:
        product_sellers_names.add(Trader.objects.get(id = tp[0]))

    # print(product_sellers)
    # print(product_sellers_names)
    product_transactions = Trader_Product.objects.filter(product = product).order_by('-date')
    traders = Trader.objects.all()
    product_in_store = Trader_Product.objects.filter(~Q(quantity = 0, quantity_packet = 0)).filter(product = product).order_by('expiration_date')
    product_in_points = Point_Product.objects.filter(~Q(quantity = 0, quantity_packet = 0)).filter(trader_product__product = product).order_by('trader_product__expiration_date')
    context = {
        'p':product,
        'point_product':product,

        'product_sellers':product_sellers_names,

        'product_transactions':product_transactions,
        'traders':traders,

        'product_in_store':product_in_store,
        'product_in_points':product_in_points,

    }
    return render(request, 'content/product_page.html',context)



@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def update_product(request, trader_id):
    failed = success = 0
    trader = Trader.objects.get( id = trader_id)
    manager = Current_manager.objects.get(user= request.user)
    ## create new bill
    ## get current trader bill un given

    if request.method == "POST":
        product_id = int(request.POST['product_id'])
        product = Product.objects.get(id = product_id)
        if product != None:
            # date = request.POST['date']
            date = timezone.now()
            new_amount =  int(request.POST['quantity'])
            quantity_packet =  int(request.POST['quantity_packet'])
            packet_price =  float(request.POST['packet_price'])
            quantity_per_packet =  int(request.POST['quantity_per_packet'])
            discount_per_packet =  float(request.POST['discount_per_packet'])

            q,r = divmod(new_amount, quantity_per_packet)

            quantity_packet += q
            new_amount = r
            production_date =  (request.POST['from_date']) if request.POST['from_date'] != "" else timezone.now()
            expiration_date =  (request.POST['to_date']) if request.POST['to_date'] != "" else timezone.now()

            product_image = request.FILES['product_image'] if 'product_image' in request.FILES else None
            total_q = new_amount + (quantity_packet * quantity_per_packet )
            total_product_cost  = (( new_amount / quantity_per_packet ) + quantity_packet ) * packet_price
            total_product_cost = round(total_product_cost , 2)

            total_discount  = ((new_amount / quantity_per_packet)  + quantity_packet ) * discount_per_packet
            trader.total_money += round ( total_product_cost -total_discount , 2)
            trader.save()


            try :
                ctb = Trader_Bill.objects.get(manager = manager, trader = trader , given_status = 0, bill_type = 0)

            except :
                 Trader_Bill.objects.create( manager = manager, trader = trader , given_status = 0, bill_type = 0)
                 ctb = Trader_Bill.objects.get(manager = manager,trader = trader , given_status = 0, bill_type = 0)

            print("new trader product")
            print((total_product_cost))
            Trader_Product.objects.create( trader = trader , product = product,trader_bill = ctb,  date = date , quantity = new_amount ,quantity_packet = quantity_packet
                                            , product_image  = product_image,
                                            discount_per_packet = discount_per_packet, quantity_per_packet = quantity_per_packet, packet_price = packet_price,
                                             production_date = production_date, expiration_date = expiration_date, total_quantity_fixed = total_q)


            success = 1

        else:
             failed = 1

    products = Product.objects.filter(trader = trader).distinct()
    try :
        ctb = Trader_Bill.objects.get(manager = manager, trader = trader , given_status = 0, bill_type = 0)

    except :
        ctb = None
    context = {'products':products , 'failed':failed, 'success':success, "trader":trader , "current_bill":ctb, }
    # print( len(products))
    return render(request, 'content/update_product.html',context = context)



@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def delete_trader_bill_line(request, line_id):
    line = Trader_Product.objects.get(id = line_id)
    trader = line.trader
    trader.total_money -= line.required_amount
    trader.save()


    line.delete()

    return redirect('content:update_product', trader.id)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def edit_trader_bill_line(request, line_id):
    # print(request.POST)
    line = Trader_Product.objects.get(id = line_id)
    trader = line.trader
    trader.total_money -= line.required_amount
    trader.save()

    line.quantity =  int(request.POST['quantity'])
    line.quantity_packet =  int(request.POST['quantity_packet'])
    line.packet_price =  float(request.POST['packet_price'])
    line.quantity_per_packet =  int(request.POST['quantity_per_packet'])
    line.discount_per_packet =  float(request.POST['discount_per_packet'])

    if request.POST['from_date'] != "":
        line.production_date =  (request.POST['from_date'])

    if request.POST['to_date'] != "" :
        line.expiration_date =  (request.POST['to_date'])

    line.save()
    line.total_quantity_fixed = line.quantity + (line.quantity_packet * line.quantity_per_packet )
    line.save()

    trader.total_money += line.required_amount
    trader.save()


    return redirect('content:update_product', trader.id)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def confirm_add_trader_bill(request, bill_id):


    bill = Trader_Bill.objects.get(id = bill_id)
    given_money_amount = float(request.POST['given_money_amount'])
    discount = float(request.POST['discount'])
    ## get current manager safe
    m_safe = Safe_Month.objects.last()
    manager = Current_manager.objects.get(user = request.user)
    if (given_money_amount + discount) <= bill.required_amount and m_safe.money >= given_money_amount:
        ##1. update bill
        bill.bill_file = request.FILES['bill_file']
        bill.given_amount += given_money_amount
        bill.discount += discount
        bill.notes = request.POST['notes']
        bill.given_status = 1
        bill.all_lines.update(given_status = 1)
        if (given_money_amount + discount) == bill.required_amount :
            bill.paid_status = 1
        bill.save()

        ##2. update trader
        trader = bill.trader
        trader.total_money -= discount
        trader.given_money += given_money_amount
        trader.save()
        #
        ##3. create new bill

        notes =" -- اسم التاجر -- "+trader.name
        previos_amount = trader.remaining_money + discount + given_money_amount
        Trader_Payment.objects.create(date = timezone.now(), discount = discount, amount = given_money_amount, reciever = trader , sender= manager, notes=notes
                                , previos_amount = previos_amount , current_amount = trader.remaining_money    )
        ##4. create new treasure entry
        if given_money_amount > 0:
            Safe_data.objects.create(day = timezone.now(), money_amount = -given_money_amount, given_person = manager, notes=notes, safe_line_status = 3 )
            ## update save_month
            m_safe.money -= given_money_amount
            m_safe.save()

    return redirect('content:update_product', bill.trader.id)








def make_sure_a_correct_product(p):
    if '.' in p and len(p.split('.',1)) == 2:
        products = Product.objects.all()
        p_name = p.split('.',1)[1]
        p_id = p.split('.',1)[0]
        for p in products:
            if p_name == p.name:
                if p_id.isdigit():
                    return True
                else:
                    return False
    return False


@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def new_product_type(request):
    traders = Trader.objects.all()

    failed = 0
    if request.method == "POST":
        product_name = request.POST['product_name']


        descreption = request.POST['descreption']
        try :
            product_image = request.FILES['product_image']
        except :
            product_image = None
        ## create and save new product
        trader = Trader.objects.filter(id = int(request.POST['trader_id'])).first()

        ## check tyhat product is not in the database i.e not in the store  ---> a new product really
        try:
            prod = Product.objects.get(name = product_name)
            ## if success failed = 1
            failed = 1
            print("existing product")

        except :
            failed = 0
            print("new product")

        if failed ==0 :
                p = Product(name = product_name, descreption = descreption, product_image = product_image )

                p.save()
                # p.total_quantity +=((quantity_packet *  p.quantity_per_packet))
                p.save()
                p.trader.add(trader)




                return redirect('content:trader_page', trader.id)

    context = {
        'traders':traders,
        'failed':failed,

    }
    return render(request, 'content/new_product_type.html',context = context)



@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def add_new_mu(request):
    Measurement_Unit.objects.create(name = request.POST['unit_name'])
    return redirect('content:new_product_type')


@login_required
@user_passes_test(lambda u: u.groups.filter(name='managers').count() != 0, login_url='content:denied_page')
def delete_mu(request):
    Measurement_Unit.objects.get(id = int(request.POST['mu_id'])).delete()
    return redirect('content:new_product_type')




@login_required
@user_passes_test(lambda u: u.groups.filter(name='NoOne').count() != 0, login_url='content:denied_page')
def reduce_product_amount_store(request, product_id):
    product = Product.objects.get(id =product_id )
    if request.method == "POST":
        try :
            quantity = int(request.POST['new_quantity'])
            quantity_packet = int(request.POST['new_quantity_packet'])
        except :
            quantity = quantity_packet = 0
        try :
            last_quantity_packet = int(request.POST['last_quantity_packet'])
            last_quantity = int(request.POST['last_quantity'])
        except :
            last_quantity_packet  = last_quantity =0


        ##  check validation
        new_amount = quantity + (quantity_packet * product.quantity_per_packet)
        old_amount = last_quantity + (last_quantity_packet * product.last_quantity_per_packet)
        if new_amount <= product.amount_new and old_amount <= product.amount_old :
            product.subtract_from_product(last_quantity,last_quantity_packet, quantity, quantity_packet )
            ## reduced amount cost
            total_cost = product.calculate_cost(last_quantity, last_quantity_packet, quantity, quantity_packet )



    context ={
        'product' : product,
    }
    return render(request, "content/reduce_product_amount_store.html", context = context)
